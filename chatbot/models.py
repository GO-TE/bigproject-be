from django.db import models
from django.conf import settings

class ChatSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    summary = models.CharField(max_length=255, blank=True, null=True)
    
class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE)
    message = models.TextField(null=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    sender = models.IntegerField(null=True)  