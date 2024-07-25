import os
import json
import requests
import faiss
import pickle
import html

from sklearn.feature_extraction.text import TfidfVectorizer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, generics
from rest_framework.decorators import permission_classes

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.memory import ConversationBufferMemory

from .models import ChatSession, ChatMessage
from .serializers import ChatSessionSerializer, ChatMessageSerializer, ChatSessionDetailSerializer

# API 키
with open('secrets.json') as f:
    keys = json.load(f)

OPENAI_API_KEY = keys['openai_api_key']
translation_api_key = keys['google_api_key']

os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY

# 챗봇 세팅
chat = ChatOpenAI(model="gpt-3.5-turbo")
embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")

# 판례 파일 경로
index_file_path = os.path.join(os.path.dirname(__file__), 'faiss_index.index')
pickle_file_path = os.path.join(os.path.dirname(__file__), 'case_contents.pkl')

# 저장된 인덱스를 로드
loaded_index_case = faiss.read_index(index_file_path)

# 판례 내용을 피클 파일에서 로드
with open(pickle_file_path, 'rb') as f:
    doc_contents_case = pickle.load(f)

# 벡터 차원
d = loaded_index_case.d

# 텍스트 데이터를 TF-IDF 벡터로 변환
vectorizer = TfidfVectorizer(max_features=5000)
vectorizer.fit(doc_contents_case)

# 코사인 유사도 계산 함수
def get_cosine_similarity(query, index, vectorizer):
    query_vector = vectorizer.transform([query]).toarray().astype('float32')
    D, I = index.search(query_vector, 3)  # 상위 3개 검색
    return I[0], D[0]

def translate_text(text, target_language):
    url = f"https://translation.googleapis.com/language/translate/v2?key={translation_api_key}"
    params = {
        'q': text,
        'target': target_language
    }
    response = requests.post(url, data=params)
    if response.status_code == 200:
        result = response.json()
        translated_text = result['data']['translations'][0]['translatedText']
        detected_language = result['data']['translations'][0]['detectedSourceLanguage']
        return translated_text, detected_language
    else:
        raise Exception(f"Error in translation: {response.status_code}, {response.text}")

