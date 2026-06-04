'use client';

import { useEffect, useState } from 'react';
import { Plus, Pencil, Trash2, Check } from 'lucide-react';
import ProtectedRoute from '@/components/ProtectedRoute';
import DashboardLayout from '@/components/layout/DashboardLayout';
import DataTable, { Modal } from '@/components/ui/DataTable';
import { subscriptionsAPI } from '@/lib/api';
import { formatCurrency } from '@/lib/utils';
import { useAuth } from '@/context/AuthContext';

export default function PlansPage() {
  const { isSuperAdmin } = useAuth();
  const [plans, setPlans] = useState([]);
  const [subscriptions, setSubscriptions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editPlan, setEditPlan] = useState(null);
  const [form, setForm] = useState({
    name: '', tier: 'starter', description: '', user_limit: 5, storage_limit_gb: 10,
    monthly_price: '', yearly_price: '', features: '', is_active: true,
  });

  const fetchData = () => {
    setLoading(true);
    Promise.all([
      subscriptionsAPI.plans(),
      subscriptionsAPI.list(),
    ]).then(([plansRes, subsRes]) => {
      setPlans(plansRes.data.data.results || plansRes.data.data || []);
      setSubscriptions(subsRes.data.data.results || subsRes.data.data || []);
    }).finally(() => setLoading(false));
  };

  useEffect(() => { fetchData(); }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const payload = {
      ...form,
      user_limit: form.user_limit ? Number(form.user_limit) : null,
      storage_limit_gb: form.storage_limit_gb ? Number(form.storage_limit_gb) : null,
      monthly_price: Number(form.monthly_price),
      yearly_price: form.yearly_price ? Number(form.yearly_price) : null,
      features: form.features.split('\n').filter(Boolean),
    };
    if (editPlan) await subscriptionsAPI.updatePlan(editPlan.id, payload);
    else await subscriptionsAPI.createPlan(payload);
    setModalOpen(false);
    fetchData();
  };

  return (
    <ProtectedRoute>
      <DashboardLayout>
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold">Subscriptions</h1>
              <p className="text-muted-foreground">Manage plans and subscriptions</p>
            </div>
            {isSuperAdmin && (
              <button onClick={() => { setEditPlan(null); setModalOpen(true); }} className="btn-primary gap-2">
                <Plus className="h-4 w-4" /> Add Plan
              </button>
            )}
          </div>

          <div className="grid gap-4 md:grid-cols-3">
            {plans.map((plan) => (
              <div key={plan.id} className="card relative">
                {isSuperAdmin && (
                  <div className="absolute right-4 top-4 flex gap-1">
                    <button onClick={() => { setEditPlan(plan); setForm({ ...plan, features: (plan.features || []).join('\n'), monthly_price: plan.monthly_price, yearly_price: plan.yearly_price || '' }); setModalOpen(true); }} className="rounded p-1 hover:bg-accent"><Pencil className="h-4 w-4" /></button>
                    <button onClick={() => subscriptionsAPI.deletePlan(plan.id).then(fetchData)} className="rounded p-1 hover:bg-accent text-destructive"><Trash2 className="h-4 w-4" /></button>
                  </div>
                )}
                <h3 className="text-lg font-semibold capitalize">{plan.name}</h3>
                <p className="mt-1 text-3xl font-bold">{formatCurrency(plan.monthly_price)}<span className="text-sm font-normal text-muted-foreground">/mo</span></p>
                <ul className="mt-4 space-y-2">
                  {(plan.features || []).map((f, i) => (
                    <li key={i} className="flex items-center gap-2 text-sm text-muted-foreground">
                      <Check className="h-4 w-4 text-green-500" /> {f}
                    </li>
                  ))}
                </ul>
                <p className="mt-4 text-xs text-muted-foreground">
                  {plan.user_limit ? `${plan.user_limit} users` : 'Unlimited users'} · {plan.storage_limit_gb ? `${plan.storage_limit_gb}GB` : 'Unlimited storage'}
                </p>
              </div>
            ))}
          </div>

          <div>
            <h2 className="mb-4 text-lg font-semibold">Active Subscriptions</h2>
            <DataTable
              loading={loading}
              columns={[
                { key: 'tenant_name', label: 'Tenant' },
                { key: 'plan', label: 'Plan', render: (r) => r.plan?.name },
                { key: 'status', label: 'Status', render: (r) => <span className="badge capitalize">{r.status}</span> },
                { key: 'start_date', label: 'Start' },
                { key: 'end_date', label: 'Expires' },
              ]}
              data={subscriptions}
            />
          </div>
        </div>

        <Modal open={modalOpen} onClose={() => setModalOpen(false)} title={editPlan ? 'Edit Plan' : 'Create Plan'}>
          <form onSubmit={handleSubmit} className="space-y-4">
            <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} className="input" placeholder="Plan name" required />
            <select value={form.tier} onChange={(e) => setForm({ ...form, tier: e.target.value })} className="input">
              <option value="starter">Starter</option>
              <option value="professional">Professional</option>
              <option value="enterprise">Enterprise</option>
            </select>
            <textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} className="input min-h-[80px]" placeholder="Description" />
            <div className="grid grid-cols-2 gap-4">
              <input type="number" value={form.user_limit} onChange={(e) => setForm({ ...form, user_limit: e.target.value })} className="input" placeholder="User limit" />
              <input type="number" value={form.storage_limit_gb} onChange={(e) => setForm({ ...form, storage_limit_gb: e.target.value })} className="input" placeholder="Storage GB" />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <input type="number" step="0.01" value={form.monthly_price} onChange={(e) => setForm({ ...form, monthly_price: e.target.value })} className="input" placeholder="Monthly price" required />
              <input type="number" step="0.01" value={form.yearly_price} onChange={(e) => setForm({ ...form, yearly_price: e.target.value })} className="input" placeholder="Yearly price" />
            </div>
            <textarea value={form.features} onChange={(e) => setForm({ ...form, features: e.target.value })} className="input min-h-[80px]" placeholder="Features (one per line)" />
            <button type="submit" className="btn-primary w-full">{editPlan ? 'Update' : 'Create'}</button>
          </form>
        </Modal>
      </DashboardLayout>
    </ProtectedRoute>
  );
}
