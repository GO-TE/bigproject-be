from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.http import (
    urlsafe_base64_encode,
    urlsafe_base64_decode,
)
from django.utils.encoding import (
    force_bytes,
    force_str,
)
from django.contrib.auth.hashers import make_password

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import (
    status,
    generics
)
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import (
    IsAuthenticated,
    AllowAny,
)
from rest_framework.decorators import permission_classes

from account.models import User
from account.serializers import (
    UserSerializer,
    LoginSerializer,
    ProfileSerializer,
)
from account.util.message import Message
from account.util.utils import validate_google_token
from bigproject.settings import EMAIL_HOST_USER


@permission_classes([AllowAny])
class CheckEmailDuplicateView(APIView):
    def post(self, request):
        email = request.data.get('email', None)
        if email is not None:
            exists = User.objects.filter(email=email).exists()
            return Response({'exists': exists}, status=status.HTTP_200_OK)
        return Response({"message": "Data is None"}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([AllowAny])
class CheckNicknameDuplicateView(APIView):
    def post(self, request):
        nickname = request.data.get('nickname', None)
        if nickname is not None:
            exists = User.objects.filter(nickname=nickname).exists()
            return Response({'exists': exists}, status.HTTP_200_OK)

        return Response({"message": "Data is None"}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([AllowAny])
class SignUpAPIView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {'message': Message.SUCCESS_SIGNUP},
                status=status.HTTP_201_CREATED
            )
        return Response(
            {'message': Message.FAILED_SIGNUP},
            status=status.HTTP_400_BAD_REQUEST)


@permission_classes([AllowAny])
class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            response = Response({
                'message': Message.SUCCESS_LOGIN,
                'access': str(access_token),
                'refresh': str(refresh),
                'nickname': user.nickname
            }, status=status.HTTP_200_OK)

            response.set_cookie(
                key='access_token',
                value=str(access_token),
                httponly=True,
                secure=True,
                samesite='Strict'
            )

            response.set_cookie(
                key='refresh_token',
                value=str(refresh),
                httponly=True,
                secure=True,
                samesite='Strict'
            )

            return response

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            response = Response({
                'message': Message.SUCCESS_LOGOUT
            }, status=status.HTTP_205_RESET_CONTENT)

            response.delete_cookie('access_token')
            response.delete_cookie('refresh_token')

            return response
        except Exception as e:
            return Response({'message': Message.FAILED_LOGOUT, 'error': str(e)},
                            status=status.HTTP_400_BAD_REQUEST)


class UserProfileRetrieveView(generics.RetrieveAPIView):
    serializer_class = ProfileSerializer

    def get_object(self):
        return self.request.user


class UserProfileUpdateView(generics.UpdateAPIView):
    serializer_class = ProfileSerializer

    def get_object(self):
        return self.request.user


@permission_classes([AllowAny])
class PasswordResetView(APIView):  # TODO: 하드코딩 제거
    def post(self, request):
        email = request.data.get('email', None)
        if email is None:
            return Response({"message": "이메일 공란"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.uuid))
            reset_link = request.build_absolute_uri(f'/account/password-reset-confirm/{uid}/{token}/')
            send_mail(
                '[GLAWBAL] Password Reset',
                f'Hi {user.nickname},\n'
                'If you did not request it, please contact customer service.'
                f'\nPlease click the link below to reset your password:\n{reset_link}',
                EMAIL_HOST_USER,
                [email],
                fail_silently=False
            )
            return Response({'message': 'Password reset link has been sent to your email.'},
                            status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response(
                {"message": "이메일이 일치하지 않습니다."},
                status=status.HTTP_400_BAD_REQUEST
            )


@permission_classes([AllowAny])
class PasswordResetConfirmView(APIView):  # TODO: 하드코딩 제거, login하는 url로 이동시켜야함...
    def post(self, request):
        uuid = force_str(urlsafe_base64_decode(request.data.get('uidb64')))
        user = User.objects.filter(uuid=uuid).first()
        if user and default_token_generator.check_token(user, request.get.data('token')):
            new_password = request.POST.get('new_password')
            user.password = make_password(new_password)
            user.save()
            return Response({'message': 'Password has been reset successfully.'},
                            status=status.HTTP_200_OK)
        return Response({'error': 'Invalid token or user'},
                        status=status.HTTP_400_BAD_REQUEST)


@permission_classes([AllowAny])
class VerifyUserEmailView(APIView):  # TODO: 하드코딩 제거, 마찬가지로 로그인하는 url로 이동...
    def post(self, request):
        email = request.data.get("email", None)
        if email is None:
            return Response({"message": "이메일 공란"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.uuid))
            link = request.build_absolute_uri(f'/account/activate/{uid}/{token}/')  # 프론트에서 비밀번호 초기화 화면으로 바꿔야할듯
            send_mail(  # 이메일 발송 따로 나누면 좋을 듯
                '[GLAWBAL] Activate your account',
                f'Hi {user.nickname},\n'
                '\nPlease click the link to activate your account\n'
                f'link: {link}\n Thank you',
                EMAIL_HOST_USER,
                [email],
                fail_silently=False
            )
            return Response(
                {"message": " Send email successfully"},
                status=status.HTTP_200_OK
            )

        except User.DoesNotExist:
            return Response(
                {"message": "Invalid access"},
                status=status.HTTP_400_BAD_REQUEST
            )


@permission_classes([AllowAny])
class ActivateUserAccountView(APIView):  # TODO: 프론트 로그인 화면으로 리다이렉트
    def get(self, request, uidb64, token):
        if not (uidb64 and token):
            return Response({'error': 'Missing required parameters'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(uuid=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({'message': 'Account activated successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid token or user'}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([AllowAny])
class GoogleLogin(APIView):
    def post(self, request):
        token = request.data.get('token', None)
        if token is None:
            return Response({'message': 'No token provided'}, status=status.HTTP_400_BAD_REQUEST)

        id_info = validate_google_token(token)
        if id_info is None:
            return Response({'message': 'Invalid Token'}, status=status.HTTP_400_BAD_REQUEST)

        email = id_info['email']
        try:
            user = User.objects.get(email=email)

        except User.DoesNotExist:
            return Response({'message': '회원가입 미진행 계정'}, status=status.HTTP_400_BAD_REQUEST)

        if user:
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token

            response = Response({
                'message': Message.SUCCESS_LOGIN,
                'access': str(access_token),
                'refresh': str(refresh)
            }, status=status.HTTP_200_OK)

            return response

        else:
            return Response({'message': 'user is None'}, status=status.HTTP_400_BAD_REQUEST)

        # TODO : dj-rest-auth 보고 최대한 그래도 library 사용해서 kakao까지 늘려보기...