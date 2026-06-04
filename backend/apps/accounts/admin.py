from django.contrib import admin
from apps.accounts.models import User, Role, Permission, RolePermission


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'full_name', 'role', 'tenant', 'status', 'is_active']
    list_filter = ['status', 'role', 'tenant']
    search_fields = ['email', 'first_name', 'last_name']


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_name', 'is_system']


admin.site.register(Permission)
admin.site.register(RolePermission)
