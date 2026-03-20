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
      <div className="min-h-screen">
        <Header onLogout={handleLogout} />
        <div className="flex items-center justify-center py-20">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-royal-600 border-t-transparent mb-4"></div>
            <p className="text-lg text-gray-400 font-body">Loading payments...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      <Header onLogout={handleLogout} />

      <main className="page-container space-y-6">
        {/* Page Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 animate-fade-in">
          <div>
            <h1 className="font-heading text-2xl font-semibold text-white">All Payments</h1>
            <p className="text-gray-400 font-body">{pagination.total} total payments</p>
          </div>
          <button
            onClick={() => navigate('/treasurer')}
            className="btn-secondary"
          >
            Back to Treasurer
          </button>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="stat-card animate-slide-up stagger-1">
            <p className="stat-label">Total Payments</p>
            <p className="stat-value">{pagination.total}</p>
          </div>
          <div className="stat-card animate-slide-up stagger-2">
            <p className="stat-label">Page Results</p>
            <p className="stat-value">{payments.length}</p>
          </div>
          <div className="stat-card animate-slide-up stagger-3">
            <p className="stat-label">Page Total</p>
            <p className="stat-value gold">{formatCurrency(pageTotal)}</p>
          </div>
        </div>

        {/* Filters */}
        <Card className="animate-slide-up stagger-4">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <label className="input-label">
                Payment Type
              </label>
              <select
                value={filters.paymentType}
                onChange={(e) => setFilters({ ...filters, paymentType: e.target.value })}
                className="input-field"
              >
                <option value="all">All Types</option>
                <option value="one-time">One-Time</option>
                <option value="installment">Installment</option>
              </select>
            </div>

            <div className="flex-1">
              <label className="input-label">
                Payment Method
              </label>
              <select
                value={filters.method}
                onChange={(e) => setFilters({ ...filters, method: e.target.value })}
                className="input-field"
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
                className="px-4 py-2.5 text-sm font-medium font-body text-gray-400 hover:text-white transition-colors"
              >
                Clear Filters
              </button>
            </div>
          </div>
        </Card>

        {/* Error Display */}
        {error && (
          <div className="alert-error">
            {error}
          </div>
        )}

        {/* Payments Table */}
        <Card>
          {payments.length > 0 ? (
            <>
              <div className="overflow-x-auto -mx-6 sm:mx-0">
                <div className="inline-block min-w-full align-middle">
                  <table className="min-w-full">
                    <thead className="table-header">
                      <tr>
                        <th className="px-5 py-3.5 text-left">
                          Date
                        </th>
                        <th className="px-5 py-3.5 text-left">
                          Member
                        </th>
                        <th className="px-5 py-3.5 text-left">
                          Amount
                        </th>
                        <th className="px-5 py-3.5 text-left">
                          Method
                        </th>
                        <th className="px-5 py-3.5 text-left">
                          Type
                        </th>
                        <th className="px-5 py-3.5 text-left">
                          Notes
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {payments.map((payment) => (
                        <tr key={payment.id} className="table-row">
                          <td className="table-cell whitespace-nowrap">
                            {formatDate(payment.date)}
                          </td>
                          <td className="table-cell whitespace-nowrap">
                            <div className="font-medium text-white">{payment.user_name}</div>
                            <div className="text-xs text-gray-500">{payment.user_email}</div>
                          </td>
                          <td className="table-cell whitespace-nowrap font-mono font-semibold text-gold-400">
                            {formatCurrency(payment.amount)}
                          </td>
                          <td className="table-cell whitespace-nowrap">
                            <span className="badge-info capitalize">
                              {payment.method}
                            </span>
                          </td>
                          <td className="table-cell whitespace-nowrap">
                            <span
                              className={`capitalize ${
                                payment.payment_type === 'installment'
                                  ? 'badge-warning'
                                  : 'badge-financial'
                              }`}
                            >
                              {payment.payment_type}
                            </span>
                          </td>
                          <td className="table-cell max-w-xs truncate text-gray-500">
                            {payment.notes || '-'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Pagination */}
              <div className="mt-4 flex items-center justify-between border-t border-surface-border pt-4">
                <p className="text-sm text-gray-400 font-body">
                  Showing {pagination.offset + 1} to{' '}
                  {Math.min(pagination.offset + pagination.limit, pagination.total)} of{' '}
                  {pagination.total} payments
                </p>
                <div className="flex gap-2">
                  <button
                    onClick={handlePrevPage}
                    disabled={pagination.offset === 0}
                    className={`px-4 py-2 text-sm font-medium font-body rounded-lg transition-colors ${
                      pagination.offset === 0
                        ? 'bg-sigma-850 text-gray-600 cursor-not-allowed border border-surface-border'
                        : 'btn-secondary'
                    }`}
                  >
                    Previous
                  </button>
                  <button
                    onClick={handleNextPage}
                    disabled={!pagination.hasMore}
                    className={`px-4 py-2 text-sm font-medium font-body rounded-lg transition-colors ${
                      !pagination.hasMore
                        ? 'bg-sigma-850 text-gray-600 cursor-not-allowed border border-surface-border'
                        : 'btn-secondary'
                    }`}
                  >
                    Next
                  </button>
                </div>
              </div>
            </>
          ) : (
            <div className="text-center py-12">
              <div className="w-14 h-14 mx-auto mb-4 rounded-xl bg-royal-500/15 border border-royal-500/20 flex items-center justify-center">
                <svg className="w-7 h-7 text-royal-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                </svg>
              </div>
              <h3 className="text-lg font-heading font-medium text-white mb-2">No Payments Found</h3>
              <p className="text-gray-400 font-body">
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
