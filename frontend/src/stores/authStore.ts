import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { User, AuthState, LoginCredentials } from '@/types'
import { authApi } from '@/lib/api'

interface AuthStore extends AuthState {
  login: (credentials: LoginCredentials) => Promise<void>
  logout: () => void
  refreshToken: () => Promise<void>
  setUser: (user: User) => void
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
        const state = get()
        const hasUser = !!state.user
        const hasToken = !!state.token
        const result = hasUser && hasToken
        console.log('🔐 [checkAuthentication]', { hasUser, hasToken, result, user: state.user?.name })
        return result
      },

      login: async (credentials: LoginCredentials) => {
        try {
          set({ isLoading: true, error: null })
          
          // Use real backend authentication
          const response = await authApi.login(credentials)
          const { user, access_token } = response.data
          
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
          
          set({
            user: enhancedUser,
            token: access_token,
            isLoading: false,
            error: null,
          })
          
        } catch (error: any) {
          console.error('Login error:', error)
          const errorMessage = error.response?.data?.detail || error.message || 'Login failed'
          set({
            error: errorMessage,
            isLoading: false,
          })
          throw error
        }
      },

      logout: () => {
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

      clearError: () => {
        set({ error: null })
      },
    }),
    {
      name: 'tsh-erp-auth',
      partialize: (state) => {
        const persisted = {
          user: state.user,
          token: state.token,
        }
        console.log('🔐 [Persist] Saving to localStorage:', persisted)
        return persisted
      },
      onRehydrateStorage: () => (state, error) => {
        if (error) {
          console.error('🔐 [Persist] Rehydration error:', error)
        } else {
          console.log('🔐 [Persist] Rehydrated state:', state)
        }
      },
    }
  )
)
