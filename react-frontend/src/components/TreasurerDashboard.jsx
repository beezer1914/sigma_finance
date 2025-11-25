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
        const data = await treasurerAPI.getStats();
        setStats(data.stats);
      } catch (err) {
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
      <div className="min-h-screen bg-gray-50">
        <Header onLogout={handleLogout} />
        <div className="flex items-center justify-center py-20">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
            <p className="text-lg text-gray-600">Loading treasurer dashboard...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header onLogout={handleLogout} />
        <div className="flex items-center justify-center py-20">
          <Card className="max-w-md">
            <div className="text-center">
              <div className="text-red-600 text-lg mb-4">{error}</div>
              <button
                onClick={() => window.location.reload()}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
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
    <div className="min-h-screen bg-gray-50">
      <Header onLogout={handleLogout} />

      <main className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8 space-y-6">
        {/* Page Header */}
        <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-lg shadow-lg p-6 text-white">
          <h1 className="text-2xl font-bold mb-2">Treasurer Dashboard</h1>
          <p className="text-indigo-100">
            Manage member payments, view financial reports, and track organization finances.
          </p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card>
            <div className="text-center">
              <div className="text-3xl mb-2">💰</div>
              <p className="text-sm text-gray-600 mb-1">Total Collected</p>
              <p className="text-2xl font-bold text-green-600">
                {formatCurrency(stats?.total_collected || 0)}
              </p>
            </div>
          </Card>
          <Card>
            <div className="text-center">
              <div className="text-3xl mb-2">📋</div>
              <p className="text-sm text-gray-600 mb-1">Active Plans</p>
              <p className="text-2xl font-bold text-blue-600">
                {stats?.active_plans || 0}
              </p>
            </div>
          </Card>
          <Card>
            <div className="text-center">
              <div className="text-3xl mb-2">👥</div>
              <p className="text-sm text-gray-600 mb-1">Total Members</p>
              <p className="text-2xl font-bold text-gray-900">
                {stats?.total_members || 0}
              </p>
            </div>
          </Card>
          <Card>
            <div className="text-center">
              <div className="text-3xl mb-2">⚠️</div>
              <p className="text-sm text-gray-600 mb-1">Unpaid Members</p>
              <p className="text-2xl font-bold text-red-600">
                {stats?.unpaid_members || 0}
              </p>
            </div>
          </Card>
        </div>

        {/* Payment Breakdown */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <h3 className="text-lg font-bold text-gray-900 mb-4">Payment Types</h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">One-Time Payments</span>
                <span className="font-bold text-gray-900">
                  {stats?.payment_types?.one_time || 0}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Installment Payments</span>
                <span className="font-bold text-gray-900">
                  {stats?.payment_types?.installment || 0}
                </span>
              </div>
            </div>
          </Card>

          <Card>
            <h3 className="text-lg font-bold text-gray-900 mb-4">Payment Methods</h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Stripe</span>
                <span className="font-bold text-gray-900">
                  {stats?.payment_methods?.stripe || 0}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Cash</span>
                <span className="font-bold text-gray-900">
                  {stats?.payment_methods?.cash || 0}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Other</span>
                <span className="font-bold text-gray-900">
                  {stats?.payment_methods?.other || 0}
                </span>
              </div>
            </div>
          </Card>
        </div>

        {/* Quick Actions */}
        <Card>
          <h2 className="text-xl font-bold text-gray-900 mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <button
              onClick={() => navigate('/members')}
              className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-left"
            >
              <div className="text-2xl mb-2">👥</div>
              <p className="font-medium text-gray-900">View Members</p>
              <p className="text-sm text-gray-600">Manage member accounts</p>
            </button>
            <button
              onClick={() => navigate('/reports')}
              className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-left"
            >
              <div className="text-2xl mb-2">📊</div>
              <p className="font-medium text-gray-900">View Reports</p>
              <p className="text-sm text-gray-600">Financial reports & analytics</p>
            </button>
            <button
              onClick={() => navigate('/treasurer/payments')}
              className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-left"
            >
              <div className="text-2xl mb-2">💳</div>
              <p className="font-medium text-gray-900">All Payments</p>
              <p className="text-sm text-gray-600">View all payment history</p>
            </button>
            <button
              onClick={() => navigate('/invites')}
              className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-left"
            >
              <div className="text-2xl mb-2">📧</div>
              <p className="font-medium text-gray-900">Send Invites</p>
              <p className="text-sm text-gray-600">Generate invite codes</p>
            </button>
          </div>
        </Card>
      </main>
    </div>
  );
}

export default TreasurerDashboard;
