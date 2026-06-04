from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from apps.notifications.models import Notification
from apps.notifications.serializers import NotificationSerializer
from apps.notifications.services import NotificationService


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['type', 'is_read']
    ordering = ['-created_at']

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        unread_count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        return Response({
            'success': True,
            'data': {**response.data, 'unread_count': unread_count},
        })


class NotificationMarkReadView(APIView):
    def post(self, request, pk):
        try:
            notification = Notification.objects.get(pk=pk, recipient=request.user)
        except Notification.DoesNotExist:
            return Response({'success': False, 'error': {'message': 'Not found.'}}, status=404)
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        return Response({'success': True, 'data': NotificationSerializer(notification).data})


class NotificationMarkAllReadView(APIView):
    def post(self, request):
        count = NotificationService.mark_all_read(request.user)
        return Response({'success': True, 'message': f'{count} notifications marked as read.'})


class NotificationDeleteView(APIView):
    def delete(self, request, pk):
        try:
            notification = Notification.objects.get(pk=pk, recipient=request.user)
        except Notification.DoesNotExist:
            return Response({'success': False, 'error': {'message': 'Not found.'}}, status=404)
        notification.delete()
        return Response({'success': True, 'message': 'Notification deleted.'})
