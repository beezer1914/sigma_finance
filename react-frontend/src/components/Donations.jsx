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
      <div className="min-h-screen bg-gray-50">
        <Header onLogout={handleLogout} />
        <div className="flex items-center justify-center py-20">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
            <p className="text-lg text-gray-600">Loading donations...</p>
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
            <h1 className="text-2xl font-bold text-gray-900">Donations Report</h1>
            <p className="text-gray-600">Track and manage external donations</p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => setShowAddModal(true)}
              className="px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-lg hover:bg-green-700 transition-colors"
            >
              Add Donation
            </button>
            <button
              onClick={() => navigate('/reports')}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Back to Reports
            </button>
          </div>
        </div>

        {error && (
          <div className="p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg">
            {error}
            <button onClick={() => setError(null)} className="ml-2 font-bold">
              &times;
            </button>
          </div>
        )}

        {/* Summary Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card>
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-1">Total Donated</p>
              <p className="text-2xl font-bold text-green-600">
                {formatCurrency(summary?.total_donated || 0)}
              </p>
            </div>
          </Card>
          <Card>
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-1">Total Donations</p>
              <p className="text-2xl font-bold text-blue-600">{summary?.donation_count || 0}</p>
            </div>
          </Card>
          <Card>
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-1">Anonymous</p>
              <p className="text-2xl font-bold text-purple-600">
                {summary?.anonymous_count || 0}
              </p>
            </div>
          </Card>
          <Card>
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-1">Average Donation</p>
              <p className="text-2xl font-bold text-orange-600">
                {formatCurrency(
                  summary?.donation_count > 0
                    ? summary.total_donated / summary.donation_count
                    : 0
                )}
              </p>
            </div>
          </Card>
        </div>

        {/* Donations by Method */}
        {summary?.by_method && Object.keys(summary.by_method).length > 0 && (
          <Card>
            <h3 className="text-lg font-bold text-gray-900 mb-4">Donations by Method</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {Object.entries(summary.by_method).map(([method, data]) => (
                <div key={method} className="text-center p-3 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-600 capitalize">{method}</p>
                  <p className="text-xl font-bold text-gray-900">{data.count}</p>
                  <p className="text-sm text-green-600">{formatCurrency(data.total)}</p>
                </div>
              ))}
            </div>
          </Card>
        )}

        {/* Monthly Trends */}
        {summary?.monthly_trends && summary.monthly_trends.length > 0 && (
          <Card>
            <h3 className="text-lg font-bold text-gray-900 mb-4">Monthly Trends</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Month
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Total
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Count
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {summary.monthly_trends.map((trend, index) => (
                    <tr key={index} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {trend.month}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-green-600 font-medium">
                        {formatCurrency(trend.total)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
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
            <h3 className="text-lg font-bold text-gray-900">All Donations</h3>
            <div className="flex flex-wrap gap-3">
              <select
                value={filters.anonymous}
                onChange={(e) => handleFilterChange('anonymous', e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Donors</option>
                <option value="false">Named</option>
                <option value="true">Anonymous</option>
              </select>
              <select
                value={filters.method}
                onChange={(e) => handleFilterChange('method', e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
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
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
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
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Date
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Donor
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Amount
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Method
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Notes
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {filteredDonations.map((donation) => (
                    <tr key={donation.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {formatDate(donation.date)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {donation.anonymous ? (
                          <span className="text-sm text-gray-500 italic">Anonymous</span>
                        ) : (
                          <div>
                            <p className="text-sm font-medium text-gray-900">
                              {donation.donor_name || 'Unknown'}
                            </p>
                            {donation.donor_email && (
                              <p className="text-xs text-gray-500">{donation.donor_email}</p>
                            )}
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-green-600">
                        {formatCurrency(donation.amount)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-700 capitalize">
                          {donation.method}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">
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
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold text-gray-900">Add Donation</h3>
                <button
                  onClick={() => setShowAddModal(false)}
                  className="text-gray-400 hover:text-gray-600"
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
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label htmlFor="anonymous" className="ml-2 text-sm text-gray-700">
                    Anonymous donation
                  </label>
                </div>

                {!newDonation.anonymous && (
                  <>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Donor Name
                      </label>
                      <input
                        type="text"
                        value={newDonation.donor_name}
                        onChange={(e) =>
                          setNewDonation((prev) => ({ ...prev, donor_name: e.target.value }))
                        }
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="John Doe"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Donor Email (optional)
                      </label>
                      <input
                        type="email"
                        value={newDonation.donor_email}
                        onChange={(e) =>
                          setNewDonation((prev) => ({ ...prev, donor_email: e.target.value }))
                        }
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="john@example.com"
                      />
                    </div>
                  </>
                )}

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
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
                      className="w-full pl-7 pr-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="0.00"
                      required
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Payment Method
                  </label>
                  <select
                    value={newDonation.method}
                    onChange={(e) =>
                      setNewDonation((prev) => ({ ...prev, method: e.target.value }))
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="cash">Cash</option>
                    <option value="check">Check</option>
                    <option value="stripe">Stripe</option>
                    <option value="other">Other</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Notes (optional)
                  </label>
                  <textarea
                    value={newDonation.notes}
                    onChange={(e) =>
                      setNewDonation((prev) => ({ ...prev, notes: e.target.value }))
                    }
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Any additional notes..."
                  />
                </div>

                <div className="flex gap-3 pt-2">
                  <button
                    type="submit"
                    disabled={addingDonation}
                    className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium disabled:opacity-50"
                  >
                    {addingDonation ? 'Adding...' : 'Add Donation'}
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowAddModal(false)}
                    className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
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
