import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import useAuthStore from '../stores/authStore';
import { profileAPI } from '../services/api';
import Header from './Header';
import Card from './Card';
import { formatDate, getStatusColor } from '../utils/formatters';

function Profile() {
  const navigate = useNavigate();
  const { user, logout, updateUser } = useAuthStore();
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Form state
  const [name, setName] = useState<string>(user?.name || '');
  const [email, setEmail] = useState<string>(user?.email || '');
  const [currentPassword, setCurrentPassword] = useState<string>('');
  const [newPassword, setNewPassword] = useState<string>('');
  const [confirmPassword, setConfirmPassword] = useState<string>('');

  // Track which section is being edited
  const [editingProfile, setEditingProfile] = useState<boolean>(false);
  const [editingPassword, setEditingPassword] = useState<boolean>(false);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const handleUpdateProfile = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    if (!name.trim()) {
      setError('Name is required');
      return;
    }

    if (!email.trim()) {
      setError('Email is required');
      return;
    }

    try {
      setLoading(true);
      const response = await profileAPI.updateProfile({ name, email });
      updateUser(response.user);
      setSuccess('Profile updated successfully');
      setEditingProfile(false);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  const handleChangePassword = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    if (!currentPassword) {
      setError('Current password is required');
      return;
    }

    if (!newPassword) {
      setError('New password is required');
      return;
    }

    if (newPassword.length < 6) {
      setError('New password must be at least 6 characters');
      return;
    }

    if (newPassword !== confirmPassword) {
      setError('New passwords do not match');
      return;
    }

    try {
      setLoading(true);
      await profileAPI.updateProfile({
        current_password: currentPassword,
        new_password: newPassword,
      });
      setSuccess('Password changed successfully');
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
      setEditingPassword(false);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to change password');
    } finally {
      setLoading(false);
    }
  };

  const handleCancelProfileEdit = () => {
    setName(user?.name || '');
    setEmail(user?.email || '');
    setEditingProfile(false);
    setError(null);
  };

  const handleCancelPasswordEdit = () => {
    setCurrentPassword('');
    setNewPassword('');
    setConfirmPassword('');
    setEditingPassword(false);
    setError(null);
  };

  return (
    <div className="min-h-screen">
      <Header onLogout={handleLogout} />

      <main className="max-w-3xl mx-auto px-4 py-8 sm:px-6 lg:px-8 space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-heading font-bold text-white">Profile Settings</h1>
            <p className="text-gray-400">Manage your account information</p>
          </div>
          <button
            onClick={() => navigate('/dashboard')}
            className="btn-secondary"
          >
            Back to Dashboard
          </button>
        </div>

        {/* Alerts */}
        {error && (
          <div className="alert-error">
            {error}
          </div>
        )}
        {success && (
          <div className="alert-success">
            {success}
          </div>
        )}

        {/* Account Overview */}
        <Card>
          <div className="flex items-center gap-4 mb-6">
            <div className="w-20 h-20 bg-royal-600/20 border border-royal-500/30 rounded-full flex items-center justify-center text-3xl font-bold text-royal-300">
              {user?.name?.charAt(0)?.toUpperCase() || '?'}
            </div>
            <div>
              <h2 className="text-xl font-heading font-bold text-white">{user?.name}</h2>
              <p className="text-gray-400">{user?.email}</p>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-sm text-gray-400 capitalize">{user?.role}</span>
                <span className="text-gray-600">|</span>
                <span
                  className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(
                    user?.financial_status
                  )}`}
                >
                  {user?.financial_status || 'Not Set'}
                </span>
              </div>
            </div>
          </div>

          {user?.initiation_date && (
            <div className="border-t border-surface-border pt-4">
              <p className="text-sm text-gray-500">
                Member since: <span className="font-medium text-gray-300">{formatDate(user.initiation_date)}</span>
              </p>
            </div>
          )}
        </Card>

        {/* Profile Information */}
        <Card>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-heading font-bold text-white">Profile Information</h3>
            {!editingProfile && (
              <button
                onClick={() => setEditingProfile(true)}
                className="text-sm text-royal-400 hover:text-royal-300 font-medium"
              >
                Edit
              </button>
            )}
          </div>

          {editingProfile ? (
            <form onSubmit={handleUpdateProfile} className="space-y-4">
              <div>
                <label className="input-label">Name</label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="input-field w-full"
                  disabled={loading}
                />
              </div>
              <div>
                <label className="input-label">Email</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="input-field w-full"
                  disabled={loading}
                />
              </div>
              <div className="flex gap-3">
                <button
                  type="submit"
                  disabled={loading}
                  className="btn-primary disabled:opacity-50"
                >
                  {loading ? 'Saving...' : 'Save Changes'}
                </button>
                <button
                  type="button"
                  onClick={handleCancelProfileEdit}
                  disabled={loading}
                  className="btn-secondary"
                >
                  Cancel
                </button>
              </div>
            </form>
          ) : (
            <div className="space-y-3">
              <div>
                <p className="text-sm text-gray-500">Name</p>
                <p className="font-medium text-gray-300">{user?.name}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Email</p>
                <p className="font-medium text-gray-300">{user?.email}</p>
              </div>
            </div>
          )}
        </Card>

        {/* Change Password */}
        <Card>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-heading font-bold text-white">Change Password</h3>
            {!editingPassword && (
              <button
                onClick={() => setEditingPassword(true)}
                className="text-sm text-royal-400 hover:text-royal-300 font-medium"
              >
                Change
              </button>
            )}
          </div>

          {editingPassword ? (
            <form onSubmit={handleChangePassword} className="space-y-4">
              <div>
                <label className="input-label">
                  Current Password
                </label>
                <input
                  type="password"
                  value={currentPassword}
                  onChange={(e) => setCurrentPassword(e.target.value)}
                  className="input-field w-full"
                  disabled={loading}
                />
              </div>
              <div>
                <label className="input-label">
                  New Password
                </label>
                <input
                  type="password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  className="input-field w-full"
                  placeholder="At least 6 characters"
                  disabled={loading}
                />
              </div>
              <div>
                <label className="input-label">
                  Confirm New Password
                </label>
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="input-field w-full"
                  disabled={loading}
                />
              </div>
              <div className="flex gap-3">
                <button
                  type="submit"
                  disabled={loading}
                  className="btn-primary disabled:opacity-50"
                >
                  {loading ? 'Changing...' : 'Change Password'}
                </button>
                <button
                  type="button"
                  onClick={handleCancelPasswordEdit}
                  disabled={loading}
                  className="btn-secondary"
                >
                  Cancel
                </button>
              </div>
            </form>
          ) : (
            <p className="text-sm text-gray-500">
              Click "Change" to update your password.
            </p>
          )}
        </Card>
      </main>
    </div>
  );
}

export default Profile;
