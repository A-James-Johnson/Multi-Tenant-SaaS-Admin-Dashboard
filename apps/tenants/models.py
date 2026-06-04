from django.db import models
from core.models import TimestampedModel


class Tenant(TimestampedModel):
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        SUSPENDED = 'suspended', 'Suspended'
        PENDING = 'pending', 'Pending'
        INACTIVE = 'inactive', 'Inactive'

    name = models.CharField(max_length=200, db_index=True)
    company_name = models.CharField(max_length=200)
    email = models.EmailField(db_index=True)
    contact_number = models.CharField(max_length=20, blank=True)
    slug = models.SlugField(max_length=200, unique=True)
    logo = models.ImageField(upload_to='tenant_logos/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    subscription_plan = models.ForeignKey(
        'subscriptions.Plan',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tenants',
    )
    is_deleted = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'tenants'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['slug']),
            models.Index(fields=['is_deleted', 'status']),
        ]

    def __str__(self):
        return self.name

    @property
    def is_active(self):
        return self.status == self.Status.ACTIVE and not self.is_deleted
