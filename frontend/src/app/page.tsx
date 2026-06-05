'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/stores/authStore';
import Link from 'next/link';

export default function Home() {
  const { isAuthenticated } = useAuthStore();
  const router = useRouter();

  useEffect(() => {
    if (isAuthenticated) {
      router.replace('/dashboard');
    }
  }, [isAuthenticated, router]);

  return (
    <div className="min-h-screen bg-gradient-to-b from-dark-surface to-dark-bg flex flex-col">
      {/* Navigation */}
      <nav className="border-b border-dark-border bg-dark-surface/50 backdrop-blur">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <div className="text-2xl font-bold text-nba-accent">🏀 CourtVision AI</div>
          <div className="space-x-4">
            <Link
              href="/auth/login"
              className="btn btn-secondary"
            >
              Login
            </Link>
            <Link
              href="/auth/register"
              className="btn btn-primary"
            >
              Sign Up
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="flex-1 flex flex-col items-center justify-center px-4 py-20">
        <div className="text-center max-w-2xl">
          <h1 className="heading-1 mb-4 text-nba-accent">CourtVision AI</h1>
          <p className="text-xl text-dark-muted mb-8">
            Professional NBA Basketball Analytics & Game Predictions Powered by AI
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
            <div className="court-card">
              <div className="text-3xl mb-2">📊</div>
              <h3 className="heading-4 mb-2">Advanced Analytics</h3>
              <p className="text-dark-muted">Real-time team and player statistics</p>
            </div>

            <div className="court-card">
              <div className="text-3xl mb-2">🤖</div>
              <h3 className="heading-4 mb-2">AI Predictions</h3>
              <p className="text-dark-muted">Intelligent game predictions & analysis</p>
            </div>

            <div className="court-card">
              <div className="text-3xl mb-2">⚡</div>
              <h3 className="heading-4 mb-2">Live Updates</h3>
              <p className="text-dark-muted">Real-time game data and scores</p>
            </div>
          </div>

          <div className="space-x-4">
            <Link
              href="/auth/register"
              className="btn btn-primary inline-block mb-4 md:mb-0"
            >
              Get Started Free
            </Link>
            <Link
              href="/auth/login"
              className="btn btn-secondary inline-block"
            >
              Already a member?
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-dark-border bg-dark-surface/50 py-6">
        <div className="max-w-7xl mx-auto px-4 text-center text-dark-muted">
          <p>&copy; 2024 CourtVision AI. All rights reserved. Phase 1 Beta.</p>
        </div>
      </footer>
    </div>
  );
}
