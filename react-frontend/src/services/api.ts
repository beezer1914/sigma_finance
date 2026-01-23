import axios, { AxiosError } from 'axios';
import type {
  LoginResponse,
  RegisterResponse,
  CreateCheckoutResponse,
  CreatePlanResponse,
  DashboardData,
  Payment,
  TreasurerStats,
  User,
  UpdateMemberRequest,
  CreateInviteRequest,
  CreateInviteResponse,
  InviteCode,
  Donation,
  CreateDonationRequest,
  PaymentFrequency,
  PaymentType,
} from '../types';

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
  (error: AxiosError) => {
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
  login: async (email: string, password: string): Promise<LoginResponse> => {
    const response = await api.post<LoginResponse>('/auth/login', { email, password });
    return response.data;
  },

  register: async (
    name: string,
    email: string,
    password: string,
    invite_code: string
  ): Promise<RegisterResponse> => {
    const response = await api.post<RegisterResponse>('/auth/register', {
      name,
      email,
      password,
      invite_code,
    });
    return response.data;
  },

  logout: async (): Promise<{ success: boolean }> => {
    const response = await api.post<{ success: boolean }>('/auth/logout');
    return response.data;
  },

  getCurrentUser: async (): Promise<{ user: User }> => {
    const response = await api.get<{ user: User }>('/auth/user');
    return response.data;
  },

  forgotPassword: async (email: string): Promise<{ success: boolean; message: string }> => {
    const response = await api.post<{ success: boolean; message: string }>('/auth/forgot-password', { email });
    return response.data;
  },

  resetPassword: async (token: string, password: string): Promise<{ success: boolean; message: string }> => {
    const response = await api.post<{ success: boolean; message: string }>('/auth/reset-password', { token, password });
    return response.data;
  },
};

// ============================================================================
// Dashboard API
// ============================================================================

export const dashboardAPI = {
  getDashboardData: async (): Promise<DashboardData> => {
    const response = await api.get<DashboardData>('/dashboard');
    return response.data;
  },
};

// ============================================================================
// Payment API
// ============================================================================

export const paymentAPI = {
  // Get payment history with pagination
  getPayments: async (limit = 50, offset = 0): Promise<{ payments: Payment[] }> => {
    const response = await api.get<{ payments: Payment[] }>('/payments', {
      params: { limit, offset },
    });
    return response.data;
  },

  // Create Stripe checkout session
  createCheckoutSession: async (
    amount: number,
    payment_type: PaymentType = 'one-time',
    notes = ''
  ): Promise<CreateCheckoutResponse> => {
    const response = await api.post<CreateCheckoutResponse>('/payments/create-checkout', {
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
  createPlan: async (
    frequency: PaymentFrequency,
    start_date: string,
    amount: number
  ): Promise<CreatePlanResponse> => {
    const response = await api.post<CreatePlanResponse>('/payment-plans', {
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
  updateProfile: async (data: Partial<User> & { current_password?: string; new_password?: string }): Promise<{ success: boolean; user: User }> => {
    const response = await api.put<{ success: boolean; user: User }>('/profile', data);
    return response.data;
  },
};

// ============================================================================
// Treasurer API (Admin/Treasurer Only)
// ============================================================================

export const treasurerAPI = {
  // Get dashboard statistics
  getStats: async (): Promise<TreasurerStats> => {
    const response = await api.get<TreasurerStats>('/treasurer/stats');
    return response.data;
  },

  // Get all members with filtering
  getMembers: async (params: Record<string, any> = {}): Promise<{ members: User[] }> => {
    const response = await api.get<{ members: User[] }>('/treasurer/members', { params });
    return response.data;
  },

  // Get single member details
  getMemberDetail: async (userId: number): Promise<{ user: User }> => {
    const response = await api.get<{ user: User }>(`/treasurer/members/${userId}`);
    return response.data;
  },

  // Update member details
  updateMember: async (
    userId: number,
    data: UpdateMemberRequest
  ): Promise<{ success: boolean; user: User }> => {
    const response = await api.put<{ success: boolean; user: User }>(
      `/treasurer/members/${userId}`,
      data
    );
    return response.data;
  },

  // Get all payments (treasurer view)
  getAllPayments: async (params: Record<string, any> = {}): Promise<{ payments: Payment[] }> => {
    const response = await api.get<{ payments: Payment[] }>('/treasurer/payments', { params });
    return response.data;
  },

  // Get reports summary
  getReportsSummary: async (): Promise<any> => {
    const response = await api.get('/treasurer/reports/summary');
    return response.data;
  },
};

// ============================================================================
// Donations API (Treasurer Only)
// ============================================================================

export const donationsAPI = {
  // Get donations list with filtering and pagination
  getDonations: async (params: Record<string, any> = {}): Promise<{ donations: Donation[] }> => {
    const response = await api.get<{ donations: Donation[] }>('/donations', { params });
    return response.data;
  },

  // Get donations summary statistics
  getSummary: async (): Promise<any> => {
    const response = await api.get('/donations/summary');
    return response.data;
  },

  // Create a manual donation entry
  createDonation: async (
    donationData: CreateDonationRequest
  ): Promise<{ success: boolean; donation: Donation }> => {
    const response = await api.post<{ success: boolean; donation: Donation }>(
      '/donations',
      donationData
    );
    return response.data;
  },
};

// ============================================================================
// Invites API (Treasurer Only)
// ============================================================================

export const invitesAPI = {
  // Get all invite codes with filtering and pagination
  getInvites: async (params: Record<string, any> = {}): Promise<{ invites: InviteCode[] }> => {
    const response = await api.get<{ invites: InviteCode[] }>('/invites', { params });
    return response.data;
  },

  // Get invite statistics
  getStats: async (): Promise<any> => {
    const response = await api.get('/invites/stats');
    return response.data;
  },

  // Create a new invite code
  createInvite: async (inviteData: CreateInviteRequest): Promise<CreateInviteResponse> => {
    const response = await api.post<CreateInviteResponse>('/invites', inviteData);
    return response.data;
  },

  // Delete an unused invite code
  deleteInvite: async (inviteId: number): Promise<{ success: boolean }> => {
    const response = await api.delete<{ success: boolean }>(`/invites/${inviteId}`);
    return response.data;
  },
};

// ============================================================================
// Export the axios instance for custom requests
// ============================================================================

export default api;
