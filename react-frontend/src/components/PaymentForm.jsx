import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { paymentAPI } from '../services/api';
import { formatCurrency } from '../utils/formatters';

// Validation schema
const paymentSchema = z.object({
  amount: z.number().min(1, 'Amount must be at least $1'),
  notes: z.string().optional(),
});

function PaymentForm({ onClose, onSuccess, paymentType = 'one-time' }) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(paymentSchema),
    defaultValues: {
      amount: '',
      notes: '',
    },
  });

  const amount = watch('amount');

  // Calculate Stripe fees
  const calculateFees = (amt) => {
    if (!amt || amt <= 0) return 0;
    const amountNum = parseFloat(amt);
    const feePercentage = 0.029; // 2.9%
    const fixedFee = 0.30;
    const totalWithFees = (amountNum + fixedFee) / (1 - feePercentage);
    return totalWithFees - amountNum;
  };

  const stripeFee = calculateFees(amount);
  const totalAmount = amount ? parseFloat(amount) + stripeFee : 0;

  const onSubmit = async (data) => {
    try {
      setIsLoading(true);
      setError(null);

      const result = await paymentAPI.createCheckoutSession(
        parseFloat(data.amount),
        paymentType,
        data.notes
      );

      if (result.success && result.checkout_url) {
        // Redirect to Stripe checkout
        window.location.href = result.checkout_url;
      } else {
        setError('Failed to create checkout session');
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Payment failed');
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900">
            {paymentType === 'installment' ? 'Make Installment Payment' : 'Make One-Time Payment'}
          </h2>
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
            <label htmlFor="amount" className="block text-gray-700 font-medium mb-2">
              Payment Amount
            </label>
            <div className="relative">
              <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500 font-medium">
                $
              </span>
              <input
                id="amount"
                type="number"
                step="0.01"
                min="1"
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

          {amount > 0 && (
            <div className="mb-4 p-4 bg-gray-50 rounded-lg">
              <div className="flex justify-between text-sm mb-2">
                <span className="text-gray-600">Payment Amount:</span>
                <span className="font-medium">{formatCurrency(amount)}</span>
              </div>
              <div className="flex justify-between text-sm mb-2">
                <span className="text-gray-600">Processing Fee (2.9% + $0.30):</span>
                <span className="font-medium">{formatCurrency(stripeFee)}</span>
              </div>
              <div className="border-t border-gray-200 pt-2 mt-2">
                <div className="flex justify-between font-bold">
                  <span>Total Amount:</span>
                  <span className="text-blue-600">{formatCurrency(totalAmount)}</span>
                </div>
              </div>
              <p className="text-xs text-gray-500 mt-2">
                The processing fee covers credit card transaction costs.
              </p>
            </div>
          )}

          <div className="mb-6">
            <label htmlFor="notes" className="block text-gray-700 font-medium mb-2">
              Notes (Optional)
            </label>
            <textarea
              id="notes"
              {...register('notes')}
              rows="3"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Add any notes about this payment..."
            ></textarea>
          </div>

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
              disabled={isLoading || !amount || amount <= 0}
              className={`flex-1 px-4 py-2 rounded-lg font-medium text-white transition-colors ${
                isLoading || !amount || amount <= 0
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-blue-600 hover:bg-blue-700'
              }`}
            >
              {isLoading ? 'Processing...' : 'Continue to Payment'}
            </button>
          </div>
        </form>

        <div className="mt-4 p-3 bg-blue-50 rounded-lg">
          <p className="text-xs text-blue-800">
            🔒 You'll be redirected to Stripe's secure checkout page to complete your payment.
          </p>
        </div>
      </div>
    </div>
  );
}

export default PaymentForm;
