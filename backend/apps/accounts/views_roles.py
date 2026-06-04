from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.accounts.models import Role
from apps.accounts.serializers import RoleSerializer


class RoleListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        roles = Role.objects.exclude(name='super_admin')
        return Response({'success': True, 'data': RoleSerializer(roles, many=True).data})
