from rest_framework import filters
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import (
    FAQ,
    Law,
    Rule,
    Glossary
)
from .serializers import (
    FAQSerializer,
    LawSerializer,
    RuleSerializer,
    GlossarySerializer
)
from .pagination import FQAPagination


class FAQListView(ListAPIView):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer
    permission_classes = [AllowAny]


class FAQByCategoryListView(ListAPIView):
    serializer_class = FAQSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        category = self.kwargs['category']
        return FAQ.objects.filter(category=category)


class LawListView(ListAPIView):
    queryset = Law.objects.all()
    serializer_class = LawSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'content']
    pagination_class = FQAPagination
    permission_classes = [AllowAny]


    def get_queryset(self):
        queryset = Law.objects.all().order_by('-law')
        title_query = self.request.query_params.get('title', None)
        content_query = self.request.query_params.get('content', None)

        if title_query:
            queryset = queryset.filter(law__icontains=title_query)
        if content_query:
            queryset = queryset.filter(content__icontains=content_query)

        return queryset

