'use client';

import { useState, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { authAPI } from '@/lib/api';

function ResetForm() {
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get('token');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (password !== confirm) { setError('Passwords do not match'); return; }
    setLoading(true);
    try {
      await authAPI.resetPassword({ token, new_password: password });
      router.push('/login');
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Reset failed');
    } finally {
      setLoading(false);
    }
  };

  if (!token) return <p className="text-destructive">Invalid reset link</p>;

  return (
    <form onSubmit={handleSubmit} className="mt-8 space-y-4">
      {error && <div className="rounded-lg bg-destructive/10 px-4 py-3 text-sm text-destructive">{error}</div>}
      <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} className="input" placeholder="New password" required minLength={8} />
      <input type="password" value={confirm} onChange={(e) => setConfirm(e.target.value)} className="input" placeholder="Confirm password" required />
      <button type="submit" disabled={loading} className="btn-primary w-full">Reset password</button>
    </form>
  );
}

export default function ResetPasswordPage() {
  return (
    <div className="flex min-h-screen items-center justify-center p-8">
      <div className="w-full max-w-md">
        <h2 className="text-2xl font-bold">Reset password</h2>
        <Suspense><ResetForm /></Suspense>
        <Link href="/login" className="mt-4 block text-center text-sm text-muted-foreground hover:text-foreground">Back to login</Link>
      </div>
    </div>
  );
}
