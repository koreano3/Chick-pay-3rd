from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.exceptions import ValidationError
from django.db import transaction
from django.contrib.auth import get_user_model

from transaction_app.models import Cash, CashTransaction, CashTransfer
from transaction_app.serializers import CashTransactionSerializer, TransferSerializer

import logging
logger = logging.getLogger("transaction")


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
                return Response({"message": "입금 성공", "balance": cash.balance}, status=status.HTTP_200_OK)
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
                    if not cash.withdraw(amount):
                        return Response({"error": "잔액 부족"}, status=400)

                    CashTransaction.objects.create(
                        user=request.user,
                        transaction_type='withdraw',
                        amount=amount,
                        memo=request.data.get('memo', '')
                    )
                    return Response({"message": "출금 성공", "balance": cash.balance}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": str(e)}, status=500)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CashTransferAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TransferSerializer(data=request.data, context={'request': request})

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        sender = request.user
        receiver = get_user_model().objects.get(email=serializer.validated_data['receiver_email'])
        amount = serializer.validated_data['amount']
        memo = serializer.validated_data.get('memo', '')

        try:
            with transaction.atomic():
                if sender.cash.balance < amount:
                    logger.warning(f"[INSUFFICIENT_FUNDS] user_id={sender.id}, amount={amount}")
                    raise ValidationError("잔액이 부족합니다.")

                sender.cash.withdraw(amount)
                receiver.cash.deposit(amount)

                transfer = CashTransfer.objects.create(
                    sender=sender, receiver=receiver, amount=amount, memo=memo
                )

                CashTransaction.objects.bulk_create([
                    CashTransaction(user=sender, transaction_type='transfer', amount=amount,
                                    memo=f"{receiver.email}님에게 송금", related_transfer=transfer),
                    CashTransaction(user=receiver, transaction_type='deposit', amount=amount,
                                    memo=f"{sender.email}로부터 입금", related_transfer=transfer),
                ])

                logger.info(f"[TRANSACTION_SUCCESS] transfer_id={transfer.id}")
                return Response({"message": "송금 완료!"}, status=200)
        except Exception as e:
            logger.error(f"[TRANSACTION_FAIL] sender={sender.email}, error={str(e)}")
            return Response({"error": "서버 오류가 발생했습니다."}, status=500)


class AllTransactionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        transactions = CashTransaction.objects.filter(user=request.user).order_by('-created_at')
        serializer = CashTransactionSerializer(transactions, many=True)
        return Response(serializer.data)
