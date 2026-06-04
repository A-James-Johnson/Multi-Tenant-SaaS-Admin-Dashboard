from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum, Count
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from datetime import timedelta

from apps.billing.models import Payment, Invoice
from apps.billing.serializers import PaymentSerializer, InvoiceSerializer, RevenueReportSerializer
from apps.billing.services import BillingService, StripeService, RazorpayService
from core.permissions import IsTenantAdmin
from apps.auditlogs.services import AuditLogService


class PaymentListCreateView(generics.ListCreateAPIView):
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'method', 'tenant']
    search_fields = ['payment_id', 'description']
    ordering = ['-payment_date']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsTenantAdmin()]
        return [IsTenantAdmin()]

    def get_queryset(self):
        user = self.request.user
        qs = Payment.objects.select_related('tenant')
        if user.is_super_admin:
            return qs
        return qs.filter(tenant=user.tenant)

    def perform_create(self, serializer):
        payment = serializer.save()
        AuditLogService.log(
            user=self.request.user,
            action='payment_create',
            description=f'Payment {payment.payment_id} created for {payment.amount}',
            resource_type='payment',
            resource_id=str(payment.id),
            tenant=payment.tenant,
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
            {'success': True, 'data': serializer.data},
            status=status.HTTP_201_CREATED,
        )


class PaymentDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsTenantAdmin]

    def get_queryset(self):
        user = self.request.user
        qs = Payment.objects.select_related('tenant')
        if user.is_super_admin:
            return qs
        return qs.filter(tenant=user.tenant)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        return Response({'success': True, 'data': PaymentSerializer(instance).data})


class InvoiceListCreateView(generics.ListCreateAPIView):
    serializer_class = InvoiceSerializer
    permission_classes = [IsTenantAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'tenant']
    search_fields = ['invoice_number']
    ordering = ['-issued_date']

    def get_queryset(self):
        user = self.request.user
        qs = Invoice.objects.select_related('tenant', 'subscription')
        if user.is_super_admin:
            return qs
        return qs.filter(tenant=user.tenant)

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


class RevenueReportView(APIView):
    permission_classes = [IsTenantAdmin]

    def get(self, request):
        user = request.user
        payments = Payment.objects.filter(status='completed')
        if not user.is_super_admin:
            payments = payments.filter(tenant=user.tenant)

        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        data = {
            'total_revenue': payments.aggregate(total=Sum('amount'))['total'] or 0,
            'monthly_revenue': payments.filter(payment_date__gte=month_start).aggregate(
                total=Sum('amount')
            )['total'] or 0,
            'pending_payments': Payment.objects.filter(status='pending').aggregate(
                total=Sum('amount')
            )['total'] or 0,
            'payment_count': payments.count(),
        }
        return Response({'success': True, 'data': RevenueReportSerializer(data).data})


class PaymentGatewayStatusView(APIView):
    permission_classes = [IsTenantAdmin]

    def get(self, request):
        return Response({
            'success': True,
            'data': {
                'stripe': {'configured': StripeService.is_configured()},
                'razorpay': {'configured': RazorpayService.is_configured()},
            }
        })
