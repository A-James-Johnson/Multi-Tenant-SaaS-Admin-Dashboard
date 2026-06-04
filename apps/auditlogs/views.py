from rest_framework import generics
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.auditlogs.models import AuditLog
from apps.auditlogs.serializers import AuditLogSerializer
from core.permissions import IsTenantAdmin


class AuditLogListView(generics.ListAPIView):
    serializer_class = AuditLogSerializer
    permission_classes = [IsTenantAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['action', 'tenant', 'user']
    search_fields = ['description', 'resource_type']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        qs = AuditLog.objects.select_related('user', 'tenant')
        if user.is_super_admin:
            return qs
        return qs.filter(tenant=user.tenant)

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({'success': True, 'data': response.data})
