from django.urls import path
from apps.settings_app.views import SettingsListView, SettingsDetailView

urlpatterns = [
    path('', SettingsListView.as_view(), name='settings-list'),
    path('<str:category>/', SettingsDetailView.as_view(), name='settings-detail'),
]
