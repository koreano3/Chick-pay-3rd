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

        # 3. 출금 처리
        amount = request.data.get('amount')
        memo = request.data.get('memo', '')

        print(f"user_id: {user_id}")
        print("====[DEBUG] user_id from JWT:", user_id)

        # user-service에 잔액 차감 요청
        response = requests.post(
            f"{settings.USER_SERVICE_URL}/zapp/api/cash/update/",
            json={"user_id": user_id, "amount": amount, "type": "withdraw"}
        )
        if not response.ok:
            return Response({"error": "출금 처리 실패"}, status=500)

        print("====[DEBUG] CashTransaction(출금) 생성 직전 ====")
        CashTransaction.objects.create(
            user_id=user_id,
            transaction_type='withdraw',
            amount=amount,
            memo=memo
        )
        print("====[DEBUG] CashTransaction(출금) 생성 완료 ====")

        # 출금 후 잔액 조회
        user_info = requests.get(
            f"{settings.USER_SERVICE_URL}/zapp/api/mypage/",
            headers={"Authorization": f"Bearer {token}"}
        )
        if not user_info.ok:
            return Response({"error": "잔액 조회 실패"}, status=500)
        balance = user_info.json().get('balance', 0)

        return Response({"message": "출금 성공", "balance": balance})

# class CashTransferAPIView(APIView):
#     def post(self, request):
#         # 1. JWT에서 보내는 사람 user_id 추출
#         auth_header = request.headers.get('Authorization')
#         if not auth_header or not auth_header.startswith('Bearer '):
#             return Response({"error": "인증 토큰이 없습니다."}, status=401)
#         token = auth_header.split(' ')[1]
#         try:
#             payload = jwt.decode(token, options={"verify_signature": False})
#             sender_id = payload.get('user_id')
#             if not sender_id:
#                 return Response({"error": "user_id 없음"}, status=401)
#         except Exception as e:
#             return Response({"error": "토큰 파싱 실패"}, status=401)

#         # 2. 요청 데이터 파싱
#         receiver_email = request.data.get('receiver_email')
#         amount = request.data.get('amount')
#         memo = request.data.get('memo', '')

#         # 3. user-service에서 받는 사람 존재 확인 및 user_id 얻기
#         response = requests.get(
#             f"{settings.USER_SERVICE_URL}/zapp/api/user/exists/",
#             params={'email': receiver_email}
#         )
#         if response.status_code != 200 or not response.json().get('exists'):
#             return Response({"error": "받는 사람을 찾을 수 없습니다."}, status=400)
#         receiver_id = response.json().get('user_id')

#         # 4. user-service에 각각 잔액 차감/증가 요청
#         # 4-1. 보내는 사람 출금
#         withdraw_res = requests.post(
#             f"{settings.USER_SERVICE_URL}/zapp/api/cash/update/",
#             json={"user_id": sender_id, "amount": amount, "type": "withdraw"}
#         )
#         if not withdraw_res.ok:
#             return Response({"error": "보내는 사람 잔액 차감 실패"}, status=500)
#         # 4-2. 받는 사람 입금
#         deposit_res = requests.post(
#             f"{settings.USER_SERVICE_URL}/zapp/api/cash/update/",
#             json={"user_id": receiver_id, "amount": amount, "type": "deposit"}
#         )
#         if not deposit_res.ok:
#             return Response({"error": "받는 사람 잔액 증가 실패"}, status=500)

#         # 5. 거래 내역 기록 (transaction-service DB)
#         CashTransaction.objects.create(
#             user_id=sender_id,
#             transaction_type='transfer',
#             amount=amount,
#             memo=memo
#         )
#         CashTransaction.objects.create(
#             user_id=receiver_id,
#             transaction_type='receive',
#             amount=amount,
#             memo=memo
#         )
#         # 필요하다면 CashTransfer 모델에도 기록

#         return Response({"message": "송금 완료!"}, status=200)

