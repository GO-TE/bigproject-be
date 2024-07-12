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
        self.faq1 = FAQ.objects.create(question="Question 1", answer="Answer 1", category=1)
        self.faq2 = FAQ.objects.create(question="Question 2", answer="Answer 2", category=2)

    def test_get_all_faqs(self):
        response = self.client.get(reverse('faq-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['question'], self.faq1.question)
        self.assertEqual(response.data[1]['question'], self.faq2.question)

class FAQByCategoryListViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.general_faq = FAQ.objects.create(question="General Question", answer="General Answer", category=1)
        self.technical_faq = FAQ.objects.create(question="Technical Question", answer="Technical Answer", category=2)

    def test_get_faqs_by_category(self):
        response = self.client.get(reverse('faq-by-category-list', kwargs={'category': 1}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['question'], self.general_faq.question)

        response = self.client.get(reverse('faq-by-category-list', kwargs={'category': 2}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['question'], self.technical_faq.question)

    def test_get_faqs_by_nonexistent_category(self):
        response = self.client.get(reverse('faq-by-category-list', kwargs={'category': 3}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

 