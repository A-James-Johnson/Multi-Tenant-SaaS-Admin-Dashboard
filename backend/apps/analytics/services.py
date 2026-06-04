from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth


class AnalyticsService:
    @staticmethod
    def get_dashboard_kpis(user):
        from apps.tenants.models import Tenant
        from apps.accounts.models import User as UserModel
        from apps.billing.models import Payment
        from apps.subscriptions.models import Subscription

        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        if user.is_super_admin:
            tenants = Tenant.objects.filter(is_deleted=False)
            users = UserModel.objects.filter(status='active')
            payments = Payment.objects.filter(status='completed')
        else:
            tenants = Tenant.objects.filter(id=user.tenant_id, is_deleted=False)
            users = UserModel.objects.filter(tenant=user.tenant, status='active')
            payments = Payment.objects.filter(tenant=user.tenant, status='completed')

        return {
            'total_revenue': float(payments.aggregate(total=Sum('amount'))['total'] or 0),
            'monthly_revenue': float(
                payments.filter(payment_date__gte=month_start).aggregate(total=Sum('amount'))['total'] or 0
            ),
            'active_users': users.count(),
            'active_tenants': tenants.filter(status='active').count(),
            'total_tenants': tenants.count(),
            'active_subscriptions': Subscription.objects.filter(status='active').count(),
        }

    @staticmethod
    def get_revenue_trend(user, months=12):
        from apps.billing.models import Payment

        since = timezone.now() - timedelta(days=months * 30)
        payments = Payment.objects.filter(status='completed', payment_date__gte=since)
        if not user.is_super_admin:
            payments = payments.filter(tenant=user.tenant)

        data = payments.annotate(
            month=TruncMonth('payment_date')
        ).values('month').annotate(
            revenue=Sum('amount')
        ).order_by('month')

        return [
            {'month': item['month'].strftime('%Y-%m') if item['month'] else '', 'revenue': float(item['revenue'] or 0)}
            for item in data
        ]

    @staticmethod
    def get_user_growth(user, months=12):
        from apps.accounts.models import User as UserModel

        since = timezone.now() - timedelta(days=months * 30)
        users = UserModel.objects.filter(created_at__gte=since)
        if not user.is_super_admin:
            users = users.filter(tenant=user.tenant)

        data = users.annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')

        return [
            {'month': item['month'].strftime('%Y-%m') if item['month'] else '', 'users': item['count']}
            for item in data
        ]

    @staticmethod
    def get_tenant_growth(months=12):
        from apps.tenants.models import Tenant

        since = timezone.now() - timedelta(days=months * 30)
        data = Tenant.objects.filter(
            is_deleted=False, created_at__gte=since
        ).annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')

        return [
            {'month': item['month'].strftime('%Y-%m') if item['month'] else '', 'tenants': item['count']}
            for item in data
        ]

    @staticmethod
    def get_subscription_distribution():
        from apps.subscriptions.models import Subscription

        data = Subscription.objects.values(
            'plan__name', 'plan__tier'
        ).annotate(count=Count('id'))

        return [
            {'name': item['plan__name'], 'tier': item['plan__tier'], 'value': item['count']}
            for item in data
        ]

    @staticmethod
    def get_recent_activities(user, limit=10):
        from apps.auditlogs.models import AuditLog

        qs = AuditLog.objects.select_related('user', 'tenant').order_by('-created_at')
        if not user.is_super_admin:
            qs = qs.filter(tenant=user.tenant)
        return qs[:limit]

    @staticmethod
    def get_recent_payments(user, limit=5):
        from apps.billing.models import Payment

        qs = Payment.objects.select_related('tenant').order_by('-payment_date')
        if not user.is_super_admin:
            qs = qs.filter(tenant=user.tenant)
        return qs[:limit]
