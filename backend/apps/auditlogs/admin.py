from django.contrib import admin
from apps.auditlogs.models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['action', 'user', 'tenant', 'ip_address', 'created_at']
    list_filter = ['action']
    search_fields = ['description']
