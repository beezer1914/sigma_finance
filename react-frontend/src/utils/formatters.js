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
    return 'bg-green-100 text-green-800';
  } else if (statusLower === 'not financial') {
    return 'bg-red-100 text-red-800';
  } else if (statusLower === 'neophyte') {
    return 'bg-blue-100 text-blue-800';
  }

  return 'bg-gray-100 text-gray-800';
};
