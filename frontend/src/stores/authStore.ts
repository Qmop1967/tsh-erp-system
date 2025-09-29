import { create } from 'zustand'
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
  // Temporarily disable persist for demo mode
  (set, get) => ({
      user: null,
      token: null,
      isLoading: false,
      error: null,
      
      checkAuthentication: () => {
        console.log('🔐 [Demo Mode] Always authenticated')
        
        // Force demo user setup every time
        const demoUser = {
          id: 1,
          name: 'Demo User',
          email: 'demo@tsh.sale',
          role: 'Admin',
          role_id: 1,
          isActive: true,
          is_active: true,
          createdAt: new Date().toISOString(),
          created_at: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          permissions: ['admin', 'dashboard.view', 'users.view', 'hr.view']
        }
        
        // Always set the demo user
        set({
          user: demoUser,
          token: 'demo-token-123',
          error: null,
          isLoading: false
        })
        
        return true // Always allow access for demo
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
    })
)
