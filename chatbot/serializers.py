from rest_framework import serializers
from .models import ChatSession, ChatMessage

class ChatSessionSerializer(serializers.ModelSerializer):
    session_id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = ChatSession
        fields = ['session_id', 'user', 'created_at', 'updated_at', 'is_active', 'summary']  

class ChatMessageSerializer(serializers.ModelSerializer):
    session_id = serializers.IntegerField(source='session.id', read_only=True)
    session = serializers.PrimaryKeyRelatedField(queryset=ChatSession.objects.all(), write_only=True)

    class Meta:
        model = ChatMessage
        fields = ['id', 'session_id', 'session', 'message', 'sent_at', 'sender']

class ChatSessionDetailSerializer(serializers.ModelSerializer):
    session_id = serializers.IntegerField(source='id', read_only=True)
    messages = ChatMessageSerializer(many=True, read_only=True, source='chatmessage_set')

    class Meta:
        model = ChatSession
        fields = ['session_id', 'user', 'created_at', 'updated_at', 'is_active', 'summary', 'messages']  
