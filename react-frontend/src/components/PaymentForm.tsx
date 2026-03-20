import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { paymentAPI } from '../services/api';
import type { PaymentType } from '../types';
import { formatCurrency } from '../utils/formatters';

// Validation schema
const paymentSchema = z.object({
  amount: z.coerce.number().min(1, 'Amount must be at least $1'),
  notes: z.string().optional(),
});

type PaymentFormData = z.infer<typeof paymentSchema>;

interface PaymentFormProps {
  onClose: () => void;
  onSuccess: () => void;
  paymentType?: PaymentType;
}

function PaymentForm({ onClose, onSuccess, paymentType = 'one-time' }: PaymentFormProps) {
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(paymentSchema) as any,
    defaultValues: {
      amount: '',
      notes: '',
    },
  });

  const amount = watch('amount');

  // Calculate Stripe fees
  const calculateFees = (amt: number): number => {
    if (!amt || amt <= 0) return 0;
    const amountNum = Number(amt);
    const feePercentage = 0.029; // 2.9%
    const fixedFee = 0.30;
    const totalWithFees = (amountNum + fixedFee) / (1 - feePercentage);
    return totalWithFees - amountNum;
  };

  const stripeFee = calculateFees(amount as any);
  const totalAmount = amount ? Number(amount) + stripeFee : 0;

  const onSubmit = async (data: any) => {
    try {
      setIsLoading(true);
      setError(null);

      const result = await paymentAPI.createCheckoutSession(
        Number(data.amount),
        paymentType,
        data.notes
      );

      if (result.success && result.checkout_url) {
        // Redirect to Stripe checkout
        window.location.href = result.checkout_url;
      } else {
        setError('Failed to create checkout session');
      }
    } catch (err: any) {
      setError(err.response?.data?.error || 'Payment failed');
      setIsLoading(false);
    }
  };

  const isDisabled = isLoading || !amount || Number(amount) <= 0;

  return (
    <div className="modal-backdrop p-4">
      <div className="bg-sigma-900 border border-surface-border rounded-2xl shadow-card max-w-md w-full p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-heading font-semibold text-white">
            {paymentType === 'installment' ? 'Make Installment Payment' : 'Make One-Time Payment'}
          </h2>
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
            <label htmlFor="amount" className="input-label">
              Payment Amount
            </label>
            <div className="relative">
              <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500 font-mono font-semibold">
                $
              </span>
              <input
                id="amount"
                type="number"
                step="0.01"
                min="1"
                {...register('amount', { valueAsNumber: true })}
                className={`input-field pl-8 ${errors.amount ? 'error' : ''}`}
                placeholder="0.00"
              />
            </div>
            {errors.amount && (
              <p className="mt-1 text-sm text-rose-400">{errors.amount.message}</p>
            )}
          </div>

          {Number(amount) > 0 && (
            <div className="mb-4 p-4 bg-surface rounded-xl border border-surface-border">
              <div className="flex justify-between text-sm mb-2">
                <span className="text-gray-400">Payment Amount:</span>
                <span className="font-mono font-semibold text-gray-300">{formatCurrency(amount)}</span>
              </div>
              <div className="flex justify-between text-sm mb-2">
                <span className="text-gray-400">Processing Fee (2.9% + $0.30):</span>
                <span className="font-mono font-semibold text-gray-300">{formatCurrency(stripeFee)}</span>
              </div>
              <div className="border-t border-surface-border pt-2 mt-2">
                <div className="flex justify-between font-bold">
                  <span className="text-white">Total Amount:</span>
                  <span className="text-royal-400 font-mono font-semibold">{formatCurrency(totalAmount)}</span>
                </div>
              </div>
              <p className="text-xs text-gray-500 mt-2">
                The processing fee covers credit card transaction costs.
              </p>
            </div>
          )}

          <div className="mb-6">
            <label htmlFor="notes" className="input-label">
              Notes (Optional)
            </label>
            <textarea
              id="notes"
              {...register('notes')}
              rows={3}
              className="input-field"
              placeholder="Add any notes about this payment..."
            ></textarea>
          </div>

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
              {isLoading ? 'Processing...' : 'Continue to Payment'}
            </button>
          </div>
        </form>

        <div className="mt-4 p-3 bg-royal-600/10 border border-royal-500/20 rounded-lg">
          <div className="flex items-center gap-2">
            <svg className="w-4 h-4 text-royal-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
            <p className="text-xs text-royal-300">
              You'll be redirected to Stripe's secure checkout page to complete your payment.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default PaymentForm;
