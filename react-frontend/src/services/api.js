import axios from 'axios';

// Create axios instance with default configuration
const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Important for session-based auth
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Unauthorized - user needs to login
      // The auth store will handle this
    }
    return Promise.reject(error);
  }
);

// ============================================================================
// Authentication API
// ============================================================================

export const authAPI = {
  login: async (email, password) => {
    const response = await api.post('/auth/login', { email, password });
    return response.data;
  },

  register: async (name, email, password, invite_code) => {
    const response = await api.post('/auth/register', {
      name,
      email,
      password,
      invite_code,
    });
    return response.data;
  },

  logout: async () => {
    const response = await api.post('/auth/logout');
    return response.data;
  },

  getCurrentUser: async () => {
    const response = await api.get('/auth/user');
    return response.data;
  },
};

// ============================================================================
// Dashboard API
// ============================================================================

export const dashboardAPI = {
  getDashboardData: async () => {
    const response = await api.get('/dashboard');
    return response.data;
  },
};

// ============================================================================
// Payment API
// ============================================================================

export const paymentAPI = {
  // Get payment history with pagination
  getPayments: async (limit = 50, offset = 0) => {
    const response = await api.get('/payments', {
      params: { limit, offset },
    });
    return response.data;
  },

  // Create Stripe checkout session
  createCheckoutSession: async (amount, payment_type = 'one-time', notes = '') => {
    const response = await api.post('/payments/create-checkout', {
      amount,
      payment_type,
      notes,
    });
    return response.data;
  },
};

// ============================================================================
// Payment Plan API
// ============================================================================

export const paymentPlanAPI = {
  // Create a new payment plan
  createPlan: async (frequency, start_date, amount) => {
    const response = await api.post('/payment-plans', {
      frequency,
      start_date,
      amount,
    });
    return response.data;
  },
};

// ============================================================================
// Profile API
// ============================================================================

export const profileAPI = {
  // Update user profile
  updateProfile: async (data) => {
    const response = await api.put('/profile', data);
    return response.data;
  },
};

// ============================================================================
// Treasurer API (Admin/Treasurer Only)
// ============================================================================

export const treasurerAPI = {
  // Get dashboard statistics
  getStats: async () => {
    const response = await api.get('/treasurer/stats');
    return response.data;
  },

  // Get all members with filtering
  getMembers: async (params = {}) => {
    const response = await api.get('/treasurer/members', { params });
    return response.data;
  },

  // Get single member details
  getMemberDetail: async (userId) => {
    const response = await api.get(`/treasurer/members/${userId}`);
    return response.data;
  },

  // Update member details
  updateMember: async (userId, data) => {
    const response = await api.put(`/treasurer/members/${userId}`, data);
    return response.data;
  },

  // Get all payments (treasurer view)
  getAllPayments: async (params = {}) => {
    const response = await api.get('/treasurer/payments', { params });
    return response.data;
  },

  // Get reports summary
  getReportsSummary: async () => {
    const response = await api.get('/treasurer/reports/summary');
    return response.data;
  },
};

// ============================================================================
// Donations API (Treasurer Only)
// ============================================================================

export const donationsAPI = {
  // Get donations list with filtering and pagination
  getDonations: async (params = {}) => {
    const response = await api.get('/donations', { params });
    return response.data;
  },

  // Get donations summary statistics
  getSummary: async () => {
    const response = await api.get('/donations/summary');
    return response.data;
  },

  // Create a manual donation entry
  createDonation: async (donationData) => {
    const response = await api.post('/donations', donationData);
    return response.data;
  },
};

// ============================================================================
// Invites API (Treasurer Only)
// ============================================================================

export const invitesAPI = {
  // Get all invite codes with filtering and pagination
  getInvites: async (params = {}) => {
    const response = await api.get('/invites', { params });
    return response.data;
  },

  // Get invite statistics
  getStats: async () => {
    const response = await api.get('/invites/stats');
    return response.data;
  },

  // Create a new invite code
  createInvite: async (inviteData) => {
    const response = await api.post('/invites', inviteData);
    return response.data;
  },

  // Delete an unused invite code
  deleteInvite: async (inviteId) => {
    const response = await api.delete(`/invites/${inviteId}`);
    return response.data;
  },
};

// ============================================================================
// Export the axios instance for custom requests
// ============================================================================

export default api;
