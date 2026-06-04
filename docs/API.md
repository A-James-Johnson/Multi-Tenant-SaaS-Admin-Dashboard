# API Documentation

Base URL: `http://localhost:8000/api/v1`

## Authentication

All endpoints except login, forgot-password, reset-password, and plan listing require JWT Bearer token.

```
Authorization: Bearer <access_token>
```

### POST /auth/login/
```json
{ "email": "admin@saasadmin.com", "password": "Admin@123456" }
```

### POST /auth/logout/
```json
{ "refresh": "<refresh_token>" }
```

### POST /auth/refresh/
```json
{ "refresh": "<refresh_token>" }
```

### GET /auth/me/
Returns current user profile.

### POST /auth/change-password/
```json
{ "old_password": "...", "new_password": "..." }
```

### POST /auth/forgot-password/
```json
{ "email": "user@example.com" }
```

### POST /auth/reset-password/
```json
{ "token": "...", "new_password": "..." }
```

---

## Tenants (Super Admin)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /tenants/ | List tenants (paginated, searchable) |
| POST | /tenants/ | Create tenant |
| GET | /tenants/{id}/ | Get tenant details |
| PATCH | /tenants/{id}/ | Update tenant |
| DELETE | /tenants/{id}/ | Soft delete tenant |
| POST | /tenants/{id}/suspend/ | Suspend tenant |
| POST | /tenants/{id}/activate/ | Activate tenant |
| GET | /tenants/metrics/ | Dashboard tenant metrics |

---

## Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /users/ | List users (filter: status, role, tenant) |
| POST | /users/ | Create user |
| GET | /users/{id}/ | Get user |
| PATCH | /users/{id}/ | Update user |
| DELETE | /users/{id}/ | Delete user |

---

## Subscriptions

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /subscriptions/plans/ | List plans |
| POST | /subscriptions/plans/ | Create plan (Super Admin) |
| GET/PATCH/DELETE | /subscriptions/plans/{id}/ | Plan CRUD |
| GET | /subscriptions/ | List subscriptions |
| POST | /subscriptions/{tenant_id}/upgrade/ | Upgrade/downgrade plan |

---

## Billing

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | /billing/payments/ | List/create payments |
| GET | /billing/payments/{id}/ | Payment detail |
| GET/POST | /billing/invoices/ | List/create invoices |
| GET | /billing/revenue/ | Revenue report |
| GET | /billing/gateways/ | Payment gateway status |

---

## Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /analytics/dashboard/ | Full dashboard data (KPIs, charts, recent activity) |

---

## Notifications

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /notifications/ | List notifications |
| POST | /notifications/{id}/read/ | Mark as read |
| POST | /notifications/read-all/ | Mark all read |
| DELETE | /notifications/{id}/ | Delete notification |

---

## Settings (Super Admin)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /settings/ | List all settings categories |
| GET/PATCH | /settings/{category}/ | Get/update settings (general, security, email) |

---

## Audit Logs

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /audit-logs/ | List audit logs (filter: action, tenant, user) |

---

## Pagination

All list endpoints support:
- `page` - Page number
- `page_size` - Items per page (max 100)
- `search` - Full-text search
- `ordering` - Sort field (prefix `-` for desc)

Response format:
```json
{
  "success": true,
  "data": {
    "count": 100,
    "next": "...",
    "previous": null,
    "total_pages": 5,
    "current_page": 1,
    "results": []
  }
}
```

## Error Format

```json
{
  "success": false,
  "error": {
    "code": 400,
    "message": "Validation error message",
    "details": {}
  }
}
```
