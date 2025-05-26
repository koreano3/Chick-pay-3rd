from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.views import LogoutView
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from user_app.models import CustomUser
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
import pyotp , json ,qrcode , base64
from io import BytesIO


@csrf_exempt
def health_check(request):
    return HttpResponse("OK", content_type="text/plain", status=200)


class LoginRequired403Mixin(AccessMixin):
    """로그인 안 했으면 403 Forbidden 터뜨리는 Mixin"""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied  # ✅ 403
        return super().dispatch(request, *args, **kwargs)

class OTPRequiredMixin:
    """OTP 인증 여부를 체크하는 Mixin (관리자는 OTP 면제)"""
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:  # ✅ superuser는 OTP 검사 건너뜀
            return super().dispatch(request, *args, **kwargs)

        if not request.session.get('otp_verified', False):
            return redirect('otp-setup')
        return super().dispatch(request, *args, **kwargs)

    
class MainTemplateView(TemplateView):
    template_name = 'main.html'

class RegisterTemplateView(TemplateView):
    template_name = 'register.html'

class LoginTemplateView(TemplateView):
    template_name = 'login.html'

class MyPageTemplateView(LoginRequired403Mixin, OTPRequiredMixin , TemplateView):
    template_name = 'mypage.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        cash = getattr(user, 'cash', None)

        context['name'] = user.name
        context['email'] = user.email
        context['birthdate'] = user.birthdate
        context['balance'] = cash.balance if cash else 0.00
        return context
    
class UnregisterTemplateView(LoginRequired403Mixin,OTPRequiredMixin, TemplateView):
    template_name = 'unregister.html'

# ✅ 실제 동작용 View (웹 페이지 렌더링)
class OTPSetupTemplateView(LoginRequired403Mixin, TemplateView):
    template_name = 'otp_setup.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if not hasattr(user, 'otp_secret') or not user.otp_secret:
            user.otp_secret = pyotp.random_base32()
            user.save()

        totp = pyotp.TOTP(user.otp_secret)
        otp_uri = totp.provisioning_uri(name=user.email, issuer_name="CHICKPAY")

        qr = qrcode.make(otp_uri)
        buffer = BytesIO()
        qr.save(buffer, format='PNG')
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()

        context.update({
            'otp_secret': user.otp_secret,
            'qr_code_url': f'data:image/png;base64,{qr_base64}',
        })

        return context

def custom_403_view(request, exception=None):
    return render(request, '403.html', status=403)
