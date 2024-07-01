from django.contrib.auth.hashers import make_password

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import JSONParser

from account.models import User
from account.serializers import UserSerializer


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


class Login(APIView):
    def post(self, request):
        data = JSONParser().parse(request)
        search_email = data['email']
        obj = User.objects.get(email=search_email)

        if data['password'] == obj.password:
            return Response(status=200)
        else:
            return Response(status=400)