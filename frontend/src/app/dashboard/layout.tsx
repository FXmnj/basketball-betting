'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/stores/authStore';
import Link from 'next/link';
import { Menu, X } from 'lucide-react';

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { isAuthenticated, user, logout } = useAuthStore();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    // Check if authenticated
    if (!isAuthenticated) {
      router.replace('/auth/login');
    }

    // Check if mobile
    const handleResize = () => {
      const mobile = window.innerWidth < 768;
      setIsMobile(mobile);
      setSidebarOpen(!mobile);
    };

    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [isAuthenticated, router]);

  const handleLogout = async () => {
    await logout();
    router.push('/auth/login');
  };

  const navItems = [
    { label: 'Dashboard', href: '/dashboard', icon: '📊' },
    { label: 'Games', href: '/dashboard/games', icon: '🎮' },
    { label: 'Teams', href: '/dashboard/teams', icon: '🏀' },
    { label: 'Players', href: '/dashboard/players', icon: '👥' },
    { label: 'Predictions', href: '/dashboard/predictions', icon: '🤖' },
    { label: 'Profile', href: '/dashboard/profile', icon: '⚙️' },
  ];

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="flex h-screen overflow-hidden bg-dark-bg">
      {/* Sidebar */}
      <div
        className={`${
          sidebarOpen ? 'w-64' : 'w-0'
        } bg-dark-surface border-r border-dark-border transition-all duration-300 flex flex-col overflow-hidden`}
      >
        {/* Logo */}
        <div className="p-6 border-b border-dark-border">
          <h1 className="text-xl font-bold text-nba-accent">🏀 CourtVision</h1>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto p-4 space-y-2">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="court-hover block px-4 py-3 rounded-lg text-dark-text hover:bg-dark-hover"
              onClick={() => isMobile && setSidebarOpen(false)}
            >
              <span className="mr-2">{item.icon}</span>
              {item.label}
            </Link>
          ))}
        </nav>

        {/* User Info */}
        <div className="border-t border-dark-border p-4">
          <div className="mb-3">
            <p className="text-xs text-dark-muted">Logged in as</p>
            <p className="font-medium text-dark-text truncate">
              {user?.firstName && user.lastName
                ? `${user.firstName} ${user.lastName}`
                : user?.email}
            </p>
            <p className="text-xs text-dark-muted capitalize">{user?.role}</p>
          </div>
          <button
            onClick={handleLogout}
            className="btn btn-secondary w-full text-sm"
          >
            Logout
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Bar */}
        <header className="bg-dark-surface border-b border-dark-border px-6 py-4 flex items-center justify-between">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 hover:bg-dark-hover rounded-lg transition-colors"
          >
            {sidebarOpen ? (
              <X className="w-5 h-5" />
            ) : (
              <Menu className="w-5 h-5" />
            )}
          </button>
          <div className="flex items-center gap-4">
            <span className="text-sm text-dark-muted">Phase 1 Beta</span>
          </div>
        </header>

        {/* Content Area */}
        <main className="flex-1 overflow-y-auto">
          <div className="p-6 max-w-7xl">{children}</div>
        </main>
      </div>
    </div>
  );
}
