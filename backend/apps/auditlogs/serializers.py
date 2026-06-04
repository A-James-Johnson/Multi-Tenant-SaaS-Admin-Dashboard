from rest_framework import serializers
from apps.auditlogs.models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True, default='')
    tenant_name = serializers.CharField(source='tenant.name', read_only=True, default='')

    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'user_email', 'tenant', 'tenant_name', 'action',
            'resource_type', 'resource_id', 'description', 'ip_address',
            'metadata', 'created_at',
        ]
