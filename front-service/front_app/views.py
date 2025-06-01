import base64
from io import BytesIO
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, redirect  # redirect 추가
from django.views.generic import TemplateView
import jwt
import pyotp
import qrcode
from django.contrib.auth.mixins import LoginRequiredMixin


class TokenRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        token = request.COOKIES.get('access_token')
        print("Cookies:", request.COOKIES)  # 쿠키 확인
        print("Token found:", token)        # 토큰 값 확인
        
        if not token:
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)
    
    
    

class MainTemplateView(TemplateView):  # 보호 필요
    template_name = 'main.html'

class RegisterTemplateView(TemplateView):  # 회원가입은 공개
    template_name = 'register.html'

class LoginTemplateView(TemplateView):  # 로그인은 공개
    template_name = 'login.html'

class MyPageTemplateView(TemplateView):  # 보호 필요
    template_name = 'mypage.html'

class CashDepositTemplateView(TemplateView):  # 보호 필요
    template_name = 'deposit.html'

class DepositCompleteTemplateView(TemplateView):  # 보호 필요
    template_name = 'deposit-complete.html'

class CashWithdrawTemplateView(TemplateView):  # 보호 필요
    template_name = 'withdraw.html'

class WithdrawCompleteTemplateView(TemplateView):  # 보호 필요
    template_name = 'withdraw-complete.html'

class CashTransferTemplateView(TemplateView):  # 보호 필요
    template_name = 'transfer.html'

class TransferCompleteTemplateView( TemplateView):  # 보호 필요
    template_name = 'transfer-complete.html'

class AllTransactionTemplateView( TemplateView):  # 보호 필요
    template_name = 'account.html'

class OTPSetupTemplateView(TemplateView):  # 이미 적용됨
    template_name = 'otp_setup.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        return context

class UnregisterTemplateView(TemplateView):  # 보호 필요
    template_name = 'unregister.html'

def bandit_report_view(request):  # 함수 기반 뷰는 데코레이터 사용 필요
    token = request.COOKIES.get('access_token')
    if not token:
        return redirect('login')
    return render(request, 'bandit_report.html')