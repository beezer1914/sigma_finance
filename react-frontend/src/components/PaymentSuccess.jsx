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
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
      <Card className="max-w-md w-full text-center">
        <div className="text-6xl mb-4">✅</div>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Payment Successful!</h1>
        <p className="text-gray-600 mb-6">
          Thank you for your payment. Your transaction has been completed successfully.
        </p>
        <p className="text-sm text-gray-500 mb-6">
          You will be redirected to your dashboard in a few seconds...
        </p>
        <Link
          to="/dashboard"
          className="inline-block px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
        >
          Return to Dashboard
        </Link>
      </Card>
    </div>
  );
}

export default PaymentSuccess;
