import { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import useAuthStore from '../stores/authStore';
import { dashboardAPI } from '../services/api';
import type { DashboardData, PaymentType } from '../types';
import Header from './Header';
import Card from './Card';
import PaymentForm from './PaymentForm';
import PaymentPlanForm from './PaymentPlanForm';
import { formatCurrency, formatDate, getStatusColor } from '../utils/formatters';

function Dashboard() {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [showPaymentForm, setShowPaymentForm] = useState<boolean>(false);
  const [showPlanForm, setShowPlanForm] = useState<boolean>(false);
  const [paymentType, setPaymentType] = useState<PaymentType>('one-time');

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        const data = await dashboardAPI.getDashboardData();
        setDashboardData(data);
      } catch (err: any) {
        setError(err.response?.data?.error || 'Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const handleMakePayment = (type: PaymentType = 'one-time') => {
    setPaymentType(type);
    setShowPaymentForm(true);
  };

  const handleEnrollPlan = () => {
    setShowPlanForm(true);
  };

  const handlePaymentSuccess = () => {
    setShowPaymentForm(false);
    window.location.reload();
  };

  const handlePlanSuccess = () => {
    setShowPlanForm(false);
    window.location.reload();
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-10 h-10 border-2 border-royal-600 border-t-transparent rounded-full animate-spin" />
          <p className="text-sm text-gray-400 font-body">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Card className="max-w-md text-center">
          <div className="text-rose-400 text-lg mb-4">{error}</div>
          <button onClick={() => window.location.reload()} className="btn-primary">
            Retry
          </button>
        </Card>
      </div>
    );
  }

  const financialStatus = user?.financial_status || dashboardData?.status;

  return (
    <div className="min-h-screen">
      <Header onLogout={handleLogout} />

      <main className="page-container space-y-6">
        {/* Welcome Banner */}
        <div className="glass-card p-6 animate-fade-in overflow-hidden relative">
          <div className="absolute inset-0 bg-gradient-to-r from-royal-600/20 to-gold-600/10 pointer-events-none" />
          <div className="relative">
            <h2 className="font-heading text-2xl font-semibold text-white mb-1">
              Welcome back, {dashboardData?.name || user?.name}
            </h2>
            <p className="text-gray-400 text-sm">
              Here's an overview of your financial status and recent activity.
            </p>
          </div>
        </div>

        {/* Status Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="stat-card animate-slide-up stagger-1">
            <p className="stat-label">Financial Status</p>
            <div className="mt-2">
              <span className={`${
                financialStatus === 'financial' ? 'badge-financial' : 'badge-not-financial'
              } text-sm px-3 py-1`}>
                {financialStatus || 'Not Set'}
              </span>
            </div>
          </div>

          <div className="stat-card animate-slide-up stagger-2">
            <p className="stat-label">Initiation Date</p>
            <p className="stat-value text-xl">
              {formatDate(dashboardData?.initiation_date) || 'Not set'}
            </p>
          </div>

          <div className="stat-card animate-slide-up stagger-3">
            <p className="stat-label">Role</p>
            <p className="stat-value text-xl capitalize">{user?.role || 'Member'}</p>
          </div>
        </div>

        {/* Payment Plan Section */}
        {dashboardData?.plan ? (
          <Card className="animate-slide-up stagger-4">
            <div className="flex items-center justify-between mb-5">
              <h3 className="font-heading text-xl font-semibold text-white">Active Payment Plan</h3>
              <span className="badge-info">Active</span>
            </div>

            <div className="mb-6">
              <div className="flex justify-between mb-2">
                <span className="text-sm text-gray-400">Payment Progress</span>
                <span className="text-sm font-mono font-semibold text-royal-300">
                  {dashboardData.percent_paid}%
                </span>
              </div>
              <div className="progress-bar-track">
                <div
                  className="progress-bar-fill"
                  style={{ width: `${dashboardData.percent_paid}%` }}
                />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="border-l-2 border-royal-500 pl-4">
                <p className="text-sm text-gray-500 mb-0.5">Frequency</p>
                <p className="text-base font-semibold text-white capitalize">
                  {dashboardData.plan.frequency}
                </p>
              </div>
              <div className="border-l-2 border-gold-500 pl-4">
                <p className="text-sm text-gray-500 mb-0.5">Total Amount</p>
                <p className="text-base font-mono font-semibold text-gold-400">
                  {formatCurrency(dashboardData.plan.total_amount)}
                </p>
              </div>
              <div className="border-l-2 border-rose-500 pl-4">
                <p className="text-sm text-gray-500 mb-0.5">Remaining</p>
                <p className="text-base font-mono font-semibold text-rose-400">
                  {formatCurrency(dashboardData.remaining_balance)}
                </p>
              </div>
            </div>

            <div className="mt-6 pt-5 border-t border-surface-border">
              <button onClick={() => handleMakePayment('installment')} className="btn-primary">
                Make Payment
              </button>
            </div>
          </Card>
        ) : (
          <Card className="animate-slide-up stagger-4">
            <div className="text-center py-8">
              <h3 className="font-heading text-xl font-semibold text-white mb-2">No Active Payment Plan</h3>
              <p className="text-gray-400 mb-6 text-sm max-w-sm mx-auto">
                Enroll in a plan to manage your dues, or make a one-time payment.
              </p>
              <div className="flex flex-col sm:flex-row gap-3 justify-center">
                <button onClick={handleEnrollPlan} className="btn-primary">
                  Enroll in Payment Plan
                </button>
                <button onClick={() => handleMakePayment('one-time')} className="btn-secondary">
                  Make One-Time Payment
                </button>
              </div>
            </div>
          </Card>
        )}

        {/* Recent Payments Section */}
        <Card className="animate-slide-up stagger-5">
          <div className="flex items-center justify-between mb-5">
            <h3 className="font-heading text-xl font-semibold text-white">Recent Payments</h3>
            <div className="flex items-center gap-3">
              <button onClick={() => handleMakePayment('one-time')} className="btn-primary text-sm">
                Make Payment
              </button>
              {dashboardData?.payments && dashboardData.payments.length > 0 && (
                <Link to="/payments" className="text-sm text-royal-400 hover:text-royal-300 font-medium transition-colors">
                  View All →
                </Link>
              )}
            </div>
          </div>

          {dashboardData?.payments && dashboardData.payments.length > 0 ? (
            <div className="overflow-x-auto -mx-6 sm:mx-0">
              <div className="inline-block min-w-full align-middle">
                <table className="min-w-full">
                  <thead>
                    <tr className="table-header">
                      <th className="px-5 py-3 text-left">Date</th>
                      <th className="px-5 py-3 text-left">Amount</th>
                      <th className="px-5 py-3 text-left">Method</th>
                      <th className="px-5 py-3 text-left">Type</th>
                    </tr>
                  </thead>
                  <tbody>
                    {dashboardData.payments.map((payment, index) => (
                      <tr key={index} className="table-row">
                        <td className="table-cell text-gray-300">
                          {formatDate(payment.date)}
                        </td>
                        <td className="table-cell font-mono font-semibold text-white">
                          {formatCurrency(payment.amount)}
                        </td>
                        <td className="table-cell">
                          <span className="badge-info capitalize">{payment.method}</span>
                        </td>
                        <td className="table-cell text-gray-400 capitalize">
                          {payment.payment_type}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ) : (
            <div className="text-center py-12">
              <h3 className="text-lg font-medium text-white mb-2">No Payments Yet</h3>
              <p className="text-gray-400 mb-6 text-sm">
                Get started by making your first payment.
              </p>
              <button onClick={() => handleMakePayment('one-time')} className="btn-primary">
                Make a Payment
              </button>
            </div>
          )}
        </Card>
      </main>

      {/* Payment Form Modal */}
      {showPaymentForm && (
        <PaymentForm
          paymentType={paymentType}
          onClose={() => setShowPaymentForm(false)}
          onSuccess={handlePaymentSuccess}
        />
      )}

      {/* Payment Plan Form Modal */}
      {showPlanForm && (
        <PaymentPlanForm
          onClose={() => setShowPlanForm(false)}
          onSuccess={handlePlanSuccess}
        />
      )}
    </div>
  );
}

export default Dashboard;
