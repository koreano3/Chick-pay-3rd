from django.urls import path
from .views.api_views import (
    CashDepositAPIView,
    CashWithdrawAPIView,
    CashTransferAPIView,
    AllTransactionAPIView,
)

urlpatterns = [
    # ✅ API endpoints (prefix: /api/)
    path('api/cash/deposit/', CashDepositAPIView.as_view(), name='api-cash-deposit'),
    path('api/cash/withdraw/', CashWithdrawAPIView.as_view(), name='api-cash-withdraw'),
    path('api/cash/transfer/', CashTransferAPIView.as_view(), name='api-cash-transfer'),
    path('api/transactions/', AllTransactionAPIView.as_view(), name='api-transactions'),
]
