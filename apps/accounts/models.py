from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from core.models import TimestampedModel


class Permission(TimestampedModel):
    class Codename(models.TextChoices):
        CREATE = 'create', 'Create'
        READ = 'read', 'Read'
        UPDATE = 'update', 'Update'
        DELETE = 'delete', 'Delete'
        MANAGE_BILLING = 'manage_billing', 'Manage Billing'
        MANAGE_USERS = 'manage_users', 'Manage Users'
        MANAGE_SETTINGS = 'manage_settings', 'Manage Settings'

    codename = models.CharField(max_length=50, choices=Codename.choices, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'permissions'
        ordering = ['codename']

    def __str__(self):
        return self.name


class Role(TimestampedModel):
    class RoleName(models.TextChoices):
        SUPER_ADMIN = 'super_admin', 'Super Admin'
        TENANT_ADMIN = 'tenant_admin', 'Tenant Admin'
        MANAGER = 'manager', 'Manager'
        USER = 'user', 'User'

    name = models.CharField(max_length=50, choices=RoleName.choices, unique=True)
    display_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    permissions = models.ManyToManyField(Permission, through='RolePermission', related_name='roles')
    is_system = models.BooleanField(default=True)

    class Meta:
        db_table = 'roles'
        ordering = ['name']

    def __str__(self):
        return self.display_name


class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)

    class Meta:
        db_table = 'role_permissions'
        unique_together = ['role', 'permission']


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('status', User.Status.ACTIVE)

        role, _ = Role.objects.get_or_create(
            name=Role.RoleName.SUPER_ADMIN,
            defaults={'display_name': 'Super Admin', 'is_system': True}
        )
        extra_fields.setdefault('role', role)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, TimestampedModel):
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        INACTIVE = 'inactive', 'Inactive'
        SUSPENDED = 'suspended', 'Suspended'
        PENDING = 'pending', 'Pending'

    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='users',
    )
    email = models.EmailField(unique=True, db_index=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    role = models.ForeignKey(Role, on_delete=models.PROTECT, related_name='users')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    email_verified = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['tenant', 'status']),
            models.Index(fields=['email']),
            models.Index(fields=['role']),
        ]

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()

    @property
    def is_super_admin(self):
        return self.role.name == 'super_admin'

    @property
    def role_name(self):
        return self.role.name if self.role else None

    def has_perm_code(self, codename):
        if self.is_super_admin:
            return True
        return self.role.permissions.filter(codename=codename).exists()


class PasswordResetToken(TimestampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reset_tokens')
    token = models.CharField(max_length=100, unique=True, db_index=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        db_table = 'password_reset_tokens'
