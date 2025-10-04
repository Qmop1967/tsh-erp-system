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
  (set, get) => ({
      user: null,
      token: null,
      isLoading: false,
      error: null,
      
      checkAuthentication: () => {
        console.log('🔐 Checking authentication...')
        
        // Check if we have stored auth data
        const authData = localStorage.getItem('tsh-erp-auth')
        if (authData) {
          try {
            const { state } = JSON.parse(authData)
            if (state?.token && state?.user) {
              console.log('✅ Found stored auth data')
              set({
                user: state.user,
                token: state.token,
                error: null,
                isLoading: false
              })
              return true
            }
          } catch (error) {
            console.error('Error parsing auth data:', error)
            localStorage.removeItem('tsh-erp-auth')
          }
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
          
          // Save to localStorage
          localStorage.setItem('tsh-erp-auth', JSON.stringify({
            state: {
              user: enhancedUser,
              token: access_token,
              isLoading: false,
              error: null
            },
            version: 0
          }))
          
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

      clearError: () => {
        set({ error: null })
      },
    })
)
