from django.urls import path
from apps.subscriptions.views import (
    PlanListCreateView, PlanDetailView,
    SubscriptionListView, UpgradeSubscriptionView,
)

urlpatterns = [
    path('plans/', PlanListCreateView.as_view(), name='plan-list'),
    path('plans/<int:pk>/', PlanDetailView.as_view(), name='plan-detail'),
    path('', SubscriptionListView.as_view(), name='subscription-list'),
    path('<int:pk>/upgrade/', UpgradeSubscriptionView.as_view(), name='subscription-upgrade'),
]
