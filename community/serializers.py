from rest_framework import serializers
from .models import Article, Comment
from account.models import User


class CommentSerializer(serializers.ModelSerializer):
    nickname = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'article', 'nickname', 'message', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']

    def get_user_nickname(self, obj):
        return obj.user.nickname


class ArticleSerializer(serializers.ModelSerializer):
    comments = serializers.SerializerMethodField()
    nickname = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = ['id', 'nickname', 'image', 'category', 'title', 'content', 'created_at', 'updated_at', 'view',
                  'is_active', 'comments']

    def get_comments(self, obj):
        comments = obj.comment_set.all()
        return CommentSerializer(comments, many=True).data

    def get_uesr_nickname(self, obj):
        return obj.user.nickname


class ArticleListSerializer(serializers.ModelSerializer):
    nickname = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = ['id', 'nickname', 'image', 'category', 'title', 'content', 'created_at', 'updated_at', 'view',
                  'is_active']

    def get_uesr_nickname(self, obj):
        return obj.user.nickname
