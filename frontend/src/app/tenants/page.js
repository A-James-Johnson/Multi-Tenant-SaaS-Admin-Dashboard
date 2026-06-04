'use client';

import { useEffect, useState } from 'react';
import { Plus, Pause, Play, Pencil, Trash2 } from 'lucide-react';
import ProtectedRoute from '@/components/ProtectedRoute';
import DashboardLayout from '@/components/layout/DashboardLayout';
import DataTable, { Modal } from '@/components/ui/DataTable';
import { tenantsAPI, subscriptionsAPI } from '@/lib/api';
import { StatusBadge, formatCurrency } from '@/lib/utils';

export default function TenantsPage() {
  const [tenants, setTenants] = useState([]);
  const [plans, setPlans] = useState([]);
  const [pagination, setPagination] = useState({});
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editTenant, setEditTenant] = useState(null);
  const [form, setForm] = useState({ name: '', company_name: '', email: '', contact_number: '', subscription_plan: '', status: 'active' });
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);

  const fetchTenants = () => {
    setLoading(true);
    tenantsAPI.list({ page, search }).then((res) => {
      setTenants(res.data.data.results || []);
      setPagination(res.data.data);
    }).finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchTenants();
    subscriptionsAPI.plans().then((res) => setPlans(res.data.data.results || res.data.data || []));
  }, [page, search]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const payload = { ...form, subscription_plan: form.subscription_plan || null };
    if (editTenant) {
      await tenantsAPI.update(editTenant.id, payload);
    } else {
      await tenantsAPI.create(payload);
    }
    setModalOpen(false);
    setEditTenant(null);
    fetchTenants();
  };

  const openEdit = (tenant) => {
    setEditTenant(tenant);
    setForm({
      name: tenant.name, company_name: tenant.company_name, email: tenant.email,
      contact_number: tenant.contact_number || '', subscription_plan: tenant.subscription_plan || '',
      status: tenant.status,
    });
    setModalOpen(true);
  };

  const columns = [
    { key: 'name', label: 'Tenant' },
    { key: 'company_name', label: 'Company' },
    { key: 'email', label: 'Email' },
    { key: 'status', label: 'Status', render: (r) => <StatusBadge status={r.status} /> },
    { key: 'subscription_plan_name', label: 'Plan' },
    { key: 'revenue', label: 'Revenue', render: (r) => formatCurrency(r.revenue) },
    { key: 'user_count', label: 'Users' },
  ];

  return (
    <ProtectedRoute superAdminOnly>
      <DashboardLayout>
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold">Tenants</h1>
              <p className="text-muted-foreground">Manage organizations on the platform</p>
            </div>
            <button onClick={() => { setEditTenant(null); setForm({ name: '', company_name: '', email: '', contact_number: '', subscription_plan: '', status: 'active' }); setModalOpen(true); }} className="btn-primary gap-2">
              <Plus className="h-4 w-4" /> Add Tenant
            </button>
          </div>
          <input type="search" placeholder="Search tenants..." value={search} onChange={(e) => { setSearch(e.target.value); setPage(1); }} className="input max-w-sm" />
          <DataTable
            columns={columns} data={tenants} loading={loading} pagination={pagination} onPageChange={setPage}
            actions={(row) => (
              <div className="flex justify-end gap-1">
                <button onClick={() => openEdit(row)} className="rounded p-1.5 hover:bg-accent"><Pencil className="h-4 w-4" /></button>
                {row.status === 'active' ? (
                  <button onClick={() => tenantsAPI.suspend(row.id).then(fetchTenants)} className="rounded p-1.5 hover:bg-accent"><Pause className="h-4 w-4" /></button>
                ) : (
                  <button onClick={() => tenantsAPI.activate(row.id).then(fetchTenants)} className="rounded p-1.5 hover:bg-accent"><Play className="h-4 w-4" /></button>
                )}
                <button onClick={() => tenantsAPI.delete(row.id).then(fetchTenants)} className="rounded p-1.5 hover:bg-accent text-destructive"><Trash2 className="h-4 w-4" /></button>
              </div>
            )}
          />
        </div>
        <Modal open={modalOpen} onClose={() => setModalOpen(false)} title={editTenant ? 'Edit Tenant' : 'Create Tenant'}>
          <form onSubmit={handleSubmit} className="space-y-4">
            {['name', 'company_name', 'email', 'contact_number'].map((f) => (
              <div key={f}>
                <label className="mb-1 block text-sm font-medium capitalize">{f.replace('_', ' ')}</label>
                <input value={form[f]} onChange={(e) => setForm({ ...form, [f]: e.target.value })} className="input" required={f !== 'contact_number'} />
              </div>
            ))}
            <div>
              <label className="mb-1 block text-sm font-medium">Plan</label>
              <select value={form.subscription_plan} onChange={(e) => setForm({ ...form, subscription_plan: e.target.value })} className="input">
                <option value="">Select plan</option>
                {plans.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
              </select>
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium">Status</label>
              <select value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })} className="input">
                <option value="active">Active</option>
                <option value="suspended">Suspended</option>
                <option value="pending">Pending</option>
              </select>
            </div>
            <button type="submit" className="btn-primary w-full">{editTenant ? 'Update' : 'Create'}</button>
          </form>
        </Modal>
      </DashboardLayout>
    </ProtectedRoute>
  );
}
