'use client';

import { useEffect, useState } from 'react';
import ProtectedRoute from '@/components/ProtectedRoute';
import DashboardLayout from '@/components/layout/DashboardLayout';
import DataTable from '@/components/ui/DataTable';
import KPICard from '@/components/ui/KPICard';
import { billingAPI } from '@/lib/api';
import { StatusBadge, formatCurrency, formatDate, formatDateTime } from '@/lib/utils';
import { DollarSign, Clock, CreditCard } from 'lucide-react';

export default function BillingPage() {
  const [payments, setPayments] = useState([]);
  const [invoices, setInvoices] = useState([]);
  const [revenue, setRevenue] = useState({});
  const [gateways, setGateways] = useState({});
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState('payments');
  const [page, setPage] = useState(1);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      billingAPI.payments({ page }),
      billingAPI.invoices({ page }),
      billingAPI.revenue(),
      billingAPI.gateways(),
    ]).then(([payRes, invRes, revRes, gwRes]) => {
      setPayments(payRes.data.data.results || []);
      setInvoices(invRes.data.data.results || []);
      setRevenue(revRes.data.data);
      setGateways(gwRes.data.data);
    }).finally(() => setLoading(false));
  }, [page]);

  return (
    <ProtectedRoute>
      <DashboardLayout>
        <div className="space-y-6">
          <div>
            <h1 className="text-2xl font-bold">Billing</h1>
            <p className="text-muted-foreground">Payments, invoices, and revenue</p>
          </div>

          <div className="grid gap-4 sm:grid-cols-3">
            <KPICard title="Total Revenue" value={formatCurrency(revenue.total_revenue)} icon={DollarSign} />
            <KPICard title="Monthly Revenue" value={formatCurrency(revenue.monthly_revenue)} icon={CreditCard} />
            <KPICard title="Pending" value={formatCurrency(revenue.pending_payments)} icon={Clock} />
          </div>

          <div className="flex gap-4 text-sm">
            <div className="rounded-lg border px-4 py-2">
              Stripe: <span className={gateways.stripe?.configured ? 'text-green-600' : 'text-muted-foreground'}>
                {gateways.stripe?.configured ? 'Configured' : 'Not configured'}
              </span>
            </div>
            <div className="rounded-lg border px-4 py-2">
              Razorpay: <span className={gateways.razorpay?.configured ? 'text-green-600' : 'text-muted-foreground'}>
                {gateways.razorpay?.configured ? 'Configured' : 'Not configured'}
              </span>
            </div>
          </div>

          <div className="flex gap-2 border-b">
            {['payments', 'invoices'].map((t) => (
              <button key={t} onClick={() => setTab(t)} className={`px-4 py-2 text-sm font-medium capitalize ${tab === t ? 'border-b-2 border-primary' : 'text-muted-foreground'}`}>
                {t}
              </button>
            ))}
          </div>

          {tab === 'payments' ? (
            <DataTable
              loading={loading}
              columns={[
                { key: 'payment_id', label: 'Payment ID' },
                { key: 'tenant_name', label: 'Tenant' },
                { key: 'amount', label: 'Amount', render: (r) => formatCurrency(r.amount) },
                { key: 'payment_date', label: 'Date', render: (r) => formatDateTime(r.payment_date) },
                { key: 'method', label: 'Method', render: (r) => <span className="capitalize">{r.method}</span> },
                { key: 'status', label: 'Status', render: (r) => <StatusBadge status={r.status} /> },
              ]}
              data={payments}
              onPageChange={setPage}
            />
          ) : (
            <DataTable
              loading={loading}
              columns={[
                { key: 'invoice_number', label: 'Invoice #' },
                { key: 'tenant_name', label: 'Tenant' },
                { key: 'total_amount', label: 'Amount', render: (r) => formatCurrency(r.total_amount) },
                { key: 'due_date', label: 'Due Date', render: (r) => formatDate(r.due_date) },
                { key: 'status', label: 'Status', render: (r) => <StatusBadge status={r.status} /> },
              ]}
              data={invoices}
              onPageChange={setPage}
            />
          )}
        </div>
      </DashboardLayout>
    </ProtectedRoute>
  );
}
