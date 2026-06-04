'use client';

import { useEffect, useState } from 'react';
import ProtectedRoute from '@/components/ProtectedRoute';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { RevenueChart, GrowthChart, DistributionChart } from '@/components/charts/Charts';
import { analyticsAPI } from '@/lib/api';
import { useAuth } from '@/context/AuthContext';

export default function AnalyticsPage() {
  const { isSuperAdmin } = useAuth();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    analyticsAPI.dashboard().then((res) => setData(res.data.data)).finally(() => setLoading(false));
  }, []);

  return (
    <ProtectedRoute>
      <DashboardLayout>
        <div className="space-y-6">
          <div>
            <h1 className="text-2xl font-bold">Analytics</h1>
            <p className="text-muted-foreground">Detailed platform analytics and reports</p>
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
                <GrowthChart data={data?.user_growth || []} dataKey="users" label="New Users" color="#6366f1" />
              )}
            </div>
            {isSuperAdmin && (
              <div className="card">
                <h3 className="mb-4 font-semibold">Tenant Growth</h3>
                {loading ? <div className="h-[300px] animate-pulse rounded bg-muted" /> : (
                  <GrowthChart data={data?.tenant_growth || []} dataKey="tenants" label="New Tenants" color="#10b981" />
                )}
              </div>
            )}
            <div className="card">
              <h3 className="mb-4 font-semibold">Subscription Distribution</h3>
              {loading ? <div className="h-[300px] animate-pulse rounded bg-muted" /> : (
                <DistributionChart data={data?.subscription_distribution || []} />
              )}
            </div>
          </div>
        </div>
      </DashboardLayout>
    </ProtectedRoute>
  );
}
