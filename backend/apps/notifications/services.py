from django.core.mail import send_mail
from django.conf import settings
from apps.notifications.models import Notification


class NotificationService:
    @staticmethod
    def create(user, type, title, message, channel='in_app', tenant=None, metadata=None):
        notification = Notification.objects.create(
            recipient=user,
            tenant=tenant or user.tenant,
            type=type,
            channel=channel,
            title=title,
            message=message,
            metadata=metadata or {},
        )
        if channel in ('email', 'both'):
            NotificationService.send_email(user, title, message)
            notification.email_sent = True
            notification.save(update_fields=['email_sent'])
        return notification

    @staticmethod
    def send_email(user, subject, message):
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )

    @staticmethod
    def mark_all_read(user):
        return Notification.objects.filter(recipient=user, is_read=False).update(
            is_read=True,
            read_at=__import__('django.utils.timezone', fromlist=['timezone']).timezone.now(),
        )
