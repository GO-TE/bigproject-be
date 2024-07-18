# tests.py
from datetime import date

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from .models import (
    FAQ,
    Law,
    Rule,
    Glossary
)
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


class LawListViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('law')

        for i in range(31):
            Law.objects.create(
                law=f"Test law{i}",
                ministry="고용노동부",
                code="10121",
                content=f"사장님 돈 좀 많이 주세요 제발요{i}",
                date=date(2023, 1, 1)
            )

    def test_list_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 20)

    def test_search_laws_by_title(self):
        response = self.client.get(self.url, {'title': "Test law1"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any("Test law1" in law['law'] for law in response.data['results']))

    def test_search_laws_by_content(self):
        response = self.client.get(self.url, {'content': "사장님"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any("사장님" in law['content'] for law in response.data['results']))