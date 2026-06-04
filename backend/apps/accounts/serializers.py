import uuid
from datetime import timedelta
from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from apps.accounts.models import User, Role, PasswordResetToken
from apps.tenants.models import Tenant
from apps.auditlogs.services import AuditLogService


class RoleSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = ['id', 'name', 'display_name', 'description', 'permissions']

    def get_permissions(self, obj):
        return list(obj.permissions.values_list('codename', flat=True))


class UserSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)
    role_id = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(), source='role', write_only=True, required=False
    )
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name', 'phone',
            'role', 'role_id', 'status', 'tenant', 'last_login', 'last_login_ip',
            'email_verified', 'created_at', 'updated_at',
        ]
        read_only_fields = ['last_login', 'last_login_ip', 'email_verified', 'created_at', 'updated_at']


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    role_id = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), source='role')

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone', 'password', 'role_id', 'status', 'tenant']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    role_id = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(), source='role', required=False
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'role_id', 'status']


class SignupSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('An account with this email already exists.')
        return value

    def create(self, validated_data):
        company_name = f"{validated_data['first_name'].strip()} {validated_data['last_name'].strip()}".strip() or 'Tenant User'
        role = Role.objects.filter(name=Role.RoleName.TENANT_ADMIN).first()
        if not role:
            role = Role.objects.create(name=Role.RoleName.TENANT_ADMIN, display_name='Tenant Admin', is_system=True)

        base_slug = slugify(company_name) or 'tenant'
        slug = base_slug
        suffix = 2
        while Tenant.objects.filter(slug=slug).exists():
            slug = f'{base_slug}-{suffix}'
            suffix += 1

        tenant = Tenant.objects.create(
            name=company_name,
            company_name=company_name,
            email=validated_data['email'],
            contact_number=validated_data.get('phone', ''),
            slug=slug,
            status=Tenant.Status.ACTIVE,
        )

        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone=validated_data.get('phone', ''),
            role=role,
            tenant=tenant,
            status=User.Status.ACTIVE,
        )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError('Invalid email or password.')
        if not user.is_active or user.status == User.Status.SUSPENDED:
            raise serializers.ValidationError('Account is suspended or inactive.')
        data['user'] = user
        return data


class TokenResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserSerializer()


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Current password is incorrect.')
        return value


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def save(self):
        email = self.validated_data['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return
        token = uuid.uuid4().hex
        PasswordResetToken.objects.create(
            user=user,
            token=token,
            expires_at=timezone.now() + timedelta(hours=24),
        )
        reset_url = f"{settings.CORS_ALLOWED_ORIGINS[0] if settings.CORS_ALLOWED_ORIGINS else 'http://localhost:3000'}/reset-password?token={token}"
        send_mail(
            subject='Password Reset Request',
            message=f'Click the link to reset your password: {reset_url}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=True,
        )


class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(min_length=8)

    def validate_token(self, value):
        try:
            reset_token = PasswordResetToken.objects.get(token=value, is_used=False)
        except PasswordResetToken.DoesNotExist:
            raise serializers.ValidationError('Invalid or expired reset token.')
        if reset_token.expires_at < timezone.now():
            raise serializers.ValidationError('Reset token has expired.')
        self.reset_token = reset_token
        return value

    def save(self):
        user = self.reset_token.user
        user.set_password(self.validated_data['new_password'])
        user.save()
        self.reset_token.is_used = True
        self.reset_token.save()
        return user


def get_tokens_for_user(user, request=None):
    refresh = RefreshToken.for_user(user)
    refresh['role'] = user.role.name
    refresh['tenant_id'] = user.tenant_id
    if request:
        user.last_login_ip = getattr(request, 'client_ip', None)
        user.save(update_fields=['last_login_ip'])
        AuditLogService.log(
            user=user,
            action='login',
            description=f'User {user.email} logged in',
            ip_address=getattr(request, 'client_ip', None),
            tenant=user.tenant,
        )
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
