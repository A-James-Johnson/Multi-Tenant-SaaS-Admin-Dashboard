from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.accounts.models import User
from apps.accounts.serializers import (
    LoginSerializer, SignupSerializer, TokenResponseSerializer, UserSerializer,
    ChangePasswordSerializer, ForgotPasswordSerializer, ResetPasswordSerializer,
    get_tokens_for_user,
)
from core.permissions import IsSuperAdmin, IsTenantAdmin
from apps.auditlogs.services import AuditLogService


class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        tokens = get_tokens_for_user(user, request)
        return Response({
            'success': True,
            'data': {
                **tokens,
                'user': UserSerializer(user).data,
            }
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        tokens = get_tokens_for_user(user, request)
        return Response({
            'success': True,
            'data': {
                **tokens,
                'user': UserSerializer(user).data,
            }
        })


class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
        except Exception:
            pass
        AuditLogService.log(
            user=request.user,
            action='logout',
            description=f'User {request.user.email} logged out',
            ip_address=getattr(request, 'client_ip', None),
            tenant=request.user.tenant,
        )
        return Response({'success': True, 'message': 'Logged out successfully.'})


class MeView(APIView):
    def get(self, request):
        return Response({'success': True, 'data': UserSerializer(request.user).data})


class ChangePasswordView(APIView):
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response({'success': True, 'message': 'Password changed successfully.'})


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'success': True,
            'message': 'If an account exists with this email, a reset link has been sent.',
        })


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': True, 'message': 'Password reset successfully.'})


class UserListCreateView(generics.ListCreateAPIView):
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'role', 'tenant']
    search_fields = ['email', 'first_name', 'last_name', 'phone']
    ordering_fields = ['created_at', 'last_login', 'email']
    ordering = ['-created_at']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsTenantAdmin()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        qs = User.objects.select_related('role', 'tenant').all()
        if user.is_super_admin:
            return qs
        return qs.filter(tenant=user.tenant)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            from apps.accounts.serializers import UserCreateSerializer
            return UserCreateSerializer
        return UserSerializer

    def perform_create(self, serializer):
        user = self.request.user
        if not user.is_super_admin:
            serializer.save(tenant=user.tenant)
        else:
            serializer.save()
        AuditLogService.log(
            user=user,
            action='user_create',
            description=f'Created user {serializer.instance.email}',
            resource_type='user',
            resource_id=str(serializer.instance.id),
            tenant=serializer.instance.tenant,
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
            {'success': True, 'data': UserSerializer(serializer.instance).data},
            status=status.HTTP_201_CREATED,
        )


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsTenantAdmin()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        qs = User.objects.select_related('role', 'tenant').all()
        if user.is_super_admin:
            return qs
        return qs.filter(tenant=user.tenant)

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            from apps.accounts.serializers import UserUpdateSerializer
            return UserUpdateSerializer
        return UserSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        return Response({'success': True, 'data': UserSerializer(instance).data})

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        AuditLogService.log(
            user=request.user,
            action='user_update',
            description=f'Updated user {instance.email}',
            resource_type='user',
            resource_id=str(instance.id),
            tenant=instance.tenant,
            ip_address=getattr(request, 'client_ip', None),
        )
        return Response({'success': True, 'data': UserSerializer(instance).data})

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        email = instance.email
        tenant = instance.tenant
        self.perform_destroy(instance)
        AuditLogService.log(
            user=request.user,
            action='user_delete',
            description=f'Deleted user {email}',
            resource_type='user',
            tenant=tenant,
            ip_address=getattr(request, 'client_ip', None),
        )
        return Response({'success': True, 'message': 'User deleted.'}, status=status.HTTP_200_OK)
