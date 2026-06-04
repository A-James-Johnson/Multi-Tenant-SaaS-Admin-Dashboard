from django.db import models
from core.models import TimestampedModel


class AuditLog(TimestampedModel):
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='audit_logs',
    )
    class Action(models.TextChoices):
        LOGIN = 'login', 'Login'
        LOGOUT = 'logout', 'Logout'
        USER_CREATE = 'user_create', 'User Creation'
        USER_UPDATE = 'user_update', 'User Update'
        USER_DELETE = 'user_delete', 'User Deletion'
        ROLE_CHANGE = 'role_change', 'Role Change'
        PAYMENT_CREATE = 'payment_create', 'Payment Action'
        PAYMENT_UPDATE = 'payment_update', 'Payment Update'
        SUBSCRIPTION_CHANGE = 'subscription_change', 'Subscription Change'
        TENANT_CREATE = 'tenant_create', 'Tenant Creation'
        TENANT_UPDATE = 'tenant_update', 'Tenant Update'
        TENANT_SUSPEND = 'tenant_suspend', 'Tenant Suspend'
        TENANT_ACTIVATE = 'tenant_activate', 'Tenant Activate'
        SETTINGS_UPDATE = 'settings_update', 'Settings Update'

    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
    )
    action = models.CharField(max_length=30, choices=Action.choices, db_index=True)
    resource_type = models.CharField(max_length=50, blank=True)
    resource_id = models.CharField(max_length=50, blank=True)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'audit_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'action']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f'{self.action} - {self.created_at}'
