import { BrowserRouter } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import { useLanguageStore } from '@/stores/languageStore'

function App() {
  // Test store access
  let storeError = null
  let authData = null
  let langData = null
  
  try {
    authData = useAuthStore()
    langData = useLanguageStore()
  } catch (error) {
    storeError = error
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <h1 className="text-4xl font-bold text-gray-900 mb-4">
        🔍 TSH ERP System - Store Test
      </h1>
      
      <div className="space-y-4">
        <div className="bg-white p-6 rounded-lg shadow-md border">
          <h2 className="text-xl font-semibold mb-4">Store Status</h2>
          
          {storeError ? (
            <div className="text-red-600">
              <strong>❌ Store Error:</strong> {storeError.message}
            </div>
          ) : (
            <div className="space-y-2">
              <div className="text-green-600">
                <strong>✅ Auth Store:</strong> Working
                <div className="text-sm text-gray-600 ml-4">
                  User: {authData?.user ? 'Logged in' : 'Not logged in'}
                </div>
              </div>
              <div className="text-green-600">
                <strong>✅ Language Store:</strong> Working
                <div className="text-sm text-gray-600 ml-4">
                  Language: {langData?.language || 'Not set'}
                  RTL: {langData?.isRTL ? 'Yes' : 'No'}
                </div>
              </div>
            </div>
          )}
        </div>
        
        <div className="bg-blue-50 p-4 border border-blue-200 rounded">
          <p className="text-blue-800">
            If stores work, testing router next...
          </p>
        </div>
      </div>
    </div>
  )
}

export default App
