from rest_framework import serializers
from apps.notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'id', 'type', 'channel', 'title', 'message', 'is_read',
            'read_at', 'metadata', 'created_at',
        ]
        read_only_fields = ['read_at', 'created_at']
