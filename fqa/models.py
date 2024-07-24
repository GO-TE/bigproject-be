from django.db import models
from django.conf import settings
from community.models import Category


class FAQ(models.Model):
    question = models.TextField(null=True)
    answer = models.TextField(null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.question


class Law(models.Model):
    law = models.CharField(null=False, max_length=100)
    ministry = models.CharField(max_length=10)
    code = models.CharField(max_length=20)
    date = models.CharField(max_length=10)
    content = models.TextField()
    total_view = models.BigIntegerField(default=0)
    week_view = models.BigIntegerField(default=0)

    def __str__(self):
        return self.law


class Rule(models.Model):
    rule = models.CharField(null=False, max_length=100)
    kind = models.CharField(max_length=20)
    code = models.CharField(max_length=10)
    ministry = models.CharField(max_length=30)
    history = models.CharField(max_length=20)
    state = models.CharField(max_length=20)
    effective = models.CharField(max_length=10)
    created = models.CharField(max_length=10)
    content = models.TextField()
    total_view = models.BigIntegerField(default=0)
    week_view = models.BigIntegerField(default=0)

    def __str__(self):
        return self.rule


class Glossary(models.Model):
    terminology = models.CharField(null=False, max_length=100)
    code = models.IntegerField()
    content = models.TextField()
    total_view = models.BigIntegerField(default=0)
    week_view = models.BigIntegerField(default=0)

    def __str__(self):
        return self.terminology
