# 임시테스트 ▽지워야함 
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse


# views_api.py
from django.contrib.auth import authenticate, login
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.exceptions import ValidationError
from django.shortcuts import redirect
from django.contrib import messages
from django.db import transaction , IntegrityError
from django.views.decorators.csrf import csrf_exempt
from transaction_app.models import Cash, CashTransaction, CashTransfer
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
        cash, created = Cash.objects.get_or_create(user_id=user_id)
        print("====[DEBUG] Cash created?:", created, "Cash object:", cash)
        cash.balance += Decimal(str(amount))
        cash.save()

        CashTransaction.objects.create(
            user_id=user_id,
            transaction_type='deposit',
            amount=amount,
            memo=memo
        )

        return Response({"message": "입금 성공", "balance": cash.balance})


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
                    if not cash.withdraw(amount):
                        return Response({"error": "잔액 부족"}, status=400)

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
    # permission_classes = [IsAuthenticated]  # 제거

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

        # 본인 송금 불가 (user-service에 API 요청해서 sender_email 조회)
        sender_email = ... # user-service에서 sender_id로 이메일 조회
        if sender_email == receiver_email:
            return Response({"error": "자기 자신에게 송금할 수 없습니다."}, status=400)

        # 잔액 부족
        sender_cash, _ = Cash.objects.get_or_create(user_id=sender_id)
        if sender_cash.balance < amount:
            return Response({"error": "잔액이 부족합니다."}, status=400)

        # 3. user-service에 receiver 존재 확인 (API 호출)
        response = requests.get(
            'http://user-service-host/api/user/exists/',
            params={'email': receiver_email}
        )
        if response.status_code != 200 or not response.json().get('exists'):
            return Response({"error": "받는 사람을 찾을 수 없습니다."}, status=400)
        receiver_id = response.json().get('user_id')  # user-service에서 user_id 반환하도록 구현 필요

        # 4. 거래 처리 (sender_id, receiver_id만 사용)
        # ... Cash, CashTransaction 등에서 user_id 필드로만 처리

        # 예시:
        sender_cash.balance -= amount
        receiver_cash, _ = Cash.objects.get_or_create(user_id=receiver_id)
        receiver_cash.balance += amount
        sender_cash.save()
        receiver_cash.save()

        # 거래 내역 기록
        transfer = CashTransfer.objects.create(
            sender_id=sender_id,
            receiver_id=receiver_id,
            amount=amount,
            memo=memo
        )
        # ... CashTransaction 등도 user_id로 기록

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
        payload = jwt.decode(token, options={"verify_signature": False})
        user_id = payload.get('user_id')
        cash, _ = Cash.objects.get_or_create(user_id=user_id)
        return Response({"balance": cash.balance})


class CashDepositCompleteAPIView(APIView):
    def get(self, request):
        # 1. Authorization 헤더에서 토큰 추출
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({"error": "인증 토큰이 없습니다."}, status=401)
        token = auth_header.split(' ')[1]

        # 2. JWT 토큰에서 user_id 추출
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            user_id = payload.get('user_id')
            if not user_id:
                return Response({"error": "user_id 없음"}, status=401)
        except Exception as e:
            return Response({"error": "토큰 파싱 실패"}, status=401)

        # 3. 사용자 정보 조회 (user-service API 호출)
        try:
            user_response = requests.get(
                f"{settings.USER_SERVICE_URL}/zapp/api/mypage/",
                headers={"Authorization": f"Bearer {token}"}
            )
            if not user_response.ok:
                return Response({"error": "사용자 정보 조회 실패"}, status=400)
            user_data = user_response.json()
        except Exception as e:
            return Response({"error": "사용자 서비스 연결 실패"}, status=500)

        # 4. 입금 내역 조회
        cash = Cash.objects.get_or_create(user_id=user_id)[0]
        recent_deposits = CashTransaction.objects.filter(
            user_id=user_id,
            transaction_type='deposit'
        ).order_by('-created_at')[:5]

        # 5. 응답 데이터 구성
        response_data = {
            "name": user_data.get("name", ""),
            "email": user_data.get("email", ""),
            "balance": float(cash.balance),
            "previous_balance": float(cash.balance) - float(recent_deposits[0].amount) if recent_deposits else float(cash.balance),
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
        # 1. Authorization 헤더에서 토큰 추출
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({"error": "인증 토큰이 없습니다."}, status=401)
        token = auth_header.split(' ')[1]

        # 2. JWT 토큰에서 user_id 추출
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            user_id = payload.get('user_id')
            if not user_id:
                return Response({"error": "user_id 없음"}, status=401)
        except Exception as e:
            return Response({"error": "토큰 파싱 실패"}, status=401)

        # 3. 사용자 정보 조회 (user-service API 호출)
        try:
            user_response = requests.get(
                f"{settings.USER_SERVICE_URL}/zapp/api/mypage/",
                headers={"Authorization": f"Bearer {token}"}
            )
            if not user_response.ok:
                return Response({"error": "사용자 정보 조회 실패"}, status=400)
            user_data = user_response.json()
        except Exception as e:
            return Response({"error": "사용자 서비스 연결 실패"}, status=500)

        # 4. 출금 내역 조회
        cash = Cash.objects.get_or_create(user_id=user_id)[0]
        recent_withdraws = CashTransaction.objects.filter(
            user_id=user_id,
            transaction_type='withdraw'
        ).order_by('-created_at')[:5]

        # 5. 응답 데이터 구성
        response_data = {
            "name": user_data.get("name", ""),
            "email": user_data.get("email", ""),
            "balance": float(cash.balance),
            "previous_balance": float(cash.balance) + float(recent_withdraws[0].amount) if recent_withdraws else float(cash.balance),
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


