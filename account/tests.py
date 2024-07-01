from django.test import TestCase
from django.urls import reverse

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
