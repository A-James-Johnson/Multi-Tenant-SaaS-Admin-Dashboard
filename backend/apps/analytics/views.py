from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.analytics.services import AnalyticsService
from apps.billing.serializers import PaymentSerializer
from apps.auditlogs.serializers import AuditLogSerializer


class DashboardAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        recent_payments = AnalyticsService.get_recent_payments(user)
        recent_activities = AnalyticsService.get_recent_activities(user)

        data = {
            'kpis': AnalyticsService.get_dashboard_kpis(user),
            'revenue_trend': AnalyticsService.get_revenue_trend(user),
            'user_growth': AnalyticsService.get_user_growth(user),
            'tenant_growth': AnalyticsService.get_tenant_growth() if user.is_super_admin else [],
            'subscription_distribution': AnalyticsService.get_subscription_distribution(),
            'recent_payments': PaymentSerializer(recent_payments, many=True).data,
            'recent_activities': AuditLogSerializer(recent_activities, many=True).data,
        }
        return Response({'success': True, 'data': data})
