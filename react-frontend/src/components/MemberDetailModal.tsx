import { useEffect, useState } from 'react';
import { treasurerAPI } from '../services/api';
import { formatCurrency, formatDate, getStatusColor } from '../utils/formatters';

function MemberDetailModal({ memberId, onClose, onUpdate, canEdit = true }) {
  const [member, setMember] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isEditMode, setIsEditMode] = useState(false);
  const [saving, setSaving] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  // Form state for editing
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    role: '',
    active: true,
    financial_status: '',
    initiation_date: '',
  });

  useEffect(() => {
    const fetchMemberDetail = async () => {
      try {
        setLoading(true);
        const data: any = await treasurerAPI.getMemberDetail(memberId);
        setMember(data);
        // Initialize form data with member details
        setFormData({
          name: data.user?.name || '',
          email: data.user?.email || '',
          role: data.user?.role || '',
          active: data.user?.active ?? true,
          financial_status: data.user?.financial_status || '',
          initiation_date: data.user?.initiation_date || '',
        });
      } catch (err: any) {
        setError(err.response?.data?.error || 'Failed to load member details');
      } finally {
        setLoading(false);
      }
    };

    if (memberId) {
      fetchMemberDetail();
    }
  }, [memberId]);

  const handleEdit = () => {
    setIsEditMode(true);
    setError(null);
    setSuccessMessage('');
  };

  const handleCancelEdit = () => {
    setIsEditMode(false);
    setError(null);
    setSuccessMessage('');
    // Reset form data to original member data
    setFormData({
      name: (member as any)?.user?.name || '',
      email: (member as any)?.user?.email || '',
      role: (member as any)?.user?.role || '',
      active: (member as any)?.user?.active ?? true,
      financial_status: (member as any)?.user?.financial_status || '',
      initiation_date: (member as any)?.user?.initiation_date || '',
    });
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      setError(null);
      const updatedData: any = await treasurerAPI.updateMember(memberId, formData as any);
      setMember({ ...member, user: updatedData.user });
      setSuccessMessage('Member updated successfully!');
      setIsEditMode(false);
      // Call onUpdate callback if provided to refresh parent component
      if (onUpdate) {
        onUpdate();
      }
      // Clear success message after 3 seconds
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to update member');
    } finally {
      setSaving(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value,
    });
  };

  // Close on escape key
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape') onClose();
    };
    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [onClose]);

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Backdrop */}
      <div
        className="modal-backdrop"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="fixed inset-0 z-50 flex min-h-full items-center justify-center p-4 pointer-events-none">
        <div className="relative bg-sigma-900 border border-surface-border rounded-xl shadow-xl max-w-3xl w-full max-h-[90vh] overflow-hidden pointer-events-auto">
          {/* Header */}
          <div className="flex items-center justify-between px-6 py-4 border-b border-surface-border">
            <h2 className="text-xl font-bold text-white font-heading">Member Details</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-white transition-colors"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Content */}
          <div className="px-6 py-4 overflow-y-auto max-h-[calc(90vh-8rem)]">
            {loading ? (
              <div className="flex items-center justify-center py-12">
                <div className="text-center">
                  <div className="w-10 h-10 border-2 border-royal-600 border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
                  <p className="text-gray-400">Loading member details...</p>
                </div>
              </div>
            ) : error ? (
              <div className="alert-error">
                {error}
              </div>
            ) : member ? (
              <div className="space-y-6">
                {/* Success Message */}
                {successMessage && (
                  <div className="alert-success">
                    {successMessage}
                  </div>
                )}

                {/* Member Info - View or Edit Mode */}
                {isEditMode ? (
                  <div className="bg-surface border border-surface-border rounded-lg p-4">
                    <h4 className="text-lg font-semibold text-white mb-4">Edit Member Details</h4>
                    <div className="space-y-4">
                      <div>
                        <label className="input-label">
                          Name
                        </label>
                        <input
                          type="text"
                          name="name"
                          value={formData.name}
                          onChange={handleInputChange}
                          className="input-field"
                        />
                      </div>
                      <div>
                        <label className="input-label">
                          Email
                        </label>
                        <input
                          type="email"
                          name="email"
                          value={formData.email}
                          onChange={handleInputChange}
                          className="input-field"
                        />
                      </div>
                      <div>
                        <label className="input-label">
                          Role
                        </label>
                        <select
                          name="role"
                          value={formData.role}
                          onChange={handleInputChange}
                          className="input-field capitalize"
                        >
                          <option value="member">Member</option>
                          <option value="president">President</option>
                          <option value="vice_1">1st Vice President</option>
                          <option value="vice_2">2nd Vice President</option>
                          <option value="vice_3">3rd Vice President</option>
                          <option value="secretary">Secretary</option>
                          <option value="treasurer">Treasurer</option>
                          <option value="admin">Admin</option>
                        </select>
                      </div>
                      <div>
                        <label className="input-label">
                          Financial Status
                        </label>
                        <select
                          name="financial_status"
                          value={formData.financial_status}
                          onChange={handleInputChange}
                          className="input-field capitalize"
                        >
                          <option value="financial">Financial</option>
                          <option value="not financial">Not Financial</option>
                          <option value="neophyte">Neophyte</option>
                        </select>
                      </div>
                      <div>
                        <label className="input-label">
                          Initiation Date
                        </label>
                        <input
                          type="date"
                          name="initiation_date"
                          value={formData.initiation_date}
                          onChange={handleInputChange}
                          className="input-field"
                        />
                      </div>
                      <div className="flex items-center">
                        <input
                          type="checkbox"
                          id="active"
                          name="active"
                          checked={formData.active}
                          onChange={handleInputChange}
                          className="h-4 w-4 rounded border-surface-border bg-sigma-850 text-royal-600 focus:ring-royal-500 focus:ring-offset-0"
                        />
                        <label htmlFor="active" className="ml-2 block text-sm text-gray-300">
                          Active Member
                        </label>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="bg-surface border border-surface-border rounded-lg p-4">
                    <div className="flex items-start gap-4">
                      <div className="w-16 h-16 bg-royal-600/20 rounded-full flex items-center justify-center text-2xl font-heading font-semibold text-royal-300">
                        {member.member?.name?.charAt(0)?.toUpperCase() || '?'}
                      </div>
                      <div className="flex-1">
                        <h3 className="text-xl font-bold text-white">{member.member?.name}</h3>
                        <p className="text-gray-400">{member.member?.email}</p>
                        <div className="flex items-center gap-2 mt-2">
                          <span className="text-sm text-gray-500 capitalize">{member.member?.role}</span>
                          <span className="text-gray-600">|</span>
                          {member.member?.is_neophyte ? (
                            <span className="badge-neophyte">
                              Neophyte (Exempt)
                            </span>
                          ) : (
                            <span
                              className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(
                                member.member?.financial_status
                              )}`}
                            >
                              {member.member?.financial_status || 'Not Set'}
                            </span>
                          )}
                          {member.member?.initiation_date && (
                            <>
                              <span className="text-gray-600">|</span>
                              <span className="text-sm text-gray-500">
                                Initiated: {formatDate(member.member.initiation_date)}
                              </span>
                            </>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Financial Summary */}
                <div>
                  <h4 className="text-lg font-semibold text-white mb-3">Financial Summary</h4>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                    <div className="bg-surface border border-surface-border rounded-lg p-3 text-center">
                      <p className="text-xs text-gray-400 mb-1 uppercase tracking-wider">Total Paid</p>
                      <p className="text-lg font-mono font-semibold text-emerald-400">
                        {formatCurrency(member.financial_summary?.total_paid || 0)}
                      </p>
                    </div>
                    <div className="bg-surface border border-surface-border rounded-lg p-3 text-center">
                      <p className="text-xs text-gray-400 mb-1 uppercase tracking-wider">Payments</p>
                      <p className="text-lg font-mono font-semibold text-royal-300">
                        {member.financial_summary?.payment_count || 0}
                      </p>
                    </div>
                    <div className="bg-surface border border-surface-border rounded-lg p-3 text-center">
                      <p className="text-xs text-gray-400 mb-1 uppercase tracking-wider">Last Payment</p>
                      <p className="text-sm font-medium text-gray-300">
                        {member.financial_summary?.last_payment
                          ? formatDate(member.financial_summary.last_payment)
                          : 'Never'}
                      </p>
                    </div>
                    <div className="bg-surface border border-surface-border rounded-lg p-3 text-center">
                      <p className="text-xs text-gray-400 mb-1 uppercase tracking-wider">Plan Balance</p>
                      <p className="text-lg font-mono font-semibold text-rose-400">
                        {formatCurrency(member.financial_summary?.plan_balance || 0)}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Active Plan */}
                {member.active_plan && (
                  <div>
                    <h4 className="text-lg font-semibold text-white mb-3">Active Payment Plan</h4>
                    <div className="bg-royal-600/10 border border-royal-500/20 rounded-lg p-4">
                      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
                        <div>
                          <p className="text-gray-400">Frequency</p>
                          <p className="font-medium text-white capitalize">{member.active_plan.frequency}</p>
                        </div>
                        <div>
                          <p className="text-gray-400">Total Amount</p>
                          <p className="font-mono font-semibold text-white">{formatCurrency(member.active_plan.total_amount)}</p>
                        </div>
                        <div>
                          <p className="text-gray-400">Installment</p>
                          <p className="font-mono font-semibold text-white">{formatCurrency(member.active_plan.installment_amount)}</p>
                        </div>
                        <div>
                          <p className="text-gray-400">Start Date</p>
                          <p className="font-medium text-white">{formatDate(member.active_plan.start_date)}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Payment History */}
                <div>
                  <h4 className="text-lg font-semibold text-white mb-3">Recent Payments</h4>
                  {member.payments && member.payments.length > 0 ? (
                    <div className="overflow-x-auto">
                      <table className="min-w-full">
                        <thead className="table-header">
                          <tr>
                            <th className="px-4 py-2.5 text-left">Date</th>
                            <th className="px-4 py-2.5 text-left">Amount</th>
                            <th className="px-4 py-2.5 text-left">Method</th>
                            <th className="px-4 py-2.5 text-left">Type</th>
                          </tr>
                        </thead>
                        <tbody>
                          {member.payments.map((payment) => (
                            <tr key={payment.id} className="table-row">
                              <td className="table-cell">
                                {formatDate(payment.date)}
                              </td>
                              <td className="table-cell font-mono font-semibold text-white">
                                {formatCurrency(payment.amount)}
                              </td>
                              <td className="table-cell">
                                <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-500/15 text-gray-300 border border-gray-500/20 capitalize">
                                  {payment.method}
                                </span>
                              </td>
                              <td className="table-cell">
                                <span
                                  className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium capitalize ${
                                    payment.payment_type === 'installment'
                                      ? 'bg-royal-500/15 text-royal-300 border border-royal-500/20'
                                      : 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/20'
                                  }`}
                                >
                                  {payment.payment_type}
                                </span>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : (
                    <div className="text-center py-8 bg-surface border border-surface-border rounded-lg">
                      <p className="text-gray-500">No payments recorded yet.</p>
                    </div>
                  )}
                </div>
              </div>
            ) : null}
          </div>

          {/* Footer */}
          <div className="flex justify-between px-6 py-4 border-t border-surface-border bg-sigma-850/50">
            {isEditMode ? (
              <>
                <button
                  onClick={handleCancelEdit}
                  disabled={saving}
                  className="btn-secondary text-sm disabled:opacity-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSave}
                  disabled={saving}
                  className="btn-primary text-sm disabled:opacity-50 flex items-center gap-2"
                >
                  {saving ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      Saving...
                    </>
                  ) : (
                    'Save Changes'
                  )}
                </button>
              </>
            ) : (
              <>
                <button
                  onClick={onClose}
                  className="btn-secondary text-sm"
                >
                  Close
                </button>
                {canEdit && (
                  <button
                    onClick={handleEdit}
                    className="btn-primary text-sm"
                  >
                    Edit Member
                  </button>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default MemberDetailModal;
