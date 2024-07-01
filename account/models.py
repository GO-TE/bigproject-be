import uuid

from django.db import models


# Create your models here.


class User(models.Model):
    id = models.AutoField(primary_key=True)
    nationality = models.CharField(max_length=50, null=False)
    work_at = models.CharField(max_length=50, null=False)
    uuid = models.CharField(max_length=36, unique=True)
    username = models.CharField(max_length=50, null=False)
    nickname = models.CharField(max_length=20, unique=True, null=False)
    password = models.CharField(max_length=128, null=False)
    email = models.EmailField(max_length=100, unique=True, null=False)
    role = models.BooleanField(default=False)
    profile_picture = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta():
        db_table = "user"

    def __str__(self):
        return self.nickname

