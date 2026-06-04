from django.contrib import admin
from apps.settings_app.models import SystemSettings


@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    list_display = ['category', 'updated_at']
