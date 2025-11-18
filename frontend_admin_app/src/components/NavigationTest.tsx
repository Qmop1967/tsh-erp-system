import { useState } from 'react'
import { useAuthStore } from '@/stores/authStore'

export function NavigationTest() {
  const { user, login, checkAuthentication } = useAuthStore()
  const [isLoading, setIsLoading] = useState(false)
  const [loginResult, setLoginResult] = useState('')
  
  const isAuthenticated = checkAuthentication()

  const testLogin = async () => {
    setIsLoading(true)
    try {
      await login({ email: 'admin@tsh-erp.com', password: 'admin123' })
      setLoginResult('Login successful!')
    } catch (error) {
      setLoginResult(`Login failed: ${error}`)
    }
    setIsLoading(false)
  }

  return (
    <div className="fixed top-0 left-0 w-full h-full bg-white z-50 overflow-y-auto">
      <div className="p-6 max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-6 text-gray-900">🔍 Navigation Debug Test</h1>
      
      <div className="space-y-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-700">Authentication Status</h3>
          <p>Authenticated: {isAuthenticated ? 'Yes' : 'No'}</p>
        </div>

        {!isAuthenticated && (
          <div>
            <button
              onClick={testLogin}
              disabled={isLoading}
              className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
            >
              {isLoading ? 'Logging in...' : 'Test Login as Admin'}
            </button>
            {loginResult && (
              <p className={`mt-2 ${loginResult.includes('successful') ? 'text-green-600' : 'text-red-600'}`}>
                {loginResult}
              </p>
            )}
          </div>
        )}

        {user && (
          <div>
            <h3 className="text-lg font-semibold text-gray-700">User Information</h3>
            <div className="bg-gray-100 p-3 rounded">
              <p><strong>Name:</strong> {user.name}</p>
              <p><strong>Email:</strong> {user.email}</p>
              <p><strong>Role:</strong> {user.role}</p>
              <p><strong>Branch:</strong> {user.branch}</p>
            </div>
          </div>
        )}

        {user?.permissions && (
          <div>
            <h3 className="text-lg font-semibold text-gray-700">Permissions</h3>
            <div className="bg-gray-100 p-3 rounded max-h-40 overflow-y-auto">
              <ul className="text-sm">
                {user.permissions.map((permission, index) => (
                  <li key={index} className="py-1">
                    <span className={`inline-block w-3 h-3 rounded-full mr-2 ${
                      permission === 'admin' || permission === 'inventory.view' || permission === 'items.view'
                        ? 'bg-green-500'
                        : 'bg-blue-500'
                    }`}></span>
                    {permission}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {user && (
          <div>
            <h3 className="text-lg font-semibold text-gray-700">Permission Checks</h3>
            <div className="bg-gray-100 p-3 rounded">
              <p>Has 'admin' permission: {user.permissions?.includes('admin') ? '✅ Yes' : '❌ No'}</p>
              <p>Has 'inventory.view' permission: {user.permissions?.includes('inventory.view') ? '✅ Yes' : '❌ No'}</p>
              <p>Has 'items.view' permission: {user.permissions?.includes('items.view') ? '✅ Yes' : '❌ No'}</p>
              <p>Has 'dashboard.view' permission: {user.permissions?.includes('dashboard.view') ? '✅ Yes' : '❌ No'}</p>
            </div>
          </div>
        )}
      </div>
      </div>
    </div>
  )
}
