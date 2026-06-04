from django.urls import path
from apps.auditlogs.views import AuditLogListView

urlpatterns = [
    path('', AuditLogListView.as_view(), name='audit-log-list'),
]
