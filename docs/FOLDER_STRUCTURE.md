# Project Folder Structure

```
Multi-Tenant SaaS Admin Dashboard/
├── .env.example
├── .gitignore
├── docker-compose.yml
├── README.md
│
├── docker/
│   └── mysql/
│       └── init.sql
│
├── docs/
│   ├── API.md
│   ├── ARCHITECTURE.md
│   └── DATABASE_SCHEMA.md
│
├── backend/
│   ├── Dockerfile
│   ├── manage.py
│   ├── requirements.txt
│   ├── config/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── core/
│   │   ├── middleware.py          # Tenant + Audit middleware
│   │   ├── permissions.py         # RBAC permission classes
│   │   ├── pagination.py
│   │   ├── exceptions.py
│   │   └── models.py              # Base model mixins
│   └── apps/
│       ├── accounts/
│       │   ├── models.py          # User, Role, Permission
│       │   ├── backends.py        # Email auth backend
│       │   ├── serializers.py
│       │   ├── views.py           # Auth + User CRUD
│       │   ├── urls.py
│       │   ├── urls_users.py
│       │   └── management/commands/seed_data.py
│       ├── tenants/
│       │   ├── models.py
│       │   ├── serializers.py
│       │   ├── views.py
│       │   └── urls.py
│       ├── subscriptions/
│       │   ├── models.py          # Plan, Subscription
│       │   ├── services.py
│       │   ├── serializers.py
│       │   ├── views.py
│       │   └── urls.py
│       ├── billing/
│       │   ├── models.py          # Payment, Invoice
│       │   ├── services.py        # Stripe, Razorpay
│       │   ├── serializers.py
│       │   ├── views.py
│       │   └── urls.py
│       ├── analytics/
│       │   ├── services.py
│       │   ├── views.py
│       │   └── urls.py
│       ├── notifications/
│       │   ├── models.py
│       │   ├── services.py
│       │   ├── serializers.py
│       │   ├── views.py
│       │   └── urls.py
│       ├── settings_app/
│       │   ├── models.py
│       │   ├── serializers.py
│       │   ├── views.py
│       │   └── urls.py
│       └── auditlogs/
│           ├── models.py
│           ├── services.py
│           ├── serializers.py
│           ├── views.py
│           └── urls.py
│
└── frontend/
    ├── Dockerfile
    ├── package.json
    ├── next.config.js
    ├── tailwind.config.js
    ├── jsconfig.json
    └── src/
        ├── app/
        │   ├── layout.js
        │   ├── globals.css
        │   ├── page.js
        │   ├── login/page.js
        │   ├── forgot-password/page.js
        │   ├── reset-password/page.js
        │   ├── dashboard/page.js
        │   ├── tenants/page.js
        │   ├── users/page.js
        │   ├── plans/page.js
        │   ├── billing/page.js
        │   ├── analytics/page.js
        │   ├── notifications/page.js
        │   └── settings/page.js
        ├── components/
        │   ├── Providers.js
        │   ├── ProtectedRoute.js
        │   ├── layout/
        │   │   ├── Sidebar.js
        │   │   ├── Navbar.js
        │   │   └── DashboardLayout.js
        │   ├── ui/
        │   │   ├── KPICard.js
        │   │   └── DataTable.js
        │   └── charts/
        │       └── Charts.js
        ├── context/
        │   ├── AuthContext.js
        │   └── ThemeContext.js
        └── lib/
            ├── api.js
            └── utils.js
```
