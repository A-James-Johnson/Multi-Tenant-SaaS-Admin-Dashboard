from django.urls import path
from apps.accounts.views import UserListCreateView, UserDetailView
from apps.accounts.views_roles import RoleListView

urlpatterns = [
    path('', UserListCreateView.as_view(), name='user-list'),
    path('roles/', RoleListView.as_view(), name='role-list'),
    path('<int:pk>/', UserDetailView.as_view(), name='user-detail'),
]
