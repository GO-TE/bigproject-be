import json
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

from community.models import Article, Comment, Category, Image

User = get_user_model()


class CommunityTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create(
            email='testuser@example.com',
            password=make_password('testpassword'),
            nickname='testuser',
            username='testusername',
            nationality='testnation',
            work_at='testwork',
            is_active=True
        )
        self.client = APIClient()
        login_url = reverse('account:login')  # 정확한 URL 네임스페이스 확인
        data = {
            'email': 'testuser@example.com',
            'password': 'testpassword'
        }
        response = self.client.post(login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        access_token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)

        self.category = Category.objects.create(major='Tech', sub='Programming')
        self.image = Image.objects.create(path='path/to/image.jpg', user=self.user)
        self.article = Article.objects.create(
            user=self.user,
            category=self.category,
            title='Test Article',
            content='This is a test article.',
            image=self.image
        )
        self.comment = Comment.objects.create(
            article=self.article,
            user=self.user,
            message='This is a test comment.'
        )

    def test_article_list_view(self):
        url = reverse('article-list')
        response = self.client.get(url)
        print("test_article_list_view Response:", json.dumps(response.data, indent=2, ensure_ascii=False))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertNotIn('comments', response.data[0])  # Ensure comments are not in the response
        self.assertEqual(response.data[0]['comment_count'], 1)  # Ensure comment count is correct

    def test_article_detail_view(self):
        url = reverse('article-detail', args=[self.article.id])
        response = self.client.get(url)
        print("test_article_detail_view Response:", json.dumps(response.data, indent=2, ensure_ascii=False))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.article.title)
        self.assertIn('comments', response.data)  # Ensure comments are in the response
        self.assertEqual(len(response.data['comments']), 1)
        self.assertEqual(response.data['comments'][0]['message'], self.comment.message)

    def test_article_create_view(self):
        url = reverse('article-create')
        data = {
            'category': self.category.id,
            'title': 'New Article',
            'content': 'Content of new article',
            'image': self.image.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Article.objects.count(), 2)

    def test_comment_list_view(self):
        url = reverse('comment-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_comment_detail_view(self):
        url = reverse('comment-detail', args=[self.comment.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], self.comment.message)

    def test_article_comment_create_view(self):
        url = reverse('article-comment-create', args=[self.article.id])
        data = {
            'article': self.article.id,
            'message': 'A new comment'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 2)

    def test_article_by_category_list_view(self):
        url = reverse('article-by-category', args=[self.category.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
