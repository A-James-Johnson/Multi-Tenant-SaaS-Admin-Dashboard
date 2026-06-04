from rest_framework import serializers
from apps.settings_app.models import SystemSettings, DEFAULT_SETTINGS


class SystemSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemSettings
        fields = ['id', 'category', 'settings', 'updated_at']
        read_only_fields = ['updated_at']


class SettingsUpdateSerializer(serializers.Serializer):
    settings = serializers.DictField()
