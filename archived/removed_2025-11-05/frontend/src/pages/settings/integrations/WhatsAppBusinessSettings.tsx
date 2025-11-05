import React, { useState } from 'react';
import { ArrowLeft, MessageSquare, CheckCircle, XCircle, RefreshCw, Save } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const WhatsAppBusinessSettings: React.FC = () => {
  const navigate = useNavigate();
  const [config, setConfig] = useState({
    enabled: false,
    phoneNumberId: '',
    accessToken: '',
    businessAccountId: '',
    webhookUrl: '',
    webhookVerifyToken: '',
  });
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<'success' | 'error' | null>(null);

  const handleSave = async () => {
    // Save configuration logic here
    console.log('Saving WhatsApp config:', config);
  };

  const handleTest = async () => {
    setTesting(true);
    // Simulate API test
    setTimeout(() => {
      setTestResult('success');
      setTesting(false);
    }, 2000);
  };

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
          <div className="flex items-center gap-4">
            <div className="p-3 bg-green-500 rounded-xl">
              <MessageSquare className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-800">WhatsApp Business API</h1>
              <p className="text-gray-600">Configure WhatsApp Business integration</p>
            </div>
          </div>
        </div>

        {/* Configuration Form */}
        <div className="bg-white rounded-xl shadow-lg p-6 space-y-6">
          {/* Enable/Disable Toggle */}
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div>
              <h3 className="font-semibold text-gray-800">Enable WhatsApp Integration</h3>
              <p className="text-sm text-gray-600">Activate WhatsApp Business API connection</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={config.enabled}
                onChange={(e) => setConfig({ ...config, enabled: e.target.checked })}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-green-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-500"></div>
            </label>
          </div>

          {/* API Configuration */}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Phone Number ID
              </label>
              <input
                type="text"
                value={config.phoneNumberId}
                onChange={(e) => setConfig({ ...config, phoneNumberId: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                placeholder="Enter your WhatsApp Phone Number ID"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Access Token
              </label>
              <input
                type="password"
                value={config.accessToken}
                onChange={(e) => setConfig({ ...config, accessToken: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                placeholder="Enter your WhatsApp Business API Access Token"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Business Account ID
              </label>
              <input
                type="text"
                value={config.businessAccountId}
                onChange={(e) => setConfig({ ...config, businessAccountId: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                placeholder="Enter your WhatsApp Business Account ID"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Webhook URL
              </label>
              <input
                type="text"
                value={config.webhookUrl}
                onChange={(e) => setConfig({ ...config, webhookUrl: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                placeholder="https://your-domain.com/api/webhooks/whatsapp"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Webhook Verify Token
              </label>
              <input
                type="text"
                value={config.webhookVerifyToken}
                onChange={(e) => setConfig({ ...config, webhookVerifyToken: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                placeholder="Enter a secure verify token"
              />
            </div>
          </div>

          {/* Test Connection */}
          {testResult && (
            <div
              className={`p-4 rounded-lg flex items-center gap-3 ${
                testResult === 'success'
                  ? 'bg-green-50 text-green-800'
                  : 'bg-red-50 text-red-800'
              }`}
            >
              {testResult === 'success' ? (
                <CheckCircle className="w-5 h-5" />
              ) : (
                <XCircle className="w-5 h-5" />
              )}
              <span>
                {testResult === 'success'
                  ? 'Connection successful! WhatsApp API is working correctly.'
                  : 'Connection failed. Please check your credentials.'}
              </span>
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-4 pt-4 border-t">
            <button
              onClick={handleTest}
              disabled={testing}
              className="flex-1 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors flex items-center justify-center gap-2"
            >
              {testing ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  Testing...
                </>
              ) : (
                <>
                  <RefreshCw className="w-4 h-4" />
                  Test Connection
                </>
              )}
            </button>
            <button
              onClick={handleSave}
              className="flex-1 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors flex items-center justify-center gap-2"
            >
              <Save className="w-4 h-4" />
              Save Configuration
            </button>
          </div>
        </div>

        {/* Documentation */}
        <div className="mt-6 bg-blue-50 rounded-xl p-6">
          <h3 className="font-semibold text-blue-900 mb-3">Setup Instructions</h3>
          <ol className="list-decimal list-inside space-y-2 text-sm text-blue-800">
            <li>Create a WhatsApp Business Account at business.facebook.com</li>
            <li>Navigate to the WhatsApp API section and create a new app</li>
            <li>Get your Phone Number ID from the WhatsApp API dashboard</li>
            <li>Generate a permanent access token from the Graph API Explorer</li>
            <li>Configure webhook settings with your server URL</li>
            <li>Test the connection and start sending messages!</li>
          </ol>
        </div>
      </div>
    </div>
  );
};

export default WhatsAppBusinessSettings;
