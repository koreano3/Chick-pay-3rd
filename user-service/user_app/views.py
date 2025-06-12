from django.shortcuts import redirect
from psutil import users
import pyotp
from rest_framework import generics
from user_app.serializers import (
    RegisterSerializer,
    UnregisterPasswordCheckSerializer
)
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction, IntegrityError
from user_app.models import Cash, CustomUser
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction, IntegrityError
from rest_framework.permissions import IsAuthenticated
from user_app.serializers import MyPageSerializer
from decimal import Decimal
from user_service.clients.kafka_producer import send_user_created_event
# from user_service.clients.kafka_client import producer
# from user_service.clients.redis_client import redis_client


# API Views

# 1. RegisterView와 RegisterAPIView의 차이점 설명

# RegisterView는 Django REST framework의 generics.CreateAPIView를 상속받아
# 회원가입 처리를 매우 간단하게 구현할 수 있습니다.
# serializer_class만 지정하면, POST 요청 시 자동으로 serializer의 유효성 검사 및 저장(save)까지 처리해줍니다.
# 즉, 커스텀 로직이 필요 없고, 단순한 생성(Create) API에 적합합니다.

# class RegisterView(generics.CreateAPIView):
#     serializer_class = UserSignupSerializer
#     permission_classes = []  # 누구나 접근 가능

# RegisterAPIView는 APIView를 상속받아 post 메서드를 직접 구현합니다.
# 이 방식은 회원가입 시 추가적인 비즈니스 로직(예: 트랜잭션 처리, Cash 객체 생성, JWT 토큰 발급 등)이 필요할 때 사용합니다.
# 즉, 회원가입과 동시에 여러 작업을 처리하거나, 예외처리, 커스텀 응답이 필요할 때 적합합니다.


# class RegisterAPIView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         serializer = RegisterSerializer(data=request.data)
#         try:
#             if serializer.is_valid():
#                 with transaction.atomic():  # 💥 여기!
#                     user = serializer.save()
#                     Cash.objects.create(user=user, balance=0)
#                     # 회원가입 성공 시 JWT 토큰 발급
#                     refresh = RefreshToken.for_user(user)
#                     return Response({
#                         "message": "Registration successful",
#                         "access_token": str(refresh.access_token),
#                         "refresh_token": str(refresh)
#                     }, status=status.HTTP_201_CREATED)
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         except IntegrityError:
#             return Response({"error": "이미 존재하는 이메일입니다."}, status=status.HTTP_400_BAD_REQUEST)
        


def login_view(request):
    if request.method == "POST":
        # 로그인 로직...
        if users is not None:
            token = RefreshToken.for_user(users)
            response = redirect('main')  # 로그인 성공 후 리다이렉트
            
            # 쿠키에 토큰 저장
            response.set_cookie(
                'access_token',     # TokenRequiredMixin에서 찾는 이름과 동일하게
                str(token.access_token),
                httponly=True,
                samesite='Lax'
            )
            return response
        
class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        print("request.data:", request.data)
        serializer = RegisterSerializer(data=request.data)
        try:
            if serializer.is_valid():
                with transaction.atomic():  # 💥 여기!
                    user = serializer.save()
                    Cash.objects.create(user=user, balance=0)

                    # ✅ Kafka 이벤트 전송
                    send_user_created_event(user.id, user.email)

                return Response({"message": "Registration successful"}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except IntegrityError:
            return Response({"error": "이미 존재하는 이메일입니다."}, status=status.HTTP_400_BAD_REQUEST)


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



# @csrf_exempt
# def health_check(request):
#     return HttpResponse("OK", content_type="text/plain", status=200)

# class MainAPIView(APIView):
#     def get(self, request):
#         return Response({"message": "Welcome to the API main endpoint."})




# class PasswordChangeAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         # 사용자로부터 받은 데이터
#         current_password = request.data.get('current_password')
#         new_password = request.data.get('new_password')
#         confirm_password = request.data.get('confirm_password')

#         # 현재 비밀번호 확인
#         if not request.user.check_password(current_password):
#             return Response({"error": "현재 비밀번호가 일치하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)

#         # 새 비밀번호와 확인 비밀번호 일치 여부 확인
#         if new_password != confirm_password:
#             return Response({"error": "새 비밀번호와 확인 비밀번호가 일치하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)

#         # 비밀번호 변경
#         request.user.set_password(new_password)
#         request.user.save()

#         return Response({"message": "비밀번호가 성공적으로 변경되었습니다."}, status=status.HTTP_200_OK)



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

class UserExistsAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        email = request.GET.get('email')
        exists = CustomUser.objects.filter(email=email).exists()
        user_id = None
        if exists:
            user_id = CustomUser.objects.get(email=email).id
        return Response({'exists': exists, 'user_id': user_id})

class CashUpdateAPIView(APIView):
    permission_classes = [AllowAny]  # 실제 서비스에서는 인증 필요!

    def post(self, request):
        print("request.data:", request.data)
        user_id = request.data.get('user_id')
        amount = request.data.get('amount')
        type_ = request.data.get('type')  # 'deposit' or 'withdraw'

        try:
            user = CustomUser.objects.get(id=user_id)
            cash = user.cash  # OneToOneField로 연결되어 있음

            if type_ == 'deposit':
                cash.balance += Decimal(str(amount))
                cash.save()
                return Response({'message': '입금 성공', 'balance': cash.balance})
            elif type_ == 'withdraw':
                if cash.balance < Decimal(str(amount)):
                    return Response({'error': '잔액 부족'}, status=400)
                cash.balance -= Decimal(str(amount))
                cash.save()
                return Response({'message': '출금 성공', 'balance': cash.balance})
            else:
                return Response({'error': '잘못된 type'}, status=400)
        except CustomUser.DoesNotExist:
            return Response({'error': '유저 없음'}, status=404)
        except Exception as e:
            print("====[DEBUG] Exception:", str(e))
            return Response({'error': str(e)}, status=500)

class UserDetailByIdAPIView(APIView):
    def get(self, request, user_id):
        try:
            user = CustomUser.objects.get(id=user_id)
            return Response({
                "id": user.id,
                "email": user.email,
                "name": user.name,
            })
        except CustomUser.DoesNotExist:
            return Response({"error": "유저를 찾을 수 없습니다."}, status=404)


# def send_message(request):
#     # Kafka 메시지 전송
#     producer.send("test", b"hello from user-service")

#     # Redis에 데이터 캐시
#     redis_client.set("example_key", "example_value")

#     return JsonResponse({"status": "ok"})