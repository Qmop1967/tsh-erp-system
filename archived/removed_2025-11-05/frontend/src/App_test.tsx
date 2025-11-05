// React is auto-imported by the JSX transform in Vite
// import React from 'react'

function App() {
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <h1 className="text-4xl font-bold text-gray-900 mb-4">
        🔍 TSH ERP System - Debug Mode
      </h1>
      <p className="text-gray-600 mb-8">
        Testing basic React rendering...
      </p>
      
      <div className="bg-white p-6 rounded-lg shadow-md border">
        <h2 className="text-xl font-semibold text-green-600">✅ Success!</h2>
        <p className="text-gray-600 mt-2">
          React app is rendering correctly. The issue might be with:
        </p>
        <ul className="mt-4 space-y-2 text-sm text-gray-700">
          <li>• Router configuration</li>
          <li>• Component imports</li>
          <li>• Store initialization</li>
          <li>• CSS loading</li>
        </ul>
      </div>
      
      <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded">
        <p className="text-blue-800">
          <strong>Next step:</strong> Add components one by one to identify the issue.
        </p>
      </div>
    </div>
  )
}

export default App
