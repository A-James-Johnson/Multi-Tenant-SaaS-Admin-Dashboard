import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('access_token');
    if (token) config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;
      const refresh = localStorage.getItem('refresh_token');
      if (refresh) {
        try {
          const res = await axios.post(`${API_URL}/auth/refresh/`, { refresh });
          localStorage.setItem('access_token', res.data.access);
          original.headers.Authorization = `Bearer ${res.data.access}`;
          return api(original);
        } catch {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          if (typeof window !== 'undefined') window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

export default api;

export const authAPI = {
  signup: (data) => api.post('/auth/signup/', data),
  login: (email, password) => api.post('/auth/login/', { email, password }),
  logout: (refresh) => api.post('/auth/logout/', { refresh }),
  me: () => api.get('/auth/me/'),
  changePassword: (data) => api.post('/auth/change-password/', data),
  forgotPassword: (email) => api.post('/auth/forgot-password/', { email }),
  resetPassword: (data) => api.post('/auth/reset-password/', data),
};

export const tenantsAPI = {
  list: (params) => api.get('/tenants/', { params }),
  get: (id) => api.get(`/tenants/${id}/`),
  create: (data) => api.post('/tenants/', data),
  update: (id, data) => api.patch(`/tenants/${id}/`, data),
  delete: (id) => api.delete(`/tenants/${id}/`),
  suspend: (id) => api.post(`/tenants/${id}/suspend/`),
  activate: (id) => api.post(`/tenants/${id}/activate/`),
  metrics: () => api.get('/tenants/metrics/'),
};

export const usersAPI = {
  list: (params) => api.get('/users/', { params }),
  roles: () => api.get('/users/roles/'),
  get: (id) => api.get(`/users/${id}/`),
  create: (data) => api.post('/users/', data),
  update: (id, data) => api.patch(`/users/${id}/`, data),
  delete: (id) => api.delete(`/users/${id}/`),
};

export const subscriptionsAPI = {
  plans: (params) => api.get('/subscriptions/plans/', { params }),
  plan: (id) => api.get(`/subscriptions/plans/${id}/`),
  createPlan: (data) => api.post('/subscriptions/plans/', data),
  updatePlan: (id, data) => api.patch(`/subscriptions/plans/${id}/`, data),
  deletePlan: (id) => api.delete(`/subscriptions/plans/${id}/`),
  list: (params) => api.get('/subscriptions/', { params }),
  upgrade: (tenantId, planId) => api.post(`/subscriptions/${tenantId}/upgrade/`, { plan_id: planId }),
};

export const billingAPI = {
  payments: (params) => api.get('/billing/payments/', { params }),
  createPayment: (data) => api.post('/billing/payments/', data),
  invoices: (params) => api.get('/billing/invoices/', { params }),
  createInvoice: (data) => api.post('/billing/invoices/', data),
  revenue: () => api.get('/billing/revenue/'),
  gateways: () => api.get('/billing/gateways/'),
};

export const analyticsAPI = {
  dashboard: () => api.get('/analytics/dashboard/'),
};

export const notificationsAPI = {
  list: (params) => api.get('/notifications/', { params }),
  markRead: (id) => api.post(`/notifications/${id}/read/`),
  markAllRead: () => api.post('/notifications/read-all/'),
  delete: (id) => api.delete(`/notifications/${id}/`),
};

export const settingsAPI = {
  list: () => api.get('/settings/'),
  get: (category) => api.get(`/settings/${category}/`),
  update: (category, data) => api.patch(`/settings/${category}/`, data),
};

export const auditLogsAPI = {
  list: (params) => api.get('/audit-logs/', { params }),
};
