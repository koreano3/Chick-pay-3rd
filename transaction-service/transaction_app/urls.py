from django.urls import path
from .views import (
    CashDepositAPIView, 
    CashWithdrawAPIView, 
    CashTransferAPIView, 
    AllTransactionAPIView, 
    CashInfoAPIView,
    CashDepositCompleteAPIView,
    CashWithdrawCompleteAPIView
)

urlpatterns = [
    path('api/cash/info/', CashInfoAPIView.as_view(), name='api-cash-info'),
    path('api/cash/deposit/', CashDepositAPIView.as_view(), name='api-cash-deposit'),
    path('api/cash/deposit/complete/', CashDepositCompleteAPIView.as_view(), name='api-cash-deposit-complete'),
    path('api/cash/withdraw/', CashWithdrawAPIView.as_view(), name='api-cash-withdraw'),
    path('api/cash/withdraw/complete/', CashWithdrawCompleteAPIView.as_view(), name='api-cash-withdraw-complete'),
    path('api/cash/transfer/', CashTransferAPIView.as_view(), name='api-cash-transfer'),
    path('api/transactions/', AllTransactionAPIView.as_view(), name='api-transactions'),
] 