import { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useNavigate, Link } from 'react-router-dom';
import useAuthStore from '../stores/authStore';
import { useRecaptcha } from '../hooks/useRecaptcha';

// Validation schema
const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(1, 'Password is required'),
});

type LoginFormData = z.infer<typeof loginSchema>;

function Login() {
  const navigate = useNavigate();
  const { login, isAuthenticated, isLoading, error, clearError } = useAuthStore();
  const { executeRecaptcha } = useRecaptcha();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, navigate]);

  const onSubmit = async (data: LoginFormData) => {
    // Get reCAPTCHA token
    const recaptchaToken = await executeRecaptcha('login');

    const result = await login(data.email, data.password, recaptchaToken);
    if (result.success) {
      navigate('/dashboard');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="w-full max-w-md animate-slide-up">
        {/* Brand */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-royal-600 text-white font-heading font-bold text-lg mb-4 shadow-glow-blue">
            ΣΔΣ
          </div>
          <h2 className="font-heading text-3xl font-semibold text-white tracking-tight">
            Welcome Back
          </h2>
          <p className="mt-2 text-gray-400 font-body text-sm">
            Sign in to Sigma Finance
          </p>
        </div>

        {/* Login Card */}
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
                onFocus={() => error && clearError()}
                className={`input-field ${errors.email ? 'error' : ''}`}
                placeholder="your@email.com"
              />
              {errors.email && (
                <p className="mt-1.5 text-sm text-rose-400">{errors.email.message}</p>
              )}
            </div>

            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label htmlFor="password" className="input-label !mb-0">
                  Password
                </label>
                <Link
                  to="/forgot-password"
                  className="text-sm text-royal-400 hover:text-royal-300 transition-colors"
                >
                  Forgot password?
                </Link>
              </div>
              <input
                id="password"
                type="password"
                {...register('password')}
                onFocus={() => error && clearError()}
                className={`input-field ${errors.password ? 'error' : ''}`}
                placeholder="••••••••"
              />
              {errors.password && (
                <p className="mt-1.5 text-sm text-rose-400">{errors.password.message}</p>
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
                  Signing in...
                </span>
              ) : (
                'Sign In'
              )}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-gray-500 text-sm">
              Don't have an account?{' '}
              <Link to="/register" className="text-royal-400 hover:text-royal-300 font-medium transition-colors">
                Register
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Login;
