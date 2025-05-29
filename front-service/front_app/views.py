from django.shortcuts import render
from django.views.generic import TemplateView

class IndexView(TemplateView):
    template_name = 'main.html'

class MainTemplateView(TemplateView):
    template_name = 'main.html'

class RegisterTemplateView(TemplateView):
    template_name = 'register.html'

class LoginTemplateView(TemplateView):
    template_name = 'login.html'

class MyPageTemplateView(TemplateView):
    template_name = 'mypage.html'

class CashDepositTemplateView(TemplateView):
    template_name = 'deposit.html'

class DepositCompleteTemplateView(TemplateView):
    template_name = 'deposit-complete.html'

class CashWithdrawTemplateView(TemplateView):
    template_name = 'withdraw.html'

class WithdrawCompleteTemplateView(TemplateView):
    template_name = 'withdraw-complete.html'

class CashTransferTemplateView(TemplateView):
    template_name = 'transfer.html'

class TransferCompleteTemplateView(TemplateView):
    template_name = 'transfer-complete.html'

class AllTransactionTemplateView(TemplateView):
    template_name = 'account.html'

class OTPSetupTemplateView(TemplateView):
    template_name = 'otp_setup.html'

class UnregisterTemplateView(TemplateView):
    template_name = 'unregister.html'

def bandit_report_view(request):
    return render(request, 'bandit_report.html')
