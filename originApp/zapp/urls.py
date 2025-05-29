# # urls.py
# from django.urls import path
# from .views.web_views import (
#     MainTemplateView,
#     RegisterTemplateView,
#     LoginTemplateView,
#     MyPageTemplateView,
#     CashDepositTemplateView,
#     DepositCompleteTemplateView,
#     CashWithdrawTemplateView,
#     WithdrawCompleteTemplateView,
#     CashTransferTemplateView,
#     TransferCompleteTemplateView,
#     AllTransactionTemplateView,
#     OTPSetupTemplateView,
#     UnregisterTemplateView,
#     bandit_report_view,
# )
# from .views.api_views import (
#     MainAPIView,
#     RegisterAPIView,
#     LoginAPIView,
#     MyPageAPIView,
#     PasswordChangeAPIView,
#     CashDepositAPIView,
#     CashWithdrawAPIView,
#     CashTransferAPIView,
#     AllTransactionAPIView,
#     UnregisterAPIView,
#     OTPVerifyAPIView,
# )
# from django.contrib.auth.views import LogoutView

# urlpatterns = [
#     # Template (HTML) views
#     path('', MainTemplateView.as_view(), name='main'),
#     path('register/', RegisterTemplateView.as_view(), name='register'),
#     path('login/', LoginTemplateView.as_view(), name='login'),
#     path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
#     path('mypage/', MyPageTemplateView.as_view(), name='mypage'),
#     path('cash/deposit/', CashDepositTemplateView.as_view(), name='cash-deposit'),
#     path('cash/deposit/complete/', DepositCompleteTemplateView.as_view(), name='deposit-complete'),
#     path('cash/withdraw/', CashWithdrawTemplateView.as_view(), name='cash-withdraw'),
#     path('cash/withdraw/complete/', WithdrawCompleteTemplateView.as_view(), name='withdraw-complete'),
#     path('cash/transfer/', CashTransferTemplateView.as_view(), name='cash-transfer'),
#     path('cash/transfer/complete/', TransferCompleteTemplateView.as_view(), name='transfer-complete'),
#     path('account/', AllTransactionTemplateView.as_view(), name='account'),
#     path('otp/setup/', OTPSetupTemplateView.as_view(), name='otp-setup'),
#     path('mypage/unregister/', UnregisterTemplateView.as_view(), name='unregister'),
#     path("bandit/", bandit_report_view, name="bandit-report"),

#     # API views
#     path('api/main/', MainAPIView.as_view(), name='api-main'),
#     path('api/register/', RegisterAPIView.as_view(), name='api-register'),
#     path('api/login/', LoginAPIView.as_view(), name='api-login'),
#     path('api/mypage/', MyPageAPIView.as_view(), name='api-mypage'),
#     path('api/change-password/', PasswordChangeAPIView.as_view(), name='api-change-password'),
#     # path('api/cash/', CashDetailAPIView.as_view(), name='api-cash-detail'),
#     path('api/cash/deposit/', CashDepositAPIView.as_view(), name='api-cash-deposit'),
#     path('api/cash/withdraw/', CashWithdrawAPIView.as_view(), name='api-cash-withdraw'),
#     path('api/cash/transfer/', CashTransferAPIView.as_view(), name='api-cash-transfer'),
#     path('api/transactions/', AllTransactionAPIView.as_view(), name='api-transactions'),
#     path('api/unregister/', UnregisterAPIView.as_view(), name='api-unregister'),
#     path('api/otp/verify/', OTPVerifyAPIView.as_view(), name='api-otp-verify')
# ]
