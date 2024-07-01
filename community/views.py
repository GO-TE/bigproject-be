from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .models import Article
from .serializers import ArticleSerializer

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_query_param = 'page'

class ArticleListView(APIView):
    pagination_class = StandardResultsSetPagination

    def get(self, request):
        articles = Article.objects.all().order_by('-created_at')
        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(articles, request)
        serializer = ArticleSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

from rest_framework import generics

class ArticleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
