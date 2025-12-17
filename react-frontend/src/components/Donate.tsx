import { useState, useEffect } from 'react';
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
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-blue-800 to-indigo-900 flex items-center justify-center px-4">
      <div className="max-w-lg w-full">
        {/* Card */}
        <div className="bg-white rounded-2xl shadow-2xl overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-600 to-indigo-600 px-8 py-10 text-center">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-white/20 rounded-full mb-4">
              <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
            </div>
            <h1 className="text-3xl font-bold text-white mb-2">Support Sigma</h1>
            <p className="text-blue-100">Your generosity helps us grow stronger</p>
          </div>

          {/* Content */}
          <div className="px-8 py-8">
            <div className="text-center mb-8">
              <p className="text-gray-600 leading-relaxed">
                Your donation supports our chapter's activities, events, and community initiatives.
                Every contribution, no matter the size, makes a difference.
              </p>
            </div>

            {/* Donation Button */}
            {loading ? (
              <div className="flex justify-center py-4">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              </div>
            ) : error ? (
              <div className="text-center text-red-600 py-4">{error}</div>
            ) : (
              <button
                onClick={handleDonate}
                disabled={!donationLink}
                className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-semibold py-4 px-6 rounded-xl transition-all duration-200 transform hover:scale-[1.02] shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed"
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
          <a
            href="/login"
            className="text-blue-200 hover:text-white transition-colors text-sm"
          >
            Already a member? Sign in
          </a>
        </div>
      </div>
    </div>
  );
}

export default Donate;
