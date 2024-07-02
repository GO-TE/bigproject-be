from django.contrib.auth.hashers import make_password

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken



from account.models import User
from account.serializers import (
    UserSerializer,
    LoginSerializer,
)
from account.util.message import Message

class CheckEmailDuplicateView(APIView):
    def get(self, request, email):
        exists = User.objects.filter(email=email).exists()
        return Response({'exists': exists})


class CheckNicknameDuplicateView(APIView):
    def get(self, request, nickname):
        exists = User.objects.filter(nickname=nickname).exists()
        return Response({'exists': exists}, status=200)


class SignUpAPIView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            print(serializer.data)
            return Response(
                {'message' : Message.SUCCESS_SIGNUP},
                status=status.HTTP_201_CREATED
            )
        return Response(
            {'message' : Message.FAILED_SIGNUP},
            status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            response = Response({
                'message' : Message.SUCCESS_LOGIN,
                'access' : str(access_token),
                'refresh' : str(refresh)
            }, status=status.HTTP_200_OK)

            response.set_cookie(
                key='acceess_token',
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
    def post(self, request):
        try:
            refresh_token = request.COOKIES.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()

            response = Response(status=status.HTTP_205_RESET_CONTENT)
            response.delete_cookie('access_token')
            response.delete_cookie('refresh_token')
            return response

        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)