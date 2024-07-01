from django.urls import path
from .views import (
    ArticleListView,
    ArticleDetailView,
    ArticleCreateView,
    CommentListCreateView
)

urlpatterns = [
    path('articles/', ArticleListView.as_view(), name='article-list'),
    path('articles/<int:pk>/', ArticleDetailView.as_view(), name='article-detail'),
    path('articles/create/', ArticleCreateView.as_view(), name='article-create'),
    path('comments/', CommentListCreateView.as_view(), name='comment-list-create'),
]