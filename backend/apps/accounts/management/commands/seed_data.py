from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal

from apps.accounts.models import User, Role, Permission, RolePermission
from apps.tenants.models import Tenant
from apps.subscriptions.models import Plan, Subscription
from apps.billing.models import Payment, Invoice
from apps.notifications.models import Notification
from apps.settings_app.models import SystemSettings, DEFAULT_SETTINGS


class Command(BaseCommand):
    help = 'Seed database with initial data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding permissions...')
        permissions = {}
        for codename, label in Permission.Codename.choices:
            perm, _ = Permission.objects.get_or_create(
                codename=codename,
                defaults={'name': label, 'description': f'{label} permission'},
            )
            permissions[codename] = perm

        self.stdout.write('Seeding roles...')
        role_configs = {
            'super_admin': {
                'display_name': 'Super Admin',
                'perms': list(permissions.keys()),
            },
            'tenant_admin': {
                'display_name': 'Tenant Admin',
                'perms': ['create', 'read', 'update', 'delete', 'manage_billing', 'manage_users', 'manage_settings'],
            },
            'manager': {
                'display_name': 'Manager',
                'perms': ['create', 'read', 'update', 'manage_users'],
            },
            'user': {
                'display_name': 'User',
                'perms': ['read'],
            },
        }

        roles = {}
        for name, config in role_configs.items():
            role, _ = Role.objects.get_or_create(
                name=name,
                defaults={'display_name': config['display_name'], 'is_system': True},
            )
            for perm_code in config['perms']:
                RolePermission.objects.get_or_create(role=role, permission=permissions[perm_code])
            roles[name] = role

        self.stdout.write('Seeding plans...')
        plans_data = [
            {
                'name': 'Starter', 'tier': 'starter', 'user_limit': 5, 'storage_limit_gb': 10,
                'monthly_price': Decimal('29.00'), 'yearly_price': Decimal('290.00'),
                'features': ['5 Users', '10GB Storage', 'Email Support', 'Basic Analytics'],
                'sort_order': 1,
            },
            {
                'name': 'Professional', 'tier': 'professional', 'user_limit': 25, 'storage_limit_gb': 100,
                'monthly_price': Decimal('99.00'), 'yearly_price': Decimal('990.00'),
                'features': ['25 Users', '100GB Storage', 'Priority Support', 'Advanced Analytics', 'API Access'],
                'sort_order': 2,
            },
            {
                'name': 'Enterprise', 'tier': 'enterprise', 'user_limit': None, 'storage_limit_gb': None,
                'monthly_price': Decimal('299.00'), 'yearly_price': Decimal('2990.00'),
                'features': ['Unlimited Users', 'Unlimited Storage', '24/7 Support', 'Custom Integrations', 'SLA'],
                'sort_order': 3,
            },
        ]
        plans = {}
        for plan_data in plans_data:
            plan, _ = Plan.objects.get_or_create(tier=plan_data['tier'], defaults=plan_data)
            plans[plan_data['tier']] = plan

        self.stdout.write('Seeding super admin...')
        if not User.objects.filter(email='admin@saasadmin.com').exists():
            User.objects.create_superuser(
                email='admin@saasadmin.com',
                password='Admin@123456',
                first_name='Super',
                last_name='Admin',
            )

        self.stdout.write('Seeding sample tenants...')
        tenants_data = [
            {'name': 'Acme Corp', 'company_name': 'Acme Corporation', 'email': 'contact@acme.com', 'plan': 'professional'},
            {'name': 'TechStart', 'company_name': 'TechStart Inc', 'email': 'hello@techstart.io', 'plan': 'starter'},
            {'name': 'GlobalTech', 'company_name': 'GlobalTech Solutions', 'email': 'info@globaltech.com', 'plan': 'enterprise'},
        ]

        for i, tdata in enumerate(tenants_data):
            slug = tdata['name'].lower().replace(' ', '-')
            tenant, created = Tenant.objects.get_or_create(
                slug=slug,
                defaults={
                    'name': tdata['name'],
                    'company_name': tdata['company_name'],
                    'email': tdata['email'],
                    'contact_number': f'+1-555-010{i}',
                    'status': 'active',
                    'subscription_plan': plans[tdata['plan']],
                },
            )
            if created:
                Subscription.objects.get_or_create(
                    tenant=tenant,
                    defaults={
                        'plan': plans[tdata['plan']],
                        'status': 'active',
                        'start_date': date.today() - timedelta(days=30 * (i + 1)),
                        'end_date': date.today() + timedelta(days=335),
                    },
                )
                tenant_admin_role = roles['tenant_admin']
                if not User.objects.filter(email=f'admin@{slug}.com').exists():
                    User.objects.create_user(
                        email=f'admin@{slug}.com',
                        password='Tenant@123',
                        first_name='Tenant',
                        last_name='Admin',
                        role=tenant_admin_role,
                        tenant=tenant,
                        status='active',
                    )
                for j in range(3):
                    Payment.objects.get_or_create(
                        tenant=tenant,
                        payment_date=timezone.now() - timedelta(days=30 * j),
                        amount=plans[tdata['plan']].monthly_price,
                        defaults={
                            'method': 'stripe' if j % 2 == 0 else 'manual',
                            'status': 'completed',
                            'description': f'Monthly subscription - {tdata["name"]}',
                        },
                    )

        self.stdout.write('Seeding system settings...')
        for category, defaults in DEFAULT_SETTINGS.items():
            SystemSettings.objects.get_or_create(category=category, defaults={'settings': defaults})

        admin_user = User.objects.get(email='admin@saasadmin.com')
        Notification.objects.get_or_create(
            recipient=admin_user,
            title='Welcome to SaaS Admin',
            defaults={
                'type': 'system_alert',
                'message': 'Your multi-tenant SaaS admin dashboard is ready.',
                'channel': 'in_app',
            },
        )

        self.stdout.write(self.style.SUCCESS('Seed data created successfully!'))
        self.stdout.write('Super Admin: admin@saasadmin.com / Admin@123456')
        self.stdout.write('Tenant Admin: admin@acme-corp.com / Tenant@123')
