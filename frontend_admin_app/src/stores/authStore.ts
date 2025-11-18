import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { User, AuthState, LoginCredentials } from '@/types'
import { authApi } from '@/lib/api'

interface AuthStore extends AuthState {
  login: (credentials: LoginCredentials) => Promise<void>
  logout: () => void
  refreshToken: () => Promise<void>
  setUser: (user: User) => void
  setAuth: (token: string, user: any) => void
  clearError: () => void
  checkAuthentication: () => boolean
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isLoading: false,
      error: null,
      
      checkAuthentication: () => {
        console.log('🔐 Checking authentication...')
        
        // With Zustand persist, the state is automatically restored
        // We just need to check if it exists
        const { user, token } = get()
        
        if (user && token) {
          console.log('✅ Found stored auth data:', user.email)
          return true
        }
        
        console.log('❌ No valid authentication found')
        return false
      },

      login: async (credentials: LoginCredentials) => {
        try {
          set({ isLoading: true, error: null })
          
          console.log('🔐 Attempting login...', credentials.email)
          
          // Use real backend authentication
          const response = await authApi.login(credentials)
          const { user, access_token } = response.data
          
          console.log('✅ Login successful', user)
          
          // Ensure the user object has all needed properties for compatibility
          const enhancedUser = {
            ...user,
            // Add backward compatibility fields
            isActive: user.is_active ?? true,
            createdAt: user.created_at || new Date().toISOString(),
            updatedAt: user.updated_at || new Date().toISOString(),
            // Ensure permissions array exists
            permissions: user.permissions || []
          }
          
          // Zustand persist middleware will automatically save to localStorage
          set({
            user: enhancedUser,
            token: access_token,
            isLoading: false,
            error: null,
          })
          
        } catch (error: any) {
          console.error('❌ Login error:', error)
          const errorMessage = error.response?.data?.detail || error.message || 'Login failed'
          set({
            error: errorMessage,
            isLoading: false,
          })
          throw error
        }
      },

      logout: () => {
        console.log('🚪 Logging out...')
        localStorage.removeItem('tsh-erp-auth')
        set({
          user: null,
          token: null,
          error: null,
        })
      },

      refreshToken: async () => {
        try {
          const { token } = get()
          if (!token) return

          const response = await authApi.refreshToken(token)
          const { user, access_token } = response.data
          
          set({
            user,
            token: access_token,
          })
        } catch (error) {
          // If refresh fails, logout user
          set({
            user: null,
            token: null,
            error: 'Session expired',
          })
          throw error
        }
      },

      setUser: (user: User) => {
        set({ user })
      },

      setAuth: (token: string, user: any) => {
        console.log('🔐 Setting auth from magic link...', user.email)
        const enhancedUser = {
          ...user,
          isActive: user.is_active ?? true,
          createdAt: user.created_at || new Date().toISOString(),
          updatedAt: user.updated_at || new Date().toISOString(),
          permissions: user.permissions || []
        }
        set({
          user: enhancedUser,
          token,
          isLoading: false,
          error: null,
        })
      },

      clearError: () => {
        set({ error: null })
      },
    }),
    {
      name: 'tsh-erp-auth', // localStorage key
      partialize: (state) => ({
        user: state.user,
        token: state.token,
      }), // Only persist user and token, not loading/error states
    }
  )
)
