from django.contrib import admin
from apps.tenants.models import Tenant


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ['name', 'company_name', 'email', 'status', 'subscription_plan']
    list_filter = ['status']
    search_fields = ['name', 'company_name', 'email']
