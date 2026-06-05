'use client';

import { useEffect, useState } from 'react';
import { useAuthStore } from '@/stores/authStore';

export default function ProfilePage() {
  const { user, updateProfile, isLoading } = useAuthStore();
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
  });
  const [message, setMessage] = useState('');

  useEffect(() => {
    if (user) {
      setFormData({
        firstName: user.firstName || '',
        lastName: user.lastName || '',
      });
    }
  }, [user]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage('');

    try {
      await updateProfile(formData);
      setMessage('Profile updated successfully! ✅');
    } catch (error: any) {
      setMessage(error.response?.data?.error || 'Failed to update profile');
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="heading-2 mb-2">⚙️ User Profile</h1>
        <p className="text-dark-muted">Manage your account settings</p>
      </div>

      {/* Profile Card */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* User Info */}
        <div className="court-card-lg">
          <h2 className="heading-3 mb-4">Account Information</h2>

          <div className="space-y-4">
            <div>
              <p className="text-sm text-dark-muted mb-1">Email</p>
              <p className="font-medium text-dark-text">{user?.email}</p>
            </div>

            <div>
              <p className="text-sm text-dark-muted mb-1">Role</p>
              <div className="flex items-center gap-2">
                <span className={`px-3 py-1 rounded text-xs font-bold ${
                  user?.role === 'ADMIN' ? 'bg-red-900/30 text-red-200' :
                  user?.role === 'PREMIUM' ? 'bg-yellow-900/30 text-yellow-200' :
                  'bg-blue-900/30 text-blue-200'
                }`}>
                  {user?.role}
                </span>
              </div>
            </div>

            <div className="bg-dark-bg/50 p-3 rounded-lg mt-4">
              <p className="text-xs text-dark-muted mb-1">Account Status</p>
              <p className="text-sm font-medium text-green-400">✅ Verified and Active</p>
            </div>
          </div>
        </div>

        {/* Stats */}
        <div className="court-card-lg">
          <h2 className="heading-3 mb-4">Account Stats</h2>

          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-dark-muted">Account Created</span>
              <span className="font-medium">Today</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-dark-muted">Last Login</span>
              <span className="font-medium">Just now</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-dark-muted">Predictions Made</span>
              <span className="font-medium">0</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-dark-muted">Accuracy Rate</span>
              <span className="font-medium">--</span>
            </div>
          </div>
        </div>
      </div>

      {/* Edit Profile */}
      <div className="court-card-lg max-w-2xl">
        <h2 className="heading-3 mb-4">Edit Profile</h2>

        {message && (
          <div className={`mb-4 px-4 py-2 rounded-lg text-sm ${
            message.includes('successfully') || message.includes('✅')
              ? 'bg-green-900/20 text-green-200 border border-green-500'
              : 'bg-red-900/20 text-red-200 border border-red-500'
          }`}>
            {message}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="firstName" className="block text-sm font-medium mb-2">
                First Name
              </label>
              <input
                id="firstName"
                type="text"
                name="firstName"
                value={formData.firstName}
                onChange={handleChange}
                placeholder="John"
                className="input"
              />
            </div>

            <div>
              <label htmlFor="lastName" className="block text-sm font-medium mb-2">
                Last Name
              </label>
              <input
                id="lastName"
                type="text"
                name="lastName"
                value={formData.lastName}
                onChange={handleChange}
                placeholder="Doe"
                className="input"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="btn btn-primary"
          >
            {isLoading ? 'Saving...' : 'Save Changes'}
          </button>
        </form>
      </div>

      {/* Phase 1 Info */}
      <div className="court-card-lg border-yellow-600/50 border-2">
        <h3 className="heading-4 mb-2">📋 Phase 1 Information</h3>
        <p className="text-dark-muted text-sm mb-3">
          You're currently viewing CourtVision AI Phase 1 Beta. More features will be added in Phase 2:
        </p>
        <ul className="text-dark-muted text-sm space-y-1">
          <li>🚀 Subscription management (Premium, Pro tiers)</li>
          <li>🔐 Two-factor authentication</li>
          <li>🎯 Advanced privacy settings</li>
          <li>📧 Email notification preferences</li>
          <li>🌙 Theme customization</li>
        </ul>
      </div>
    </div>
  );
}
