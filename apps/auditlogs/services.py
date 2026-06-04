from apps.auditlogs.models import AuditLog


class AuditLogService:
    @staticmethod
    def log(user=None, action='', description='', resource_type='', resource_id='',
            tenant=None, ip_address=None, metadata=None):
        AuditLog.objects.create(
            user=user,
            action=action,
            description=description,
            resource_type=resource_type,
            resource_id=resource_id,
            tenant=tenant,
            ip_address=ip_address,
            metadata=metadata or {},
        )
