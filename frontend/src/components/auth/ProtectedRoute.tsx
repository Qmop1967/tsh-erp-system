import { Navigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'

interface ProtectedRouteProps {
  children: React.ReactNode
  requiredPermissions?: string[]
}

export function ProtectedRoute({ children, requiredPermissions }: ProtectedRouteProps) {
  const { user, token } = useAuthStore()

  console.log('ProtectedRoute - user:', user, 'token:', token)

  // TEMPORARY: Bypass authentication for demo/testing
  // Comment out these lines to restore full authentication
  console.log('DEMO MODE: Bypassing authentication')
  return <>{children}</>

  // Original authentication logic (uncomment to restore)
  /*
  if (!user || !token) {
    console.log('No user or token, redirecting to login')
    return <Navigate to="/login" replace />
  }

  // Check permissions if required
  if (requiredPermissions && requiredPermissions.length > 0) {
    const hasPermission = requiredPermissions.some(permission => 
      user.permissions?.includes(permission)
    )
    
    if (!hasPermission) {
      return (
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Access Denied</h1>
            <p className="text-gray-600">You don't have permission to access this page.</p>
          </div>
        </div>
      )
    }
  }

  return <>{children}</>
  */
}
