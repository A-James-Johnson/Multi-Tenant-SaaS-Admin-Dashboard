from django.urls import path
from apps.tenants.views import (
    TenantListCreateView, TenantDetailView,
    TenantSuspendView, TenantActivateView, TenantMetricsView,
)

urlpatterns = [
    path('', TenantListCreateView.as_view(), name='tenant-list'),
    path('metrics/', TenantMetricsView.as_view(), name='tenant-metrics'),
    path('<int:pk>/', TenantDetailView.as_view(), name='tenant-detail'),
    path('<int:pk>/suspend/', TenantSuspendView.as_view(), name='tenant-suspend'),
    path('<int:pk>/activate/', TenantActivateView.as_view(), name='tenant-activate'),
]
