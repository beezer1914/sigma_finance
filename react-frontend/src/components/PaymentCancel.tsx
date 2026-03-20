import { Link } from 'react-router-dom';
import Card from './Card';

function PaymentCancel() {
  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <Card className="max-w-md w-full text-center animate-slide-up">
        {/* Rose X icon */}
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-rose-500/20 mb-5">
          <svg className="w-8 h-8 text-rose-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </div>

        <h1 className="font-heading text-2xl font-semibold text-white mb-2 tracking-tight">
          Payment Cancelled
        </h1>
        <p className="text-gray-400 mb-6">
          Your payment was not completed. No charges have been made to your account.
        </p>
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <Link
            to="/dashboard"
            className="btn-primary px-6 py-2.5 text-center"
          >
            Return to Dashboard
          </Link>
          <button
            onClick={() => window.history.back()}
            className="btn-secondary px-6 py-2.5"
          >
            Try Again
          </button>
        </div>
      </Card>
    </div>
  );
}

export default PaymentCancel;
