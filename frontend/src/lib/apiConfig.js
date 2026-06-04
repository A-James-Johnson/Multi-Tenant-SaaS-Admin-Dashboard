const getDefaultApiUrl = () => {
  if (typeof window !== 'undefined') {
    const host = window.location.hostname;
    if (host === 'localhost' || host === '127.0.0.1' || host.startsWith('192.168.')) {
      return 'http://localhost:8000';
    }
  }

  if (process.env.NODE_ENV === 'development') {
    return 'http://localhost:8000';
  }

  return 'https://multi-tenant-saas-admin-dashboard.onrender.com';
};

const DEFAULT_API_URL = getDefaultApiUrl();

export const getApiBaseUrl = () => {
  const value = process.env.NEXT_PUBLIC_API_URL || DEFAULT_API_URL;
  return value.replace(/\/+$/, '');
};

export const API_BASE_URL = getApiBaseUrl();
export const API_PREFIX = `${API_BASE_URL}/api/v1`;

export const getErrorMessage = (error, fallback = 'Something went wrong. Please try again.') => {
  if (error?.response?.data) {
    const data = error.response.data;
    if (typeof data === 'string') return data;
    if (data?.detail) return data.detail;
    if (data?.message) return data.message;
    if (data?.errors) {
      const messages = Object.values(data.errors).flat().filter(Boolean);
      if (messages.length) return messages.join(' ');
    }
  }

  return error?.message || fallback;
};
