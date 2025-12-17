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
        <span className="px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-700">
          Used
        </span>
      );
    }
    if (invite.is_expired) {
      return (
        <span className="px-2 py-1 text-xs font-medium rounded-full bg-red-100 text-red-700">
          Expired
        </span>
      );
    }
    return (
      <span className="px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-700">
        Available
      </span>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header onLogout={handleLogout} />
        <div className="flex items-center justify-center py-20">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
            <p className="text-lg text-gray-600">Loading invites...</p>
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
            <h1 className="text-2xl font-bold text-gray-900">Invite Codes</h1>
            <p className="text-gray-600">Generate and manage member invite codes</p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => {
                setShowCreateModal(true);
                setCreatedInvite(null);
              }}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Create Invite
            </button>
            <button
              onClick={() => navigate('/treasurer')}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Back to Treasurer
            </button>
          </div>
        </div>

        {/* Alerts */}
        {error && (
          <div className="p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg">
            {error}
            <button onClick={() => setError(null)} className="ml-2 font-bold">
              &times;
            </button>
          </div>
        )}
        {success && (
          <div className="p-4 bg-green-100 border border-green-400 text-green-700 rounded-lg">
            {success}
            <button onClick={() => setSuccess(null)} className="ml-2 font-bold">
              &times;
            </button>
          </div>
        )}

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card>
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-1">Total Created</p>
              <p className="text-2xl font-bold text-gray-900">{stats?.total || 0}</p>
            </div>
          </Card>
          <Card>
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-1">Used</p>
              <p className="text-2xl font-bold text-green-600">{stats?.used || 0}</p>
            </div>
          </Card>
          <Card>
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-1">Available</p>
              <p className="text-2xl font-bold text-blue-600">{stats?.unused || 0}</p>
            </div>
          </Card>
          <Card>
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-1">Expired</p>
              <p className="text-2xl font-bold text-red-600">{stats?.expired || 0}</p>
            </div>
          </Card>
        </div>

        {/* Invites List */}
        <Card>
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-4">
            <h3 className="text-lg font-bold text-gray-900">All Invite Codes</h3>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
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
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Code
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Role
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Created
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Expires
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Used By
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {invites.map((invite) => (
                    <tr key={invite.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center gap-2">
                          <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">
                            {invite.code}
                          </code>
                          {!invite.used && !invite.is_expired && (
                            <button
                              onClick={() => handleCopyCode(invite.code)}
                              className="text-gray-400 hover:text-blue-600"
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
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm text-gray-900 capitalize">{invite.role}</span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">{getStatusBadge(invite)}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {invite.created_at ? formatDate(invite.created_at) : '-'}
                        {invite.created_by && (
                          <span className="block text-xs text-gray-400">
                            by {invite.created_by}
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {invite.expires_at ? formatDate(invite.expires_at) : 'Never'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {invite.used_by || '-'}
                        {invite.used_at && (
                          <span className="block text-xs text-gray-400">
                            {formatDate(invite.used_at)}
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        {!invite.used && (
                          <button
                            onClick={() => handleDeleteInvite(invite.id)}
                            className="text-red-600 hover:text-red-800 font-medium"
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
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold text-gray-900">Create Invite Code</h3>
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <span className="text-2xl">&times;</span>
                </button>
              </div>

              {createdInvite ? (
                <div className="space-y-4">
                  <div className="p-4 bg-green-50 border border-green-200 rounded-lg text-center">
                    <p className="text-sm text-green-700 mb-2">Invite code created!</p>
                    <code className="text-2xl font-mono font-bold text-green-800 block mb-3">
                      {createdInvite.code}
                    </code>
                    <button
                      onClick={() => handleCopyCode(createdInvite.code)}
                      className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm"
                    >
                      Copy Code
                    </button>
                  </div>
                  <p className="text-sm text-gray-600 text-center">
                    Role: <span className="font-medium capitalize">{createdInvite.role}</span>
                    <br />
                    Expires: {createdInvite.expires_at ? formatDate(createdInvite.expires_at) : 'Never'}
                  </p>
                  <button
                    onClick={() => {
                      setCreatedInvite(null);
                      setShowCreateModal(false);
                    }}
                    className="w-full px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    Done
                  </button>
                </div>
              ) : (
                <form onSubmit={handleCreateInvite} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Email (optional)
                    </label>
                    <input
                      type="email"
                      value={newInvite.email}
                      onChange={(e) =>
                        setNewInvite((prev) => ({ ...prev, email: e.target.value }))
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Send invite to this email"
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      Leave blank to just generate a code without sending
                    </p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Role</label>
                    <select
                      value={newInvite.role}
                      onChange={(e) =>
                        setNewInvite((prev) => ({ ...prev, role: e.target.value }))
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
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
                    <label className="block text-sm font-medium text-gray-700 mb-1">
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
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
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
                      className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium disabled:opacity-50"
                    >
                      {creating ? 'Creating...' : 'Create Invite'}
                    </button>
                    <button
                      type="button"
                      onClick={() => setShowCreateModal(false)}
                      className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
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
