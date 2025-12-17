// ============================================================================
// User Types
// ============================================================================

export type UserRole = 'member' | 'treasurer' | 'president' | '1st vice' | '2nd vice' | 'secretary';

export type FinancialStatus = 'financial' | 'not financial';

export interface User {
  id: number;
  name: string;
  email: string;
  role: UserRole;
  financial_status: FinancialStatus;
  active: boolean;
  created_at: string;
  initiation_date?: string;
  dues_current_semester?: boolean;
  is_neophyte?: boolean;
  total_paid?: number;
  has_active_plan?: boolean;
  plan_balance?: number;
}

// ============================================================================
// Authentication Types
// ============================================================================

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  success: boolean;
  message: string;
  user: User;
}

export interface RegisterRequest {
  name: string;
  email: string;
  password: string;
  invite_code: string;
}

export interface RegisterResponse {
  success: boolean;
  message: string;
  user: User;
}

// ============================================================================
// Auth Store Types
// ============================================================================

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  initializeAuth: () => Promise<void>;
  login: (email: string, password: string) => Promise<{ success: boolean; error?: string }>;
  register: (name: string, email: string, password: string, invite_code: string) => Promise<{ success: boolean; error?: string }>;
  logout: () => Promise<{ success: boolean }>;
  updateUser: (userData: User) => void;
  clearError: () => void;
}

// ============================================================================
// Payment Types
// ============================================================================

export type PaymentType = 'one-time' | 'installment';
export type PaymentStatus = 'pending' | 'completed' | 'failed';

export interface Payment {
  id: number;
  user_id: number;
  user_name?: string;
  user_email?: string;
  amount: number | string;
  payment_type: PaymentType;
  status: PaymentStatus;
  stripe_session_id?: string;
  notes?: string;
  created_at: string;
  date?: string;
  method?: string;
}

export interface CreateCheckoutRequest {
  amount: number;
  payment_type: PaymentType;
  notes?: string;
}

export interface CreateCheckoutResponse {
  success: boolean;
  checkout_url: string;
  session_id: string;
}

// ============================================================================
// Payment Plan Types
// ============================================================================

export type PaymentFrequency = 'weekly' | 'biweekly' | 'monthly';

export interface PaymentPlan {
  id: number;
  user_id: number;
  frequency: PaymentFrequency;
  start_date: string;
  amount: number;
  active: boolean;
  created_at: string;
}

export interface CreatePlanRequest {
  frequency: PaymentFrequency;
  start_date: string;
  amount: number;
}

export interface CreatePlanResponse {
  success: boolean;
  plan: PaymentPlan;
  message: string;
}

// ============================================================================
// Invite Types
// ============================================================================

export interface InviteCode {
  id: number;
  code: string;
  role: UserRole;
  used: boolean;
  used_by?: number;
  used_at?: string;
  expires_at?: string;
  created_by: number;
  created_at: string;
}

export interface CreateInviteRequest {
  email?: string;
  role: UserRole;
  expires_at?: string;
  expires_in_days?: number;
}

export interface CreateInviteResponse {
  success: boolean;
  invite: InviteCode;
  message: string;
}

// ============================================================================
// Dashboard Types
// ============================================================================

export interface DashboardData {
  user: User;
  name: string;
  status: FinancialStatus;
  financial_status: FinancialStatus;
  initiation_date?: string;
  plan?: PaymentPlan & { total_amount: number };
  percent_paid?: number;
  remaining_balance?: number;
  payments?: Array<{
    date: string;
    amount: number;
    method: string;
    payment_type: PaymentType;
  }>;
  upcoming_payments: Payment[];
  payment_plan?: PaymentPlan;
}

// ============================================================================
// Treasurer Types
// ============================================================================

export interface TreasurerStats {
  total_members: number;
  financial_members: number;
  total_collected_semester: number;
  pending_payments: number;
}

export interface UpdateMemberRequest {
  name?: string;
  email?: string;
  role?: UserRole;
  financial_status?: FinancialStatus;
  initiation_date?: string;
  active?: boolean;
}

// ============================================================================
// Donation Types
// ============================================================================

export interface Donation {
  id: number;
  amount: number;
  donor_name?: string;
  donor_email?: string;
  method?: string;
  anonymous?: boolean;
  date?: string;
  notes?: string;
  created_at: string;
}

export interface CreateDonationRequest {
  amount: number;
  donor_name?: string;
  donor_email?: string;
  method?: string;
  anonymous?: boolean;
  notes?: string;
}

// ============================================================================
// API Response Types
// ============================================================================

export interface ApiError {
  error: string;
}

export interface ApiSuccess {
  success: boolean;
  message: string;
}

// ============================================================================
// Form Data Types
// ============================================================================

export interface LoginFormData {
  email: string;
  password: string;
}

export interface RegisterFormData {
  name: string;
  email: string;
  password: string;
  confirmPassword: string;
  invite_code: string;
}

export interface PaymentPlanFormData {
  frequency: PaymentFrequency;
  start_date: string;
  amount: number;
}

export interface InviteFormData {
  role: UserRole;
  expires_at?: string;
}