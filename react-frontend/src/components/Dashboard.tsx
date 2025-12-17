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
    // Refresh dashboard data
    window.location.reload();
  };

  const handlePlanSuccess = () => {
    setShowPlanForm(false);
    // Refresh dashboard data
    window.location.reload();
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
          <p className="text-lg text-gray-600">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Card className="max-w-md">
          <div className="text-center">
            <div className="text-red-600 text-lg mb-4">⚠️ {error}</div>
            <button
              onClick={() => window.location.reload()}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              Retry
            </button>
          </div>
        </Card>
      </div>
    );
  }

  const financialStatus = user?.financial_status || dashboardData?.status;

  return (
    <div className="min-h-screen bg-gray-50">
      <Header onLogout={handleLogout} />

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8 space-y-6">
        {/* Welcome Banner */}
        <div className="bg-gradient-to-r from-blue-600 to-blue-700 rounded-lg shadow-lg p-6 text-white">
          <h2 className="text-2xl font-bold mb-2">
            Welcome back, {dashboardData?.name || user?.name}!
          </h2>
          <p className="text-blue-100">
            Here's an overview of your financial status and recent activity.
          </p>
        </div>

        {/* Status Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card>
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 mb-1">Financial Status</p>
                <span
                  className={`inline-block px-3 py-1 rounded-full text-sm font-semibold ${getStatusColor(
                    financialStatus
                  )}`}
                >
                  {financialStatus || 'Not Set'}
                </span>
              </div>
              <div className="text-3xl">💰</div>
            </div>
          </Card>

          <Card>
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 mb-1">Initiation Date</p>
                <p className="text-lg font-bold text-gray-900">
                  {formatDate(dashboardData?.initiation_date) || 'Not set'}
                </p>
              </div>
              <div className="text-3xl">📅</div>
            </div>
          </Card>

          <Card>
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 mb-1">Role</p>
                <p className="text-lg font-bold text-gray-900 capitalize">{user?.role || 'Member'}</p>
              </div>
              <div className="text-3xl">👤</div>
            </div>
          </Card>
        </div>

        {/* Payment Plan Section */}
        {dashboardData?.plan ? (
          <Card>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900">Active Payment Plan</h2>
              <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-semibold">
                Active
              </span>
            </div>

            <div className="mb-6">
              <div className="flex justify-between mb-2">
                <span className="text-sm font-medium text-gray-600">Payment Progress</span>
                <span className="text-sm font-bold text-blue-600">
                  {dashboardData.percent_paid}% Complete
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                <div
                  className="bg-gradient-to-r from-blue-500 to-blue-600 h-3 rounded-full transition-all duration-500 ease-out"
                  style={{ width: `${dashboardData.percent_paid}%` }}
                ></div>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
              <div className="border-l-4 border-blue-500 pl-4">
                <p className="text-sm text-gray-600 mb-1">Frequency</p>
                <p className="text-lg font-bold text-gray-900 capitalize">
                  {dashboardData.plan.frequency}
                </p>
              </div>
              <div className="border-l-4 border-green-500 pl-4">
                <p className="text-sm text-gray-600 mb-1">Total Amount</p>
                <p className="text-lg font-bold text-gray-900">
                  {formatCurrency(dashboardData.plan.total_amount)}
                </p>
              </div>
              <div className="border-l-4 border-red-500 pl-4">
                <p className="text-sm text-gray-600 mb-1">Remaining Balance</p>
                <p className="text-lg font-bold text-red-600">
                  {formatCurrency(dashboardData.remaining_balance)}
                </p>
              </div>
            </div>

            <div className="mt-6 pt-6 border-t border-gray-200">
              <button
                onClick={() => handleMakePayment('installment')}
                className="w-full sm:w-auto px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
              >
                Make Payment
              </button>
            </div>
          </Card>
        ) : (
          <Card>
            <div className="text-center py-8">
              <div className="text-5xl mb-4">📋</div>
              <h3 className="text-lg font-bold text-gray-900 mb-2">No Active Payment Plan</h3>
              <p className="text-gray-600 mb-6">
                You don't have an active payment plan. Enroll in a plan to manage your dues, or make a one-time payment.
              </p>
              <div className="flex flex-col sm:flex-row gap-3 justify-center">
                <button
                  onClick={handleEnrollPlan}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
                >
                  Enroll in Payment Plan
                </button>
                <button
                  onClick={() => handleMakePayment('one-time')}
                  className="px-6 py-2 border border-blue-600 text-blue-600 rounded-lg hover:bg-blue-50 transition-colors font-medium"
                >
                  Make One-Time Payment
                </button>
              </div>
            </div>
          </Card>
        )}

        {/* Recent Payments Section */}
        <Card>
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-gray-900">Recent Payments</h2>
            <div className="flex items-center gap-3">
              <button
                onClick={() => handleMakePayment('one-time')}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium text-sm"
              >
                Make One-Time Payment
              </button>
              {dashboardData?.payments && dashboardData.payments.length > 0 && (
                <Link
                  to="/payments"
                  className="text-sm text-blue-600 hover:text-blue-700 font-medium"
                >
                  View All →
                </Link>
              )}
            </div>
          </div>

          {dashboardData?.payments && dashboardData.payments.length > 0 ? (
            <div className="overflow-x-auto -mx-6 sm:mx-0">
              <div className="inline-block min-w-full align-middle">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Date
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Amount
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Method
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Type
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {dashboardData.payments.map((payment, index) => (
                      <tr key={index} className="hover:bg-gray-50 transition-colors">
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {formatDate(payment.date)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-gray-900">
                          {formatCurrency(payment.amount)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 capitalize">
                            {payment.method}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 capitalize">
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
              <div className="text-5xl mb-4">💳</div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No Payments Yet</h3>
              <p className="text-gray-600 mb-6">
                You haven't made any payments yet. Get started by making your first payment.
              </p>
              <button
                onClick={() => handleMakePayment('one-time')}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
              >
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
