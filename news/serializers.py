from rest_framework import serializers
from news.models import NewsArticle


class NewsArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsArticle
        fields = ['id', 'title', 'image_link', 'news_agency',
                  'timestamp', 'news_content', 'total_view']