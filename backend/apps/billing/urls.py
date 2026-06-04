from django.urls import path
from apps.billing.views import (
    PaymentListCreateView, PaymentDetailView,
    InvoiceListCreateView, RevenueReportView, PaymentGatewayStatusView,
)

urlpatterns = [
    path('payments/', PaymentListCreateView.as_view(), name='payment-list'),
    path('payments/<int:pk>/', PaymentDetailView.as_view(), name='payment-detail'),
    path('invoices/', InvoiceListCreateView.as_view(), name='invoice-list'),
    path('revenue/', RevenueReportView.as_view(), name='revenue-report'),
    path('gateways/', PaymentGatewayStatusView.as_view(), name='gateway-status'),
]
