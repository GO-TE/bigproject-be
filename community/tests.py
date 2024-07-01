from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from .models import Article, Category, Image

class ArticleDetailTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.category = Category.objects.create(major='Tech', sub='Programming')
        self.image = Image.objects.create(user=self.user, path='path/to/image.jpg')
        self.article = Article.objects.create(
            user=self.user, image=self.image, category=self.category,
            title='Sample Title', content='Sample content'
        )

    def test_get_article(self):
        """
        Ensure we can retrieve an article.
        """
        url = reverse('article-detail', args=[self.article.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Sample Title')

    def test_update_article(self):
        """
        Ensure we can update an article.
        """
        url = reverse('article-detail', args=[self.article.id])
        data = {'title': 'Updated Title', 'content': 'Updated content'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Title')

    def test_delete_article(self):
        """
        Ensure we can delete an article.
        """
        url = reverse('article-detail', args=[self.article.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Check the article is actually deleted
        self.assertFalse(Article.objects.filter(id=self.article.id).exists())
