from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from account.models import User
from community.models import Article, Category, Comment
from rest_framework_simplejwt.tokens import RefreshToken

class CommunityTests(APITestCase):
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
        self.category = Category.objects.create(major='Test Major', sub='Test Sub')
        self.article = Article.objects.create(user=self.user, category=self.category, title='Test Title', content='Test Content')

    def authenticate(self):
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(refresh.access_token))

    def test_create_article(self):
        self.authenticate()
        url = reverse('article-create')
        data = {
            'category': self.category.id,
            'title': 'New Title',
            'content': 'New Content'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_articles(self):
        url = reverse('article-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

    def test_retrieve_article(self):
        self.authenticate()
        url = reverse('article-detail', args=[self.article.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_article(self):
        self.authenticate()
        url = reverse('article-detail', args=[self.article.id])
        data = {
            'category': self.category.id,
            'title': 'Updated Title',
            'content': 'Updated Content'
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_article(self):
        self.authenticate()
        url = reverse('article-detail', args=[self.article.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_create_comment(self):
        self.authenticate()
        url = reverse('article-comment-create', args=[self.article.id])
        data = {
            'article': self.article.id,  # Add the article field
            'message': 'Test Comment'
        }
        response = self.client.post(url, data, format='json')
        if response.status_code != status.HTTP_201_CREATED:
            self.fail(f"Create comment failed with status code {response.status_code} and response data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_comments(self):
        url = reverse('comment-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_comment(self):
        comment = Comment.objects.create(article=self.article, user=self.user, message='Test Comment')
        self.authenticate()
        url = reverse('comment-detail', args=[comment.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_comment(self):
        comment = Comment.objects.create(article=self.article, user=self.user, message='Test Comment')
        self.authenticate()
        url = reverse('comment-detail', args=[comment.id])
        data = {
            'article': self.article.id,  # Add the article field
            'message': 'Updated Comment'
        }
        response = self.client.put(url, data, format='json')
        if response.status_code != status.HTTP_200_OK:
            self.fail(f"Update comment failed with status code {response.status_code} and response data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_delete_comment(self):
        comment = Comment.objects.create(article=self.article, user=self.user, message='Test Comment')
        self.authenticate()
        url = reverse('comment-detail', args=[comment.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
