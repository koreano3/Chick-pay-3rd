from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import OTPVerifyAPIView, PasswordChangeAPIView, RegisterAPIView, UnregisterAPIView, UserDetailByIdAPIView
from .views import MyPageAPIView, UserExistsAPIView, CashUpdateAPIView

urlpatterns = [
    # API 엔드포인트
    path('api/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/register/', RegisterAPIView.as_view(), name='register'),
    path('api/mypage/', MyPageAPIView.as_view(), name='api-mypage'),
    path('api/user/me/', MyPageAPIView.as_view(), name='user-info'),
    path('api/change-password/', PasswordChangeAPIView.as_view(), name='api-change-password'),
    path('api/unregister/', UnregisterAPIView.as_view(), name='api-unregister'),
    path('api/otp/verify/', OTPVerifyAPIView.as_view(), name='api-otp-verify'),
    path('api/user/exists/', UserExistsAPIView.as_view(), name='user-exists'),
    path('api/cash/update/', CashUpdateAPIView.as_view(), name='cash-update'),
    path('api/user/<int:user_id>/', UserDetailByIdAPIView.as_view()),
] 