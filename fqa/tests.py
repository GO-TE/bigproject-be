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


class RuleListViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('rule')

        for i in range(31):
            Rule.objects.create(
                rule=f"Test rule{i}",
                kind="무슨무슨 법",
                code="10121",
                content=f"사장님 돈 좀 많이 주세요 제발요{i}",
                effective=date(2023, 1, 1),
                created=date(2023, 1, 1),
            )

    def test_list_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 20)

    def test_search_laws_by_title(self):
        response = self.client.get(self.url, {'title': "Test rule1"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any("Test rule1" in rule['rule'] for rule in response.data['results']))

    def test_search_laws_by_content(self):
        response = self.client.get(self.url, {'content': "사장님"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any("사장님" in rule['content'] for rule in response.data['results']))


class GlossaryListViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('glossary')

        for i in range(31):
            Glossary.objects.create(
                terminology=f"있어보이는말{i}",
                code=f'1232{i}',
                content=f"좀 어려워서 안써도 될듯{i}"
            )

    def test_list_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 20)

    def test_search_laws_by_title(self):
        response = self.client.get(self.url, {'title': "있어보이는말1"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any("있어보이는말1" in glossary['terminology'] for glossary in response.data['results']))

    def test_search_laws_by_content(self):
        response = self.client.get(self.url, {'content': "좀 어려워서"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any("어려워서" in glossary['content'] for glossary in response.data['results']))


class ViewUpdateTests(TestCase):
    def setUp(self):
        self.law = Law.objects.create(
            law="Test law",
            ministry="고용노동부",
            code="10121",
            content="사장님 돈 좀 많이 주세요 제발요",
            date=date(2023, 1, 1)
        )
        self.rule = Rule.objects.create(
            rule="Test rule",
            kind="무슨무슨 법",
            code="10121",
            content=f"사장님 돈 좀 많이 주세요 제발요",
            effective=date(2023, 1, 1),
            created=date(2023, 1, 1),
        )
        self.glossary = Glossary.objects.create(
            terminology="있어보이는말",
            code='1232',
            content=f"좀 어려워서 안써도 될듯"
        )

        self.url = reverse('view-update')

    def test_increase_law_view_count(self):
        data = {"category": "law", "id": self.law.id}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_views'], 1)
        self.assertEqual(response.data['week_views'], 1)
        self.law.refresh_from_db()
        self.assertEqual(self.law.total_view, 1)
        self.assertEqual(self.law.week_view, 1)

    def test_increase_rule_view_count(self):
        data = {"category": "rule", "id": self.rule.id}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_views'], 1)
        self.assertEqual(response.data['week_views'], 1)
        self.rule.refresh_from_db()
        self.assertEqual(self.rule.total_view, 1)
        self.assertEqual(self.rule.week_view, 1)

    def test_increase_glossary_view_count(self):
        data = {"category": "glossary", "id": self.glossary.id}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_views'], 1)
        self.assertEqual(response.data['week_views'], 1)
        self.glossary.refresh_from_db()
        self.assertEqual(self.glossary.total_view, 1)
        self.assertEqual(self.glossary.week_view, 1)

    def test_invalid_category(self):
        data = {"category": "invalid", "id": self.law.id}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Invalid category')

    def test_missing_id(self):
        data = {"category": "law"}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Category and ID are required')

    def test_non_existent_id(self):
        data = {"category": "law", "id": 999}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'Law with ID 999 does not exist')
