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
  amount: z.coerce.number().min(100, 'Amount must be at least $100'),
});

type PlanFormData = z.infer<typeof planSchema>;

interface PaymentPlanFormProps {
  onClose: () => void;
  onSuccess: (plan?: any) => void;
}

function PaymentPlanForm({ onClose, onSuccess }: PaymentPlanFormProps) {
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(planSchema) as any,
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
    if (!amount || (amount as any) <= 0) return null;

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

    const installmentAmount = Number(amount) / numPayments;

    return {
      numPayments,
      intervalText,
      installmentAmount: installmentAmount.toFixed(2),
    };
  };

  const planDetails = getPlanDetails();

  const onSubmit = async (data: any) => {
    try {
      setIsLoading(true);
      setError(null);

      const result = await paymentPlanAPI.createPlan(
        data.frequency as any,
        data.start_date,
        Number(data.amount)
      );

      if (result.success) {
        onSuccess && onSuccess(result.plan);
      } else {
        setError('Failed to create payment plan');
        setIsLoading(false);
      }
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to create payment plan');
      setIsLoading(false);
    }
  };

  const isDisabled = isLoading || !amount || Number(amount) < 100;

  return (
    <div className="modal-backdrop p-4">
      <div className="bg-sigma-900 border border-surface-border rounded-2xl shadow-card max-w-lg w-full p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-heading font-semibold text-white">Enroll in Payment Plan</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-white text-2xl font-bold transition-colors"
          >
            &times;
          </button>
        </div>

        {error && (
          <div className="alert-error mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)}>
          <div className="mb-4">
            <label htmlFor="frequency" className="input-label">
              Payment Frequency
            </label>
            <select
              id="frequency"
              {...register('frequency')}
              className={`input-field ${errors.frequency ? 'error' : ''}`}
            >
              <option value="weekly">Weekly (10 payments)</option>
              <option value="monthly">Monthly (5 payments)</option>
              <option value="quarterly">Quarterly (2 payments)</option>
            </select>
            {errors.frequency && (
              <p className="mt-1 text-sm text-rose-400">{errors.frequency.message}</p>
            )}
          </div>

          <div className="mb-4">
            <label htmlFor="start_date" className="input-label">
              Start Date
            </label>
            <input
              id="start_date"
              type="date"
              {...register('start_date')}
              className={`input-field ${errors.start_date ? 'error' : ''}`}
            />
            {errors.start_date && (
              <p className="mt-1 text-sm text-rose-400">{errors.start_date.message}</p>
            )}
          </div>

          <div className="mb-4">
            <label htmlFor="amount" className="input-label">
              Total Amount
            </label>
            <div className="relative">
              <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500 font-mono font-semibold">
                $
              </span>
              <input
                id="amount"
                type="number"
                step="0.01"
                min="100"
                {...register('amount', { valueAsNumber: true })}
                className={`input-field pl-8 ${errors.amount ? 'error' : ''}`}
                placeholder="0.00"
              />
            </div>
            {errors.amount && (
              <p className="mt-1 text-sm text-rose-400">{errors.amount.message}</p>
            )}
          </div>

          {planDetails && (
            <div className="mb-6 bg-surface rounded-xl border border-surface-border overflow-hidden">
              <div className="border-l-4 border-l-royal-500 p-4">
                <h3 className="font-heading font-bold text-white mb-3">Plan Summary</h3>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Total Amount:</span>
                    <span className="font-mono font-semibold text-white">{formatCurrency(amount)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Payment Schedule:</span>
                    <span className="font-medium text-gray-300">{planDetails.intervalText}</span>
                  </div>
                  <div className="flex justify-between pt-2 border-t border-surface-border">
                    <span className="text-gray-400">Per Installment:</span>
                    <span className="text-royal-400 font-mono font-semibold text-lg">
                      {formatCurrency(planDetails.installmentAmount)}
                    </span>
                  </div>
                </div>
                <p className="text-xs text-gray-500 mt-3">
                  You can make payments toward your plan at any time. The plan completes when
                  you've paid the total amount.
                </p>
              </div>
            </div>
          )}

          <div className="flex gap-3">
            <button
              type="button"
              onClick={onClose}
              className="btn-secondary flex-1"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isDisabled}
              className={`btn-primary flex-1 ${isDisabled ? 'opacity-50 cursor-not-allowed' : ''}`}
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
