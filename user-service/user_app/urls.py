from django.urls import path
from .views import api_views, web_views

urlpatterns = [
    # API 엔드포인트
    path('api/register/', api_views.RegisterAPIView.as_view(), name='register'),
    path('api/login/', api_views.LoginAPIView.as_view(), name='login'),
    path('api/mypage/', api_views.MyPageAPIView.as_view(), name='mypage'),
    path('api/password-change/', api_views.PasswordChangeAPIView.as_view(), name='password-change'),
    path('api/otp/', api_views.OTPVerifyAPIView.as_view(), name='otp'),
    path('api/unregister/', api_views.UnregisterAPIView.as_view(), name='unregister'),

    # 웹 페이지 엔드포인트
    path('', web_views.MainTemplateView.as_view(), name='main'),
    path('register/', web_views.RegisterTemplateView.as_view(), name='register-page'),
    path('login/', web_views.LoginTemplateView.as_view(), name='login-page'),
    path('mypage/', web_views.MyPageTemplateView.as_view(), name='mypage-page'),
    path('unregister/', web_views.UnregisterTemplateView.as_view(), name='unregister-page'),
    path('otp-setup/', web_views.OTPSetupTemplateView.as_view(), name='otp-setup'),
] 