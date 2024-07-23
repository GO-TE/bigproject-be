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