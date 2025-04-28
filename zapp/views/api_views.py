# 임시테스트 ▽지워야함 
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


# views_api.py
from django.contrib.auth import authenticate, login
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import redirect
from django.contrib import messages
from django.db import transaction , IntegrityError

from zapp.models import Cash, CashTransaction, CashTransfer, CustomUser
from zapp.serializers import (
    RegisterSerializer, MyPageSerializer, CashSerializer,
    CashTransactionSerializer, TransferSerializer
)
from django.db import transaction
import pyotp

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
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({"error": "이메일과 비밀번호를 모두 입력하세요."}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            request.session['otp_verified'] = False  # ✅ 로그인 성공하면 otp_verified = False로 초기화
            return Response({"message": "로그인 성공!"})
        else:
            return Response({"error": "이메일 또는 비밀번호가 틀렸습니다."}, status=401)
        
class MyPageAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = MyPageSerializer(request.user)
        return Response(serializer.data)

class PasswordChangeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
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
    permission_classes = [IsAuthenticated]

    def post(self, request):
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


class CashWithdrawAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
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

class CashTransferAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TransferSerializer(data=request.data, context={'request': request})

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)  # ✅ 오류는 serializer가 다 들고 있음

        sender = request.user
        receiver = CustomUser.objects.get(email=serializer.validated_data['receiver_email'])  # validate에서 이미 체크 끝났음
        amount = serializer.validated_data['amount']
        memo = serializer.validated_data.get('memo', '')

        try:
            with transaction.atomic():
                sender.cash.withdraw(amount)
                receiver.cash.deposit(amount)

                transfer = CashTransfer.objects.create(
                    sender=sender,
                    receiver=receiver,
                    amount=amount,
                    memo=memo
                )

                CashTransaction.objects.bulk_create([
                    CashTransaction(user=sender, transaction_type='transfer', amount=amount, memo=f"{receiver.email}님에게 송금", related_transfer=transfer),
                    CashTransaction(user=receiver, transaction_type='deposit', amount=amount, memo=f"{sender.email}로부터 입금", related_transfer=transfer),
                ])

                return Response({"message": "송금 완료!"}, status=200)

        except Exception as e:
            return Response({"error": "서버 오류가 발생했습니다."}, status=500)
        
        
class OTPVerifyAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        otp_code = request.data.get('otp_code')

        if not user.otp_secret:
            return Response({"error": "OTP 설정이 안 되어 있습니다."}, status=400)

        totp = pyotp.TOTP(user.otp_secret)

        if totp.verify(otp_code):
            request.session['otp_verified'] = True  # ✅ OTP 인증 성공했으면 True로 변경
            return Response({"message": "인증 성공"}, status=200)
        else:
            return Response({"error": "OTP 인증 실패"}, status=400)


class AllTransactionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        transactions = CashTransaction.objects.filter(user=request.user).order_by('-created_at')
        serializer = CashTransactionSerializer(transactions, many=True)
        return Response(serializer.data)



class UnregisterAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        request.user.delete()
        return Response({"message": "회원탈퇴 완료"}, status=status.HTTP_204_NO_CONTENT)
