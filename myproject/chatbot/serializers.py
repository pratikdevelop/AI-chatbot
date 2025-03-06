from rest_framework import serializers
from .models import User, ChatMessage

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'name', 'phone', 'profile_picture', 'preferences']
        extra_kwargs = {'password': {'write_only': True}}

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['message', 'response', 'timestamp']