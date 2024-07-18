from rest_framework import (
    filters,
    status
)
from rest_framework.response import Response
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


class RuleListView(ListAPIView):
    queryset = Rule.objects.all()
    serializer_class = RuleSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'content']
    pagination_class = FQAPagination
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Rule.objects.all().order_by('-rule')
        title_query = self.request.query_params.get('title', None)
        content_query = self.request.query_params.get('content', None)

        if title_query:
            queryset = queryset.filter(rule__icontains=title_query)
        if content_query:
            queryset = queryset.filter(content__icontains=content_query)

        return queryset


class GlossaryListView(ListAPIView):
    queryset = Glossary.objects.all()
    serializer_class = GlossarySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'content']
    pagination_class = FQAPagination
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Glossary.objects.all().order_by('-terminology')
        title_query = self.request.query_params.get('title', None)
        content_query = self.request.query_params.get('content', None)

        if title_query:
            queryset = queryset.filter(terminology__icontains=title_query)
        if content_query:
            queryset = queryset.filter(content__icontains=content_query)

        return queryset


class ViewUpdateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        obj = request.data.get('category', None)
        obj_id = request.data.get('id', None)

        if not obj or not obj_id:
            return Response(
                {'message': 'Category and ID are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        model_map = {
            'law': Law,
            'rule': Rule,
            'glossary': Glossary
        }

        model = model_map.get(obj.lower(), None)

        if not model:
            return Response(
                {'message': 'Invalid category'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            instance = model.objects.get(id=obj_id)
            instance.total_view += 1
            instance.week_view += 1
            instance.save()
            return Response(
                {'status': 'views updated', 'total_views': instance.total_view, 'week_views': instance.week_view},
                status=status.HTTP_200_OK
            )
        except model.DoesNotExist:
            return Response(
                {'message': f'{obj.capitalize()} with ID {obj_id} does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )