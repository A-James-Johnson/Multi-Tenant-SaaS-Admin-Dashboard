# System Architecture

## Multi-Tenant Strategy

This platform uses a **Shared Database, Shared Schema** approach with tenant isolation via foreign keys:

1. All tenant-scoped data includes a `tenant_id` column
2. API views filter queries based on the authenticated user's tenant
3. Super Admin users bypass tenant filtering for platform management
4. Middleware supports explicit tenant context via headers

## Security Architecture

```
Request → CORS → JWT Auth → Permission Check → Tenant Filter → View
                ↓
         AuditLogMiddleware (IP capture)
```

### RBAC Permission Matrix

| Permission | Super Admin | Tenant Admin | Manager | User |
|-----------|:-----------:|:------------:|:-------:|:----:|
| Create | ✓ | ✓ | ✓ | |
| Read | ✓ | ✓ | ✓ | ✓ |
| Update | ✓ | ✓ | ✓ | |
| Delete | ✓ | ✓ | | |
| Manage Billing | ✓ | ✓ | | |
| Manage Users | ✓ | ✓ | ✓ | |
| Manage Settings | ✓ | ✓ | | |

## Backend App Responsibilities

| App | Responsibility |
|-----|---------------|
| accounts | User model, JWT auth, roles & permissions |
| tenants | Organization CRUD, suspend/activate |
| subscriptions | Plan management, subscription lifecycle |
| billing | Payments, invoices, gateway integration |
| analytics | Aggregated dashboard metrics |
| notifications | In-app and email notifications |
| settings_app | System-wide configuration |
| auditlogs | Immutable audit trail |

## Payment Gateway Integration

Architecture supports pluggable payment providers:

```
BillingService → StripeService / RazorpayService
                      ↓
              Gateway API (when configured)
                      ↓
              Payment record + Notification
```

Configure via environment variables:
- `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`, `STRIPE_WEBHOOK_SECRET`
- `RAZORPAY_KEY_ID`, `RAZORPAY_KEY_SECRET`

## Frontend Architecture

```
App Router (Next.js 14)
├── AuthContext (JWT token management)
├── ThemeContext (Dark/Light mode)
├── ProtectedRoute (Auth guard)
├── DashboardLayout (Sidebar + Navbar)
└── Pages (Dashboard, Tenants, Users, ...)
    └── API Layer (Axios + interceptors)
        └── Auto token refresh on 401
```

## Deployment

Docker Compose orchestrates three services:
1. **MySQL 8.0** - Persistent data storage
2. **Django/Gunicorn** - API backend (3 workers)
3. **Next.js** - Frontend (standalone output)

Production checklist:
- Set strong `DJANGO_SECRET_KEY`
- Set `DJANGO_DEBUG=False`
- Configure SMTP for email notifications
- Add payment gateway credentials
- Use HTTPS reverse proxy (nginx/traefik)
- Enable MySQL backups
