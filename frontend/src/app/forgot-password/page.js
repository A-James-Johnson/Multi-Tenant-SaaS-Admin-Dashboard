'use client';

import { useState } from 'react';
import Link from 'next/link';
import { authAPI } from '@/lib/api';

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [sent, setSent] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await authAPI.forgotPassword(email);
      setSent(true);
    } catch {
      setSent(true);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center p-8">
      <div className="w-full max-w-md">
        <h2 className="text-2xl font-bold">Forgot password</h2>
        <p className="mt-1 text-muted-foreground">Enter your email to receive a reset link</p>
        {sent ? (
          <div className="mt-8 rounded-lg bg-accent p-4 text-sm">
            If an account exists with this email, a reset link has been sent.
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="mt-8 space-y-4">
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} className="input" placeholder="Email" required />
            <button type="submit" disabled={loading} className="btn-primary w-full">Send reset link</button>
          </form>
        )}
        <Link href="/login" className="mt-4 block text-center text-sm text-muted-foreground hover:text-foreground">
          Back to login
        </Link>
      </div>
    </div>
  );
}
