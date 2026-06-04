from django.utils.text import slugify
from rest_framework import serializers
from apps.tenants.models import Tenant
from apps.subscriptions.models import Plan


class TenantSerializer(serializers.ModelSerializer):
    subscription_plan_name = serializers.CharField(source='subscription_plan.name', read_only=True)
    user_count = serializers.SerializerMethodField()
    revenue = serializers.SerializerMethodField()

    class Meta:
        model = Tenant
        fields = [
            'id', 'name', 'company_name', 'email', 'contact_number', 'slug',
            'logo', 'status', 'subscription_plan', 'subscription_plan_name',
            'user_count', 'revenue', 'created_at', 'updated_at',
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at']

    def get_user_count(self, obj):
        return obj.users.filter(status='active').count()

    def get_revenue(self, obj):
        total = obj.payments.filter(status='completed').values_list('amount', flat=True)
        return sum(total) if total else 0


class TenantCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = [
            'name', 'company_name', 'email', 'contact_number',
            'subscription_plan', 'status',
        ]

    def create(self, validated_data):
        name = validated_data['name']
        base_slug = slugify(name)
        slug = base_slug
        counter = 1
        while Tenant.objects.filter(slug=slug).exists():
            slug = f'{base_slug}-{counter}'
            counter += 1
        validated_data['slug'] = slug
        return super().create(validated_data)


class TenantMetricsSerializer(serializers.Serializer):
    total_tenants = serializers.IntegerField()
    active_tenants = serializers.IntegerField()
    suspended_tenants = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=14, decimal_places=2)
