from django.db import models
from django.conf import settings
from community.models import Category

class FAQ(models.Model):
    question = models.TextField(null=True)
    answer = models.TextField(null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.question