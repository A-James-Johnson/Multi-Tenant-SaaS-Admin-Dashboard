import threading

from django.core.exceptions import ValidationError
from django.core.validators import validate_ipv46_address

_thread_locals = threading.local()


def normalize_client_ip(ip):
    """Return a valid IP or None. Empty/invalid values break GenericIPAddressField."""
    if not ip:
        return None
    try:
        validate_ipv46_address(ip)
        return ip
    except ValidationError:
        return None


def get_current_tenant():
    return getattr(_thread_locals, 'tenant', None)


def set_current_tenant(tenant):
    _thread_locals.tenant = tenant


class TenantMiddleware:
    """Resolve tenant from JWT token or X-Tenant-ID header."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.tenant = None
        set_current_tenant(None)

        tenant_id = request.headers.get('X-Tenant-ID')
        if tenant_id:
            from apps.tenants.models import Tenant
            try:
                request.tenant = Tenant.objects.get(id=tenant_id, is_deleted=False)
                set_current_tenant(request.tenant)
            except (Tenant.DoesNotExist, ValueError):
                pass

        response = self.get_response(request)
        return response


class AuditLogMiddleware:
    """Capture IP address for audit logging."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.client_ip = normalize_client_ip(self._get_client_ip(request))
        return self.get_response(request)

    @staticmethod
    def _get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR') or None
