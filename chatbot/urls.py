from django.urls import path
from .views import (
    ChatSessionListView,
    ChatSessionDetailView,
    CreateNewSessionView,
    OpenAIChatView
)

urlpatterns = [
    path('sessions/', ChatSessionListView.as_view(), name='session-list'),
    path('sessions/<int:pk>/', ChatSessionDetailView.as_view(), name='session-detail'),
    path('sessions/new/', CreateNewSessionView.as_view(), name='create-session'),
    path('chat/', OpenAIChatView.as_view(), name='openai_chat'),
]

# sessions 예제 출력 결과
# {
#     "session_id": 6,
#     "user": 5,
#     "created_at": "2024-07-10T17:40:36.850735+09:00",
#     "updated_at": "2024-07-10T17:40:43.892665+09:00",
#     "is_active": true,
#     "summary": "호주 고용법 알려줘."
#   }



# sessions/<int:pk>/ 예제 출력 결과 >> 정보 + 메세지
# {
#   "session_id": 6,
#   "user": 5,
#   "created_at": "2024-07-10T17:40:36.850735+09:00",
#   "updated_at": "2024-07-10T17:40:43.892665+09:00",
#   "is_active": true,
#   "summary": "호주 고용법 알려줘.",
#   "messages": [
#     {
#       "id": 3,
#       "session_id": 6,
#       "message": "호주 고용법 알려줘.",
#       "sent_at": "2024-07-10T17:40:41.152591+09:00",
#       "sender": 1
#     },
#     {
#       "id": 4,
#       "session_id": 6,
#       "message": "호주 고용법은 호주 고용주와 고용인 간의 관계를 규율하는 광범위한 규정과 정책을 다루고 있습니다. 여기에는 최저 임금, 근무 시간, 휴가 권리, 직장 건강 및 안전, 차별, 해고 등과 관련된 법률이 포함됩니다. Fair Work Act 2009는 다양한 주 및 테리토리 법률과 함께 호주의 고 용 관계를 규율하는 기본 법률입니다. 공정하고 안전한 근무 환경을 보장하려면 고용주와 직원 모두 호주 고용법에 따른 권리와 의무를 이해하는 것이 중요합니다. 더 알고 싶은 호주 고용법의 특정 측 면이 있습니까?",
#       "sent_at": "2024-07-10T17:40:41.153592+09:00",
#       "sender": 0
#     }
#   ]
#}