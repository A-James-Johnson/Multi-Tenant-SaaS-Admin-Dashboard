# Database Schema

MySQL 8.0 with utf8mb4 charset. Django ORM manages migrations; this documents the logical schema.

## ER Diagram

```mermaid
erDiagram
    TENANTS ||--o{ USERS : has
    TENANTS ||--o| SUBSCRIPTIONS : has
    TENANTS ||--o{ PAYMENTS : has
    TENANTS ||--o{ INVOICES : has
    TENANTS ||--o{ NOTIFICATIONS : has
    TENANTS ||--o{ AUDIT_LOGS : has
    PLANS ||--o{ SUBSCRIPTIONS : includes
    PLANS ||--o{ TENANTS : assigned
    ROLES ||--o{ USERS : assigned
    ROLES ||--o{ ROLE_PERMISSIONS : has
    PERMISSIONS ||--o{ ROLE_PERMISSIONS : has
    USERS ||--o{ NOTIFICATIONS : receives
    USERS ||--o{ AUDIT_LOGS : performs
    SUBSCRIPTIONS ||--o{ INVOICES : generates

    TENANTS {
        bigint id PK
        varchar name
        varchar company_name
        varchar email
        varchar contact_number
        varchar slug UK
        enum status
        bigint subscription_plan_id FK
        boolean is_deleted
        json metadata
        datetime created_at
        datetime updated_at
    }

    USERS {
        bigint id PK
        bigint tenant_id FK
        varchar email UK
        varchar first_name
        varchar last_name
        varchar phone
        bigint role_id FK
        enum status
        boolean is_active
        datetime last_login
        varchar last_login_ip
        datetime created_at
    }

    ROLES {
        bigint id PK
        varchar name UK
        varchar display_name
        boolean is_system
    }

    PERMISSIONS {
        bigint id PK
        varchar codename UK
        varchar name
    }

    ROLE_PERMISSIONS {
        bigint role_id FK
        bigint permission_id FK
    }

    PLANS {
        bigint id PK
        varchar name
        enum tier UK
        int user_limit
        int storage_limit_gb
        decimal monthly_price
        decimal yearly_price
        json features
        boolean is_active
    }

    SUBSCRIPTIONS {
        bigint id PK
        bigint tenant_id FK UK
        bigint plan_id FK
        enum status
        date start_date
        date end_date
        date trial_end_date
        boolean auto_renew
    }

    PAYMENTS {
        bigint id PK
        varchar payment_id UK
        bigint tenant_id FK
        decimal amount
        varchar currency
        datetime payment_date
        enum method
        enum status
        varchar gateway_payment_id
        json gateway_response
    }

    INVOICES {
        bigint id PK
        varchar invoice_number UK
        bigint tenant_id FK
        bigint subscription_id FK
        decimal amount
        decimal tax_amount
        decimal total_amount
        date due_date
        date issued_date
        enum status
        json line_items
    }

    NOTIFICATIONS {
        bigint id PK
        bigint tenant_id FK
        bigint recipient_id FK
        enum type
        enum channel
        varchar title
        text message
        boolean is_read
        datetime read_at
        json metadata
    }

    AUDIT_LOGS {
        bigint id PK
        bigint tenant_id FK
        bigint user_id FK
        enum action
        varchar resource_type
        varchar resource_id
        text description
        varchar ip_address
        json metadata
        datetime created_at
    }

    SYSTEM_SETTINGS {
        bigint id PK
        enum category UK
        json settings
        datetime updated_at
    }

    PASSWORD_RESET_TOKENS {
        bigint id PK
        bigint user_id FK
        varchar token UK
        datetime expires_at
        boolean is_used
    }
```

## Indexes

| Table | Index | Columns |
|-------|-------|---------|
| tenants | idx_status | status |
| tenants | idx_slug | slug |
| tenants | idx_deleted_status | is_deleted, status |
| users | idx_tenant_status | tenant_id, status |
| users | idx_email | email |
| payments | idx_tenant_status | tenant_id, status |
| payments | idx_payment_date | payment_date |
| audit_logs | idx_tenant_action | tenant_id, action |
| audit_logs | idx_created_at | created_at |
| notifications | idx_recipient_read | recipient_id, is_read |

## Multi-Tenant Isolation

- **Shared database** with `tenant_id` foreign key on tenant-scoped tables
- **TenantMiddleware** resolves tenant from `X-Tenant-ID` header
- **JWT tokens** include `tenant_id` claim for tenant-scoped users
- **Super Admin** has `tenant_id = NULL` with platform-wide access
- **Query filtering** enforced at view layer based on user role
