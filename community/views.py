from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import (
    CreateAPIView,
    RetrieveUpdateDestroyAPIView,
    ListAPIView
)
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.decorators import permission_classes

from .models import Article, Comment, Category
from .serializers import (
    ArticleSerializer,
    CommentSerializer,
    ArticleListSerializer,
)
from .permissions import IsOwnerOrReadOnly

@permission_classes([AllowAny])
class ArticleListView(APIView):

    def get(self, request):
        try:
            articles = Article.objects.select_related('user', 'category').order_by('-created_at')
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

            serializer = ArticleListSerializer(articles, many=True)
            return Response(serializer.data)

        except Exception as e:
            return Response({"error": str(e)}, status=500)

@permission_classes([IsAuthenticated,IsOwnerOrReadOnly])
class ArticleDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Article.objects.select_related('user', 'category').prefetch_related('comment_set')
    serializer_class = ArticleSerializer

    def retrieve(self, request, *args, **kwargs):
        try:
            article = self.get_object()
            article.increment_view_count()
            serializer = self.get_serializer(article)
            return Response(serializer.data)
        except Article.DoesNotExist:
            raise NotFound("Article not found")
        except Exception as e:
            return Response({"error": str(e)}, status=500)

@permission_classes([IsAuthenticated])
class ArticleCreateView(CreateAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

    def perform_create(self, serializer):
        try:
            serializer.save(user=self.request.user)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

@permission_classes([AllowAny])
class CommentListView(ListAPIView):
    queryset = Comment.objects.select_related('article', 'user')
    serializer_class = CommentSerializer

@permission_classes([IsAuthenticated,IsOwnerOrReadOnly])
class CommentDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.select_related('article', 'user')
    serializer_class = CommentSerializer

    def get_object(self):
        try:
            comment = super().get_object()
            return comment
        except Comment.DoesNotExist:
            raise NotFound("Comment not found")
        except Exception as e:
            return Response({"error": str(e)}, status=500)

@permission_classes([IsAuthenticated])
class ArticleCommentCreateView(CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        try:
            article_id = self.kwargs.get('article_pk')
            article = Article.objects.get(pk=article_id)
            serializer.save(user=self.request.user, article=article)
        except Article.DoesNotExist:
            raise NotFound("Article not found")
        except Exception as e:
            return Response({"error": str(e)}, status=500)

@permission_classes([AllowAny])
class ArticleByCategoryListView(APIView):

    def get(self, request, category_id):
        try:
            category = Category.objects.get(id=category_id)
            articles = Article.objects.filter(category=category).select_related('user', 'category').order_by('-created_at')

            if not articles.exists():
                return Response({"articles": [], "message": "No articles found in this category."}, status=200)

            serializer = ArticleSerializer(articles, many=True)
            return Response(serializer.data)
        except Category.DoesNotExist:
            raise NotFound("Category not found")
        except Exception as e:
            return Response({"error": str(e)}, status=500)
