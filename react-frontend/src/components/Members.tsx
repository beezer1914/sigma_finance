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
      <div className="min-h-screen">
        <Header onLogout={handleLogout} />
        <div className="flex items-center justify-center py-20">
          <div className="text-center">
            <div className="w-10 h-10 border-2 border-royal-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-gray-400">Loading members...</p>
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
            <h1 className="font-heading">Members</h1>
            <p className="text-gray-400 mt-1">
              {pagination.total} total members
            </p>
          </div>
          <div className="flex items-center gap-3">
            {delinquentCount > 0 && (
              <button
                onClick={handleShowDelinquent}
                className="px-4 py-2 text-sm font-medium text-rose-300 bg-rose-500/10 border border-rose-500/20 rounded-lg hover:bg-rose-500/20 transition-colors flex items-center gap-2"
              >
                <span>Delinquent</span>
                <span className="bg-rose-600 text-white px-2 py-0.5 rounded-full text-xs">
                  {delinquentCount}
                </span>
              </button>
            )}
            <button
              onClick={() => navigate('/treasurer')}
              className="btn-secondary text-sm"
            >
              Back to Treasurer
            </button>
          </div>
        </div>

        {/* Filter Bar */}
        <Card>
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <label className="input-label">
                Search Members
              </label>
              <input
                type="text"
                placeholder="Search by name or email..."
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
                className="input-field"
              />
            </div>
            <div className="flex-1">
              <label className="input-label">
                Financial Status
              </label>
              <select
                value={filters.status}
                onChange={(e) => setFilters({ ...filters, status: e.target.value })}
                className="input-field"
              >
                <option value="all">All Members</option>
                <option value="financial">Financial</option>
                <option value="not financial">Not Financial</option>
                <option value="neophyte">Neophyte</option>
              </select>
            </div>
            <div className="flex-1">
              <label className="input-label">
                Payment Plan
              </label>
              <select
                value={filters.hasPlan}
                onChange={(e) => setFilters({ ...filters, hasPlan: e.target.value })}
                className="input-field"
              >
                <option value="all">All</option>
                <option value="active">Active Plan</option>
                <option value="none">No Plan</option>
              </select>
            </div>
            <div className="flex items-end">
              <button
                onClick={handleClearFilters}
                className="px-4 py-2.5 text-sm font-medium text-gray-400 hover:text-white transition-colors"
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

        {/* Members Table */}
        <Card>
          {members.length > 0 ? (
            <>
              <div className="overflow-x-auto -mx-6 sm:mx-0">
                <div className="inline-block min-w-full align-middle">
                  <table className="min-w-full">
                    <thead className="table-header">
                      <tr>
                        <th className="px-5 py-3.5 text-left">
                          Name
                        </th>
                        <th className="px-5 py-3.5 text-left">
                          Email
                        </th>
                        <th className="px-5 py-3.5 text-left">
                          Status
                        </th>
                        <th className="px-5 py-3.5 text-left">
                          Total Paid
                        </th>
                        <th className="px-5 py-3.5 text-left">
                          Plan
                        </th>
                        <th className="px-5 py-3.5 text-left">
                          Balance
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {members.map((member) => (
                        <tr
                          key={member.id}
                          onClick={() => setSelectedMemberId(member.id)}
                          className={`table-row cursor-pointer ${
                            isDelinquent(member) ? 'bg-rose-500/10 border-l-4 border-l-rose-500' : ''
                          }`}
                        >
                          <td className="table-cell whitespace-nowrap">
                            <div className="font-medium text-white">{member.name}</div>
                            <div className="text-xs text-gray-500 capitalize">{member.role}</div>
                          </td>
                          <td className="table-cell whitespace-nowrap">
                            {member.email}
                          </td>
                          <td className="table-cell whitespace-nowrap">
                            {member.is_neophyte ? (
                              <span className="badge-neophyte">
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
                          <td className="table-cell whitespace-nowrap font-mono font-semibold text-white">
                            {formatCurrency(member.total_paid)}
                          </td>
                          <td className="table-cell whitespace-nowrap">
                            {member.has_active_plan ? (
                              <span className="badge-info">
                                Active
                              </span>
                            ) : (
                              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-500/15 text-gray-400 border border-gray-500/20">
                                None
                              </span>
                            )}
                          </td>
                          <td className="table-cell whitespace-nowrap">
                            {member.has_active_plan ? (
                              <span className="font-mono font-semibold text-rose-400">
                                {formatCurrency(member.plan_balance)}
                              </span>
                            ) : (
                              <span className="text-gray-500">-</span>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Pagination */}
              <div className="mt-4 flex items-center justify-between border-t border-surface-border pt-4">
                <p className="text-sm text-gray-400">
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
                        ? 'opacity-50 cursor-not-allowed border border-surface-border text-gray-500'
                        : 'border border-surface-border text-gray-300 hover:bg-surface-hover'
                    }`}
                  >
                    Previous
                  </button>
                  <button
                    onClick={handleNextPage}
                    disabled={!pagination.hasMore}
                    className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
                      !pagination.hasMore
                        ? 'opacity-50 cursor-not-allowed border border-surface-border text-gray-500'
                        : 'border border-surface-border text-gray-300 hover:bg-surface-hover'
                    }`}
                  >
                    Next
                  </button>
                </div>
              </div>
            </>
          ) : (
            <div className="text-center py-12">
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-royal-600/20 flex items-center justify-center">
                <svg className="w-8 h-8 text-royal-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-white mb-2">No Members Found</h3>
              <p className="text-gray-400">
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