class CashTransferAPIView(APIView):
    def post(self, request):
        # 1. JWT에서 보내는 사람 user_id 추출
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
        receiver_email = request.data.get('receiver_email')
        amount = request.data.get('amount')
        memo = request.data.get('memo', '')

        # 3. user-service에서 받는 사람 존재 확인 및 user_id 얻기
        response = requests.get(
            f"{settings.USER_SERVICE_URL}/zapp/api/user/exists/",
            params={'email': receiver_email}
        )
        if response.status_code != 200 or not response.json().get('exists'):
            return Response({"error": "받는 사람을 찾을 수 없습니다."}, status=400)
        receiver_id = response.json().get('user_id')

        # 4. user-service에 각각 잔액 차감/증가 요청
        withdraw_res = requests.post(
            f"{settings.USER_SERVICE_URL}/zapp/api/cash/update/",
            json={"user_id": sender_id, "amount": amount, "type": "withdraw"}
        )
        if not withdraw_res.ok:
            return Response({"error": "보내는 사람 잔액 차감 실패"}, status=500)
        deposit_res = requests.post(
            f"{settings.USER_SERVICE_URL}/zapp/api/cash/update/",
            json={"user_id": receiver_id, "amount": amount, "type": "deposit"}
        )
        if not deposit_res.ok:
            return Response({"error": "받는 사람 잔액 증가 실패"}, status=500)

        # 5. 거래 내역 기록 (CashTransfer + CashTransaction)
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
            memo=memo,
            related_transfer=transfer
        )
        CashTransaction.objects.create(
            user_id=receiver_id,
            transaction_type='receive',
            amount=amount,
            memo=memo,
            related_transfer=transfer
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
        # JWT에서 user_id 추출
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            user_id = payload.get('user_id')
            if not user_id:
                return Response({"error": "user_id 없음"}, status=401)
        except Exception as e:
            return Response({"error": "토큰 파싱 실패"}, status=401)

        # user-service에서 유저 정보 가져오기
        user_info = requests.get(
            f"{settings.USER_SERVICE_URL}/zapp/api/mypage/",
            headers={"Authorization": f"Bearer {token}"}
        )
        if not user_info.ok:
            return Response({"error": "사용자 정보 조회 실패"}, status=400)
        user_data = user_info.json()

        # 최근 출금 내역 조회
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
                    "transaction_method": tx.memo or "계좌 이체"
                }
                for tx in recent_withdraws
            ]
        }
        return Response(response_data)


class CashTransferCompleteAPIView(APIView):
    def get(self, request):
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

        # user-service에서 유저 정보 가져오기
        user_info = requests.get(
            f"{settings.USER_SERVICE_URL}/zapp/api/mypage/",
            headers={"Authorization": f"Bearer {token}"}
        )
        if not user_info.ok:
            return Response({"error": "사용자 정보 조회 실패"}, status=400)
        user_data = user_info.json()
        sender_email = user_data.get("email", "")

        # 최근 송금(CashTransfer) 내역 1건 조회
        from .models import CashTransfer
        tx = (
            CashTransfer.objects
            .filter(sender_id=user_id)
            .order_by('-created_at')
            .first()
        )
        if not tx:
            return Response({"error": "최근 송금 내역이 없습니다."}, status=404)

        receiver_id = tx.receiver_id

        # user-service에 receiver_id로 유저 정보 요청 (API가 필요!)
        receiver_email = ""
        receiver_name = ""
        receiver_info = requests.get(
            f"{settings.USER_SERVICE_URL}/zapp/api/user/{receiver_id}/",
            headers={"Authorization": f"Bearer {token}"}
        )
        if receiver_info.ok:
            receiver_data = receiver_info.json()
            receiver_email = receiver_data.get("email", "")
            receiver_name = receiver_data.get("name", "")

        response_data = {
            "sender_email": sender_email,
            "receiver_email": receiver_email,
            "receiver_name": receiver_name,
            "amount": float(tx.amount),
            "memo": tx.memo,
            "created_at": tx.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "transaction_id": f"CP{tx.id:013d}",
        }
        return Response(response_data)


