from rest_framework import serializers
from .models import Document


# 1. Serializer for the Chat Endpoint
class ChatRequestSerializer(serializers.Serializer):
    prompt = serializers.CharField(required=True, max_length=5000)


# 2. Serializer for the Document CRUD ViewSet
class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ["id", "title", "content", "created_at", "updated_at", "active"]
        read_only_fields = ["id", "created_at", "updated_at"]
