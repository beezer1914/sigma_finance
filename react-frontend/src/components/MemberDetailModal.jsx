import { useEffect, useState } from 'react';
import { treasurerAPI } from '../services/api';
import { formatCurrency, formatDate, getStatusColor } from '../utils/formatters';

function MemberDetailModal({ memberId, onClose }) {
  const [member, setMember] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchMemberDetail = async () => {
      try {
        setLoading(true);
        const data = await treasurerAPI.getMemberDetail(memberId);
        setMember(data);
      } catch (err) {
        setError(err.response?.data?.error || 'Failed to load member details');
      } finally {
        setLoading(false);
      }
    };

    if (memberId) {
      fetchMemberDetail();
    }
  }, [memberId]);

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
        className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="relative bg-white rounded-xl shadow-xl max-w-3xl w-full max-h-[90vh] overflow-hidden">
          {/* Header */}
          <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-bold text-gray-900">Member Details</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
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
                  <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mb-2"></div>
                  <p className="text-gray-600">Loading member details...</p>
                </div>
              </div>
            ) : error ? (
              <div className="p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg">
                {error}
              </div>
            ) : member ? (
              <div className="space-y-6">
                {/* Member Info */}
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="flex items-start gap-4">
                    <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center text-2xl">
                      {member.member?.name?.charAt(0)?.toUpperCase() || '?'}
                    </div>
                    <div className="flex-1">
                      <h3 className="text-xl font-bold text-gray-900">{member.member?.name}</h3>
                      <p className="text-gray-600">{member.member?.email}</p>
                      <div className="flex items-center gap-2 mt-2">
                        <span className="text-sm text-gray-500 capitalize">{member.member?.role}</span>
                        <span className="text-gray-300">|</span>
                        {member.member?.is_neophyte ? (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
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
                      </div>
                    </div>
                  </div>
                </div>

                {/* Financial Summary */}
                <div>
                  <h4 className="text-lg font-semibold text-gray-900 mb-3">Financial Summary</h4>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                    <div className="bg-green-50 rounded-lg p-3 text-center">
                      <p className="text-xs text-gray-600 mb-1">Total Paid</p>
                      <p className="text-lg font-bold text-green-600">
                        {formatCurrency(member.financial_summary?.total_paid || 0)}
                      </p>
                    </div>
                    <div className="bg-blue-50 rounded-lg p-3 text-center">
                      <p className="text-xs text-gray-600 mb-1">Payments</p>
                      <p className="text-lg font-bold text-blue-600">
                        {member.financial_summary?.payment_count || 0}
                      </p>
                    </div>
                    <div className="bg-purple-50 rounded-lg p-3 text-center">
                      <p className="text-xs text-gray-600 mb-1">Last Payment</p>
                      <p className="text-sm font-medium text-purple-600">
                        {member.financial_summary?.last_payment
                          ? formatDate(member.financial_summary.last_payment)
                          : 'Never'}
                      </p>
                    </div>
                    <div className="bg-red-50 rounded-lg p-3 text-center">
                      <p className="text-xs text-gray-600 mb-1">Plan Balance</p>
                      <p className="text-lg font-bold text-red-600">
                        {formatCurrency(member.financial_summary?.plan_balance || 0)}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Active Plan */}
                {member.active_plan && (
                  <div>
                    <h4 className="text-lg font-semibold text-gray-900 mb-3">Active Payment Plan</h4>
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
                        <div>
                          <p className="text-gray-600">Frequency</p>
                          <p className="font-medium capitalize">{member.active_plan.frequency}</p>
                        </div>
                        <div>
                          <p className="text-gray-600">Total Amount</p>
                          <p className="font-medium">{formatCurrency(member.active_plan.total_amount)}</p>
                        </div>
                        <div>
                          <p className="text-gray-600">Installment</p>
                          <p className="font-medium">{formatCurrency(member.active_plan.installment_amount)}</p>
                        </div>
                        <div>
                          <p className="text-gray-600">Start Date</p>
                          <p className="font-medium">{formatDate(member.active_plan.start_date)}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Payment History */}
                <div>
                  <h4 className="text-lg font-semibold text-gray-900 mb-3">Recent Payments</h4>
                  {member.payments && member.payments.length > 0 ? (
                    <div className="overflow-x-auto">
                      <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                          <tr>
                            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
                            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Method</th>
                            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                          </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                          {member.payments.map((payment) => (
                            <tr key={payment.id} className="hover:bg-gray-50">
                              <td className="px-4 py-2 text-sm text-gray-900">
                                {formatDate(payment.date)}
                              </td>
                              <td className="px-4 py-2 text-sm font-medium text-gray-900">
                                {formatCurrency(payment.amount)}
                              </td>
                              <td className="px-4 py-2 text-sm">
                                <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800 capitalize">
                                  {payment.method}
                                </span>
                              </td>
                              <td className="px-4 py-2 text-sm">
                                <span
                                  className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium capitalize ${
                                    payment.payment_type === 'installment'
                                      ? 'bg-blue-100 text-blue-800'
                                      : 'bg-green-100 text-green-800'
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
                    <div className="text-center py-8 bg-gray-50 rounded-lg">
                      <p className="text-gray-500">No payments recorded yet.</p>
                    </div>
                  )}
                </div>
              </div>
            ) : null}
          </div>

          {/* Footer */}
          <div className="flex justify-end px-6 py-4 border-t border-gray-200 bg-gray-50">
            <button
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default MemberDetailModal;
