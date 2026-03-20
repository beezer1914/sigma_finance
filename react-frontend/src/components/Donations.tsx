import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import useAuthStore from '../stores/authStore';
import { donationsAPI } from '../services/api';
import Header from './Header';
import Card from './Card';
import { formatCurrency, formatDate } from '../utils/formatters';

function Donations() {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const [donations, setDonations] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [exporting, setExporting] = useState(false);

  // Filters
  const [filters, setFilters] = useState({
    anonymous: '',
    method: '',
  });

  // Add donation modal state
  const [showAddModal, setShowAddModal] = useState(false);
  const [addingDonation, setAddingDonation] = useState(false);
  const [newDonation, setNewDonation] = useState({
    donor_name: '',
    donor_email: '',
    amount: '',
    method: 'cash',
    anonymous: false,
    notes: '',
  });

  useEffect(() => {
    // Check if user has full access
    const hasFullAccess = ['admin', 'treasurer', 'president', 'vice_1'].includes(user?.role);
    if (user && !hasFullAccess) {
      navigate('/dashboard');
      return;
    }

    fetchData();
  }, [user, navigate]);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch donations and summary in parallel
      const [donationsData, summaryData] = await Promise.all([
        donationsAPI.getDonations({ limit: 100 }),
        donationsAPI.getSummary(),
      ]);

      setDonations(donationsData.donations);
      setSummary(summaryData.summary);
    } catch (err) {
      if (err.response?.status === 403) {
        navigate('/dashboard');
      } else {
        setError(err.response?.data?.error || 'Failed to load donations');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const handleFilterChange = (key, value) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  };

  const handleAddDonation = async (e) => {
    e.preventDefault();
    if (!newDonation.amount || parseFloat(newDonation.amount) <= 0) {
      setError('Please enter a valid amount');
      return;
    }

    try {
      setAddingDonation(true);
      setError(null);

      await donationsAPI.createDonation({
        donor_name: newDonation.anonymous ? '' : newDonation.donor_name,
        donor_email: newDonation.anonymous ? '' : newDonation.donor_email,
        amount: parseFloat(newDonation.amount),
        method: newDonation.method,
        anonymous: newDonation.anonymous,
        notes: newDonation.notes,
      });

      // Reset form and close modal
      setNewDonation({
        donor_name: '',
        donor_email: '',
        amount: '',
        method: 'cash',
        anonymous: false,
        notes: '',
      });
      setShowAddModal(false);

      // Refresh data
      await fetchData();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to add donation');
    } finally {
      setAddingDonation(false);
    }
  };

  const handleExportCSV = async () => {
    try {
      setExporting(true);
      const data = await donationsAPI.getDonations({ limit: 1000 });
      const allDonations = data.donations;

      if (allDonations.length === 0) {
        alert('No donations to export');
        return;
      }

      // Create CSV content
      const headers = ['Date', 'Donor Name', 'Donor Email', 'Amount', 'Method', 'Anonymous', 'Notes'];
      const rows = allDonations.map((d) => [
        d.date,
        d.donor_name || '',
        d.donor_email || '',
        d.amount,
        d.method,
        d.anonymous ? 'Yes' : 'No',
        (d.notes || '').replace(/,/g, ';'),
      ]);

      const csvContent = [
        headers.join(','),
        ...rows.map((row) => row.map((cell) => `"${cell}"`).join(',')),
      ].join('\n');

      // Download file
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = `donations_export_${new Date().toISOString().split('T')[0]}.csv`;
      link.click();
      URL.revokeObjectURL(link.href);
    } catch (err) {
      setError('Failed to export donations');
    } finally {
      setExporting(false);
    }
  };

  // Filter donations
  const filteredDonations = donations.filter((donation) => {
    if (filters.anonymous && filters.anonymous !== '') {
      const isAnon = filters.anonymous === 'true';
      if (donation.anonymous !== isAnon) return false;
    }
    if (filters.method && donation.method !== filters.method) return false;
    return true;
  });

  if (loading) {
    return (
      <div className="min-h-screen">
        <Header onLogout={handleLogout} />
        <div className="flex items-center justify-center py-20">
          <div className="text-center">
            <div className="w-10 h-10 border-2 border-royal-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-lg text-gray-400">Loading donations...</p>
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
            <h1 className="text-2xl font-heading font-bold text-white">Donations Report</h1>
            <p className="text-gray-400">Track and manage external donations</p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => setShowAddModal(true)}
              className="btn-primary"
            >
              Add Donation
            </button>
            <button
              onClick={() => navigate('/reports')}
              className="btn-secondary"
            >
              Back to Reports
            </button>
          </div>
        </div>

        {error && (
          <div className="alert-error">
            {error}
            <button onClick={() => setError(null)} className="ml-2 font-bold cursor-pointer">
              &times;
            </button>
          </div>
        )}

        {/* Summary Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="stat-card text-center">
            <p className="text-sm text-gray-400 mb-1">Total Donated</p>
            <p className="text-2xl font-mono font-semibold text-emerald-400">
              {formatCurrency(summary?.total_donated || 0)}
            </p>
          </div>
          <div className="stat-card text-center">
            <p className="text-sm text-gray-400 mb-1">Total Donations</p>
            <p className="text-2xl font-mono font-semibold text-royal-300">{summary?.donation_count || 0}</p>
          </div>
          <div className="stat-card text-center">
            <p className="text-sm text-gray-400 mb-1">Anonymous</p>
            <p className="text-2xl font-mono font-semibold text-gold-400">
              {summary?.anonymous_count || 0}
            </p>
          </div>
          <div className="stat-card text-center">
            <p className="text-sm text-gray-400 mb-1">Average Donation</p>
            <p className="text-2xl font-mono font-semibold text-emerald-400">
              {formatCurrency(
                summary?.donation_count > 0
                  ? summary.total_donated / summary.donation_count
                  : 0
              )}
            </p>
          </div>
        </div>

        {/* Donations by Method */}
        {summary?.by_method && Object.keys(summary.by_method).length > 0 && (
          <Card>
            <h3 className="text-lg font-heading font-bold text-white mb-4">Donations by Method</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {Object.entries(summary.by_method).map(([method, data]: [string, any]) => (
                <div key={method} className="text-center p-3 bg-surface border border-surface-border rounded-lg">
                  <p className="text-sm text-gray-400 capitalize">{method}</p>
                  <p className="text-xl font-mono font-semibold text-white">{data.count}</p>
                  <p className="text-sm font-mono text-emerald-400">{formatCurrency(data.total)}</p>
                </div>
              ))}
            </div>
          </Card>
        )}

        {/* Monthly Trends */}
        {summary?.monthly_trends && summary.monthly_trends.length > 0 && (
          <Card>
            <h3 className="text-lg font-heading font-bold text-white mb-4">Monthly Trends</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full">
                <thead>
                  <tr className="table-header">
                    <th className="table-cell text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                      Month
                    </th>
                    <th className="table-cell text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                      Total
                    </th>
                    <th className="table-cell text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                      Count
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {summary.monthly_trends.map((trend, index) => (
                    <tr key={index} className="table-row">
                      <td className="table-cell whitespace-nowrap text-sm font-medium text-white">
                        {trend.month}
                      </td>
                      <td className="table-cell whitespace-nowrap text-sm font-mono font-semibold text-emerald-400">
                        {formatCurrency(trend.total)}
                      </td>
                      <td className="table-cell whitespace-nowrap text-sm text-gray-400">
                        {trend.count} donations
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        )}

        {/* Filters and Donations List */}
        <Card>
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-4">
            <h3 className="text-lg font-heading font-bold text-white">All Donations</h3>
            <div className="flex flex-wrap gap-3">
              <select
                value={filters.anonymous}
                onChange={(e) => handleFilterChange('anonymous', e.target.value)}
                className="input-field"
              >
                <option value="">All Donors</option>
                <option value="false">Named</option>
                <option value="true">Anonymous</option>
              </select>
              <select
                value={filters.method}
                onChange={(e) => handleFilterChange('method', e.target.value)}
                className="input-field"
              >
                <option value="">All Methods</option>
                <option value="cash">Cash</option>
                <option value="check">Check</option>
                <option value="stripe">Stripe</option>
                <option value="other">Other</option>
              </select>
              <button
                onClick={handleExportCSV}
                disabled={exporting}
                className="btn-secondary disabled:opacity-50"
              >
                {exporting ? 'Exporting...' : 'Export CSV'}
              </button>
            </div>
          </div>

          {filteredDonations.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No donations found. Click "Add Donation" to record your first donation.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full">
                <thead>
                  <tr className="table-header">
                    <th className="table-cell text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                      Date
                    </th>
                    <th className="table-cell text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                      Donor
                    </th>
                    <th className="table-cell text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                      Amount
                    </th>
                    <th className="table-cell text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                      Method
                    </th>
                    <th className="table-cell text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                      Notes
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {filteredDonations.map((donation) => (
                    <tr key={donation.id} className="table-row">
                      <td className="table-cell whitespace-nowrap text-sm text-gray-300">
                        {formatDate(donation.date)}
                      </td>
                      <td className="table-cell whitespace-nowrap">
                        {donation.anonymous ? (
                          <span className="text-sm text-gray-500 italic">Anonymous</span>
                        ) : (
                          <div>
                            <p className="text-sm font-medium text-white">
                              {donation.donor_name || 'Unknown'}
                            </p>
                            {donation.donor_email && (
                              <p className="text-xs text-gray-500">{donation.donor_email}</p>
                            )}
                          </div>
                        )}
                      </td>
                      <td className="table-cell whitespace-nowrap text-sm font-mono font-semibold text-emerald-400">
                        {formatCurrency(donation.amount)}
                      </td>
                      <td className="table-cell whitespace-nowrap">
                        <span className="px-2 py-1 text-xs font-medium rounded-full bg-sigma-800 text-gray-300 capitalize">
                          {donation.method}
                        </span>
                      </td>
                      <td className="table-cell text-sm text-gray-500 max-w-xs truncate">
                        {donation.notes || '-'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      </main>

      {/* Add Donation Modal */}
      {showAddModal && (
        <div className="modal-backdrop">
          <div className="bg-sigma-900 border border-surface-border rounded-2xl shadow-card max-w-md w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-heading font-bold text-white">Add Donation</h3>
                <button
                  onClick={() => setShowAddModal(false)}
                  className="text-gray-500 hover:text-gray-300"
                >
                  <span className="text-2xl">&times;</span>
                </button>
              </div>

              <form onSubmit={handleAddDonation} className="space-y-4">
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="anonymous"
                    checked={newDonation.anonymous}
                    onChange={(e) =>
                      setNewDonation((prev) => ({ ...prev, anonymous: e.target.checked }))
                    }
                    className="h-4 w-4 rounded border-surface-border bg-sigma-800 text-royal-600 focus:ring-royal-500"
                  />
                  <label htmlFor="anonymous" className="ml-2 text-sm text-gray-300">
                    Anonymous donation
                  </label>
                </div>

                {!newDonation.anonymous && (
                  <>
                    <div>
                      <label className="input-label">
                        Donor Name
                      </label>
                      <input
                        type="text"
                        value={newDonation.donor_name}
                        onChange={(e) =>
                          setNewDonation((prev) => ({ ...prev, donor_name: e.target.value }))
                        }
                        className="input-field w-full"
                        placeholder="John Doe"
                      />
                    </div>
                    <div>
                      <label className="input-label">
                        Donor Email (optional)
                      </label>
                      <input
                        type="email"
                        value={newDonation.donor_email}
                        onChange={(e) =>
                          setNewDonation((prev) => ({ ...prev, donor_email: e.target.value }))
                        }
                        className="input-field w-full"
                        placeholder="john@example.com"
                      />
                    </div>
                  </>
                )}

                <div>
                  <label className="input-label">
                    Amount *
                  </label>
                  <div className="relative">
                    <span className="absolute left-3 top-2 text-gray-500">$</span>
                    <input
                      type="number"
                      step="0.01"
                      min="0.01"
                      value={newDonation.amount}
                      onChange={(e) =>
                        setNewDonation((prev) => ({ ...prev, amount: e.target.value }))
                      }
                      className="input-field w-full pl-7"
                      placeholder="0.00"
                      required
                    />
                  </div>
                </div>

                <div>
                  <label className="input-label">
                    Payment Method
                  </label>
                  <select
                    value={newDonation.method}
                    onChange={(e) =>
                      setNewDonation((prev) => ({ ...prev, method: e.target.value }))
                    }
                    className="input-field w-full"
                  >
                    <option value="cash">Cash</option>
                    <option value="check">Check</option>
                    <option value="stripe">Stripe</option>
                    <option value="other">Other</option>
                  </select>
                </div>

                <div>
                  <label className="input-label">
                    Notes (optional)
                  </label>
                  <textarea
                    value={newDonation.notes}
                    onChange={(e) =>
                      setNewDonation((prev) => ({ ...prev, notes: e.target.value }))
                    }
                    rows={3}
                    className="input-field w-full"
                    placeholder="Any additional notes..."
                  />
                </div>

                <div className="flex gap-3 pt-2">
                  <button
                    type="submit"
                    disabled={addingDonation}
                    className="btn-primary flex-1 disabled:opacity-50"
                  >
                    {addingDonation ? 'Adding...' : 'Add Donation'}
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowAddModal(false)}
                    className="btn-secondary"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Donations;
