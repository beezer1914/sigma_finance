import { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import useAuthStore from '../stores/authStore';
import { treasurerAPI } from '../services/api';
import type { User } from '../types';
import Header from './Header';
import Card from './Card';
import MemberDetailModal from './MemberDetailModal';
import { formatCurrency, getStatusColor } from '../utils/formatters';

function Members() {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const [members, setMembers] = useState<User[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [pagination, setPagination] = useState({
    total: 0,
    limit: 20,
    offset: 0,
    hasMore: false,
  });

  // Filter state
  const [filters, setFilters] = useState({
    search: '',
    status: 'all',
    hasPlan: 'all',
  });

  // Debounced search
  const [searchInput, setSearchInput] = useState('');

  // Member detail modal
  const [selectedMemberId, setSelectedMemberId] = useState(null);

  const fetchMembers = useCallback(async (offset = 0) => {
    try {
      setLoading(true);
      const params = {
        limit: pagination.limit,
        offset,
        ...(filters.search && { search: filters.search }),
        ...(filters.status !== 'all' && { status: filters.status }),
        ...(filters.hasPlan !== 'all' && { has_plan: filters.hasPlan }),
      };

      const data: any = await treasurerAPI.getMembers(params);
      setMembers(data.members);
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
        setError(err.response?.data?.error || 'Failed to load members');
      }
    } finally {
      setLoading(false);
    }
  }, [filters, pagination.limit, navigate]);

  useEffect(() => {
    // Check if user has full access (treasurer, admin, president, vice_1)
    const hasFullAccess = ['admin', 'treasurer', 'president', 'vice_1'].includes(user?.role);
    if (user && !hasFullAccess) {
      navigate('/dashboard');
      return;
    }

    fetchMembers(0);
  }, [user, navigate, filters]);

  // Debounce search input
  useEffect(() => {
    const timer = setTimeout(() => {
      setFilters((prev) => ({ ...prev, search: searchInput }));
    }, 300);

    return () => clearTimeout(timer);
  }, [searchInput]);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const handlePrevPage = () => {
    const newOffset = Math.max(0, pagination.offset - pagination.limit);
    fetchMembers(newOffset);
  };

  const handleNextPage = () => {
    if (pagination.hasMore) {
      fetchMembers(pagination.offset + pagination.limit);
    }
  };

  const handleClearFilters = () => {
    setSearchInput('');
    setFilters({ search: '', status: 'all', hasPlan: 'all' });
  };

  const handleShowDelinquent = () => {
    setSearchInput('');
    setFilters({ search: '', status: 'not financial', hasPlan: 'none' });
  };

  // Check if member is delinquent (not financial + no active plan + not a neophyte)
  const isDelinquent = (member) => {
    // Neophytes are exempt from dues, never delinquent
    if (member.is_neophyte || member.financial_status === 'neophyte') {
      return false;
    }
    return member.financial_status === 'not financial' && !member.has_active_plan;
  };

  // Count delinquent members on current page
  const delinquentCount = members.filter(isDelinquent).length;

  if (loading && members.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header onLogout={handleLogout} />
        <div className="flex items-center justify-center py-20">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
            <p className="text-lg text-gray-600">Loading members...</p>
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
            <h1 className="text-2xl font-bold text-gray-900">Members</h1>
            <p className="text-gray-600">
              {pagination.total} total members
            </p>
          </div>
          <div className="flex items-center gap-3">
            {delinquentCount > 0 && (
              <button
                onClick={handleShowDelinquent}
                className="px-4 py-2 text-sm font-medium text-red-700 bg-red-100 border border-red-300 rounded-lg hover:bg-red-200 transition-colors flex items-center gap-2"
              >
                <span>Delinquent</span>
                <span className="bg-red-600 text-white px-2 py-0.5 rounded-full text-xs">
                  {delinquentCount}
                </span>
              </button>
            )}
            <button
              onClick={() => navigate('/treasurer')}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Back to Treasurer
            </button>
          </div>
        </div>

        {/* Filter Bar */}
        <Card>
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Search Members
              </label>
              <input
                type="text"
                placeholder="Search by name or email..."
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Financial Status
              </label>
              <select
                value={filters.status}
                onChange={(e) => setFilters({ ...filters, status: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Members</option>
                <option value="financial">Financial</option>
                <option value="not financial">Not Financial</option>
                <option value="neophyte">Neophyte</option>
              </select>
            </div>
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Payment Plan
              </label>
              <select
                value={filters.hasPlan}
                onChange={(e) => setFilters({ ...filters, hasPlan: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All</option>
                <option value="active">Active Plan</option>
                <option value="none">No Plan</option>
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

        {/* Members Table */}
        <Card>
          {members.length > 0 ? (
            <>
              <div className="overflow-x-auto -mx-6 sm:mx-0">
                <div className="inline-block min-w-full align-middle">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Name
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Email
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Status
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Total Paid
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Plan
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Balance
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {members.map((member) => (
                        <tr
                          key={member.id}
                          onClick={() => setSelectedMemberId(member.id)}
                          className={`hover:bg-gray-50 transition-colors cursor-pointer ${
                            isDelinquent(member) ? 'bg-red-50 border-l-4 border-l-red-500' : ''
                          }`}
                        >
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="font-medium text-gray-900">{member.name}</div>
                            <div className="text-sm text-gray-500 capitalize">{member.role}</div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                            {member.email}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            {member.is_neophyte ? (
                              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                Neophyte (Exempt)
                              </span>
                            ) : (
                              <span
                                className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(
                                  member.financial_status
                                )}`}
                              >
                                {member.financial_status || 'Not Set'}
                              </span>
                            )}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            {formatCurrency(member.total_paid)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            {member.has_active_plan ? (
                              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                Active
                              </span>
                            ) : (
                              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-600">
                                None
                              </span>
                            )}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm">
                            {member.has_active_plan ? (
                              <span className="font-medium text-red-600">
                                {formatCurrency(member.plan_balance)}
                              </span>
                            ) : (
                              <span className="text-gray-400">-</span>
                            )}
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
                  {pagination.total} members
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
              <div className="text-5xl mb-4">👥</div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No Members Found</h3>
              <p className="text-gray-600">
                {filters.search || filters.status !== 'all' || filters.hasPlan !== 'all'
                  ? 'No members match your current filters.'
                  : 'No members in the system yet.'}
              </p>
            </div>
          )}
        </Card>
      </main>

      {/* Member Detail Modal */}
      {selectedMemberId && (
        <MemberDetailModal
          memberId={selectedMemberId}
          onClose={() => setSelectedMemberId(null)}
          onUpdate={() => fetchMembers(pagination.offset)}
        />
      )}
    </div>
  );
}

export default Members;
