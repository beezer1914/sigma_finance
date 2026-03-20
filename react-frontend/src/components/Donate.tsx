import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';

function Donate() {
  const [donationLink, setDonationLink] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDonationLink = async () => {
      try {
        const response = await api.get('/donate/link');
        setDonationLink(response.data.donation_link);
      } catch (err) {
        setError('Unable to load donation link');
        console.error('Error fetching donation link:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchDonationLink();
  }, []);

  const handleDonate = () => {
    if (donationLink) {
      window.open(donationLink, '_blank', 'noopener,noreferrer');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="max-w-lg w-full animate-slide-up">
        {/* Card */}
        <div className="glass-card overflow-hidden">
          {/* Header */}
          <div className="relative px-8 pt-10 pb-8 text-center">
            {/* Subtle gradient overlay at top of card */}
            <div className="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-royal-600 via-gold-500 to-royal-600" />

            <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-royal-600 mb-5 shadow-glow-blue">
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
            </div>
            <h1 className="font-heading text-3xl font-semibold text-white mb-2 tracking-tight">
              Support Sigma
            </h1>
            <p className="text-gray-400">Your generosity helps us grow stronger</p>
          </div>

          {/* Content */}
          <div className="px-8 pb-8">
            <div className="text-center mb-8">
              <p className="text-gray-400 leading-relaxed">
                Your donation supports our chapter's activities, events, and community initiatives.
                Every contribution, no matter the size, makes a difference.
              </p>
            </div>

            {/* Donation Button */}
            {loading ? (
              <div className="flex justify-center py-4">
                <div className="w-8 h-8 border-2 border-royal-600 border-t-transparent rounded-full animate-spin" />
              </div>
            ) : error ? (
              <div className="alert-error text-center py-4">{error}</div>
            ) : (
              <button
                onClick={handleDonate}
                disabled={!donationLink}
                className="w-full bg-gradient-to-r from-gold-600 to-gold-500 hover:from-gold-500 hover:to-gold-400 text-gray-900 font-semibold py-4 px-6 rounded-xl transition-all duration-200 transform hover:scale-[1.02] shadow-lg hover:shadow-gold-500/25 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <span className="flex items-center justify-center gap-2">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Make a Donation
                </span>
              </button>
            )}

            {/* Security Note */}
            <div className="mt-6 flex items-center justify-center gap-2 text-sm text-gray-500">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
              <span>Secure payment powered by Stripe</span>
            </div>
          </div>
        </div>

        {/* Back Link */}
        <div className="text-center mt-6">
          <Link
            to="/login"
            className="text-royal-400 hover:text-royal-300 font-medium transition-colors text-sm"
          >
            Already a member? Sign in
          </Link>
        </div>
      </div>
    </div>
  );
}

export default Donate;
