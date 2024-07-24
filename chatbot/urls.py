from django.urls import path
from .views import (
    ChatSessionListView,
    ChatSessionDetailView,
    CreateNewSessionView,
    OpenAIChatView,
    CaseSearchView
)

urlpatterns = [
    path('sessions/', ChatSessionListView.as_view(), name='session-list'),
    path('sessions/<int:pk>/', ChatSessionDetailView.as_view(), name='session-detail'),
    path('sessions/new/', CreateNewSessionView.as_view(), name='create-session'),
    path('chat/', OpenAIChatView.as_view(), name='openai_chat'),
    path('chat/precedent/', CaseSearchView.as_view(), name='search-precedent'),
]