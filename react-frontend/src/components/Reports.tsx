import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import useAuthStore from '../stores/authStore';
import { treasurerAPI } from '../services/api';
import Header from './Header';
import Card from './Card';
import { formatCurrency } from '../utils/formatters';

function Reports() {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    // Check if user has report access
    const hasReportAccess = ['admin', 'treasurer', 'president', 'vice_1', 'vice_2', 'secretary'].includes(user?.role);
    if (user && !hasReportAccess) {
      navigate('/dashboard');
      return;
    }

    const fetchSummary = async () => {
      try {
        setLoading(true);
        const data = await treasurerAPI.getReportsSummary();
        setSummary(data.summary);
      } catch (err) {
        if (err.response?.status === 403) {
          navigate('/dashboard');
        } else {
          setError(err.response?.data?.error || 'Failed to load reports');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchSummary();
  }, [user, navigate]);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const handleExportCSV = async () => {
    try {
      setExporting(true);
      // Fetch all payments for export
      const data = await treasurerAPI.getAllPayments({ limit: 1000 });
      const payments = data.payments;

      if (payments.length === 0) {
        alert('No payments to export');
        return;
      }

      // Create CSV content
      const headers = ['Date', 'Member Name', 'Email', 'Amount', 'Method', 'Type', 'Notes'];
      const rows = payments.map((p) => [
        p.date,
        p.user_name || '',
        p.user_email || '',
        p.amount,
        p.method,
        p.payment_type,
        (p.notes || '').replace(/,/g, ';'), // Replace commas to avoid CSV issues
      ]);

      const csvContent = [
        headers.join(','),
        ...rows.map((row) => row.map((cell) => `"${cell}"`).join(',')),
      ].join('\n');

      // Download file
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = `payments_export_${new Date().toISOString().split('T')[0]}.csv`;
      link.click();
      URL.revokeObjectURL(link.href);
    } catch (err) {
      setError('Failed to export payments');
    } finally {
      setExporting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen">
        <Header onLogout={handleLogout} />
        <div className="flex items-center justify-center py-20">
          <div className="text-center">
            <div className="w-10 h-10 border-2 border-royal-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-lg text-gray-400">Loading reports...</p>
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
            <h1 className="text-2xl font-heading font-bold text-white">Reports</h1>
            <p className="text-gray-400">Financial reports and analytics</p>
          </div>
          <button
            onClick={() => navigate('/treasurer')}
            className="btn-secondary"
          >
            Back to Treasurer
          </button>
        </div>

        {error && (
          <div className="alert-error">
            {error}
          </div>
        )}

        {/* Summary Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="stat-card text-center">
            <p className="text-sm text-gray-400 mb-1">Total Collected (All Time)</p>
            <p className="text-3xl font-mono font-semibold text-emerald-400">
              {formatCurrency(summary?.total_collected || 0)}
            </p>
          </div>
          <div className="stat-card text-center">
            <p className="text-sm text-gray-400 mb-1">Total Payments</p>
            <p className="text-3xl font-mono font-semibold text-royal-300">
              {(summary?.by_type?.one_time || 0) + (summary?.by_type?.installment || 0)}
            </p>
          </div>
          <div className="stat-card text-center">
            <p className="text-sm text-gray-400 mb-1">Months of Data</p>
            <p className="text-3xl font-mono font-semibold text-gold-400">
              {summary?.trends?.length || 0}
            </p>
          </div>
        </div>

        {/* Payment Breakdown */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <h3 className="text-lg font-heading font-bold text-white mb-4">Payments by Type</h3>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-gray-400">One-Time</span>
                  <span className="font-mono font-semibold text-gray-300">{summary?.by_type?.one_time || 0}</span>
                </div>
                <div className="progress-bar-track">
                  <div
                    className="progress-bar-fill bg-emerald-500"
                    style={{
                      width: `${
                        ((summary?.by_type?.one_time || 0) /
                          ((summary?.by_type?.one_time || 0) + (summary?.by_type?.installment || 0) || 1)) *
                        100
                      }%`,
                    }}
                  ></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-gray-400">Installment</span>
                  <span className="font-mono font-semibold text-gray-300">{summary?.by_type?.installment || 0}</span>
                </div>
                <div className="progress-bar-track">
                  <div
                    className="progress-bar-fill bg-royal-400"
                    style={{
                      width: `${
                        ((summary?.by_type?.installment || 0) /
                          ((summary?.by_type?.one_time || 0) + (summary?.by_type?.installment || 0) || 1)) *
                        100
                      }%`,
                    }}
                  ></div>
                </div>
              </div>
            </div>
          </Card>

          <Card>
            <h3 className="text-lg font-heading font-bold text-white mb-4">Payments by Method</h3>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-gray-400">Stripe</span>
                  <span className="font-mono font-semibold text-gray-300">{summary?.by_method?.stripe || 0}</span>
                </div>
                <div className="progress-bar-track">
                  <div className="progress-bar-fill bg-violet-500" style={{ width: `${getMethodPercentage('stripe')}%` }}></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-gray-400">Cash</span>
                  <span className="font-mono font-semibold text-gray-300">{summary?.by_method?.cash || 0}</span>
                </div>
                <div className="progress-bar-track">
                  <div className="progress-bar-fill bg-gold-500" style={{ width: `${getMethodPercentage('cash')}%` }}></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-gray-400">Other</span>
                  <span className="font-mono font-semibold text-gray-300">{summary?.by_method?.other || 0}</span>
                </div>
                <div className="progress-bar-track">
                  <div className="progress-bar-fill bg-gray-500" style={{ width: `${getMethodPercentage('other')}%` }}></div>
                </div>
              </div>
            </div>
          </Card>
        </div>

        {/* Monthly Trends */}
        {summary?.trends && summary.trends.length > 0 && (
          <Card>
            <h3 className="text-lg font-heading font-bold text-white mb-4">Monthly Trends (Last 6 Months)</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full">
                <thead>
                  <tr className="table-header">
                    <th className="table-cell text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                      Month
                    </th>
                    <th className="table-cell text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                      Total Collected
                    </th>
                    <th className="table-cell text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                      Payment Count
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {summary.trends.map((trend, index) => (
                    <tr key={index} className="table-row">
                      <td className="table-cell whitespace-nowrap text-sm font-medium text-white">
                        {trend.month}
                      </td>
                      <td className="table-cell whitespace-nowrap text-sm font-mono font-semibold text-emerald-400">
                        {formatCurrency(trend.total)}
                      </td>
                      <td className="table-cell whitespace-nowrap text-sm text-gray-400">
                        {trend.count} payments
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        )}

        {/* Export & Actions */}
        <Card>
          <h3 className="text-lg font-heading font-bold text-white mb-4">Export & Actions</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <button
              onClick={handleExportCSV}
              disabled={exporting}
              className="p-4 bg-surface border border-surface-border rounded-xl hover:border-royal-500/40 transition-colors text-left disabled:opacity-50"
            >
              <p className="font-medium text-white">
                {exporting ? 'Exporting...' : 'Export to CSV'}
              </p>
              <p className="text-sm text-gray-500 mt-1">Download all payment data</p>
            </button>
            <button
              onClick={() => navigate('/donations')}
              className="p-4 bg-surface border border-surface-border rounded-xl hover:border-royal-500/40 transition-colors text-left"
            >
              <p className="font-medium text-white">Donations Report</p>
              <p className="text-sm text-gray-500 mt-1">View and manage donations</p>
            </button>
            <button
              onClick={() => navigate('/members')}
              className="p-4 bg-surface border border-surface-border rounded-xl hover:border-royal-500/40 transition-colors text-left"
            >
              <p className="font-medium text-white">Delinquent Members</p>
              <p className="text-sm text-gray-500 mt-1">View members needing attention</p>
            </button>
          </div>
        </Card>
      </main>
    </div>
  );

  function getMethodPercentage(method) {
    const total =
      (summary?.by_method?.stripe || 0) +
      (summary?.by_method?.cash || 0) +
      (summary?.by_method?.other || 0);
    if (total === 0) return 0;
    return ((summary?.by_method?.[method] || 0) / total) * 100;
  }
}

export default Reports;
