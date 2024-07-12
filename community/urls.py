from django.urls import path
from .views import (
    ArticleListView,
    ArticleDetailView,
    ArticleCreateView,
    CommentListView,
    CommentDetailView,
    ArticleCommentCreateView,
    ArticleByCategoryListView,
)

urlpatterns = [
    path('articles/', ArticleListView.as_view(), name='article-list'),
    path('articles/<int:pk>/', ArticleDetailView.as_view(), name='article-detail'),
    path('articles/create/', ArticleCreateView.as_view(), name='article-create'),
    path('comments/', CommentListView.as_view(), name='comment-list'),
    path('comments/<int:pk>/', CommentDetailView.as_view(), name='comment-detail'),
    path('articles/<int:article_pk>/comments/', ArticleCommentCreateView.as_view(), name='article-comment-create'),
    path('articles/category/<int:category_id>/', ArticleByCategoryListView.as_view(), name='article-by-category'), 
]
