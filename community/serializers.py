from rest_framework import serializers
from .models import Article, Comment


class CommentSerializer(serializers.ModelSerializer):
    user_nickname = serializers.CharField(source='user.nickname', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'article', 'user_nickname', 'message', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']


class ArticleSerializer(serializers.ModelSerializer):
    comments = serializers.SerializerMethodField()
    user_nickname = serializers.CharField(source='user.nickname', read_only=True)

    class Meta:
        model = Article
        fields = ['id', 'user_nickname', 'image', 'category', 'title', 'content', 'created_at', 'updated_at', 'view',
                  'is_active', 'comments']

    def get_comments(self, obj):
        comments = obj.comment_set.all()
        return CommentSerializer(comments, many=True).data


class ArticleListSerializer(serializers.ModelSerializer):
    user_nickname = serializers.CharField(source='user.nickname', read_only=True)
    comment_count = serializers.IntegerField(source='comment_set.count', read_only=True)


    class Meta:
        model = Article
        fields = ['id', 'user_nickname', 'image', 'category', 'title', 'content', 'created_at', 'updated_at', 'view',
                  'is_active', 'comment_count']
