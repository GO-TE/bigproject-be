import uuid

from django.contrib.auth.hashers import (
    make_password,
    check_password,
)
from django.core.validators import MinLengthValidator

from rest_framework import serializers

from account.models import User
from account.util.message import Message


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


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise serializers.ValidationError(Message.INVALID_LOGIN)

            if not check_password(password, user.password):
                raise serializers.ValidationError(Message.INVALID_LOGIN)

        data['user'] = user
        return data

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['nationality', 'work_at', 'username','nickname', 'email']
