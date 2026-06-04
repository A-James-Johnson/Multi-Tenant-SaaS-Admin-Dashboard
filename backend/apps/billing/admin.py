from django.contrib import admin
from apps.billing.models import Payment, Invoice


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['payment_id', 'tenant', 'amount', 'status', 'method', 'payment_date']
    list_filter = ['status', 'method']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'tenant', 'total_amount', 'status', 'due_date']
    list_filter = ['status']
