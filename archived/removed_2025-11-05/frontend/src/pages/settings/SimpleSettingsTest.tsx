import React from 'react';

const SimpleSettingsTest: React.FC = () => {
  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-4">Settings Test Page</h1>
      <p className="text-gray-600 mb-4">If you can see this, the settings route is working!</p>
      
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
        <h2 className="text-lg font-semibold text-blue-800">✅ Frontend Route: Working</h2>
        <p className="text-blue-700">The settings route is properly configured and accessible.</p>
      </div>

      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
        <h2 className="text-lg font-semibold text-yellow-800">🔧 API Test</h2>
        <button 
          onClick={async () => {
            try {
              const response = await fetch('http://localhost:8000/api/settings/system/info');
              const data = await response.json();
              alert(`API Response: ${JSON.stringify(data, null, 2)}`);
            } catch (error) {
              alert(`API Error: ${error}`);
            }
          }}
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
        >
          Test API Connection
        </button>
      </div>
      
      <div className="mt-4">
        <p className="text-sm text-gray-500">
          Current URL: {window.location.href}
        </p>
      </div>
    </div>
  );
};

export default SimpleSettingsTest;
