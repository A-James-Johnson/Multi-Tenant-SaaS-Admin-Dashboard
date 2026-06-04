from django.db import models
from core.models import TimestampedModel


class Notification(TimestampedModel):
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications',
    )
    class Type(models.TextChoices):
        PLAN_EXPIRY = 'plan_expiry', 'Plan Expiry'
        PAYMENT_SUCCESS = 'payment_success', 'Payment Success'
        PAYMENT_FAILURE = 'payment_failure', 'Payment Failure'
        USER_INVITATION = 'user_invitation', 'User Invitation'
        SYSTEM_ALERT = 'system_alert', 'System Alert'

    class Channel(models.TextChoices):
        IN_APP = 'in_app', 'In App'
        EMAIL = 'email', 'Email'
        BOTH = 'both', 'Both'

    recipient = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='notifications',
    )
    type = models.CharField(max_length=30, choices=Type.choices)
    channel = models.CharField(max_length=10, choices=Channel.choices, default=Channel.IN_APP)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    email_sent = models.BooleanField(default=False)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['tenant', 'type']),
        ]

    def __str__(self):
        return self.title
