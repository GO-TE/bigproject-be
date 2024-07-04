from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from account.models import User
from rest_framework_simplejwt.tokens import RefreshToken

class AccountTests(APITestCase):
    def setUp(self):
        self.user_data = {
            'email': 'testuser@example.com',
            'password': 'password123',
            'username': 'testuser',
            'nickname': 'testnickname',
            'nationality': 'Korea',
            'work_at': 'Company'
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_signup(self):
        url = reverse('account:signup')
        data = {
            'email': 'newuser@example.com',
            'password': 'newpassword123',
            'username': 'newuser',
            'nickname': 'newnickname',
            'nationality': 'Korea',
            'work_at': 'NewCompany'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_login(self):
        url = reverse('account:login')
        data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_logout(self):
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(refresh.access_token))
        url = reverse('account:logout')
        data = {'refresh_token': str(refresh)}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)

    def test_check_email_duplicate(self):
        url = reverse('account:check-email-duplicate', args=[self.user_data['email']])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['exists'])

    def test_check_nickname_duplicate(self):
        url = reverse('account:check-nickname-duplicate', args=[self.user_data['nickname']])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['exists'])

