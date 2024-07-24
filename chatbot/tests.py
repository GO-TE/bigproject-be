from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import ChatSession, ChatMessage
from account.models import User
import json
import numpy as np

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
        self.assertIn('summary', response.data[0])
        print(f"\ntest_get_session_list >> Session list retrieved: {json.dumps(response.data, indent=2, ensure_ascii=False)}")

    def test_get_session_detail(self):
        ChatMessage.objects.create(session=self.session, **self.message_data)

        response = self.client.get(f'/chatbot/sessions/{self.session.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['session_id'], self.session.id)
        self.assertIn('messages', response.data)
        self.assertIn('summary', response.data)
        print(f"\ntest_get_session_detail >> Session details retrieved for ID: {self.session.id}\nDetails: {json.dumps(response.data, indent=2, ensure_ascii=False)}")

    def test_get_messages(self):
        ChatMessage.objects.create(session=self.session, **self.message_data)
        response = self.client.get(f'/chatbot/sessions/{self.session.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('messages', response.data)
        self.assertIn('summary', response.data)
        print(f"\ntest_get_messages >> Messages retrieved for session ID: {self.session.id}\nMessages: {json.dumps(response.data['messages'], indent=2, ensure_ascii=False)}")

    def test_openai_chat_and_case_search(self):
        query1 = '제가 회사에서 발생한 화재로 크게 다쳤어요. 이와 관련된 법 조언을 얻을 수 있을까요?'
        query2 = 'I quit my job, but the boss didn\'t pay me. what should i do'
        nation = 'korea'

        # 첫 번째 쿼리
        response1 = self.client.post('/chatbot/chat/', {
            'session_id': self.session.id,
            'query': query1,
            'nation': nation
        }, format='json')
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertIn('response', response1.data)
        self.assertIn('ui_texts', response1.data)
        result1 = response1.data['response']
        ui_texts1 = response1.data['ui_texts']

        # 판례 검색 - 첫 번째 질문
        case_response1 = self.client.post('/chatbot/chat/precedent/', {
            'query': query1,
            'detected_language': 'ko'
        }, format='json')
        self.assertEqual(case_response1.status_code, status.HTTP_200_OK)
        self.assertIn('case_results', case_response1.data)
        self.assertIn('ui_texts', case_response1.data)
        case_results1 = case_response1.data['case_results']
        ui_texts2_1 = case_response1.data['ui_texts']

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
        self.assertIn('ui_texts', response2.data)
        result2 = response2.data['response']
        ui_texts2 = response2.data['ui_texts']

        # 판례 검색 - 두 번째 질문
        case_response2 = self.client.post('/chatbot/chat/precedent/', {
            'query': query2,
            'detected_language': 'en'
        }, format='json')
        self.assertEqual(case_response2.status_code, status.HTTP_200_OK)
        self.assertIn('case_results', case_response2.data)
        self.assertIn('ui_texts', case_response2.data)
        case_results2 = case_response2.data['case_results']
        ui_texts2_2 = case_response2.data['ui_texts']

        def convert_to_serializable(data):
            if isinstance(data, np.int64):
                return int(data)
            if isinstance(data, np.float32):
                return float(data)
            raise TypeError(f"Object of type {data.__class__.__name__} is not JSON serializable")

        print(f"\nSession ID: {self.session.id}")
        print(f"First Query: {query1}")
        print(f"First Response: {result1}")
        print(f"First UI Texts: {json.dumps(ui_texts1, indent=2, ensure_ascii=False)}")
        print(f"First Case Search Results: {json.dumps(case_results1, indent=2, ensure_ascii=False, default=convert_to_serializable)}")
        print(f"First Case UI Texts: {json.dumps(ui_texts2_1, indent=2, ensure_ascii=False)}")
        print(f"Second Query: {query2}")
        print(f"Second Response: {result2}")
        print(f"Second UI Texts: {json.dumps(ui_texts2, indent=2, ensure_ascii=False)}")
        print(f"Second Case Search Results: {json.dumps(case_results2, indent=2, ensure_ascii=False, default=convert_to_serializable)}")
        print(f"Second Case UI Texts: {json.dumps(ui_texts2_2, indent=2, ensure_ascii=False)}")

        # 세션 상세 정보와 메시지 확인
        response_detail = self.client.get(f'/chatbot/sessions/{self.session.id}/')
        self.assertEqual(response_detail.status_code, status.HTTP_200_OK)
        self.assertIn('summary', response_detail.data)
        print(f"\ntest_get_session_detail >> Session details after chat:\n{json.dumps(response_detail.data, indent=2, ensure_ascii=False)}")

        # 세션 리스트 확인
        response_list = self.client.get('/chatbot/sessions/')
        self.assertEqual(response_list.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response_list.data), 1)
        print(f"\ntest_openai_chat >> Session list retrieved: {json.dumps(response_list.data, indent=2, ensure_ascii=False)}")
