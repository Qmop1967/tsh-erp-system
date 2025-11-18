import React from 'react';
import { ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const ZohoIntegrationSimple: React.FC = () => {
  const navigate = useNavigate();
  
  console.log('ZohoIntegrationSimple rendering');

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <button
            onClick={() => navigate('/settings')}
            className="flex items-center gap-2 text-gray-600 hover:text-gray-800 mb-4"
          >
            <ArrowLeft className="w-5 h-5" />
            Back to Settings
          </button>
          <h1 className="text-3xl font-bold text-gray-800">Zoho Integration</h1>
          <p className="text-gray-600">Sync data with Zoho CRM, Books & Inventory</p>
        </div>

        {/* Simple Content */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Zoho Configuration</h2>
          <p className="text-gray-600">
            This is a simplified version of the Zoho integration page.
            The component is loading correctly!
          </p>
        </div>
      </div>
    </div>
  );
};

export default ZohoIntegrationSimple;
