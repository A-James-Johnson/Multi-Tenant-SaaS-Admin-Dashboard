from datetime import date, timedelta
from django.utils import timezone
from apps.subscriptions.models import Subscription, Plan


class SubscriptionService:
    @staticmethod
    def create_subscription(tenant, plan, trial_days=14):
        start = date.today()
        trial_end = start + timedelta(days=trial_days)
        return Subscription.objects.create(
            tenant=tenant,
            plan=plan,
            status=Subscription.Status.TRIAL,
            start_date=start,
            trial_end_date=trial_end,
            end_date=trial_end,
        )

    @staticmethod
    def upgrade_plan(tenant, new_plan):
        subscription, _ = Subscription.objects.get_or_create(
            tenant=tenant,
            defaults={
                'plan': new_plan,
                'status': Subscription.Status.ACTIVE,
                'start_date': date.today(),
            }
        )
        old_plan = subscription.plan
        subscription.plan = new_plan
        subscription.status = Subscription.Status.ACTIVE
        subscription.end_date = date.today() + timedelta(days=30)
        subscription.save()
        tenant.subscription_plan = new_plan
        tenant.save()
        return subscription, old_plan

    @staticmethod
    def check_expiring_subscriptions(days=7):
        threshold = date.today() + timedelta(days=days)
        return Subscription.objects.filter(
            end_date__lte=threshold,
            status=Subscription.Status.ACTIVE,
        ).select_related('tenant', 'plan')