@permission_classes([IsAuthenticated])
class OpenAIChatView(APIView):

    def post(self, request):
        session_id = request.data.get('session_id')
        query = request.data.get('query')
        nation = request.data.get('nation')

        if not session_id:
            return Response({'error': 'Session ID is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not query:
            return Response({'error': 'Query is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not nation:
            return Response({'error': 'Nation is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # 벡터 데이터베이스 로드
        directory = f"./DB/{nation}db"
        database = Chroma(persist_directory=directory, embedding_function=embeddings)

        try:
            session = ChatSession.objects.prefetch_related('chatmessage_set').get(id=session_id, user=request.user)
        except ChatSession.DoesNotExist:
            return Response({'error': 'Session not found or access denied.'}, status=status.HTTP_404_NOT_FOUND)

        # 검색기 설정
        k = 3
        retriever = database.as_retriever(search_kwargs={"k": k})

        # ConversationChain 설정
        memory = ConversationBufferMemory(output_key='result')
        conversation = RetrievalQA.from_llm(
            llm=chat, 
            retriever=retriever, 
            memory=memory, 
            return_source_documents=True, 
            output_key='result'
        )

        # 이전 대화 불러오기
        previous_messages = session.chatmessage_set.order_by('sent_at')
        for message in previous_messages:
            if message.sender == 1:
                memory.chat_memory.add_user_message(message.message)
            else:
                memory.chat_memory.add_ai_message(message.message)

        # target_language 설정 >> 일 할 국가 nation 설정
        target_language = 'ko' if nation == 'korea' else 'en'

        # 입력 메시지 번역 (얻은 답변을 처음 질문받았을 때의 언어로 번역)
        translated_query, detected_language = translate_text(query, target_language)

        # 관련 정보를 포함하여 대화 모델에 전달
        instructions = (
            "'저'라는 표현과 '제'라는 단어는 사용하지 마시고 상대방에게 말하듯이 해주세요. "
            "당신은 제3의 입장입니다. 자신의 회사가 아닌 사용자 입장에서 상황을 이해하고 공감해 주세요. "
            "상대방의 상황에 대해 적극적으로 공감하는 말을 먼저 해주세요. "
            "공감하는 말 다음에는 관련 법률 내용을 요약해서 자세하게 설명해주세요."
            "법률 내용 설명 다음에는 인사이트나 조언을 길게 해주세요."
            "법률 정보는 지어내지 마시고 DB에 있는 내용을 사용해 주세요."
        )
        conversation_input = f"Instructions:\n{instructions}\n\nQuestion:\n{translated_query}"

        result = conversation(conversation_input)
        translated_result, _ = translate_text(result['result'], detected_language)
        
        translated_result = html.unescape(translated_result)

        # 새 메시지 저장
        new_message = ChatMessage(session=session, message=query, sender=1)  # 1 for user
        new_message.save()

        bot_response = ChatMessage(session=session, message=translated_result, sender=0)  # 0 for AI
        bot_response.save()

        # 세션 요약 업데이트 (첫 번째 메시지를 요약으로 사용, 12글자 초과 시 ...로 대체)
        first_message = previous_messages.first().message if previous_messages.exists() else query
        session.summary = first_message if len(first_message) <= 12 else first_message[:9] + '...'
        session.save()

        translated_ui_texts = {
            "search_cases": translate_text("판례 찾기", detected_language)[0]
        }

        return Response({"response": translated_result, "ui_texts": translated_ui_texts}, status=status.HTTP_200_OK)

@permission_classes([IsAuthenticated])
class CaseSearchView(APIView):

    def post(self, request):
        query = request.data.get('query')

        if not query:
            return Response({'error': 'Query is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            translated_query, detected_language = translate_text(query, 'en')  # 기본 번역 언어를 영어로 설정
            # 질문(query)에 대해 판례 검색
            top_indices, top_scores = get_cosine_similarity(query, loaded_index_case, vectorizer)
            case_results = [
                {"index": index, "score": score, "content": doc_contents_case[index]}
                for index, score in zip(top_indices, top_scores)
            ]

            # 판례 내용을 감지된 언어로 번역하여 content에 저장
            for case in case_results:
                translated_text, _ = translate_text(case['content'], detected_language)
                case['content'] = html.unescape(translated_text) 

            translated_ui_texts_2 = {
                "case_example": translate_text("판례 사례", detected_language)[0],
                "full_text": translate_text("내용 전문", detected_language)[0]
            }

            return Response({"case_results": case_results, "ui_texts": translated_ui_texts_2}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 전체 채팅 세션 나열
@permission_classes([IsAuthenticated])
class ChatSessionListView(generics.ListAPIView):
    queryset = ChatSession.objects.all()
    serializer_class = ChatSessionSerializer

    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user).prefetch_related('chatmessage_set')

# 특정 채팅 세션 ID의 정보 및 메시지 나열, 세션 삭제
@permission_classes([IsAuthenticated])
class ChatSessionDetailView(generics.RetrieveDestroyAPIView):
    queryset = ChatSession.objects.all()
    serializer_class = ChatSessionDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user).prefetch_related('chatmessage_set')

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        session = ChatSession.objects.prefetch_related('chatmessage_set').filter(id=instance.id, user=request.user).first()
        if not session:
            return Response({'error': 'Session not found or access denied.'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(instance)
        messages = ChatMessage.objects.filter(session=session).select_related('session')
        messages_serializer = ChatMessageSerializer(messages, many=True)
        data = serializer.data
        data['messages'] = messages_serializer.data
        return Response(data)

# 새 대화 세션 생성
@permission_classes([IsAuthenticated])
class CreateNewSessionView(APIView):

    def post(self, request):
        session = ChatSession.objects.create(user=request.user)
        serializer = ChatSessionSerializer(session)
    
        return Response(serializer.data, status=status.HTTP_201_CREATED)
