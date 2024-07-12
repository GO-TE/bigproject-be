from rest_framework import serializers
from .models import Article, Comment


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'article', 'user', 'message', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']  # user와 timestamp 필드를 읽기 전용으로 설정


class ArticleSerializer(serializers.ModelSerializer):
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = ['id', 'user', 'image', 'category', 'title', 'content', 'created_at', 'updated_at', 'view',
                  'is_active', 'comments']

    def get_comments(self, obj):
        comments = obj.comment_set.all()
        return CommentSerializer(comments, many=True).data
