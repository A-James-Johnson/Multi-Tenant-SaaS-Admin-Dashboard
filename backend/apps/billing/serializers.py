from rest_framework import serializers
from apps.billing.models import Payment, Invoice


class PaymentSerializer(serializers.ModelSerializer):
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'payment_id', 'tenant', 'tenant_name', 'amount', 'currency',
            'payment_date', 'method', 'status', 'gateway_payment_id',
            'description', 'created_at',
        ]
        read_only_fields = ['payment_id', 'created_at']


class InvoiceSerializer(serializers.ModelSerializer):
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)

    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'tenant', 'tenant_name', 'subscription',
            'amount', 'tax_amount', 'total_amount', 'currency', 'due_date',
            'issued_date', 'status', 'line_items', 'notes', 'created_at',
        ]
        read_only_fields = ['invoice_number', 'created_at']


class RevenueReportSerializer(serializers.Serializer):
    total_revenue = serializers.DecimalField(max_digits=14, decimal_places=2)
    monthly_revenue = serializers.DecimalField(max_digits=14, decimal_places=2)
    pending_payments = serializers.DecimalField(max_digits=14, decimal_places=2)
    payment_count = serializers.IntegerField()
