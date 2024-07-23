from django.db import models

# Create your models here.

class NewsArticle(models.Model):
    title = models.CharField(max_length=255, unique=True)
    summary = models.TextField()
    news_link = models.URLField(unique=True)
    image_link = models.URLField(blank=True, null=True)
    news_agency = models.CharField(max_length=255)
    timestamp = models.CharField(max_length=100)
    news_content = models.TextField()
    total_view = models.BigIntegerField(default=0)
    week_view = models.BigIntegerField(default=0)

    def __str__(self):
        return self.title