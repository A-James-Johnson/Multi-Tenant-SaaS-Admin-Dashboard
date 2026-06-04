from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from apps.subscriptions.models import Plan, Subscription
from apps.subscriptions.serializers import PlanSerializer, SubscriptionSerializer, UpgradePlanSerializer
from apps.subscriptions.services import SubscriptionService
from rest_framework.permissions import AllowAny, IsAuthenticated
from core.permissions import IsSuperAdmin, IsTenantAdmin
from apps.auditlogs.services import AuditLogService


class PlanListCreateView(generics.ListCreateAPIView):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['tier', 'is_active']
    ordering = ['sort_order', 'monthly_price']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsSuperAdmin()]
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({'success': True, 'data': response.data})

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            {'success': True, 'data': serializer.data},
            status=status.HTTP_201_CREATED,
        )


class PlanDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = [IsSuperAdmin]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        return Response({'success': True, 'data': PlanSerializer(instance).data})

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response({'success': True, 'data': response.data})

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.subscriptions.exists() or instance.tenants.exists():
            return Response(
                {'success': False, 'error': {'message': 'Cannot delete plan with active subscriptions.'}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        self.perform_destroy(instance)
        return Response({'success': True, 'message': 'Plan deleted.'})


class SubscriptionListView(generics.ListAPIView):
    serializer_class = SubscriptionSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status', 'plan']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        qs = Subscription.objects.select_related('tenant', 'plan')
        if user.is_super_admin:
            return qs
        return qs.filter(tenant=user.tenant)

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({'success': True, 'data': response.data})


class UpgradeSubscriptionView(APIView):
    permission_classes = [IsTenantAdmin]

    def post(self, request, pk):
        serializer = UpgradePlanSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_plan = serializer.validated_data['plan_id']

        try:
            if request.user.is_super_admin:
                from apps.tenants.models import Tenant
                tenant = Tenant.objects.get(pk=pk)
            else:
                tenant = request.user.tenant
                if tenant.id != pk:
                    return Response({'success': False, 'error': {'message': 'Forbidden.'}}, status=403)
        except Exception:
            return Response({'success': False, 'error': {'message': 'Tenant not found.'}}, status=404)

        subscription, old_plan = SubscriptionService.upgrade_plan(tenant, new_plan)
        AuditLogService.log(
            user=request.user,
            action='subscription_change',
            description=f'Changed plan from {old_plan.name} to {new_plan.name} for {tenant.name}',
            resource_type='subscription',
            resource_id=str(subscription.id),
            tenant=tenant,
            ip_address=getattr(request, 'client_ip', None),
        )
        return Response({'success': True, 'data': SubscriptionSerializer(subscription).data})
