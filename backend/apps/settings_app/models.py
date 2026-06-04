from django.db import models
from core.models import TimestampedModel


class SystemSettings(TimestampedModel):
    """Singleton-style system settings."""

    class Category(models.TextChoices):
        GENERAL = 'general', 'General'
        SECURITY = 'security', 'Security'
        EMAIL = 'email', 'Email'

    category = models.CharField(max_length=20, choices=Category.choices, unique=True)
    settings = models.JSONField(default=dict)

    class Meta:
        db_table = 'system_settings'
        verbose_name_plural = 'System settings'

    def __str__(self):
        return f'{self.category} settings'


DEFAULT_SETTINGS = {
    'general': {
        'company_name': 'SaaS Admin Platform',
        'logo_url': '',
        'support_email': 'support@saasadmin.com',
        'timezone': 'UTC',
    },
    'security': {
        'password_min_length': 8,
        'password_require_uppercase': True,
        'password_require_numbers': True,
        'password_require_special': True,
        'session_timeout_minutes': 60,
        'mfa_enabled': False,
        'max_login_attempts': 5,
    },
    'email': {
        'smtp_host': '',
        'smtp_port': 587,
        'smtp_user': '',
        'smtp_password': '',
        'smtp_use_tls': True,
        'from_email': 'noreply@saasadmin.com',
    },
}
