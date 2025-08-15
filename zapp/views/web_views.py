from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.views import LogoutView
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from zapp.models import Cash, CashTransaction, CashTransfer, CustomUser
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
import pyotp , json ,qrcode , base64
from io import BytesIO


@csrf_exempt
def health_check(request):
    return HttpResponse("OK", content_type="text/plain", status=200)


class MainTemplateView(TemplateView):
    template_name = 'main.html'

class RegisterTemplateView(TemplateView):
    template_name = 'register.html'

class LoginTemplateView(TemplateView):
    template_name = 'login.html'

class MyPageTemplateView(TemplateView):
    template_name = 'mypage.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            user = self.request.user
            cash = getattr(user, 'cash', None)
            context['name'] = user.name
            context['email'] = user.email
            context['birthdate'] = user.birthdate
            context['balance'] = cash.balance if cash else 0.00
        else:
            # 로그인하지 않은 경우 기본 정보 제공
            context['name'] = "사용자"
            context['email'] = "user@example.com"
            context['birthdate'] = "1990-01-01"
            context['balance'] = 10000.00
        return context
    
class CashDepositTemplateView(TemplateView):
    template_name = 'deposit.html'

class DepositCompleteTemplateView(TemplateView):
    template_name = 'deposit-complete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            user = self.request.user
            cash = getattr(user, 'cash', None)
            
            # 최근 입금 내역 조회
            recent_deposits = CashTransaction.objects.filter(user=user, transaction_type='deposit').order_by('-created_at')
            
            # 최신 입금액과 이전 잔액 계산
            latest_amount = recent_deposits[0].amount if recent_deposits else 0
            previous_balance = cash.balance - latest_amount if cash else 0.00
            
            context['name'] = user.name
            context['email'] = user.email
            context['balance'] = cash.balance if cash else 0.00
            context['recent_deposits'] = recent_deposits
            context['previous_balance'] = previous_balance
        else:
            # 로그인하지 않은 경우 기본 정보 제공
            context['name'] = "사용자"
            context['email'] = "user@example.com"
            context['balance'] = 10000.00
            context['recent_deposits'] = []
            context['previous_balance'] = 10000.00
        
        return context

class CashWithdrawTemplateView(TemplateView):
    template_name = 'withdraw.html'


class WithdrawCompleteTemplateView(TemplateView):
    template_name = 'withdraw-complete.html'  # ✅ template_name 명시

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            user = self.request.user
            cash = getattr(user, 'cash', None)

            # 최근 출금 내역 조회
            recent_withdraws = CashTransaction.objects.filter(
                user=user,
                transaction_type='withdraw'
            ).order_by('-created_at')

            # 최신 출금액과 이전 잔액 계산
            latest_amount = recent_withdraws[0].amount if recent_withdraws else 0
            previous_balance = cash.balance + latest_amount if cash else 0.00

            context['name'] = user.name
            context['email'] = user.email
            context['balance'] = cash.balance if cash else 0.00
            context['recent_withdraws'] = recent_withdraws
            context['previous_balance'] = previous_balance
        else:
            # 로그인하지 않은 경우 기본 정보 제공
            context['name'] = "사용자"
            context['email'] = "user@example.com"
            context['balance'] = 10000.00
            context['recent_withdraws'] = []
            context['previous_balance'] = 10000.00

        return context

class CashTransferTemplateView(TemplateView):
    template_name = 'transfer.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            user = self.request.user
            context.update({
                'name': user.name,
                'email': user.email
            })
        else:
            # 로그인하지 않은 경우 기본 정보 제공
            context.update({
                'name': "사용자",
                'email': "user@example.com"
            })
        return context

class TransferCompleteTemplateView(TemplateView):
    template_name = 'transfer-complete.html'  # ✅ template_name 명시

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            user = self.request.user
            transfer = CashTransfer.objects.filter(sender=user).order_by('-created_at').first()

            context.update({
                'sender_email': user.email,
                'receiver_email': transfer.receiver.email if transfer else '',
                'receiver_name': transfer.receiver.name if transfer else '',
                'amount': transfer.amount if transfer else 0.00,
                'memo': transfer.memo if transfer else '',
                'created_at': transfer.created_at if transfer else None,
            })
        else:
            # 로그인하지 않은 경우 기본 정보 제공
            context.update({
                'sender_email': "user@example.com",
                'receiver_email': "receiver@example.com",
                'receiver_name': "받는사람",
                'amount': 1000.00,
                'memo': "테스트 송금",
                'created_at': datetime.now(),
            })

        return context

class AllTransactionTemplateView(TemplateView):
    template_name = 'account.html'  # ✅ template_name 명시

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            user = self.request.user
            cash = getattr(user, 'cash', None)

            transaction_list = CashTransaction.objects.filter(user=user).order_by('-created_at')
            paginator = Paginator(transaction_list, 5)
            page_number = self.request.GET.get("page")
            page_obj = paginator.get_page(page_number)

            context.update({
                'transactions': page_obj,
                'name': user.name,
                'email': user.email,
                'balance': cash.balance if cash else 0.00,
                'page_obj': page_obj,
            })
        else:
            # 로그인하지 않은 경우 기본 정보 제공
            context.update({
                'transactions': [],
                'name': "사용자",
                'email': "user@example.com",
                'balance': 10000.00,
                'page_obj': None,
            })

        return context

class UnregisterTemplateView(TemplateView):
    template_name = 'unregister.html'


# ✅ 실제 동작용 View (웹 페이지 렌더링)
class OTPSetupTemplateView(TemplateView):
    template_name = 'otp_setup.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 기본 OTP 정보 제공
        context.update({
            'otp_secret': "JBSWY3DPEHPK3PXP",
            'qr_code_url': "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",
        })

        return context


def custom_403_view(request, exception=None):
    return render(request, '403.html', status=403)


#bandit report
def bandit_report_view(request):
    with open("analysis/bandit-report.json") as f:
        data = json.load(f)

    context = {
        "issues": data.get("results", []),
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    return render(request, "bandit_report.html", context)
