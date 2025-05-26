from django.urls import path
from . import api_views

urlpatterns = [
    # API 엔드포인트
    path('api/register/', api_views.RegisterAPIView.as_view(), name='register'),
    path('api/login/', api_views.LoginAPIView.as_view(), name='login'),
    path('api/mypage/', api_views.MyPageAPIView.as_view(), name='mypage'),
    path('api/password-change/', api_views.PasswordChangeAPIView.as_view(), name='password-change'),
    path('api/otp/', api_views.OTPVerifyAPIView.as_view(), name='otp'),
    path('api/unregister/', api_views.UnregisterAPIView.as_view(), name='unregister'),
] 