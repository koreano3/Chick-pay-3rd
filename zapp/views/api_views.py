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
from zapp.models import Cash, CashTransaction, CashTransfer, CustomUser
from zapp.serializers import (
    LoginSerializer,RegisterSerializer, MyPageSerializer,
    CashTransactionSerializer, TransferSerializer, UnregisterPasswordCheckSerializer
)

import pyotp
import logging
logger = logging.getLogger("transaction")

@csrf_exempt
def health_check(request):
    return HttpResponse("OK", content_type="text/plain", status=200)

class MainAPIView(APIView):
    def get(self, request):
        return Response({"message": "Welcome to the API main endpoint."})

class RegisterAPIView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        try:
            if serializer.is_valid():
                with transaction.atomic():  # 💥 여기!
                    user = serializer.save()
                    Cash.objects.create(user=user, balance=0)
                return Response({"message": "Registration successful"}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except IntegrityError:
            return Response({"error": "이미 존재하는 이메일입니다."}, status=status.HTTP_400_BAD_REQUEST)

class LoginAPIView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            return Response({"message": "로그인 성공!"}, status=200)
        
        return Response(serializer.errors, status=400)
        
class MyPageAPIView(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            serializer = MyPageSerializer(request.user)
            return Response(serializer.data)
        else:
            # 로그인하지 않은 경우 기본 정보 반환
            return Response({
                "name": "사용자",
                "email": "user@example.com",
                "birthdate": "1990-01-01",
                "balance": 10000.00
            })

class PasswordChangeAPIView(APIView):
    def post(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "로그인이 필요합니다."}, status=status.HTTP_401_UNAUTHORIZED)
            
        # 사용자로부터 받은 데이터
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')

        # 현재 비밀번호 확인
        if not request.user.check_password(current_password):
            return Response({"error": "현재 비밀번호가 일치하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 새 비밀번호와 확인 비밀번호 일치 여부 확인
        if new_password != confirm_password:
            return Response({"error": "새 비밀번호와 확인 비밀번호가 일치하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 비밀번호 변경
        request.user.set_password(new_password)
        request.user.save()

        return Response({"message": "비밀번호가 성공적으로 변경되었습니다."}, status=status.HTTP_200_OK)

class CashDepositAPIView(APIView):
    def post(self, request):
        if request.user.is_authenticated:
            cash, _ = Cash.objects.get_or_create(user=request.user)
            serializer = CashTransactionSerializer(data=request.data)

            if serializer.is_valid():
                amount = serializer.validated_data['amount']
                try:
                    with transaction.atomic():
                        cash.deposit(amount)
                        CashTransaction.objects.create(
                            user=request.user,
                            transaction_type='deposit',
                            amount=amount,
                            memo=request.data.get('memo', '')
                        )
                    return Response({
                        "message": "입금 성공",
                        "balance": cash.balance
                    }, status=status.HTTP_200_OK)
                except Exception as e:
                    return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            # 로그인하지 않은 경우 데모 응답
            return Response({
                "message": "입금 성공 (데모)",
                "balance": 10000.00
            }, status=status.HTTP_200_OK)

class CashWithdrawAPIView(APIView):
    def post(self, request):
        if request.user.is_authenticated:
            cash, _ = Cash.objects.get_or_create(user=request.user)
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
                            user=request.user,
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
        else:
            # 로그인하지 않은 경우 데모 응답
            return Response({
                "message": "출금 성공 (데모)",
                "balance": 10000.00
            }, status=status.HTTP_200_OK)

class CashTransferAPIView(APIView):
    def post(self, request):
        if request.user.is_authenticated:
            serializer = TransferSerializer(data=request.data, context={'request': request})

            if not serializer.is_valid():
                return Response(serializer.errors, status=400)

            sender = request.user
            receiver = CustomUser.objects.get(email=serializer.validated_data['receiver_email'])
            amount = serializer.validated_data['amount']
            memo = serializer.validated_data.get('memo', '')

            try:
                with transaction.atomic():
                    # 💡 비즈니스 로직: 잔액 부족
                    if sender.cash.balance < amount:
                        logger.warning(f"[INSUFFICIENT_FUNDS] user_id={sender.id}, amount={amount}")
                        raise ValidationError("잔액이 부족합니다.")

                    # 💸 실제 송금 처리
                    sender.cash.withdraw(amount)
                    receiver.cash.deposit(amount)


                    transfer = CashTransfer.objects.create(
                        sender=sender,
                        receiver=receiver,
                        amount=amount,
                        memo=memo
                    )

                    CashTransaction.objects.bulk_create([
                        CashTransaction(
                            user=sender,
                            transaction_type='transfer',
                            amount=amount,
                            memo=f"{receiver.email}님에게 송금",
                            related_transfer=transfer
                        ),
                        CashTransaction(
                            user=receiver,
                            transaction_type='deposit',
                            amount=amount,
                            memo=f"{sender.email}로부터 입금",
                            related_transfer=transfer
                        ),
                    ])

                    logger.info(
                        f"[TRANSACTION_SUCCESS] transfer_id={transfer.id}, "
                        f"sender_id={sender.id}, receiver_id={receiver.id}, amount={amount}"
                    )

                    return Response({"message": "송금 완료!"}, status=200)

            except Exception as e:
                logger.error(
                    f"[TRANSACTION_FAIL] user_id={sender.id}, "
                    f"receiver_email={serializer.validated_data['receiver_email']}, "
                    f"amount={amount}, error={str(e)}"
                )
                return Response({"error": "서버 오류가 발생했습니다."}, status=500)
        else:
            # 로그인하지 않은 경우 데모 응답
            return Response({"message": "송금 완료 (데모)!"}, status=200)

class AllTransactionAPIView(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            transactions = CashTransaction.objects.filter(user=request.user).order_by('-created_at')
            serializer = CashTransactionSerializer(transactions, many=True)
            return Response(serializer.data)
        else:
            # 로그인하지 않은 경우 빈 리스트 반환
            return Response([])

class UnregisterAPIView(APIView):
    def delete(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "로그인이 필요합니다."}, status=status.HTTP_401_UNAUTHORIZED)
            
        serializer = UnregisterPasswordCheckSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)  # ❗ 여기서 비번 검증함

        request.user.delete()
        return Response({"message": "회원탈퇴 완료"}, status=status.HTTP_204_NO_CONTENT)
