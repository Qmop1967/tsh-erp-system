import { Navigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'

interface ProtectedRouteProps {
  children: React.ReactNode
  requiredPermissions?: string[]
}

export function ProtectedRoute({ children, requiredPermissions }: ProtectedRouteProps) {
  const { user, token } = useAuthStore()

  console.log('ProtectedRoute - user:', user, 'token:', token)

  // Check authentication
  if (!user || !token) {
    console.log('No user or token, redirecting to login')
    return <Navigate to="/login" replace />
  }

  // Check permissions if required
  if (requiredPermissions && requiredPermissions.length > 0) {
    const hasPermission = requiredPermissions.some(permission => 
      user.permissions?.includes(permission) || user.permissions?.includes('admin')
    )
    
    if (!hasPermission) {
      return (
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Access Denied</h1>
            <p className="text-gray-600">You don't have permission to access this page.</p>
            <p className="text-sm text-gray-500 mt-2">Required: {requiredPermissions.join(', ')}</p>
            <p className="text-sm text-gray-500">Your permissions: {user.permissions?.join(', ')}</p>
          </div>
        </div>
      )
    }
  }

  return <>{children}</>
}
