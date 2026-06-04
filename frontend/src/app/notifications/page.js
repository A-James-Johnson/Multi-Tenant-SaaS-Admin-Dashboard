'use client';

import { useEffect, useState } from 'react';
import { CheckCheck, Trash2 } from 'lucide-react';
import ProtectedRoute from '@/components/ProtectedRoute';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { notificationsAPI } from '@/lib/api';
import { formatDateTime } from '@/lib/utils';

const TYPE_COLORS = {
  plan_expiry: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
  payment_success: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
  payment_failure: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
  user_invitation: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
  system_alert: 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400',
};

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchNotifications = () => {
    setLoading(true);
    notificationsAPI.list().then((res) => {
      setNotifications(res.data.data.results || []);
    }).finally(() => setLoading(false));
  };

  useEffect(() => { fetchNotifications(); }, []);

  return (
    <ProtectedRoute>
      <DashboardLayout>
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold">Notifications</h1>
              <p className="text-muted-foreground">In-app notification center</p>
            </div>
            <button onClick={() => notificationsAPI.markAllRead().then(fetchNotifications)} className="btn-secondary gap-2">
              <CheckCheck className="h-4 w-4" /> Mark all read
            </button>
          </div>

          <div className="space-y-3">
            {loading ? (
              [...Array(5)].map((_, i) => <div key={i} className="h-20 animate-pulse rounded-xl bg-muted" />)
            ) : notifications.length === 0 ? (
              <div className="card text-center text-muted-foreground py-12">No notifications</div>
            ) : (
              notifications.map((n) => (
                <div key={n.id} className={`card flex items-start justify-between ${!n.is_read ? 'border-primary/30 bg-primary/5' : ''}`}>
                  <div className="flex gap-3">
                    <span className={`badge ${TYPE_COLORS[n.type] || ''}`}>{n.type.replace('_', ' ')}</span>
                    <div>
                      <p className="font-medium">{n.title}</p>
                      <p className="mt-1 text-sm text-muted-foreground">{n.message}</p>
                      <p className="mt-2 text-xs text-muted-foreground">{formatDateTime(n.created_at)}</p>
                    </div>
                  </div>
                  <div className="flex gap-1">
                    {!n.is_read && (
                      <button onClick={() => notificationsAPI.markRead(n.id).then(fetchNotifications)} className="rounded p-1.5 hover:bg-accent">
                        <CheckCheck className="h-4 w-4" />
                      </button>
                    )}
                    <button onClick={() => notificationsAPI.delete(n.id).then(fetchNotifications)} className="rounded p-1.5 hover:bg-accent text-destructive">
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </DashboardLayout>
    </ProtectedRoute>
  );
}
