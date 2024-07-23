from django.test import TestCase
from django.urls import reverse
from django.core.cache import cache

from rest_framework import status
from rest_framework.test import APIClient

from news.models import NewsArticle


# Create your tests here.


class NewsAPITestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.news_article = NewsArticle.objects.create(
            title="Test News Title",
            summary="Test News Summary",
            news_link="http://example.com/test-news",
            image_link="http://example.com/test-image.jpg",
            news_agency="Test Agency",
            timestamp="2024.07.11. 오후 2:40",
            news_content="Test News Content"
        )



    def test_get_news_article_detail(self):
        url = reverse('news:detail')
        response = self.client.get(url, {'id': self.news_article.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.news_article.title)

    def test_get_news_article_detail_not_found(self):
        url = reverse('news:detail')
        response = self.client.get(url, {'id': 999}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], '찾는 뉴스 id가 없당게요')

    def test_get_news_index_thumbnail(self):
        cache.set('news_articles', [{
            'id': self.news_article.id,
            'title': self.news_article.title,
            'summary': self.news_article.summary,
            'image_link': self.news_article.image_link
        }], timeout=60 * 60)
        url = reverse('news:thumbnail')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['articles'][0]['title'], self.news_article.title)

    def test_get_news_index_thumbnail_no_cache(self):
        url = reverse('news:thumbnail')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'No articles found')

    def test_news_list_view(self):
        url = reverse('news:list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], self.news_article.title)

    def test_news_list_view_search(self):
        url = reverse('news:list')
        response = self.client.get(url, {'search': 'Test News Title'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], self.news_article.title)
