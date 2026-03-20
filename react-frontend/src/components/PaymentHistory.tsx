import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import useAuthStore from '../stores/authStore';
import { paymentAPI } from '../services/api';
import type { Payment } from '../types';
import Header from './Header';
import { formatCurrency, formatDate } from '../utils/formatters';

interface Pagination {
  total: number;
  limit: number;
  offset: number;
  hasMore: boolean;
}

interface Filters {
  paymentType: string;
  method: string;
  dateRange: string;
}

function PaymentHistory() {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const [payments, setPayments] = useState<Payment[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [pagination, setPagination] = useState<Pagination>({
    total: 0,
    limit: 20,
    offset: 0,
    hasMore: false,
  });

  // Filter state
  const [filters, setFilters] = useState<Filters>({
    paymentType: 'all',
    method: 'all',
    dateRange: 'all',
  });

  const fetchPayments = async (offset = 0) => {
    try {
      setLoading(true);
      const data: any = await paymentAPI.getPayments(pagination.limit, offset);
      setPayments(data.payments);
      setPagination({
        total: data.pagination.total,
        limit: data.pagination.limit,
        offset: data.pagination.offset,
        hasMore: data.pagination.has_more,
      });
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to load payment history');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPayments();
  }, []);

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

  // Filter payments client-side
  const filteredPayments = payments.filter((payment) => {
    // Payment type filter
    if (filters.paymentType !== 'all' && payment.payment_type !== filters.paymentType) {
      return false;
    }

    // Method filter
    if (filters.method !== 'all' && payment.method !== filters.method) {
      return false;
    }

    // Date range filter
    if (filters.dateRange !== 'all') {
      const paymentDate = new Date(payment.date);
      const now = new Date();

      if (filters.dateRange === 'week') {
        const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
        if (paymentDate < weekAgo) return false;
      } else if (filters.dateRange === 'month') {
        const monthAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
        if (paymentDate < monthAgo) return false;
      } else if (filters.dateRange === 'year') {
        const yearAgo = new Date(now.getTime() - 365 * 24 * 60 * 60 * 1000);
        if (paymentDate < yearAgo) return false;
      }
    }

    return true;
  });

  // Calculate totals
  const totalAmount = filteredPayments.reduce(
    (sum, p) => sum + parseFloat(String(p.amount)),
    0
  );

  if (loading && payments.length === 0) {
    return (
      <div className="min-h-screen">
        <Header onLogout={handleLogout} />
        <div className="flex items-center justify-center py-20">
          <div className="text-center">
            <div className="w-10 h-10 border-2 border-royal-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-lg text-gray-400">Loading payment history...</p>
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
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="font-heading text-white">Payment History</h1>
            <p className="text-gray-400">View and filter your payment records</p>
          </div>
          <button
            onClick={() => navigate('/dashboard')}
            className="btn-secondary text-sm"
          >
            Back to Dashboard
          </button>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="stat-card">
            <div className="text-center">
              <p className="stat-label">Total Payments</p>
              <p className="stat-value">{pagination.total}</p>
            </div>
          </div>
          <div className="stat-card">
            <div className="text-center">
              <p className="stat-label">Filtered Results</p>
              <p className="stat-value text-royal-400">{filteredPayments.length}</p>
            </div>
          </div>
          <div className="stat-card">
            <div className="text-center">
              <p className="stat-label">Filtered Total</p>
              <p className="stat-value gold">{formatCurrency(totalAmount)}</p>
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="glass-card p-5">
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
                <option value="card">Card</option>
                <option value="check">Check</option>
              </select>
            </div>

            <div className="flex-1">
              <label className="input-label">
                Date Range
              </label>
              <select
                value={filters.dateRange}
                onChange={(e) => setFilters({ ...filters, dateRange: e.target.value })}
                className="input-field"
              >
                <option value="all">All Time</option>
                <option value="week">Last 7 Days</option>
                <option value="month">Last 30 Days</option>
                <option value="year">Last Year</option>
              </select>
            </div>

            <div className="flex items-end">
              <button
                onClick={() => setFilters({ paymentType: 'all', method: 'all', dateRange: 'all' })}
                className="text-sm font-medium text-gray-500 hover:text-white transition-colors px-4 py-2.5"
              >
                Clear Filters
              </button>
            </div>
          </div>
        </div>

        {/* Payments Table */}
        <div className="glass-card p-5">
          {error && (
            <div className="alert-error mb-4">
              {error}
            </div>
          )}

          {filteredPayments.length > 0 ? (
            <>
              <div className="overflow-x-auto -mx-5 sm:mx-0">
                <div className="inline-block min-w-full align-middle">
                  <table className="min-w-full">
                    <thead className="table-header">
                      <tr>
                        <th className="px-5 py-3.5 text-left">
                          Date
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
                      {filteredPayments.map((payment) => (
                        <tr key={payment.id} className="table-row">
                          <td className="table-cell whitespace-nowrap">
                            {formatDate(payment.date)}
                          </td>
                          <td className="table-cell whitespace-nowrap font-mono font-semibold text-white">
                            {formatCurrency(payment.amount)}
                          </td>
                          <td className="table-cell whitespace-nowrap">
                            <span className="badge bg-sigma-700/50 text-gray-300 border border-surface-border capitalize">
                              {payment.method}
                            </span>
                          </td>
                          <td className="table-cell whitespace-nowrap">
                            <span
                              className={`badge capitalize ${
                                payment.payment_type === 'installment'
                                  ? 'bg-royal-500/15 text-royal-300 border border-royal-500/20'
                                  : 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/20'
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
                <p className="text-sm text-gray-500">
                  Showing {pagination.offset + 1} to{' '}
                  {Math.min(pagination.offset + pagination.limit, pagination.total)} of{' '}
                  {pagination.total} payments
                </p>
                <div className="flex gap-2">
                  <button
                    onClick={handlePrevPage}
                    disabled={pagination.offset === 0}
                    className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors border ${
                      pagination.offset === 0
                        ? 'border-surface-border text-gray-300 opacity-50 cursor-not-allowed'
                        : 'border-surface-border text-gray-300 hover:bg-surface-hover'
                    }`}
                  >
                    Previous
                  </button>
                  <button
                    onClick={handleNextPage}
                    disabled={!pagination.hasMore}
                    className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors border ${
                      !pagination.hasMore
                        ? 'border-surface-border text-gray-300 opacity-50 cursor-not-allowed'
                        : 'border-surface-border text-gray-300 hover:bg-surface-hover'
                    }`}
                  >
                    Next
                  </button>
                </div>
              </div>
            </>
          ) : (
            <div className="text-center py-12">
              <svg className="w-12 h-12 text-gray-600 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
              </svg>
              <h3 className="text-lg font-heading font-medium text-white mb-2">No Payments Found</h3>
              <p className="text-gray-500">
                {payments.length === 0
                  ? "You haven't made any payments yet."
                  : 'No payments match your current filters.'}
              </p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default PaymentHistory;
