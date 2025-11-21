import { create } from 'zustand';
import { authAPI } from '../services/api';

const useAuthStore = create((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: true,
  error: null,

  // Initialize auth state by checking if user is already logged in
  initializeAuth: async () => {
    try {
      set({ isLoading: true, error: null });
      const data = await authAPI.getCurrentUser();
      set({
        user: data.user,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (error) {
      // User is not authenticated
      set({
        user: null,
        isAuthenticated: false,
        isLoading: false,
      });
    }
  },

  // Login action
  login: async (email, password) => {
    try {
      set({ isLoading: true, error: null });
      const data = await authAPI.login(email, password);
      set({
        user: data.user,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      });
      return { success: true };
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Login failed';
      set({
        error: errorMessage,
        isLoading: false,
      });
      return { success: false, error: errorMessage };
    }
  },

  // Register action
  register: async (name, email, password, invite_code) => {
    try {
      set({ isLoading: true, error: null });
      await authAPI.register(name, email, password, invite_code);
      set({
        isLoading: false,
        error: null,
      });
      return { success: true };
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Registration failed';
      set({
        error: errorMessage,
        isLoading: false,
      });
      return { success: false, error: errorMessage };
    }
  },

  // Logout action
  logout: async () => {
    try {
      await authAPI.logout();
      set({
        user: null,
        isAuthenticated: false,
        error: null,
      });
      return { success: true };
    } catch (error) {
      // Even if API call fails, clear local state
      set({
        user: null,
        isAuthenticated: false,
        error: null,
      });
      return { success: true };
    }
  },

  // Update user data (after profile update)
  updateUser: (userData) => set({ user: userData }),

  // Clear error
  clearError: () => set({ error: null }),
}));

export default useAuthStore;
