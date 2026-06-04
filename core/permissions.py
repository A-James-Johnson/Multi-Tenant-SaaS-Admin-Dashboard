from rest_framework import permissions


class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_super_admin


class IsTenantAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_super_admin or request.user.role_name == 'tenant_admin'
        )


class HasPermission(permissions.BasePermission):
    required_permission = None

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.is_super_admin:
            return True
        perm = getattr(view, 'required_permission', None) or self.required_permission
        if not perm:
            return True
        return request.user.has_perm_code(perm)


PERMISSION_MAP = {
    'create': 'create',
    'list': 'read',
    'retrieve': 'read',
    'update': 'update',
    'partial_update': 'update',
    'destroy': 'delete',
}
