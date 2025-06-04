import re
from rest_framework import serializers
from django.contrib.auth import get_user_model , password_validation





# 💰 캐시 정보 Serializer (조회용)
# class CashSerializer(serializers.ModelSerializer):
#     email = serializers.EmailField(source='user.email', read_only=True)

#     class Meta:
#         model = Cash
#         fields = ['name', 'user', 'email', 'balance', 'created_at', 'updated_at']
#         read_only_fields = ['nane' ,'user', 'email', 'balance', 'created_at', 'updated_at']


# 💸 캐시 충전/사용 Serializer 이거 쓰임
class CashTransactionSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("금액은 0보다 커야 합니다.")
        return value

#쓰임
class TransferSerializer(serializers.Serializer):
    receiver_email = serializers.EmailField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    memo = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def validate(self, data):
        # 3. 송금액 > 0
        if data['amount'] <= 0:
            raise serializers.ValidationError({"amount": "송금액은 0보다 커야 합니다."})
        return data

