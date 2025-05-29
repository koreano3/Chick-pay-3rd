# urls.py
from django.urls import path
from .views import (
    IndexView,
    MainTemplateView,
    RegisterTemplateView,
    LoginTemplateView,
    MyPageTemplateView,
    CashDepositTemplateView,
    DepositCompleteTemplateView,
    CashWithdrawTemplateView,
    WithdrawCompleteTemplateView,
    CashTransferTemplateView,
    TransferCompleteTemplateView,
    AllTransactionTemplateView,
    OTPSetupTemplateView,
    UnregisterTemplateView,
    bandit_report_view,
)
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', MainTemplateView.as_view(), name='main'),
    path('register/', RegisterTemplateView.as_view(), name='register'),
    path('login/', LoginTemplateView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('mypage/', MyPageTemplateView.as_view(), name='mypage'),
    path('cash/deposit/', CashDepositTemplateView.as_view(), name='cash-deposit'),
    path('cash/deposit/complete/', DepositCompleteTemplateView.as_view(), name='deposit-complete'),
    path('cash/withdraw/', CashWithdrawTemplateView.as_view(), name='cash-withdraw'),
    path('cash/withdraw/complete/', WithdrawCompleteTemplateView.as_view(), name='withdraw-complete'),
    path('cash/transfer/', CashTransferTemplateView.as_view(), name='cash-transfer'),
    path('cash/transfer/complete/', TransferCompleteTemplateView.as_view(), name='transfer-complete'),
    path('account/', AllTransactionTemplateView.as_view(), name='account'),
    path('otp/setup/', OTPSetupTemplateView.as_view(), name='otp-setup'),
    path('mypage/unregister/', UnregisterTemplateView.as_view(), name='unregister'),
    path("bandit/", bandit_report_view, name="bandit-report"),
]
