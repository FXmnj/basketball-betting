'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuthStore } from '@/stores/authStore';

export default function LoginPage() {
  const router = useRouter();
  const { login, isLoading, error } = useAuthStore();
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [localError, setLocalError] = useState('');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLocalError('');

    if (!formData.email || !formData.password) {
      setLocalError('Email and password are required');
      return;
    }

    try {
      await login(formData.email, formData.password);
      router.push('/dashboard');
    } catch (err: any) {
      setLocalError(err.response?.data?.error || 'Login failed');
    }
  };

  // Demo credentials for quick testing
  const fillDemoCredentials = () => {
    setFormData({ email: 'user@courtvision.ai', password: 'TestPassword123' });
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-dark-surface to-dark-bg flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="heading-2 text-nba-accent mb-2">🏀 CourtVision AI</h1>
          <p className="text-dark-muted">Login to your account</p>
        </div>

        {/* Form Card */}
        <div className="court-card-lg mb-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Error Message */}
            {(error || localError) && (
              <div className="bg-red-900/20 border border-red-500 text-red-200 px-4 py-2 rounded-lg text-sm">
                {error || localError}
              </div>
            )}

            {/* Email */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium mb-2 text-dark-text">
                Email Address
              </label>
              <input
                id="email"
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="you@example.com"
                className="input"
                required
              />
            </div>

            {/* Password */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium mb-2 text-dark-text">
                Password
              </label>
              <input
                id="password"
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="••••••••"
                className="input"
                required
              />
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={isLoading}
              className="btn btn-primary w-full mt-6"
            >
              {isLoading ? 'Logging in...' : 'Login'}
            </button>
          </form>
        </div>

        {/* Demo Credentials */}
        <div className="court-card mb-6">
          <p className="text-sm text-dark-muted mb-3">🧪 Testing? Try these demo credentials:</p>
          <div className="space-y-2 mb-3 text-xs font-mono bg-dark-bg/50 p-3 rounded">
            <div>Email: <span className="text-nba-gold">user@courtvision.ai</span></div>
            <div>Password: <span className="text-nba-gold">TestPassword123</span></div>
          </div>
          <button
            type="button"
            onClick={fillDemoCredentials}
            className="btn btn-secondary w-full text-sm"
          >
            Fill Demo Credentials
          </button>
        </div>

        {/* Link to Register */}
        <div className="text-center">
          <p className="text-dark-muted">
            Don't have an account?{' '}
            <Link href="/auth/register" className="text-nba-accent hover:underline">
              Sign up here
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
