from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.settings_app.models import SystemSettings, DEFAULT_SETTINGS
from apps.settings_app.serializers import SystemSettingsSerializer, SettingsUpdateSerializer
from core.permissions import IsSuperAdmin
from apps.auditlogs.services import AuditLogService


class SettingsListView(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        for category, defaults in DEFAULT_SETTINGS.items():
            SystemSettings.objects.get_or_create(
                category=category,
                defaults={'settings': defaults},
            )
        settings = SystemSettings.objects.all()
        return Response({
            'success': True,
            'data': SystemSettingsSerializer(settings, many=True).data,
        })


class SettingsDetailView(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request, category):
        obj, _ = SystemSettings.objects.get_or_create(
            category=category,
            defaults={'settings': DEFAULT_SETTINGS.get(category, {})},
        )
        return Response({'success': True, 'data': SystemSettingsSerializer(obj).data})

    def patch(self, request, category):
        serializer = SettingsUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj, _ = SystemSettings.objects.get_or_create(
            category=category,
            defaults={'settings': DEFAULT_SETTINGS.get(category, {})},
        )
        obj.settings = {**obj.settings, **serializer.validated_data['settings']}
        obj.save()
        AuditLogService.log(
            user=request.user,
            action='settings_update',
            description=f'Updated {category} settings',
            resource_type='settings',
            resource_id=category,
            ip_address=getattr(request, 'client_ip', None),
        )
        return Response({'success': True, 'data': SystemSettingsSerializer(obj).data})
