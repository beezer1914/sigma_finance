import { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import useAuthStore from '../stores/authStore';
import { treasurerAPI } from '../services/api';
import Header from './Header';
import Card from './Card';
import { formatCurrency, formatDate } from '../utils/formatters';

function TreasurerPayments() {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({
    total: 0,
    limit: 25,
    offset: 0,
    hasMore: false,
  });

  // Filter state
  const [filters, setFilters] = useState({
    paymentType: 'all',
    method: 'all',
  });

  const fetchPayments = useCallback(async (offset = 0) => {
    try {
      setLoading(true);
      const params = {
        limit: pagination.limit,
        offset,
        ...(filters.paymentType !== 'all' && { payment_type: filters.paymentType }),
        ...(filters.method !== 'all' && { method: filters.method }),
      };

      const data: any = await treasurerAPI.getAllPayments(params);
      setPayments(data.payments);
      setPagination({
        total: data.pagination.total,
        limit: data.pagination.limit,
        offset: data.pagination.offset,
        hasMore: data.pagination.has_more,
      });
    } catch (err: any) {
      if (err.response?.status === 403) {
        navigate('/dashboard');
      } else {
        setError(err.response?.data?.error || 'Failed to load payments');
      }
    } finally {
      setLoading(false);
    }
  }, [filters, pagination.limit, navigate]);

  useEffect(() => {
    // Check if user has full access
    const hasFullAccess = ['admin', 'treasurer', 'president', 'vice_1'].includes(user?.role);
    if (user && !hasFullAccess) {
      navigate('/dashboard');
      return;
    }

    fetchPayments(0);
  }, [user, navigate, filters]);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const handlePrevPage = () => {
    const newOffset = Math.max(0, pagination.offset - pagination.limit);
    fetchPayments(newOffset);
  };

  const handleNextPage = () => {
    if (pagination.hasMore) {
      fetchPayments(pagination.offset + pagination.limit);
    }
  };

  const handleClearFilters = () => {
    setFilters({ paymentType: 'all', method: 'all' });
  };

  // Calculate totals for current page
  const pageTotal = payments.reduce((sum, p) => sum + parseFloat(p.amount), 0);

  if (loading && payments.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header onLogout={handleLogout} />
        <div className="flex items-center justify-center py-20">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
            <p className="text-lg text-gray-600">Loading payments...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header onLogout={handleLogout} />

      <main className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8 space-y-6">
        {/* Page Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">All Payments</h1>
            <p className="text-gray-600">{pagination.total} total payments</p>
          </div>
          <button
            onClick={() => navigate('/treasurer')}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Back to Treasurer
          </button>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <Card>
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-1">Total Payments</p>
              <p className="text-2xl font-bold text-gray-900">{pagination.total}</p>
            </div>
          </Card>
          <Card>
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-1">Page Results</p>
              <p className="text-2xl font-bold text-blue-600">{payments.length}</p>
            </div>
          </Card>
          <Card>
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-1">Page Total</p>
              <p className="text-2xl font-bold text-green-600">{formatCurrency(pageTotal)}</p>
            </div>
          </Card>
        </div>

        {/* Filters */}
        <Card>
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Payment Type
              </label>
              <select
                value={filters.paymentType}
                onChange={(e) => setFilters({ ...filters, paymentType: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Types</option>
                <option value="one-time">One-Time</option>
                <option value="installment">Installment</option>
              </select>
            </div>

            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Payment Method
              </label>
              <select
                value={filters.method}
                onChange={(e) => setFilters({ ...filters, method: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Methods</option>
                <option value="stripe">Stripe</option>
                <option value="cash">Cash</option>
                <option value="check">Check</option>
              </select>
            </div>

            <div className="flex items-end">
              <button
                onClick={handleClearFilters}
                className="px-4 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors"
              >
                Clear Filters
              </button>
            </div>
          </div>
        </Card>

        {/* Error Display */}
        {error && (
          <div className="p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg">
            {error}
          </div>
        )}

        {/* Payments Table */}
        <Card>
          {payments.length > 0 ? (
            <>
              <div className="overflow-x-auto -mx-6 sm:mx-0">
                <div className="inline-block min-w-full align-middle">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Date
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Member
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
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Notes
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {payments.map((payment) => (
                        <tr key={payment.id} className="hover:bg-gray-50 transition-colors">
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {formatDate(payment.date)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="font-medium text-gray-900">{payment.user_name}</div>
                            <div className="text-sm text-gray-500">{payment.user_email}</div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-gray-900">
                            {formatCurrency(payment.amount)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm">
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 capitalize">
                              {payment.method}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm">
                            <span
                              className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize ${
                                payment.payment_type === 'installment'
                                  ? 'bg-blue-100 text-blue-800'
                                  : 'bg-green-100 text-green-800'
                              }`}
                            >
                              {payment.payment_type}
                            </span>
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">
                            {payment.notes || '-'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Pagination */}
              <div className="mt-4 flex items-center justify-between border-t border-gray-200 pt-4">
                <p className="text-sm text-gray-600">
                  Showing {pagination.offset + 1} to{' '}
                  {Math.min(pagination.offset + pagination.limit, pagination.total)} of{' '}
                  {pagination.total} payments
                </p>
                <div className="flex gap-2">
                  <button
                    onClick={handlePrevPage}
                    disabled={pagination.offset === 0}
                    className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
                      pagination.offset === 0
                        ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                        : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    Previous
                  </button>
                  <button
                    onClick={handleNextPage}
                    disabled={!pagination.hasMore}
                    className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
                      !pagination.hasMore
                        ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                        : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    Next
                  </button>
                </div>
              </div>
            </>
          ) : (
            <div className="text-center py-12">
              <div className="text-5xl mb-4">💳</div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No Payments Found</h3>
              <p className="text-gray-600">
                {filters.paymentType !== 'all' || filters.method !== 'all'
                  ? 'No payments match your current filters.'
                  : 'No payments in the system yet.'}
              </p>
            </div>
          )}
        </Card>
      </main>
    </div>
  );
}

export default TreasurerPayments;
