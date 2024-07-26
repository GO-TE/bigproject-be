from rest_framework import serializers
from .models import Article, Comment


class CommentSerializer(serializers.ModelSerializer):
    user_nickname = serializers.CharField(source='user.nickname', read_only=True)
    is_author = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'article', 'user_nickname', 'message', 'created_at', 'updated_at', 'is_author']
        read_only_fields = ['user', 'created_at', 'updated_at']

    def get_is_author(self, obj):
        request = self.context.get('request')
        return obj.user == request.user if request else False


class ArticleSerializer(serializers.ModelSerializer):
    comments = serializers.SerializerMethodField()
    user_nickname = serializers.CharField(source='user.nickname', read_only=True)
    is_author = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = ['id', 'user_nickname', 'image', 'category', 'title', 'content', 'created_at', 'updated_at', 'view',
                  'is_active', 'comments', 'is_author']

    def get_comments(self, obj):
        comments = obj.comment_set.all()
        return CommentSerializer(comments, many=True).data

    def get_is_author(self, obj):  # is_author 필드를 계산하기 위한 메서드
        request = self.context.get('request')
        return obj.user == request.user if request else False


class ArticleListSerializer(serializers.ModelSerializer):
    user_nickname = serializers.CharField(source='user.nickname', read_only=True)
    comment_count = serializers.IntegerField(source='comment_set.count', read_only=True)

    class Meta:
        model = Article
        fields = ['id', 'user_nickname', 'image', 'category', 'title', 'content', 'created_at', 'updated_at', 'view',
                  'is_active', 'comment_count']
