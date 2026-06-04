'use client';

import { useEffect, useState } from 'react';
import ProtectedRoute from '@/components/ProtectedRoute';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { settingsAPI, authAPI } from '@/lib/api';
import { useAuth } from '@/context/AuthContext';

const TABS = [
  { id: 'general', label: 'General' },
  { id: 'security', label: 'Security' },
  { id: 'email', label: 'Email' },
  { id: 'password', label: 'Change Password' },
];

export default function SettingsPage() {
  const { isSuperAdmin } = useAuth();
  const [tab, setTab] = useState('general');
  const [settings, setSettings] = useState({});
  const [passwordForm, setPasswordForm] = useState({ old_password: '', new_password: '', confirm: '' });
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isSuperAdmin) {
      settingsAPI.list().then((res) => {
        const map = {};
        (res.data.data || []).forEach((s) => { map[s.category] = s.settings; });
        setSettings(map);
      });
    }
  }, [isSuperAdmin]);

  const handleSave = async (category) => {
    setLoading(true);
    try {
      await settingsAPI.update(category, { settings: settings[category] });
      setMessage('Settings saved successfully');
    } catch {
      setMessage('Failed to save settings');
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordChange = async (e) => {
    e.preventDefault();
    if (passwordForm.new_password !== passwordForm.confirm) {
      setMessage('Passwords do not match');
      return;
    }
    setLoading(true);
    try {
      await authAPI.changePassword({
        old_password: passwordForm.old_password,
        new_password: passwordForm.new_password,
      });
      setMessage('Password changed successfully');
      setPasswordForm({ old_password: '', new_password: '', confirm: '' });
    } catch {
      setMessage('Failed to change password');
    } finally {
      setLoading(false);
    }
  };

  const updateSetting = (category, key, value) => {
    setSettings({ ...settings, [category]: { ...settings[category], [key]: value } });
  };

  const visibleTabs = isSuperAdmin ? TABS : TABS.filter((t) => t.id === 'password');

  return (
    <ProtectedRoute>
      <DashboardLayout>
        <div className="space-y-6">
          <div>
            <h1 className="text-2xl font-bold">Settings</h1>
            <p className="text-muted-foreground">System configuration and preferences</p>
          </div>

          {message && (
            <div className="rounded-lg bg-accent px-4 py-3 text-sm">{message}</div>
          )}

          <div className="flex gap-2 border-b">
            {visibleTabs.map((t) => (
              <button key={t.id} onClick={() => { setTab(t.id); setMessage(''); }} className={`px-4 py-2 text-sm font-medium ${tab === t.id ? 'border-b-2 border-primary' : 'text-muted-foreground'}`}>
                {t.label}
              </button>
            ))}
          </div>

          {tab === 'general' && isSuperAdmin && (
            <div className="card max-w-lg space-y-4">
              {['company_name', 'support_email', 'timezone'].map((key) => (
                <div key={key}>
                  <label className="mb-1 block text-sm font-medium capitalize">{key.replace('_', ' ')}</label>
                  <input value={settings.general?.[key] || ''} onChange={(e) => updateSetting('general', key, e.target.value)} className="input" />
                </div>
              ))}
              <button onClick={() => handleSave('general')} disabled={loading} className="btn-primary">Save General Settings</button>
            </div>
          )}

          {tab === 'security' && isSuperAdmin && (
            <div className="card max-w-lg space-y-4">
              <div>
                <label className="mb-1 block text-sm font-medium">Password Min Length</label>
                <input type="number" value={settings.security?.password_min_length || 8} onChange={(e) => updateSetting('security', 'password_min_length', Number(e.target.value))} className="input" />
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium">Session Timeout (minutes)</label>
                <input type="number" value={settings.security?.session_timeout_minutes || 60} onChange={(e) => updateSetting('security', 'session_timeout_minutes', Number(e.target.value))} className="input" />
              </div>
              <label className="flex items-center gap-2">
                <input type="checkbox" checked={settings.security?.mfa_enabled || false} onChange={(e) => updateSetting('security', 'mfa_enabled', e.target.checked)} />
                <span className="text-sm">Enable MFA</span>
              </label>
              <button onClick={() => handleSave('security')} disabled={loading} className="btn-primary">Save Security Settings</button>
            </div>
          )}

          {tab === 'email' && isSuperAdmin && (
            <div className="card max-w-lg space-y-4">
              {['smtp_host', 'smtp_port', 'smtp_user', 'smtp_password', 'from_email'].map((key) => (
                <div key={key}>
                  <label className="mb-1 block text-sm font-medium uppercase">{key.replace('smtp_', 'SMTP ').replace('_', ' ')}</label>
                  <input type={key.includes('password') ? 'password' : key === 'smtp_port' ? 'number' : 'text'} value={settings.email?.[key] || ''} onChange={(e) => updateSetting('email', key, key === 'smtp_port' ? Number(e.target.value) : e.target.value)} className="input" />
                </div>
              ))}
              <button onClick={() => handleSave('email')} disabled={loading} className="btn-primary">Save Email Settings</button>
            </div>
          )}

          {tab === 'password' && (
            <form onSubmit={handlePasswordChange} className="card max-w-lg space-y-4">
              <input type="password" value={passwordForm.old_password} onChange={(e) => setPasswordForm({ ...passwordForm, old_password: e.target.value })} className="input" placeholder="Current password" required />
              <input type="password" value={passwordForm.new_password} onChange={(e) => setPasswordForm({ ...passwordForm, new_password: e.target.value })} className="input" placeholder="New password" required minLength={8} />
              <input type="password" value={passwordForm.confirm} onChange={(e) => setPasswordForm({ ...passwordForm, confirm: e.target.value })} className="input" placeholder="Confirm new password" required />
              <button type="submit" disabled={loading} className="btn-primary">Change Password</button>
            </form>
          )}
        </div>
      </DashboardLayout>
    </ProtectedRoute>
  );
}
