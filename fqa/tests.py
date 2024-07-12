# tests.py
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from .models import FAQ
from community.models import Category


class FAQListViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.category1 = Category.objects.create(major='general', sub='general')
        self.category2 = Category.objects.create(major='exception', sub='exception')

        self.faq1 = FAQ.objects.create(question="Question 1", answer="Answer 1", category=self.category1)
        self.faq2 = FAQ.objects.create(question="Question 2", answer="Answer 2", category=self.category2)

    def test_get_all_faqs(self):
        response = self.client.get(reverse('faq-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['question'], self.faq1.question)
        self.assertEqual(response.data[1]['question'], self.faq2.question)
