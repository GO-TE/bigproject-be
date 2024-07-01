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
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)  # 시리얼라이저 오류 메시지 출력
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
