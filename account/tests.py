from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.hashers import make_password

from rest_framework import status
from rest_framework.test import APITestCase

from account.models import User


class UserRegistrationTests(APITestCase):
    def test_user_signup(self):
        url = reverse('account:signup')
        data = {
            'nationality': 'RepublicOfKorea',
            'work_at': 'Australia',
            'username': 'testuser',
            'nickname': 'testnick',
            'password': 'strongpassword123',
            'email': 'test@example.com',
        }
        response = self.client.post(url, data, format='json')
        print(response.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().email, 'test@example.com')


class UserLoginTests(APITestCase):

    def setUp(self):
        # 테스트용 사용자 생성
        self.user = User.objects.create(
            email='testuser@example.com',
            password=make_password('password123')  # 비밀번호 해싱
        )

    def test_login(self):
        url = reverse('account:login')
        data = {
            'email': 'testuser@example.com',
            'password': 'password123',
        }
        response = self.client.post(url, data, format='json')

        # 응답 상태 코드 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 응답 데이터 확인
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

        # JWT 토큰이 포함되어 있는지 확인
        access_token = response.data['access']
        refresh_token = response.data['refresh']
        self.assertIsNotNone(access_token)
        self.assertIsNotNone(refresh_token)

    def test_login_invalid_credentials(self):
        url = reverse('account:login')
        data = {
            'email': 'testuser@example.com',
            'password': 'wrongpassword',
        }
        response = self.client.post(url, data, format='json')

        # 응답 상태 코드 확인
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # 응답 데이터 확인
        self.assertIn('non_field_errors', response.data)
