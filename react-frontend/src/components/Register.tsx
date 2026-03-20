import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useNavigate, Link } from 'react-router-dom';
import useAuthStore from '../stores/authStore';
import { useRecaptcha } from '../hooks/useRecaptcha';

// Validation schema
const registerSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Invalid email address'),
  password: z.string()
    .min(12, 'Password must be at least 12 characters')
    .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
    .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
    .regex(/\d/, 'Password must contain at least one digit')
    .regex(/[!@#$%^&*(),.?":{}|<>]/, 'Password must contain at least one special character'),
  confirmPassword: z.string(),
  invite_code: z.string().min(1, 'Invite code is required'),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ['confirmPassword'],
});

type RegisterFormData = z.infer<typeof registerSchema>;

function Register() {
  const navigate = useNavigate();
  const { register: registerUser, isAuthenticated, isLoading, error, clearError } = useAuthStore();
  const [successMessage, setSuccessMessage] = useState<string>('');
  const { executeRecaptcha } = useRecaptcha();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  });

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, navigate]);

  // Clear errors when component unmounts
  useEffect(() => {
    return () => clearError();
  }, [clearError]);

  const onSubmit = async (data: RegisterFormData) => {
    clearError();
    setSuccessMessage('');

    const recaptchaToken = await executeRecaptcha('register');

    const result = await registerUser(
      data.name,
      data.email,
      data.password,
      data.invite_code,
      recaptchaToken
    );

    if (result.success) {
      setSuccessMessage('Account created successfully! Redirecting to dashboard...');
      setTimeout(() => {
        navigate('/dashboard');
      }, 1000);
    }
  };

  const fields = [
    { id: 'name', label: 'Full Name', type: 'text', placeholder: 'John Doe', error: errors.name },
    { id: 'email', label: 'Email', type: 'email', placeholder: 'your@email.com', error: errors.email },
    { id: 'password', label: 'Password', type: 'password', placeholder: '••••••••', error: errors.password,
      hint: 'Must be 12+ characters with uppercase, lowercase, digit, and special character' },
    { id: 'confirmPassword', label: 'Confirm Password', type: 'password', placeholder: '••••••••', error: errors.confirmPassword },
    { id: 'invite_code', label: 'Invite Code', type: 'text', placeholder: 'Your invite code', error: errors.invite_code },
  ];

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md animate-slide-up">
        {/* Brand */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-royal-600 text-white font-heading font-bold text-lg mb-4 shadow-glow-blue">
            ΣΔΣ
          </div>
          <h2 className="font-heading text-3xl font-semibold text-white tracking-tight">
            Create Account
          </h2>
          <p className="mt-2 text-gray-400 font-body text-sm">
            Join Sigma Finance
          </p>
        </div>

        {/* Register Card */}
        <div className="glass-card p-8">
          {error && (
            <div className="alert-error mb-5">{error}</div>
          )}

          {successMessage && (
            <div className="alert-success mb-5">{successMessage}</div>
          )}

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            {fields.map((field) => (
              <div key={field.id}>
                <label htmlFor={field.id} className="input-label">
                  {field.label}
                </label>
                <input
                  id={field.id}
                  type={field.type}
                  {...register(field.id as keyof RegisterFormData)}
                  className={`input-field ${field.error ? 'error' : ''}`}
                  placeholder={field.placeholder}
                />
                {field.error && (
                  <p className="mt-1.5 text-sm text-rose-400">{field.error.message}</p>
                )}
                {field.hint && (
                  <p className="mt-1.5 text-xs text-gray-500">{field.hint}</p>
                )}
              </div>
            ))}

            <button
              type="submit"
              disabled={isLoading}
              className={`w-full btn-primary py-3 text-base mt-2 ${
                isLoading ? 'opacity-50 cursor-not-allowed' : ''
              }`}
            >
              {isLoading ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Creating Account...
                </span>
              ) : (
                'Register'
              )}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-gray-500 text-sm">
              Already have an account?{' '}
              <Link to="/login" className="text-royal-400 hover:text-royal-300 font-medium transition-colors">
                Login
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Register;
