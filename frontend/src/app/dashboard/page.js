'use client';

import { useEffect, useState } from 'react';
import { DollarSign, Users, Building2, TrendingUp } from 'lucide-react';
import ProtectedRoute from '@/components/ProtectedRoute';
import DashboardLayout from '@/components/layout/DashboardLayout';
import KPICard from '@/components/ui/KPICard';
import { RevenueChart, GrowthChart, DistributionChart } from '@/components/charts/Charts';
import { analyticsAPI } from '@/lib/api';
import { formatCurrency, formatDateTime } from '@/lib/utils';

export default function DashboardPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    analyticsAPI.dashboard().then((res) => {
      setData(res.data.data);
    }).catch(console.error).finally(() => setLoading(false));
  }, []);

  const kpis = data?.kpis || {};

  return (
    <ProtectedRoute>
      <DashboardLayout>
        <div className="space-y-6">
          <div>
            <h1 className="text-2xl font-bold">Dashboard</h1>
            <p className="text-muted-foreground">Overview of your SaaS platform</p>
          </div>

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <KPICard title="Total Revenue" value={formatCurrency(kpis.total_revenue)} icon={DollarSign} />
            <KPICard title="Monthly Revenue" value={formatCurrency(kpis.monthly_revenue)} icon={TrendingUp} />
            <KPICard title="Active Users" value={kpis.active_users || 0} icon={Users} />
            <KPICard title="Active Tenants" value={kpis.active_tenants || 0} icon={Building2} />
          </div>

          <div className="grid gap-6 lg:grid-cols-2">
            <div className="card">
              <h3 className="mb-4 font-semibold">Revenue Trend</h3>
              {loading ? <div className="h-[300px] animate-pulse rounded bg-muted" /> : (
                <RevenueChart data={data?.revenue_trend || []} />
              )}
            </div>
            <div className="card">
              <h3 className="mb-4 font-semibold">User Growth</h3>
              {loading ? <div className="h-[300px] animate-pulse rounded bg-muted" /> : (
                <GrowthChart data={data?.user_growth || []} dataKey="users" label="Users" color="#8b5cf6" />
              )}
            </div>
          </div>

          <div className="grid gap-6 lg:grid-cols-3">
            <div className="card lg:col-span-1">
              <h3 className="mb-4 font-semibold">Subscription Distribution</h3>
              {loading ? <div className="h-[300px] animate-pulse rounded bg-muted" /> : (
                <DistributionChart data={data?.subscription_distribution || []} />
              )}
            </div>
            <div className="card lg:col-span-2">
              <h3 className="mb-4 font-semibold">Recent Payments</h3>
              <div className="space-y-3">
                {(data?.recent_payments || []).map((p) => (
                  <div key={p.id} className="flex items-center justify-between rounded-lg border p-3">
                    <div>
                      <p className="font-medium">{p.tenant_name}</p>
                      <p className="text-xs text-muted-foreground">{p.payment_id}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-medium">{formatCurrency(p.amount)}</p>
                      <p className="text-xs text-muted-foreground">{formatDateTime(p.payment_date)}</p>
                    </div>
                  </div>
                ))}
                {!loading && !data?.recent_payments?.length && (
                  <p className="text-center text-muted-foreground py-4">No recent payments</p>
                )}
              </div>
            </div>
          </div>

          <div className="card">
            <h3 className="mb-4 font-semibold">Recent Activity</h3>
            <div className="space-y-2">
              {(data?.recent_activities || []).map((a) => (
                <div key={a.id} className="flex items-center justify-between rounded-lg border p-3 text-sm">
                  <div>
                    <p>{a.description}</p>
                    <p className="text-xs text-muted-foreground">{a.user_email}</p>
                  </div>
                  <span className="text-xs text-muted-foreground">{formatDateTime(a.created_at)}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </DashboardLayout>
    </ProtectedRoute>
  );
}
