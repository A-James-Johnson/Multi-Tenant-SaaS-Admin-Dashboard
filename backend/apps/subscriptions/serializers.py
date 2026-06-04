from rest_framework import serializers
from apps.subscriptions.models import Plan, Subscription


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = [
            'id', 'name', 'tier', 'description', 'user_limit', 'storage_limit_gb',
            'monthly_price', 'yearly_price', 'features', 'is_active', 'sort_order',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']


class SubscriptionSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)
    plan_id = serializers.PrimaryKeyRelatedField(
        queryset=Plan.objects.all(), source='plan', write_only=True, required=False
    )
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)

    class Meta:
        model = Subscription
        fields = [
            'id', 'tenant', 'tenant_name', 'plan', 'plan_id', 'status',
            'start_date', 'end_date', 'trial_end_date', 'auto_renew',
            'cancelled_at', 'created_at', 'updated_at',
        ]
        read_only_fields = ['cancelled_at', 'created_at', 'updated_at']


class UpgradePlanSerializer(serializers.Serializer):
    plan_id = serializers.PrimaryKeyRelatedField(queryset=Plan.objects.filter(is_active=True))
