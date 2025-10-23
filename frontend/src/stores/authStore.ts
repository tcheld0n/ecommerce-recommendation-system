import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { User } from '@/types/user'
import { authService } from '@/services/authService'

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
}

interface AuthActions {
  login: (email: string, password: string) => Promise<void>
  register: (userData: any) => Promise<void>
  logout: () => void
  getCurrentUser: () => Promise<void>
  updateUser: (userData: any) => Promise<void>
  clearError: () => void
}

export const useAuthStore = create<AuthState & AuthActions>()(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null })
        try {
          const tokens = await authService.login({ email, password })
          authService.setTokens(tokens)
          
          const user = await authService.getCurrentUser()
          set({ user, isAuthenticated: true, isLoading: false })
        } catch (error: any) {
          set({ 
            error: error.response?.data?.detail || 'Login failed', 
            isLoading: false 
          })
          throw error
        }
      },

      register: async (userData: any) => {
        set({ isLoading: true, error: null })
        try {
          const tokens = await authService.register(userData)
          authService.setTokens(tokens)
          
          const user = await authService.getCurrentUser()
          set({ user, isAuthenticated: true, isLoading: false })
        } catch (error: any) {
          set({ 
            error: error.response?.data?.detail || 'Registration failed', 
            isLoading: false 
          })
          throw error
        }
      },

      logout: () => {
        authService.clearTokens()
        set({ user: null, isAuthenticated: false, error: null })
      },

      getCurrentUser: async () => {
        if (!authService.isAuthenticated()) {
          return
        }

        set({ isLoading: true })
        try {
          const user = await authService.getCurrentUser()
          set({ user, isAuthenticated: true, isLoading: false })
        } catch (error) {
          authService.clearTokens()
          set({ user: null, isAuthenticated: false, isLoading: false })
        }
      },

      updateUser: async (userData: any) => {
        set({ isLoading: true, error: null })
        try {
          const user = await authService.updateUser(userData)
          set({ user, isLoading: false })
        } catch (error: any) {
          set({ 
            error: error.response?.data?.detail || 'Update failed', 
            isLoading: false 
          })
          throw error
        }
      },

      clearError: () => set({ error: null })
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ 
        user: state.user, 
        isAuthenticated: state.isAuthenticated 
      })
    }
  )
)
