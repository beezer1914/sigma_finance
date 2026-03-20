/**
 * Format currency to USD
 */
export const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(amount);
};

/**
 * Format date to readable format
 */
export const formatDate = (dateString) => {
  if (!dateString) return 'N/A';

  const date = new Date(dateString);
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }).format(date);
};

/**
 * Format date with time
 */
export const formatDateTime = (dateString) => {
  if (!dateString) return 'N/A';

  const date = new Date(dateString);
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  }).format(date);
};

/**
 * Get status badge color
 */
export const getStatusColor = (status) => {
  const statusLower = status?.toLowerCase();

  if (statusLower === 'financial') {
    return 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/20';
  } else if (statusLower === 'not financial') {
    return 'bg-rose-500/15 text-rose-400 border border-rose-500/20';
  } else if (statusLower === 'neophyte') {
    return 'bg-royal-500/15 text-royal-300 border border-royal-500/20';
  }

  return 'bg-gray-500/15 text-gray-400 border border-gray-500/20';
};
