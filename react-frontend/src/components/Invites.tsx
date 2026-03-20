import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import useAuthStore from '../stores/authStore';
import { invitesAPI } from '../services/api';
import Header from './Header';
import Card from './Card';
import { formatDate } from '../utils/formatters';

function Invites() {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const [invites, setInvites] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  // Filter state
  const [statusFilter, setStatusFilter] = useState('');

  // Create invite modal state
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [creating, setCreating] = useState(false);
  const [newInvite, setNewInvite] = useState({
    email: '',
    role: 'member',
    expires_in_days: 7,
  });

  // Created invite display
  const [createdInvite, setCreatedInvite] = useState(null);

  useEffect(() => {
    // Check if user has report access (can create invites)
    const hasReportAccess = ['admin', 'treasurer', 'president', 'vice_1', 'vice_2', 'secretary'].includes(user?.role);
    if (user && !hasReportAccess) {
      navigate('/dashboard');
      return;
    }

    fetchData();
  }, [user, navigate, statusFilter]);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      const params: any = {};
      if (statusFilter) params.status = statusFilter;

      const [invitesData, statsData] = await Promise.all([
        invitesAPI.getInvites(params),
        invitesAPI.getStats(),
      ]);

      setInvites(invitesData.invites);
      setStats(statsData.stats);
    } catch (err: any) {
      if (err.response?.status === 403) {
        navigate('/dashboard');
      } else {
        setError(err.response?.data?.error || 'Failed to load invites');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const handleCreateInvite = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    try {
      setCreating(true);
      const response = await invitesAPI.createInvite(newInvite as any);

      setCreatedInvite(response.invite);
      setSuccess(response.message);

      // Reset form
      setNewInvite({
        email: '',
        role: 'member',
        expires_in_days: 7,
      });

      // Refresh data
      await fetchData();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to create invite');
    } finally {
      setCreating(false);
    }
  };

  const handleDeleteInvite = async (inviteId) => {
    if (!confirm('Are you sure you want to delete this invite code?')) return;

    try {
      setError(null);
      await invitesAPI.deleteInvite(inviteId);
      setSuccess('Invite code deleted');
      await fetchData();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to delete invite');
    }
  };

  const handleCopyCode = (code) => {
    navigator.clipboard.writeText(code);
    setSuccess('Code copied to clipboard!');
    setTimeout(() => setSuccess(null), 2000);
  };

  const getStatusBadge = (invite) => {
    if (invite.used) {
      return (
        <span className="px-2 py-1 text-xs font-medium rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
          Used
        </span>
      );
    }
    if (invite.is_expired) {
      return (
        <span className="px-2 py-1 text-xs font-medium rounded-full bg-rose-500/10 text-rose-400 border border-rose-500/20">
          Expired
        </span>
      );
    }
    return (
      <span className="px-2 py-1 text-xs font-medium rounded-full bg-royal-500/10 text-royal-300 border border-royal-500/20">
        Available
      </span>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen">
        <Header onLogout={handleLogout} />
        <div className="flex items-center justify-center py-20">
          <div className="text-center">
            <div className="w-10 h-10 border-2 border-royal-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-lg text-gray-400">Loading invites...</p>
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
            <h1 className="text-2xl font-heading font-bold text-white">Invite Codes</h1>
            <p className="text-gray-400">Generate and manage member invite codes</p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => {
                setShowCreateModal(true);
                setCreatedInvite(null);
              }}
              className="btn-primary"
            >
              Create Invite
            </button>
            <button
              onClick={() => navigate('/treasurer')}
              className="btn-secondary"
            >
              Back to Treasurer
            </button>
          </div>
        </div>

        {/* Alerts */}
        {error && (
          <div className="alert-error">
            {error}
            <button onClick={() => setError(null)} className="ml-2 font-bold cursor-pointer">
              &times;
            </button>
          </div>
        )}
        {success && (
          <div className="alert-success">
            {success}
            <button onClick={() => setSuccess(null)} className="ml-2 font-bold cursor-pointer">
              &times;
            </button>
          </div>
        )}

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="stat-card text-center">
            <p className="text-sm text-gray-400 mb-1">Total Created</p>
            <p className="text-2xl font-mono font-semibold text-white">{stats?.total || 0}</p>
          </div>
          <div className="stat-card text-center">
            <p className="text-sm text-gray-400 mb-1">Used</p>
            <p className="text-2xl font-mono font-semibold text-emerald-400">{stats?.used || 0}</p>
          </div>
          <div className="stat-card text-center">
            <p className="text-sm text-gray-400 mb-1">Available</p>
            <p className="text-2xl font-mono font-semibold text-royal-300">{stats?.unused || 0}</p>
          </div>
          <div className="stat-card text-center">
            <p className="text-sm text-gray-400 mb-1">Expired</p>
            <p className="text-2xl font-mono font-semibold text-rose-400">{stats?.expired || 0}</p>
          </div>
        </div>

        {/* Invites List */}
        <Card>
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-4">
            <h3 className="text-lg font-heading font-bold text-white">All Invite Codes</h3>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="input-field"
            >
              <option value="">All Status</option>
              <option value="unused">Available</option>
              <option value="used">Used</option>
              <option value="expired">Expired</option>
            </select>
          </div>

          {invites.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No invite codes found. Click "Create Invite" to generate one.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full">
                <thead>
                  <tr className="table-header">
                    <th className="table-cell text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                      Code
                    </th>
                    <th className="table-cell text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                      Role
                    </th>
                    <th className="table-cell text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="table-cell text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                      Created
                    </th>
                    <th className="table-cell text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                      Expires
                    </th>
                    <th className="table-cell text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                      Used By
                    </th>
                    <th className="table-cell text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {invites.map((invite) => (
                    <tr key={invite.id} className="table-row">
                      <td className="table-cell whitespace-nowrap">
                        <div className="flex items-center gap-2">
                          <code className="font-mono text-sm bg-sigma-800 px-2 py-1 rounded text-royal-300">
                            {invite.code}
                          </code>
                          {!invite.used && !invite.is_expired && (
                            <button
                              onClick={() => handleCopyCode(invite.code)}
                              className="text-gray-500 hover:text-royal-400"
                              title="Copy code"
                            >
                              <svg
                                className="w-4 h-4"
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                              >
                                <path
                                  strokeLinecap="round"
                                  strokeLinejoin="round"
                                  strokeWidth={2}
                                  d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
                                />
                              </svg>
                            </button>
                          )}
                        </div>
                      </td>
                      <td className="table-cell whitespace-nowrap">
                        <span className="text-sm text-gray-300 capitalize">{invite.role}</span>
                      </td>
                      <td className="table-cell whitespace-nowrap">{getStatusBadge(invite)}</td>
                      <td className="table-cell whitespace-nowrap text-sm text-gray-400">
                        {invite.created_at ? formatDate(invite.created_at) : '-'}
                        {invite.created_by && (
                          <span className="block text-xs text-gray-500">
                            by {invite.created_by}
                          </span>
                        )}
                      </td>
                      <td className="table-cell whitespace-nowrap text-sm text-gray-400">
                        {invite.expires_at ? formatDate(invite.expires_at) : 'Never'}
                      </td>
                      <td className="table-cell whitespace-nowrap text-sm text-gray-400">
                        {invite.used_by || '-'}
                        {invite.used_at && (
                          <span className="block text-xs text-gray-500">
                            {formatDate(invite.used_at)}
                          </span>
                        )}
                      </td>
                      <td className="table-cell whitespace-nowrap text-sm">
                        {!invite.used && (
                          <button
                            onClick={() => handleDeleteInvite(invite.id)}
                            className="text-rose-400 hover:text-rose-300 font-medium"
                          >
                            Delete
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      </main>

      {/* Create Invite Modal */}
      {showCreateModal && (
        <div className="modal-backdrop">
          <div className="bg-sigma-900 border border-surface-border rounded-2xl shadow-card max-w-md w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-heading font-bold text-white">Create Invite Code</h3>
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="text-gray-500 hover:text-gray-300"
                >
                  <span className="text-2xl">&times;</span>
                </button>
              </div>

              {createdInvite ? (
                <div className="space-y-4">
                  <div className="p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-lg text-center">
                    <p className="text-sm text-emerald-400 mb-2">Invite code created!</p>
                    <code className="text-2xl font-mono font-bold text-emerald-300 block mb-3">
                      {createdInvite.code}
                    </code>
                    <button
                      onClick={() => handleCopyCode(createdInvite.code)}
                      className="btn-primary text-sm"
                    >
                      Copy Code
                    </button>
                  </div>
                  <p className="text-sm text-gray-400 text-center">
                    Role: <span className="font-medium text-gray-300 capitalize">{createdInvite.role}</span>
                    <br />
                    Expires: {createdInvite.expires_at ? formatDate(createdInvite.expires_at) : 'Never'}
                  </p>
                  <button
                    onClick={() => {
                      setCreatedInvite(null);
                      setShowCreateModal(false);
                    }}
                    className="btn-secondary w-full"
                  >
                    Done
                  </button>
                </div>
              ) : (
                <form onSubmit={handleCreateInvite} className="space-y-4">
                  <div>
                    <label className="input-label">
                      Email (optional)
                    </label>
                    <input
                      type="email"
                      value={newInvite.email}
                      onChange={(e) =>
                        setNewInvite((prev) => ({ ...prev, email: e.target.value }))
                      }
                      className="input-field w-full"
                      placeholder="Send invite to this email"
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      Leave blank to just generate a code without sending
                    </p>
                  </div>

                  <div>
                    <label className="input-label">Role</label>
                    <select
                      value={newInvite.role}
                      onChange={(e) =>
                        setNewInvite((prev) => ({ ...prev, role: e.target.value }))
                      }
                      className="input-field w-full"
                    >
                      <option value="member">Member</option>
                      <option value="treasurer">Treasurer</option>
                      <option value="admin">Admin</option>
                      <option value="president">President</option>
                      <option value="vice_1">1st Vice President</option>
                      <option value="vice_2">2nd Vice President</option>
                      <option value="secretary">Secretary</option>
                    </select>
                  </div>

                  <div>
                    <label className="input-label">
                      Expires In (days)
                    </label>
                    <select
                      value={newInvite.expires_in_days}
                      onChange={(e) =>
                        setNewInvite((prev) => ({
                          ...prev,
                          expires_in_days: parseInt(e.target.value),
                        }))
                      }
                      className="input-field w-full"
                    >
                      <option value={1}>1 day</option>
                      <option value={3}>3 days</option>
                      <option value={7}>7 days</option>
                      <option value={14}>14 days</option>
                      <option value={30}>30 days</option>
                      <option value={90}>90 days</option>
                    </select>
                  </div>

                  <div className="flex gap-3 pt-2">
                    <button
                      type="submit"
                      disabled={creating}
                      className="btn-primary flex-1 disabled:opacity-50"
                    >
                      {creating ? 'Creating...' : 'Create Invite'}
                    </button>
                    <button
                      type="button"
                      onClick={() => setShowCreateModal(false)}
                      className="btn-secondary"
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Invites;
