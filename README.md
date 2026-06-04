# Multi-Tenant SaaS Admin Dashboard

Production-ready multi-tenant SaaS admin platform with Django REST API backend and Next.js frontend.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Next.js Frontend                         │
│  (React, Tailwind, Recharts, Axios, Context API)            │
└──────────────────────────┬──────────────────────────────────┘
                           │ REST API (JWT)
┌──────────────────────────▼──────────────────────────────────┐
│                   Django REST Framework                      │
│  ┌─────────┬─────────┬──────────────┬─────────┬───────────┐ │
│  │ accounts│ tenants │ subscriptions│ billing │ analytics │ │
│  └─────────┴─────────┴──────────────┴─────────┴───────────┘ │
│  Middleware: TenantMiddleware, AuditLogMiddleware            │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                      MySQL 8.0                               │
│  Shared DB + tenant_id isolation on tenant-scoped tables     │
└─────────────────────────────────────────────────────────────┘
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14, Tailwind CSS, Recharts, Axios |
| Backend | Django 5, Django REST Framework |
| Database | MySQL 8.0 |
| Auth | JWT (Simple JWT) |
| Deployment | Docker, Docker Compose |

## Deployment Ready (Docker)

The repository is now set up for containerized deployment with:
- backend static file collection on startup
- environment-based DB and CORS/CSRF configuration
- health checks for the backend service
- optimized Docker ignore files for smaller images

### Production deployment steps

```bash
cp .env.example .env
# update the values for your host / database / secret key

docker compose up --build -d
```

Then open:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api/v1
- Swagger docs: http://localhost:8000/api/docs

## Quick Start (Docker)

```bash
# Clone and configure
cp .env.example .env

# Start all services
docker-compose up --build

# Access
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/api/v1
# API Docs: http://localhost:8000/api/docs
```

## Local Development

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure MySQL and copy env
cp ../.env.example ../.env

python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Demo Credentials

| Role | Email | Password |
|------|-------|----------|
| Super Admin | admin@saasadmin.com | Admin@123456 |
| Tenant Admin | admin@acme-corp.com | Tenant@123 |

## Features

- **Authentication**: Login, logout, JWT refresh, forgot/reset/change password
- **Multi-Tenant**: Tenant CRUD, suspend/activate, data isolation
- **RBAC**: Super Admin, Tenant Admin, Manager, User with granular permissions
- **Subscriptions**: Starter, Professional, Enterprise plans
- **Billing**: Payments, invoices, revenue reports, Stripe/Razorpay ready
- **Analytics**: KPIs, revenue/user/tenant growth charts
- **Notifications**: In-app + email notification center
- **Settings**: General, security, email SMTP configuration
- **Audit Logs**: Login, user, payment, subscription events

## Project Structure

```
├── backend/
│   ├── config/           # Django settings, URLs
│   ├── core/             # Middleware, permissions, pagination
│   └── apps/
│       ├── accounts/     # Users, roles, permissions, auth
│       ├── tenants/      # Tenant management
│       ├── subscriptions/# Plans & subscriptions
│       ├── billing/      # Payments & invoices
│       ├── analytics/    # Dashboard analytics
│       ├── notifications/# Notification center
│       ├── settings_app/ # System settings
│       └── auditlogs/    # Audit trail
├── frontend/
│   └── src/
│       ├── app/          # Next.js pages
│       ├── components/   # UI components
│       ├── context/      # Auth & theme providers
│       └── lib/          # API client & utilities
├── docker/               # MySQL init scripts
├── docs/                 # API docs, schema, ER diagram
└── docker-compose.yml
```

## API Documentation

See [docs/API.md](docs/API.md) and live Swagger UI at `/api/docs/`.

## Screenshots

Below are the current project screenshots for quick visual reference in the repository.

![Dashboard overview](image.png)

![Tenant management view](image-1.png)

![Billing and subscriptions view](image-2.png)

![Analytics dashboard](image-3.png)

![Notifications and settings](image-4.png)

![User management view](image-5.png)

## License

MIT