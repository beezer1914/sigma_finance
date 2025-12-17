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
      <div className="min-h-screen bg-gray-50">
        <Header onLogout={handleLogout} />
        <div className="flex items-center justify-center py-20">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
            <p className="text-lg text-gray-600">Loading reports...</p>
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
            <h1 className="text-2xl font-bold text-gray-900">Reports</h1>
            <p className="text-gray-600">Financial reports and analytics</p>
          </div>
          <button
            onClick={() => navigate('/treasurer')}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Back to Treasurer
          </button>
        </div>

        {error && (
          <div className="p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg">
            {error}
          </div>
        )}

        {/* Summary Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card>
            <div className="text-center">
              <div className="text-3xl mb-2">💰</div>
              <p className="text-sm text-gray-600 mb-1">Total Collected (All Time)</p>
              <p className="text-3xl font-bold text-green-600">
                {formatCurrency(summary?.total_collected || 0)}
              </p>
            </div>
          </Card>
          <Card>
            <div className="text-center">
              <div className="text-3xl mb-2">📊</div>
              <p className="text-sm text-gray-600 mb-1">Total Payments</p>
              <p className="text-3xl font-bold text-blue-600">
                {(summary?.by_type?.one_time || 0) + (summary?.by_type?.installment || 0)}
              </p>
            </div>
          </Card>
          <Card>
            <div className="text-center">
              <div className="text-3xl mb-2">📈</div>
              <p className="text-sm text-gray-600 mb-1">Months of Data</p>
              <p className="text-3xl font-bold text-purple-600">
                {summary?.trends?.length || 0}
              </p>
            </div>
          </Card>
        </div>

        {/* Payment Breakdown */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <h3 className="text-lg font-bold text-gray-900 mb-4">Payments by Type</h3>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-gray-600">One-Time</span>
                  <span className="font-medium">{summary?.by_type?.one_time || 0}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-green-500 h-2 rounded-full"
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
                  <span className="text-gray-600">Installment</span>
                  <span className="font-medium">{summary?.by_type?.installment || 0}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-500 h-2 rounded-full"
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
            <h3 className="text-lg font-bold text-gray-900 mb-4">Payments by Method</h3>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-gray-600">Stripe</span>
                  <span className="font-medium">{summary?.by_method?.stripe || 0}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-purple-500 h-2 rounded-full" style={{ width: `${getMethodPercentage('stripe')}%` }}></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-gray-600">Cash</span>
                  <span className="font-medium">{summary?.by_method?.cash || 0}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-yellow-500 h-2 rounded-full" style={{ width: `${getMethodPercentage('cash')}%` }}></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-gray-600">Other</span>
                  <span className="font-medium">{summary?.by_method?.other || 0}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-gray-500 h-2 rounded-full" style={{ width: `${getMethodPercentage('other')}%` }}></div>
                </div>
              </div>
            </div>
          </Card>
        </div>

        {/* Monthly Trends */}
        {summary?.trends && summary.trends.length > 0 && (
          <Card>
            <h3 className="text-lg font-bold text-gray-900 mb-4">Monthly Trends (Last 6 Months)</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Month
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Total Collected
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Payment Count
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {summary.trends.map((trend, index) => (
                    <tr key={index} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {trend.month}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-green-600 font-medium">
                        {formatCurrency(trend.total)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
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
          <h3 className="text-lg font-bold text-gray-900 mb-4">Export & Actions</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <button
              onClick={handleExportCSV}
              disabled={exporting}
              className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-left"
            >
              <div className="text-2xl mb-2">📤</div>
              <p className="font-medium text-gray-900">
                {exporting ? 'Exporting...' : 'Export to CSV'}
              </p>
              <p className="text-sm text-gray-500">Download all payment data</p>
            </button>
            <button
              onClick={() => navigate('/donations')}
              className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-left"
            >
              <div className="text-2xl mb-2">🎁</div>
              <p className="font-medium text-gray-900">Donations Report</p>
              <p className="text-sm text-gray-500">View and manage donations</p>
            </button>
            <button
              onClick={() => navigate('/members')}
              className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-left"
            >
              <div className="text-2xl mb-2">⚠️</div>
              <p className="font-medium text-gray-900">Delinquent Members</p>
              <p className="text-sm text-gray-500">View members needing attention</p>
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
