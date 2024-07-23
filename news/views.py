from django.core.cache import cache

from rest_framework import filters
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes


from news.models import NewsArticle
from news.serializers import NewsArticleSerializer
from news.pagination import NewsPagination


@permission_classes([AllowAny])
class NewsIndexThumbnailView(APIView):  # 메인 페이지 3개 띄우기 (레디스 살짝 오버 엔지니어링 느낌 있음)
    def get(self, reqeust):
        articles = cache.get('news_articles')
        if not articles:
            articles = list(NewsArticle.objects.order_by('-timestamp').values('id', 'title', 'image_link', 'news_agency', 'summary', 'timestamp'))[:3]
        else:
            return Response({'error': 'No articles found'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'articles': articles}, status=status.HTTP_200_OK)


@permission_classes([AllowAny])
class NewsListView(ListAPIView):
    queryset = NewsArticle.objects.all()
    serializer_class = NewsArticleSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title']
    pagination_class = NewsPagination

    def get_queryset(self):
        queryset = NewsArticle.objects.all().order_by('-timestamp')
        title_query = self.request.query_params.get('title', None)

        if title_query:
            queryset = queryset.filter(title__icontains=title_query)

        return queryset


@permission_classes([AllowAny])
class NewsArticleDetailView(APIView):
    def get(self, request):
        id = request.query_params.get('id', None)
        news = NewsArticle.objects.get(id=request.data.get(id, None))

        if news is None:
            return Response(
                {'message': '찾는 뉴스 id가 없당게요'},
                status=status.HTTP_404_NOT_FOUND
            )

        data = {
            'title': news.title,
            'summary': news.summary,
            'news_link': news.news_link,
            'image_link': news.image_link,
            'news_agency': news.news_agency,
            'timestamp': news.timestamp,
            'news_content': news.news_content
        }

        return Response(data, status.HTTP_200_OK)
