import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import useAuthStore from '../stores/authStore';
import { treasurerAPI } from '../services/api';
import Header from './Header';
import Card from './Card';
import { formatCurrency } from '../utils/formatters';

function TreasurerDashboard() {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Check if user has full access
    const hasFullAccess = ['admin', 'treasurer', 'president', 'vice_1'].includes(user?.role);
    if (user && !hasFullAccess) {
      navigate('/dashboard');
      return;
    }

    const fetchStats = async () => {
      try {
        setLoading(true);
        const data: any = await treasurerAPI.getStats();
        setStats(data.stats || data);
      } catch (err: any) {
        if (err.response?.status === 403) {
          navigate('/dashboard');
        } else {
          setError(err.response?.data?.error || 'Failed to load stats');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, [user, navigate]);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  if (loading) {
    return (
      <div className="min-h-screen">
        <Header onLogout={handleLogout} />
        <div className="flex items-center justify-center py-20">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-royal-600 border-t-transparent mb-4"></div>
            <p className="text-lg text-gray-400 font-body">Loading treasurer dashboard...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen">
        <Header onLogout={handleLogout} />
        <div className="flex items-center justify-center py-20">
          <Card className="max-w-md">
            <div className="text-center">
              <div className="alert-error mb-4">{error}</div>
              <button
                onClick={() => window.location.reload()}
                className="btn-primary"
              >
                Retry
              </button>
            </div>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      <Header onLogout={handleLogout} />

      <main className="page-container space-y-6">
        {/* Page Header — glass card with gradient overlay */}
        <div className="glass-card p-6 animate-fade-in overflow-hidden relative">
          <div className="absolute inset-0 bg-gradient-to-r from-royal-600/20 to-gold-600/10 pointer-events-none" />
          <div className="relative">
            <h2 className="font-heading text-2xl font-semibold text-white mb-1">
              Treasurer Dashboard
            </h2>
            <p className="text-gray-400 text-sm font-body">
              Manage member payments, view financial reports, and track organization finances.
            </p>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="stat-card animate-slide-up stagger-1">
            <div className="flex items-center gap-3">
              <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-emerald-500/15 border border-emerald-500/20 flex items-center justify-center">
                <svg className="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <p className="stat-label">Total Collected</p>
                <p className="stat-value gold">
                  {formatCurrency(stats?.total_collected || 0)}
                </p>
              </div>
            </div>
          </div>

          <div className="stat-card animate-slide-up stagger-2">
            <div className="flex items-center gap-3">
              <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-royal-500/15 border border-royal-500/20 flex items-center justify-center">
                <svg className="w-5 h-5 text-royal-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
                </svg>
              </div>
              <div>
                <p className="stat-label">Active Plans</p>
                <p className="stat-value">
                  {stats?.active_plans || 0}
                </p>
              </div>
            </div>
          </div>

          <div className="stat-card animate-slide-up stagger-3">
            <div className="flex items-center gap-3">
              <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-royal-500/15 border border-royal-500/20 flex items-center justify-center">
                <svg className="w-5 h-5 text-royal-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </div>
              <div>
                <p className="stat-label">Total Members</p>
                <p className="stat-value">
                  {stats?.total_members || 0}
                </p>
              </div>
            </div>
          </div>

          <div className="stat-card animate-slide-up stagger-4">
            <div className="flex items-center gap-3">
              <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-rose-500/15 border border-rose-500/20 flex items-center justify-center">
                <svg className="w-5 h-5 text-rose-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4.5c-.77-.833-2.694-.833-3.464 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
              <div>
                <p className="stat-label">Unpaid Members</p>
                <p className="stat-value text-rose-400">
                  {stats?.unpaid_members || 0}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Payment Breakdown */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card className="animate-slide-up stagger-5">
            <h3 className="text-lg font-heading font-semibold text-white mb-4">Payment Types</h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-400 font-body">One-Time Payments</span>
                <span className="font-mono font-semibold text-white">
                  {stats?.payment_types?.one_time || 0}
                </span>
              </div>
              <div className="divider" />
              <div className="flex justify-between items-center">
                <span className="text-gray-400 font-body">Installment Payments</span>
                <span className="font-mono font-semibold text-white">
                  {stats?.payment_types?.installment || 0}
                </span>
              </div>
            </div>
          </Card>

          <Card className="animate-slide-up stagger-6">
            <h3 className="text-lg font-heading font-semibold text-white mb-4">Payment Methods</h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-400 font-body">Stripe</span>
                <span className="font-mono font-semibold text-white">
                  {stats?.payment_methods?.stripe || 0}
                </span>
              </div>
              <div className="divider" />
              <div className="flex justify-between items-center">
                <span className="text-gray-400 font-body">Cash</span>
                <span className="font-mono font-semibold text-white">
                  {stats?.payment_methods?.cash || 0}
                </span>
              </div>
              <div className="divider" />
              <div className="flex justify-between items-center">
                <span className="text-gray-400 font-body">Other</span>
                <span className="font-mono font-semibold text-white">
                  {stats?.payment_methods?.other || 0}
                </span>
              </div>
            </div>
          </Card>
        </div>

        {/* Quick Actions */}
        <Card>
          <h3 className="text-xl font-heading font-semibold text-white mb-4">Quick Actions</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <button
              onClick={() => navigate('/members')}
              className="glass-card p-4 text-left group hover:border-royal-500/30 transition-all duration-200"
            >
              <div className="w-9 h-9 rounded-lg bg-royal-500/15 border border-royal-500/20 flex items-center justify-center mb-3 group-hover:bg-royal-500/25 transition-colors">
                <svg className="w-5 h-5 text-royal-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </div>
              <p className="font-medium text-white font-body">View Members</p>
              <p className="text-sm text-gray-500 font-body">Manage member accounts</p>
            </button>

            <button
              onClick={() => navigate('/reports')}
              className="glass-card p-4 text-left group hover:border-royal-500/30 transition-all duration-200"
            >
              <div className="w-9 h-9 rounded-lg bg-gold-500/15 border border-gold-500/20 flex items-center justify-center mb-3 group-hover:bg-gold-500/25 transition-colors">
                <svg className="w-5 h-5 text-gold-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <p className="font-medium text-white font-body">View Reports</p>
              <p className="text-sm text-gray-500 font-body">Financial reports & analytics</p>
            </button>

            <button
              onClick={() => navigate('/treasurer/payments')}
              className="glass-card p-4 text-left group hover:border-royal-500/30 transition-all duration-200"
            >
              <div className="w-9 h-9 rounded-lg bg-emerald-500/15 border border-emerald-500/20 flex items-center justify-center mb-3 group-hover:bg-emerald-500/25 transition-colors">
                <svg className="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                </svg>
              </div>
              <p className="font-medium text-white font-body">All Payments</p>
              <p className="text-sm text-gray-500 font-body">View all payment history</p>
            </button>

            <button
              onClick={() => navigate('/invites')}
              className="glass-card p-4 text-left group hover:border-royal-500/30 transition-all duration-200"
            >
              <div className="w-9 h-9 rounded-lg bg-royal-500/15 border border-royal-500/20 flex items-center justify-center mb-3 group-hover:bg-royal-500/25 transition-colors">
                <svg className="w-5 h-5 text-royal-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
              <p className="font-medium text-white font-body">Send Invites</p>
              <p className="text-sm text-gray-500 font-body">Generate invite codes</p>
            </button>
          </div>
        </Card>
      </main>
    </div>
  );
}

export default TreasurerDashboard;
