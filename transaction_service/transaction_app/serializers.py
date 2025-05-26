from rest_framework import serializers
from django.contrib.auth import get_user_model
from transaction_app.models import CashTransaction

class CashTransactionSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("금액은 0보다 커야 합니다.")
        return value
    
class TransferSerializer(serializers.Serializer):
    receiver_email = serializers.EmailField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    memo = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def validate(self, data):
        request = self.context['request']
        sender = request.user

        # 1. 본인에게 송금 불가
        if sender.email == data['receiver_email']:
            raise serializers.ValidationError({"receiver_email": "자기 자신에게 송금할 수 없습니다."})

        # 2. 받는 사람 존재 여부
        try:
            receiver = CustomUser.objects.get(email=data['receiver_email'])
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError({"receiver_email": "받는 사람을 찾을 수 없습니다."})

        # 3. 송금액 > 0
        if data['amount'] <= 0:
            raise serializers.ValidationError({"amount": "송금액은 0보다 커야 합니다."})

        # 4. 잔액 부족
        if sender.cash.balance < data['amount']:
            raise serializers.ValidationError({"amount": "잔액이 부족합니다."})

        return data 