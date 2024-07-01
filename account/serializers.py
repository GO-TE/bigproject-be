import uuid

from django.contrib.auth.hashers import make_password
from django.core.validators import MinLengthValidator

from rest_framework import serializers

from account.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'nationality', 'work_at', 'username',
            'nickname', 'password', 'email',
        ]
        extra_kwargs = {
            'password': {'write_only': True, 'validators': [MinLengthValidator(8)]},
            'email': {'required': True},
        }

    def create(self, validated_data):
        validated_data['uuid'] = str(uuid.uuid4())
        validated_data['password'] = make_password(validated_data['password'])
        user = User.objects.create(**validated_data)
        return user

