import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Link, useParams, useNavigate } from 'react-router-dom';
import { authAPI } from '../services/api';

// Validation schema
const resetPasswordSchema = z.object({
  password: z.string().min(8, 'Password must be at least 8 characters'),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ['confirmPassword'],
});

type ResetPasswordFormData = z.infer<typeof resetPasswordSchema>;

function ResetPassword() {
  const { token } = useParams<{ token: string }>();
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ResetPasswordFormData>({
    resolver: zodResolver(resetPasswordSchema),
  });

  const onSubmit = async (data: ResetPasswordFormData) => {
    if (!token) {
      setError('Invalid reset link');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      await authAPI.resetPassword(token, data.password);
      setSuccess(true);
      // Redirect to login after 2 seconds
      setTimeout(() => navigate('/login'), 2000);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to reset password');
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
              Password Reset Successful
            </h2>
            <p className="text-gray-400 mb-4">
              Your password has been updated successfully.
            </p>
            <p className="text-sm text-gray-500">
              Redirecting to login...
            </p>
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
            Reset Your Password
          </h2>
          <p className="mt-2 text-gray-400 font-body text-sm">
            Enter your new password below
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
              <label htmlFor="password" className="input-label">
                New Password
              </label>
              <input
                id="password"
                type="password"
                {...register('password')}
                onFocus={() => setError(null)}
                className={`input-field ${errors.password ? 'error' : ''}`}
                placeholder="••••••••"
              />
              {errors.password && (
                <p className="mt-1.5 text-sm text-rose-400">{errors.password.message}</p>
              )}
            </div>

            <div>
              <label htmlFor="confirmPassword" className="input-label">
                Confirm Password
              </label>
              <input
                id="confirmPassword"
                type="password"
                {...register('confirmPassword')}
                onFocus={() => setError(null)}
                className={`input-field ${errors.confirmPassword ? 'error' : ''}`}
                placeholder="••••••••"
              />
              {errors.confirmPassword && (
                <p className="mt-1.5 text-sm text-rose-400">{errors.confirmPassword.message}</p>
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
                  Resetting...
                </span>
              ) : (
                'Reset Password'
              )}
            </button>
          </form>

          <div className="mt-6 text-center">
            <Link to="/login" className="text-royal-400 hover:text-royal-300 font-medium transition-colors text-sm">
              Back to Login
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ResetPassword;
