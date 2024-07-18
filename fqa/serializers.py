from rest_framework import serializers

from .models import (
    FAQ,
    Law,
    Rule,
    Glossary
)


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ['id', 'question', 'answer',
                  'category']


class LawSerializer(serializers.ModelSerializer):
    class Meta:
        model = Law
        fields = "__all__"


class RuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rule
        fields = "__all__"


class GlossarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Glossary
        fields = "__all__"
