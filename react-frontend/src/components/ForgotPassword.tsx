import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Link } from 'react-router-dom';
import { authAPI } from '../services/api';

// Validation schema
const forgotPasswordSchema = z.object({
  email: z.string().email('Invalid email address'),
});

type ForgotPasswordFormData = z.infer<typeof forgotPasswordSchema>;

function ForgotPassword() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ForgotPasswordFormData>({
    resolver: zodResolver(forgotPasswordSchema),
  });

  const onSubmit = async (data: ForgotPasswordFormData) => {
    setIsLoading(true);
    setError(null);

    try {
      await authAPI.forgotPassword(data.email);
      setSuccess(true);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to send reset email');
    } finally {
      setIsLoading(false);
    }
  };

  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center px-4">
        <div className="w-full max-w-md animate-slide-up">
          {/* Brand */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-royal-600 text-white font-heading font-bold text-lg mb-4 shadow-glow-blue">
              ΣΔΣ
            </div>
          </div>

          {/* Success Card */}
          <div className="glass-card p-8 text-center">
            {/* Emerald checkmark */}
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-emerald-500/20 mb-5">
              <svg className="w-8 h-8 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
              </svg>
            </div>

            <h2 className="font-heading text-2xl font-semibold text-white mb-3 tracking-tight">
              Check Your Email
            </h2>
            <p className="text-gray-400 mb-4">
              If your email is registered, you'll receive a password reset link shortly.
            </p>
            <p className="text-sm text-gray-500 mb-6">
              The link will expire in 10 minutes for security.
            </p>
            <Link
              to="/login"
              className="text-royal-400 hover:text-royal-300 font-medium transition-colors"
            >
              Back to Login
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="w-full max-w-md animate-slide-up">
        {/* Brand */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-royal-600 text-white font-heading font-bold text-lg mb-4 shadow-glow-blue">
            ΣΔΣ
          </div>
          <h2 className="font-heading text-3xl font-semibold text-white tracking-tight">
            Forgot Password?
          </h2>
          <p className="mt-2 text-gray-400 font-body text-sm">
            Enter your email and we'll send you a reset link
          </p>
        </div>

        {/* Form Card */}
        <div className="glass-card p-8">
          {error && (
            <div className="alert-error mb-5">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            <div>
              <label htmlFor="email" className="input-label">
                Email
              </label>
              <input
                id="email"
                type="email"
                {...register('email')}
                onFocus={() => setError(null)}
                className={`input-field ${errors.email ? 'error' : ''}`}
                placeholder="your@email.com"
              />
              {errors.email && (
                <p className="mt-1.5 text-sm text-rose-400">{errors.email.message}</p>
              )}
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className={`w-full btn-primary py-3 text-base ${
                isLoading ? 'opacity-50 cursor-not-allowed' : ''
              }`}
            >
              {isLoading ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Sending...
                </span>
              ) : (
                'Send Reset Link'
              )}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-gray-500 text-sm">
              Remember your password?{' '}
              <Link to="/login" className="text-royal-400 hover:text-royal-300 font-medium transition-colors">
                Back to Login
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ForgotPassword;
