'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';
import { Loader2 } from 'lucide-react';

export default function SignupPage() {
  const [form, setForm] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    password: '',
    confirmPassword: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { signup } = useAuth();
  const router = useRouter();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (form.password !== form.confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    setLoading(true);
    try {
      await signup({
        first_name: form.first_name,
        last_name: form.last_name,
        email: form.email,
        company_name: form.first_name + ' ' + form.last_name,
        phone: form.phone,
        password: form.password,
      });
      router.push('/dashboard');
    } catch (err) {
      setError(err.response?.data?.error?.message || err.response?.data?.message || 'Unable to create account.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen">
      <div className="hidden flex-1 flex-col justify-between bg-primary p-12 text-primary-foreground lg:flex">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-white/10 text-lg font-bold">S</div>
          <span className="text-xl font-semibold">SaaS Admin</span>
        </div>
        <div>
          <h1 className="text-4xl font-bold leading-tight">Create your tenant workspace</h1>
          <p className="mt-4 text-primary-foreground/70">Register your company and start managing users, billing, and analytics in one place.</p>
        </div>
        <p className="text-sm text-primary-foreground/50">© 2026 SaaS Admin Platform</p>
      </div>
      <div className="flex flex-1 items-center justify-center p-8">
        <div className="w-full max-w-xl">
          <h2 className="text-2xl font-bold">Create your account</h2>
          <p className="mt-1 text-muted-foreground">Register a new tenant admin account</p>
          <form onSubmit={handleSubmit} className="mt-8 space-y-4">
            {error && <div className="rounded-lg bg-destructive/10 px-4 py-3 text-sm text-destructive">{error}</div>}
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <label className="mb-1.5 block text-sm font-medium">First name</label>
                <input name="first_name" value={form.first_name} onChange={handleChange} className="input" placeholder="Jane" required />
              </div>
              <div>
                <label className="mb-1.5 block text-sm font-medium">Last name</label>
                <input name="last_name" value={form.last_name} onChange={handleChange} className="input" placeholder="Doe" required />
              </div>
            </div>
            <div>
              <label className="mb-1.5 block text-sm font-medium">Email</label>
              <input name="email" type="email" value={form.email} onChange={handleChange} className="input" placeholder="you@company.com" required />
            </div>
            <div>
              <label className="mb-1.5 block text-sm font-medium">Phone (optional)</label>
              <input name="phone" value={form.phone} onChange={handleChange} className="input" placeholder="+1 555 123 4567" />
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <label className="mb-1.5 block text-sm font-medium">Password</label>
                <input name="password" type="password" value={form.password} onChange={handleChange} className="input" placeholder="At least 8 characters" required />
              </div>
              <div>
                <label className="mb-1.5 block text-sm font-medium">Confirm password</label>
                <input name="confirmPassword" type="password" value={form.confirmPassword} onChange={handleChange} className="input" placeholder="Repeat your password" required />
              </div>
            </div>
            <button type="submit" disabled={loading} className="btn-primary w-full">
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Create account'}
            </button>
          </form>
          <p className="mt-6 text-center text-sm text-muted-foreground">
            Already have an account? <Link href="/login" className="text-primary hover:underline">Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
