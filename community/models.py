from django.db import models
from django.conf import settings

class User(models.Model):
    # User 모델은 이미 프로젝트에 존재한다고 가정합니다.
    pass

class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    major = models.CharField(max_length=30, null=True)
    sub = models.CharField(max_length=30, null=True)

    def __str__(self):
        return f"{self.major} - {self.sub}"

class Image(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    path = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.path

class Article(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    image = models.ForeignKey(Image, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, null=True)
    content = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    view = models.BigIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def increment_view_count(self):
        self.view += 1
        self.save(update_fields=['view'])

    def __str__(self):
        return self.title

class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    message = models.CharField(max_length=200, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.message

