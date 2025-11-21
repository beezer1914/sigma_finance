import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { paymentPlanAPI } from '../services/api';
import { formatCurrency } from '../utils/formatters';

// Validation schema
const planSchema = z.object({
  frequency: z.enum(['weekly', 'monthly', 'quarterly']),
  start_date: z.string().min(1, 'Start date is required'),
  amount: z.number().min(100, 'Amount must be at least $100'),
});

function PaymentPlanForm({ onClose, onSuccess }) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(planSchema),
    defaultValues: {
      frequency: 'monthly',
      start_date: new Date().toISOString().split('T')[0],
      amount: '',
    },
  });

  const frequency = watch('frequency');
  const amount = watch('amount');

  // Calculate plan details
  const getPlanDetails = () => {
    if (!amount || amount <= 0) return null;

    let numPayments, intervalText;

    switch (frequency) {
      case 'weekly':
        numPayments = 10;
        intervalText = '10 weekly payments';
        break;
      case 'monthly':
        numPayments = 5;
        intervalText = '5 monthly payments';
        break;
      case 'quarterly':
        numPayments = 2;
        intervalText = '2 quarterly payments';
        break;
      default:
        numPayments = 1;
        intervalText = '1 payment';
    }

    const installmentAmount = amount / numPayments;

    return {
      numPayments,
      intervalText,
      installmentAmount: installmentAmount.toFixed(2),
    };
  };

  const planDetails = getPlanDetails();

  const onSubmit = async (data) => {
    try {
      setIsLoading(true);
      setError(null);

      const result = await paymentPlanAPI.createPlan(
        data.frequency,
        data.start_date,
        parseFloat(data.amount)
      );

      if (result.success) {
        onSuccess && onSuccess(result.plan);
      } else {
        setError('Failed to create payment plan');
        setIsLoading(false);
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to create payment plan');
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-lg w-full p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Enroll in Payment Plan</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl font-bold"
          >
            ×
          </button>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)}>
          <div className="mb-4">
            <label htmlFor="frequency" className="block text-gray-700 font-medium mb-2">
              Payment Frequency
            </label>
            <select
              id="frequency"
              {...register('frequency')}
              className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                errors.frequency ? 'border-red-500' : 'border-gray-300'
              }`}
            >
              <option value="weekly">Weekly (10 payments)</option>
              <option value="monthly">Monthly (5 payments)</option>
              <option value="quarterly">Quarterly (2 payments)</option>
            </select>
            {errors.frequency && (
              <p className="mt-1 text-sm text-red-500">{errors.frequency.message}</p>
            )}
          </div>

          <div className="mb-4">
            <label htmlFor="start_date" className="block text-gray-700 font-medium mb-2">
              Start Date
            </label>
            <input
              id="start_date"
              type="date"
              {...register('start_date')}
              className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                errors.start_date ? 'border-red-500' : 'border-gray-300'
              }`}
            />
            {errors.start_date && (
              <p className="mt-1 text-sm text-red-500">{errors.start_date.message}</p>
            )}
          </div>

          <div className="mb-4">
            <label htmlFor="amount" className="block text-gray-700 font-medium mb-2">
              Total Amount
            </label>
            <div className="relative">
              <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500 font-medium">
                $
              </span>
              <input
                id="amount"
                type="number"
                step="0.01"
                min="100"
                {...register('amount', { valueAsNumber: true })}
                className={`w-full pl-8 pr-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors.amount ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="0.00"
              />
            </div>
            {errors.amount && (
              <p className="mt-1 text-sm text-red-500">{errors.amount.message}</p>
            )}
          </div>

          {planDetails && (
            <div className="mb-6 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
              <h3 className="font-bold text-gray-900 mb-3">Plan Summary</h3>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-600">Total Amount:</span>
                  <span className="font-bold text-gray-900">{formatCurrency(amount)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Payment Schedule:</span>
                  <span className="font-medium text-gray-900">{planDetails.intervalText}</span>
                </div>
                <div className="flex justify-between pt-2 border-t border-blue-200">
                  <span className="text-gray-600">Per Installment:</span>
                  <span className="font-bold text-blue-600 text-lg">
                    {formatCurrency(planDetails.installmentAmount)}
                  </span>
                </div>
              </div>
              <p className="text-xs text-gray-600 mt-3">
                💡 You can make payments toward your plan at any time. The plan completes when
                you've paid the total amount.
              </p>
            </div>
          )}

          <div className="flex gap-3">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading || !amount || amount < 100}
              className={`flex-1 px-4 py-2 rounded-lg font-medium text-white transition-colors ${
                isLoading || !amount || amount < 100
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-blue-600 hover:bg-blue-700'
              }`}
            >
              {isLoading ? 'Creating Plan...' : 'Create Payment Plan'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default PaymentPlanForm;
