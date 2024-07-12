from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import (
    CreateAPIView,
    RetrieveUpdateDestroyAPIView,
    ListAPIView
)
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import Article, Comment
from .serializers import (
    ArticleSerializer,
    CommentSerializer,
)
from .permissions import IsOwnerOrReadOnly


class ArticleListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        articles = Article.objects.select_related('user', 'category').prefetch_related('comment_set').order_by(
            '-created_at')
        title = request.query_params.get('title', None)
        content = request.query_params.get('content', None)
        username = request.query_params.get('user', None)

        if title:
            articles = articles.filter(title__icontains=title)
        if content:
            articles = articles.filter(content__icontains=content)
        if username:
            articles = articles.filter(user__username__icontains=username)

        if not articles.exists():
            return Response({"articles": [], "message": "No articles found matching your query."}, status=200)

        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data)


class ArticleDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Article.objects.select_related('user', 'category').prefetch_related('comment_set')
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def retrieve(self, request, *args, **kwargs):
        article = self.get_object()
        article.increment_view_count()
        serializer = self.get_serializer(article)
        return Response(serializer.data)


class ArticleCreateView(CreateAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CommentListView(ListAPIView):
    queryset = Comment.objects.select_related('article', 'user')
    serializer_class = CommentSerializer
    permission_classes = [AllowAny]


class CommentDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.select_related('article', 'user')
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]


class ArticleCommentCreateView(CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        article_id = self.kwargs.get('article_pk')
        article = Article.objects.get(pk=article_id)
        serializer.save(user=self.request.user, article=article)


class ArticleByCategoryListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, category_id):
        articles = Article.objects.filter(category_id=category_id).select_related('user', 'category').prefetch_related(
            'comment_set').order_by('-created_at')

        if not articles.exists():
            return Response({"articles": [], "message": "No articles found in this category."}, status=200)

        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data)
