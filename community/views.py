from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import (
    CreateAPIView,
    RetrieveUpdateDestroyAPIView,
    ListAPIView
)
from rest_framework.permissions import IsAuthenticated

from .models import Article, Comment
from .serializers import ArticleSerializer, CommentSerializer
from .permissions import IsOwnerOrReadOnly

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    page_query_param = 'page'


class ArticleListView(APIView):
    pagination_class = StandardResultsSetPagination

    def get(self, request):
        articles = Article.objects.all().order_by('-created_at')
        paginate = request.query_params.get('page', None)

        if paginate:
            paginator = self.pagination_class()
            result_page = paginator.paginate_queryset(articles, request)
            serializer = ArticleSerializer(result_page, many=True)
            return paginator.get_paginated_response(serializer.data)
        else:
            serializer = ArticleSerializer(articles, many=True)
            return Response(serializer.data)


class ArticleDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Article.objects.all()
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
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated]


class CommentDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]


class ArticleCommentCreateView(CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        article_id = self.kwargs.get('article_pk')
        serializer.save(user=self.request.user, article_id=article_id)
