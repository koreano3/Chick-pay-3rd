# 임시테스트 ▽지워야함 
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse


# views_api.py
from django.contrib.auth import authenticate, login
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework.exceptions import ValidationError
from django.shortcuts import redirect
from django.contrib import messages
from django.db import transaction , IntegrityError
from django.views.decorators.csrf import csrf_exempt
from user_app.models import CustomUser, Cash
from user_app.serializers import (
    LoginSerializer,RegisterSerializer, MyPageSerializer,UnregisterPasswordCheckSerializer
)

import pyotp
import logging
from rest_framework_simplejwt.tokens import RefreshToken


class CookieLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(request, username=email, password=password)  # 또는 email=email
        if user is not None:
            refresh = RefreshToken.for_user(user)
            request.session['otp_verified'] = False  # ✅ 세션에 OTP 상태 유지

            response = JsonResponse({'message': '로그인 성공'})
            response.set_cookie('access_token', str(refresh.access_token), httponly=True, secure=True, samesite='Lax', max_age=3600)
            response.set_cookie('refresh_token', str(refresh), httponly=True, secure=True, samesite='Lax', max_age=7*24*3600)
            return response
        else:
            return JsonResponse({'error': '이메일 또는 비밀번호가 틀렸습니다'}, status=401)


logger = logging.getLogger("transaction")

@csrf_exempt
def health_check(request):
    return HttpResponse("OK", content_type="text/plain", status=200)

class MainAPIView(APIView):
    def get(self, request):
        return Response({"message": "Welcome to the API main endpoint."})

class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        try:
            if serializer.is_valid():
                with transaction.atomic():  # 💥 여기!
                    user = serializer.save()
                    Cash.objects.create(user=user, balance=0)
                    # 회원가입 성공 시 JWT 토큰 발급
                    refresh = RefreshToken.for_user(user)
                    return Response({
                        "message": "Registration successful",
                        "access_token": str(refresh.access_token),
                        "refresh_token": str(refresh)
                    }, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError:
            return Response({"error": "이미 존재하는 이메일입니다."}, status=status.HTTP_400_BAD_REQUEST)

# class LoginAPIView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         serializer = LoginSerializer(data=request.data)
        
#         if serializer.is_valid():
#             user = serializer.validated_data['user']
#             refresh = RefreshToken.for_user(user)
#             request.session['otp_verified'] = False  # OTP 인증 상태는 세션에 유지
            
#             return Response({
#                 'message': '로그인 성공!',
#                 'access_token': str(refresh.access_token),
#                 'refresh_token': str(refresh),
#             }, status=200)
        
#         return Response(serializer.errors, status=400)
        
class MyPageAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = MyPageSerializer(request.user)
        return Response(serializer.data)

class PasswordChangeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # 사용자로부터 받은 데이터
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')

        # 현재 비밀번호 확인
        if not request.user.check_password(current_password):
            return Response({"error": "현재 비밀번호가 일치하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 새 비밀번호와 확인 비밀번호 일치 여부 확인
        if new_password != confirm_password:
            return Response({"error": "새 비밀번호와 확인 비밀번호가 일치하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 비밀번호 변경
        request.user.set_password(new_password)
        request.user.save()

        return Response({"message": "비밀번호가 성공적으로 변경되었습니다."}, status=status.HTTP_200_OK)



class OTPVerifyAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        otp_code = request.data.get('otp_code')

        if not user.otp_secret:
            return Response({"error": "OTP 설정이 안 되어 있습니다."}, status=400)

        totp = pyotp.TOTP(user.otp_secret)

        if totp.verify(otp_code):
            # OTP 인증 성공 시 새로운 JWT 토큰 발급
            refresh = RefreshToken.for_user(user)
            # OTP 인증 여부를 토큰에 포함
            refresh['otp_verified'] = True
            
            return Response({
                "message": "인증 성공",
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh)
            }, status=200)
        else:
            return Response({"error": "OTP 인증 실패"}, status=400)



class UnregisterAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        serializer = UnregisterPasswordCheckSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)  # ❗ 여기서 비번 검증함

        request.user.delete()
        return Response({"message": "회원탈퇴 완료"}, status=status.HTTP_204_NO_CONTENT)
