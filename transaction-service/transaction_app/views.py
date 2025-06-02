# 임시테스트 ▽지워야함 
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse


# views_api.py
from django.contrib.auth import authenticate, login, get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.exceptions import ValidationError
from django.shortcuts import redirect
from django.contrib import messages
from django.db import transaction , IntegrityError
from django.views.decorators.csrf import csrf_exempt
from transaction_app.models import CashTransaction, CashTransfer
from transaction_app.serializers import (
    CashTransactionSerializer, TransferSerializer,
)
from rest_framework_simplejwt.authentication import JWTAuthentication

import pyotp
import logging
import requests
import jwt
from django.conf import settings
from decimal import Decimal

logger = logging.getLogger("transaction")


class CashDepositAPIView(APIView):
    def post(self, request):
        # 1. Authorization 헤더에서 토큰 추출
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({"error": "인증 토큰이 없습니다."}, status=401)
        token = auth_header.split(' ')[1]

        # 2. JWT 토큰에서 user_id 추출
        try:
            payload = jwt.decode(token, options={"verify_signature": False})  # 개발용, 실제 서비스는 키 검증 필요
            user_id = payload.get('user_id')
            if not user_id:
                return Response({"error": "user_id 없음"}, status=401)
        except Exception as e:
            return Response({"error": "토큰 파싱 실패"}, status=401)

        # 3. user_id로 거래 처리
        amount = request.data.get('amount')
        memo = request.data.get('memo', '')

        print(f"user_id: {user_id}") 

        print("====[DEBUG] user_id from JWT:", user_id)
        # 변경: user-service에 잔액 증가 요청
        response = requests.post(
            f"{settings.USER_SERVICE_URL}/zapp/api/cash/update/",
            json={"user_id": user_id, "amount": amount, "type": "deposit"}
        )
        if not response.ok:
            return Response({"error": "입금 처리 실패"}, status=500)


        print("====[DEBUG] CashTransaction 생성 직전 ====")
        CashTransaction.objects.create(
            user_id=user_id,
            transaction_type='deposit',
            amount=amount,
            memo=memo
        )
        print("====[DEBUG] CashTransaction 생성 완료 ====")

        return Response({"message": "입금 성공", "balance": amount})


class CashWithdrawAPIView(APIView):

    def post(self, request):
        # JWT에서 user_id 추출
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({"error": "인증 토큰이 없습니다."}, status=401)
        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            user_id = payload.get('user_id')
            if not user_id:
                return Response({"error": "user_id 없음"}, status=401)
        except Exception as e:
            return Response({"error": "토큰 파싱 실패"}, status=401)

        print(f"user_id: {user_id}") 
        cash, _ = Cash.objects.get_or_create(user_id=user_id)
        serializer = CashTransactionSerializer(data=request.data)

        if serializer.is_valid():
            amount = serializer.validated_data['amount']
            try:
                with transaction.atomic():
                    # 출금 시 잔액이 부족하면 처리하지 않음
                    response = requests.post(
                        f"{settings.USER_SERVICE_URL}/zapp/api/cash/update/",
                        json={"user_id": user_id, "amount": amount, "type": "withdraw"}
                    )
                    if not response.ok:
                        return Response({"error": "출금 처리 실패"}, status=500)

                    # 출금 내역 기록
                    CashTransaction.objects.create(
                        user_id=user_id,
                        transaction_type='withdraw',
                        amount=amount,
                        memo=request.data.get('memo', '')
                    )

                    # 성공적인 출금 후 잔액과 함께 응답 반환
                    return Response({
                        "message": "출금 성공",
                        "balance": cash.balance  # 잔액 반환
                    }, status=status.HTTP_200_OK)

            except Exception as e:
                return Response({"error": str(e)}, status=500)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CashTransferAPIView(APIView):
    def post(self, request):
        # 1. JWT에서 user_id 추출
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({"error": "인증 토큰이 없습니다."}, status=401)
        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            sender_id = payload.get('user_id')
            if not sender_id:
                return Response({"error": "user_id 없음"}, status=401)
        except Exception as e:
            return Response({"error": "토큰 파싱 실패"}, status=401)

        # 2. 요청 데이터 파싱
        serializer = TransferSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        receiver_email = serializer.validated_data['receiver_email']
        amount = serializer.validated_data['amount']
        memo = serializer.validated_data.get('memo', '')

        # 3. user-service에서 sender_email 조회
        sender_info = requests.get(
            f"{settings.USER_SERVICE_URL}/zapp/api/mypage/",
            headers={"Authorization": f"Bearer {token}"}
        )
        if not sender_info.ok:
            return Response({"error": "보내는 사람 정보 조회 실패"}, status=400)
        sender_email = sender_info.json().get('email')
        if sender_email == receiver_email:
            return Response({"error": "자기 자신에게 송금할 수 없습니다."}, status=400)

        # 4. user-service에 receiver 존재 확인 (API 호출)
        response = requests.get(
            f"{settings.USER_SERVICE_URL}/zapp/api/user/exists/",
            params={'email': receiver_email}
        )
        if response.status_code != 200 or not response.json().get('exists'):
            return Response({"error": "받는 사람을 찾을 수 없습니다."}, status=400)
        receiver_id = response.json().get('user_id')

        # 5. 송금(잔액 차감/증가) user-service에 각각 요청
        # 5-1. 보내는 사람 출금
        withdraw_res = requests.post(
            f"{settings.USER_SERVICE_URL}/zapp/api/cash/update/",
            json={"user_id": sender_id, "amount": amount, "type": "withdraw"}
        )
        if not withdraw_res.ok:
            return Response({"error": "보내는 사람 잔액 차감 실패"}, status=500)
        # 5-2. 받는 사람 입금
        deposit_res = requests.post(
            f"{settings.USER_SERVICE_URL}/zapp/api/cash/update/",
            json={"user_id": receiver_id, "amount": amount, "type": "deposit"}
        )
        if not deposit_res.ok:
            return Response({"error": "받는 사람 잔액 증가 실패"}, status=500)

        # 거래 내역 기록 (transaction-service DB)
        transfer = CashTransfer.objects.create(
            sender_id=sender_id,
            receiver_id=receiver_id,
            amount=amount,
            memo=memo
        )
        CashTransaction.objects.create(
            user_id=sender_id,
            transaction_type='transfer',
            amount=amount,
            memo=memo
        )
        CashTransaction.objects.create(
            user_id=receiver_id,
            transaction_type='receive',
            amount=amount,
            memo=memo
        )
        return Response({"message": "송금 완료!"}, status=200)


