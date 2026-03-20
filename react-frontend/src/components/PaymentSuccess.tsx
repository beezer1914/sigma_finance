import { useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Card from './Card';

function PaymentSuccess() {
  const navigate = useNavigate();

  // Auto-redirect to dashboard after 5 seconds
  useEffect(() => {
    const timer = setTimeout(() => {
      navigate('/dashboard');
    }, 5000);

    return () => clearTimeout(timer);
  }, [navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <Card className="max-w-md w-full text-center animate-slide-up">
        {/* Emerald checkmark */}
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-emerald-500/20 mb-5">
          <svg className="w-8 h-8 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
          </svg>
        </div>

        <h1 className="font-heading text-2xl font-semibold text-white mb-2 tracking-tight">
          Payment Successful!
        </h1>
        <p className="text-gray-400 mb-4">
          Thank you for your payment. Your transaction has been completed successfully.
        </p>
        <p className="text-sm text-gray-500 mb-6">
          You will be redirected to your dashboard in a few seconds...
        </p>
        <Link
          to="/dashboard"
          className="btn-primary inline-flex items-center justify-center px-6 py-2.5"
        >
          Return to Dashboard
        </Link>
      </Card>
    </div>
  );
}

export default PaymentSuccess;
