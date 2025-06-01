from django.conf import settings
from django.db import models

# Create your models here.
class Cash(models.Model):
    user_id = models.IntegerField()  # 유저 PK만 저장
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def deposit(self, amount):
        self.balance += amount
        self.save()

    def withdraw(self, amount):
        if self.balance >= amount:
            self.balance -= amount
            self.save()

            return True
        return False

    def __str__(self):
        return f"{self.user_id} - Balance: {self.balance}"

class CashTransfer(models.Model):
    sender_id = models.IntegerField()
    receiver_id = models.IntegerField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    memo = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender_id} → {self.receiver_id}: {self.amount}원"


#쓰임
class CashTransaction(models.Model):
    TRANSACTION_TYPES = (
        ('deposit', '입금'),
        ('withdraw', '출금'),
        ('transfer', '송금'),  # ✅ 튜플 형식!
    )
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)

    amount = models.DecimalField(max_digits=12, decimal_places=2)

    user_id = models.IntegerField()
    memo = models.CharField(max_length=255, blank=True, null=True)
    related_transfer = models.ForeignKey(
        'CashTransfer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transactions'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.get_transaction_type_display()}] {self.user_id} - {self.amount}원"

