import React, { useState } from 'react'
import { useAuthStore } from '../stores/authStore'

export function DebugLogin() {
  const [logs, setLogs] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const { login, user, token, error } = useAuthStore()

  const addLog = (message: string) => {
    const timestamp = new Date().toLocaleTimeString()
    setLogs(prev => [...prev, `[${timestamp}] ${message}`])
    console.log(message)
  }

  const testLogin = async () => {
    setLoading(true)
    setLogs([])
    
    try {
      addLog('🚀 Starting login test...')
      addLog('📧 Email: test.admin@tsh.com')
      addLog('🔒 Password: admin123')
      
      addLog('📡 Calling login API...')
      await login({ email: 'test.admin@tsh.com', password: 'admin123' })
      
      addLog('✅ Login successful!')
      
      // Wait a moment for state to update
      setTimeout(() => {
        const currentUser = useAuthStore.getState().user
        const currentToken = useAuthStore.getState().token
        const isAuth = useAuthStore.getState().isAuthenticated
        
        addLog(`👤 User after login: ${currentUser ? JSON.stringify(currentUser, null, 2) : 'Still null'}`)
        addLog(`🔑 Token after login: ${currentToken ? currentToken.substring(0, 20) + '...' : 'Still undefined'}`)
        addLog(`🔐 Is Authenticated: ${isAuth}`)
        
        if (isAuth) {
          addLog('🎉 Authentication successful! Should redirect to dashboard now.')
          // Try manual navigation
          window.location.href = '/dashboard'
        } else {
          addLog('❌ Authentication failed - user not properly authenticated')
        }
      }, 100)
      
    } catch (err: any) {
      addLog(`❌ Login failed: ${err.message}`)
      addLog(`📋 Full error: ${JSON.stringify(err, null, 2)}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">🔍 Login Debug Tool</h1>
        
        <div className="bg-white p-6 rounded-lg shadow-lg mb-6">
          <h2 className="text-xl font-semibold mb-4">Current Auth State</h2>
          <div className="space-y-2 text-sm">
            <p><strong>User:</strong> {user ? JSON.stringify(user, null, 2) : 'Not logged in'}</p>
            <p><strong>Token:</strong> {token ? `${token.substring(0, 20)}...` : 'No token'}</p>
            <p><strong>Error:</strong> {error || 'No error'}</p>
            <p><strong>LocalStorage:</strong> {localStorage.getItem('tsh-erp-auth') ? `Present (${localStorage.getItem('tsh-erp-auth')?.substring(0, 50)}...)` : 'Not present'}</p>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-lg mb-6">
          <div className="flex gap-4">
            <button
              onClick={testLogin}
              disabled={loading}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? '🔄 Testing Login...' : '🧪 Test Login'}
            </button>
            
            <button
              onClick={() => {
                localStorage.removeItem('tsh-erp-auth')
                window.location.reload()
              }}
              className="bg-red-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-red-700"
            >
              🗑️ Clear Storage & Reload
            </button>
          </div>
        </div>

        <div className="bg-black text-green-400 p-6 rounded-lg shadow-lg font-mono text-sm">
          <h3 className="text-lg font-semibold mb-4 text-white">📋 Debug Logs</h3>
          <div className="space-y-1 max-h-96 overflow-y-auto">
            {logs.length === 0 ? (
              <p className="text-gray-500">Click "Test Login" to see debug logs...</p>
            ) : (
              logs.map((log, index) => (
                <div key={index} className="whitespace-pre-wrap">{log}</div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
