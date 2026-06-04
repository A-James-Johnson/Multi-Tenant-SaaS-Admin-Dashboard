from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Sum, Count, Q

from apps.tenants.models import Tenant
from apps.tenants.serializers import TenantSerializer, TenantCreateSerializer, TenantMetricsSerializer
from core.permissions import IsSuperAdmin
from apps.auditlogs.services import AuditLogService
from apps.subscriptions.services import SubscriptionService


class TenantListCreateView(generics.ListCreateAPIView):
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'subscription_plan']
    search_fields = ['name', 'company_name', 'email']
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsSuperAdmin()]
        return [IsSuperAdmin()]

    def get_queryset(self):
        return Tenant.objects.filter(is_deleted=False).select_related('subscription_plan')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TenantCreateSerializer
        return TenantSerializer

    def perform_create(self, serializer):
        tenant = serializer.save()
        if tenant.subscription_plan:
            SubscriptionService.create_subscription(tenant, tenant.subscription_plan)
        AuditLogService.log(
            user=self.request.user,
            action='tenant_create',
            description=f'Created tenant {tenant.name}',
            resource_type='tenant',
            resource_id=str(tenant.id),
            tenant=tenant,
            ip_address=getattr(self.request, 'client_ip', None),
        )

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({'success': True, 'data': response.data})

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            {'success': True, 'data': TenantSerializer(serializer.instance).data},
            status=status.HTTP_201_CREATED,
        )


class TenantDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsSuperAdmin]

    def get_queryset(self):
        return Tenant.objects.filter(is_deleted=False).select_related('subscription_plan')

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return TenantCreateSerializer
        return TenantSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        return Response({'success': True, 'data': TenantSerializer(instance).data})

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = TenantCreateSerializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        AuditLogService.log(
            user=request.user,
            action='tenant_update',
            description=f'Updated tenant {instance.name}',
            resource_type='tenant',
            resource_id=str(instance.id),
            tenant=instance,
            ip_address=getattr(request, 'client_ip', None),
        )
        return Response({'success': True, 'data': TenantSerializer(instance).data})

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_deleted = True
        instance.status = Tenant.Status.INACTIVE
        instance.save()
        AuditLogService.log(
            user=request.user,
            action='tenant_update',
            description=f'Deleted tenant {instance.name}',
            resource_type='tenant',
            resource_id=str(instance.id),
            tenant=instance,
            ip_address=getattr(request, 'client_ip', None),
        )
        return Response({'success': True, 'message': 'Tenant deleted.'})


class TenantSuspendView(APIView):
    permission_classes = [IsSuperAdmin]

    def post(self, request, pk):
        try:
            tenant = Tenant.objects.get(pk=pk, is_deleted=False)
        except Tenant.DoesNotExist:
            return Response({'success': False, 'error': {'message': 'Tenant not found.'}}, status=404)
        tenant.status = Tenant.Status.SUSPENDED
        tenant.save()
        AuditLogService.log(
            user=request.user, action='tenant_suspend',
            description=f'Suspended tenant {tenant.name}',
            resource_type='tenant', resource_id=str(tenant.id), tenant=tenant,
            ip_address=getattr(request, 'client_ip', None),
        )
        return Response({'success': True, 'data': TenantSerializer(tenant).data})


class TenantActivateView(APIView):
    permission_classes = [IsSuperAdmin]

    def post(self, request, pk):
        try:
            tenant = Tenant.objects.get(pk=pk, is_deleted=False)
        except Tenant.DoesNotExist:
            return Response({'success': False, 'error': {'message': 'Tenant not found.'}}, status=404)
        tenant.status = Tenant.Status.ACTIVE
        tenant.save()
        AuditLogService.log(
            user=request.user, action='tenant_activate',
            description=f'Activated tenant {tenant.name}',
            resource_type='tenant', resource_id=str(tenant.id), tenant=tenant,
            ip_address=getattr(request, 'client_ip', None),
        )
        return Response({'success': True, 'data': TenantSerializer(tenant).data})


class TenantMetricsView(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        tenants = Tenant.objects.filter(is_deleted=False)
        from apps.billing.models import Payment
        total_revenue = Payment.objects.filter(status='completed').aggregate(
            total=Sum('amount')
        )['total'] or 0
        data = {
            'total_tenants': tenants.count(),
            'active_tenants': tenants.filter(status='active').count(),
            'suspended_tenants': tenants.filter(status='suspended').count(),
            'total_revenue': total_revenue,
        }
        return Response({'success': True, 'data': TenantMetricsSerializer(data).data})
