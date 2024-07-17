from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import ChatSession, ChatMessage
from account.models import User
import json
import time

class ChatbotTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpass123',
            username='testuser',
            nickname='testnick',
            nationality='Korea',
            work_at='TestCompany'
        )
        self.client.force_authenticate(user=self.user)
        self.session = ChatSession.objects.create(user=self.user)
        self.message_data = {
            'message': 'Hello, how are you?',
            'sender': 1
        }

    def test_create_new_session(self):
        response = self.client.post('/chatbot/sessions/new/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('session_id', response.data)
        print(f"\n test_create_new_session >> New session created with ID: {response.data['session_id']}")

    def test_get_session_list(self):
        response = self.client.get('/chatbot/sessions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        self.assertIn('summary', response.data[0])  # Check if summary is in the session list
        print(f"\ntest_get_session_list >> Session list retrieved: {json.dumps(response.data, indent=2, ensure_ascii=False)}")

    def test_get_session_detail(self):
        ChatMessage.objects.create(session=self.session, **self.message_data)
        
        response = self.client.get(f'/chatbot/sessions/{self.session.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['session_id'], self.session.id)
        self.assertIn('messages', response.data)
        self.assertIn('summary', response.data)  # Check if summary is in the session detail
        print(f"\ntest_get_session_detail >> Session details retrieved for ID: {self.session.id}\nDetails: {json.dumps(response.data, indent=2, ensure_ascii=False)}")

    def test_get_messages(self):
        ChatMessage.objects.create(session=self.session, **self.message_data)
        response = self.client.get(f'/chatbot/sessions/{self.session.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('messages', response.data)
        self.assertIn('summary', response.data)  # Check if summary is in the session detail
        print(f"\ntest_get_messages >> Messages retrieved for session ID: {self.session.id}\nMessages: {json.dumps(response.data['messages'], indent=2, ensure_ascii=False)}")

    def test_openai_chat(self):
        query1 = '호주 고용법 알려줘.' #  << 한국 고용법 , 영국 고용법 >> Hãy cho tôi biết về luật lao động của nước Anh.
        query2 = '호주 고용법 알려줘.' # 한국 고용법 >> Xin vui lòng cho chúng tôi biết về luật lao động của Hàn Quốc.
        nation = 'australia' # 일 할 국가 설정

        # 첫 번째 쿼리
        response1 = self.client.post('/chatbot/chat/', {
            'session_id': self.session.id,
            'query': query1,
            'nation': nation
        }, format='json')
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertIn('response', response1.data)
        self.assertIn('search_results', response1.data)
        result1 = response1.data['response']
        search_results1 = response1.data['search_results']

        # 세션 요약 확인
        session = ChatSession.objects.get(id=self.session.id)
        self.assertEqual(session.summary, query1[:9] + '...' if len(query1) > 12 else query1)

        # 두 번째 쿼리
        response2 = self.client.post('/chatbot/chat/', {
            'session_id': self.session.id,
            'query': query2,
            'nation': nation
        }, format='json')
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertIn('response', response2.data)
        self.assertIn('search_results', response2.data)
        result2 = response2.data['response']
        search_results2 = response2.data['search_results']

        print(f"\nSession ID: {self.session.id}")
        print(f"First Query: {query1}")
        print(f"First Response: {result1}")
        print(f"First Search Results: {json.dumps(search_results1, indent=2, ensure_ascii=False)}")
        print(f"Second Query: {query2}")
        print(f"Second Response: {result2}")
        print(f"Second Search Results: {json.dumps(search_results2, indent=2, ensure_ascii=False)}")

        # 세션 상세 정보와 메시지 확인
        response_detail = self.client.get(f'/chatbot/sessions/{self.session.id}/')
        self.assertEqual(response_detail.status_code, status.HTTP_200_OK)
        self.assertIn('summary', response_detail.data)  # Check if summary is in the session detail
        print(f"\ntest_get_session_detail >> Session details after chat:\n{json.dumps(response_detail.data, indent=2, ensure_ascii=False)}")

        # 세션 리스트 확인
        response_list = self.client.get('/chatbot/sessions/')
        self.assertEqual(response_list.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response_list.data), 1)
        print(f"\ntest_openai_chat >> Session list retrieved: {json.dumps(response_list.data, indent=2, ensure_ascii=False)}")