class AllTransactionAPIView(APIView):
    def get(self, request):
        # JWT에서 user_id 추출
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({"error": "인증 토큰이 없습니다."}, status=401)
        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            user_id = payload.get('user_id')
            if not user_id:
                return Response({"error": "user_id 없음"}, status=401)
        except Exception as e:
            return Response({"error": "토큰 파싱 실패"}, status=401)

        transactions = CashTransaction.objects.filter(user_id=user_id).order_by('-created_at')
        serializer = CashTransactionSerializer(transactions, many=True)
        return Response(serializer.data)


class CashInfoAPIView(APIView):
    def get(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({"error": "인증 토큰이 없습니다."}, status=401)
        token = auth_header.split(' ')[1]
        user_info = requests.get(
            f"{settings.USER_SERVICE_URL}/zapp/api/mypage/",
            headers={"Authorization": f"Bearer {token}"}
        )
        if not user_info.ok:
            return Response({"error": "잔액 조회 실패"}, status=400)
        balance = user_info.json().get('balance', 0)
        return Response({"balance": balance})


class CashDepositCompleteAPIView(APIView):
    def get(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({"error": "인증 토큰이 없습니다."}, status=401)
        token = auth_header.split(' ')[1]
        # JWT에서 user_id 추출
        payload = jwt.decode(token, options={"verify_signature": False})
        user_id = payload.get('user_id')
        if not user_id:
            return Response({"error": "user_id 없음"}, status=401)

        # user-service에서 유저 정보 가져오기
        user_info = requests.get(
            f"{settings.USER_SERVICE_URL}/zapp/api/mypage/",
            headers={"Authorization": f"Bearer {token}"}
        )
        if not user_info.ok:
            return Response({"error": "사용자 정보 조회 실패"}, status=400)
        user_data = user_info.json()

        # 트랜잭션 조회
        recent_deposits = CashTransaction.objects.filter(
            user_id=user_id,
            transaction_type='deposit'
        ).order_by('-created_at')[:5]

        response_data = {
            "name": user_data.get("name", ""),
            "email": user_data.get("email", ""),
            "balance": float(user_data.get("balance", 0)),
            "previous_balance": float(user_data.get("balance", 0)) - float(recent_deposits[0].amount) if recent_deposits else float(user_data.get("balance", 0)),
            "recent_deposits": [
                {
                    "id": str(tx.id),
                    "amount": float(tx.amount),
                    "created_at": tx.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "transaction_method": tx.memo or "계좌 이체"
                }
                for tx in recent_deposits
            ]
        }
        return Response(response_data)


class CashWithdrawCompleteAPIView(APIView):
    def get(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({"error": "인증 토큰이 없습니다."}, status=401)
        token = auth_header.split(' ')[1]
        user_info = requests.get(
            f"{settings.USER_SERVICE_URL}/zapp/api/mypage/",
            headers={"Authorization": f"Bearer {token}"}
        )
        if not user_info.ok:
            return Response({"error": "사용자 정보 조회 실패"}, status=400)
        user_data = user_info.json()
        user_id = user_data.get('id')
        recent_withdraws = CashTransaction.objects.filter(
            user_id=user_id,
            transaction_type='withdraw'
        ).order_by('-created_at')[:5]
        response_data = {
            "name": user_data.get("name", ""),
            "email": user_data.get("email", ""),
            "balance": float(user_data.get("balance", 0)),
            "previous_balance": float(user_data.get("balance", 0)) + float(recent_withdraws[0].amount) if recent_withdraws else float(user_data.get("balance", 0)),
            "recent_withdraws": [
                {
                    "id": str(tx.id),
                    "amount": float(tx.amount),
                    "created_at": tx.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "transaction_method": tx.memo or "계좌 이체",
                    "bank_name": getattr(tx, 'bank_name', None),
                }
                for tx in recent_withdraws
            ]
        }
        return Response(response_data)


