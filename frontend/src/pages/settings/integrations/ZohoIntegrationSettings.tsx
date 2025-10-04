import React, { useState } from 'react';
import { ArrowLeft, Database, CheckCircle, XCircle, RefreshCw, Save, Download, Settings } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import ZohoSyncMappingsAdvanced from './ZohoSyncMappingsAdvanced';

interface ZohoModule {
  name: string;
  enabled: boolean;
  lastSync: string | null;
}

const ZohoIntegrationSettings: React.FC = () => {
  console.log('ZohoIntegrationSettings component mounting...');
  const navigate = useNavigate();
  const [config, setConfig] = useState({
    enabled: true,
    clientId: '1000.SLY5X93N58VN46HXQIIZSOQKG8J3ZJ',
    clientSecret: '0581c245cd951e1453042ff2bcf223768e128fed9f',
    refreshToken: '1000.442cace0b2ef482fd2003d0f9282a27c.924fb7daaeb23f1994d96766cf563d4c',
    organizationId: '748369814',
  });
  
  const [modules, setModules] = useState<ZohoModule[]>([
    { name: 'Zoho CRM', enabled: true, lastSync: '2025-10-04 10:30:00' },
    { name: 'Zoho Books', enabled: true, lastSync: '2025-10-04 10:25:00' },
    { name: 'Zoho Inventory', enabled: true, lastSync: '2025-10-04 10:20:00' },
    { name: 'Zoho Invoice', enabled: false, lastSync: null },
  ]);

  const [syncing, setSyncing] = useState(false);
  const [syncResult, setSyncResult] = useState<'success' | 'error' | null>(null);
  const [activeView, setActiveView] = useState<'config' | 'mappings'>('config');

  const handleSync = async (moduleName: string) => {
    setSyncing(true);
    try {
      const response = await fetch(`http://localhost:8000/api/settings/integrations/zoho/modules/${encodeURIComponent(moduleName)}/sync`, {
        method: 'POST',
      });
      
      const data = await response.json();
      
      if (data.status === 'success') {
        const updatedModules = modules.map(m => 
          m.name === moduleName 
            ? { ...m, lastSync: new Date().toISOString().replace('T', ' ').substring(0, 19) }
            : m
        );
        setModules(updatedModules);
        setSyncResult('success');
      } else {
        setSyncResult('error');
      }
    } catch (error) {
      console.error('Error syncing module:', error);
      setSyncResult('error');
    } finally {
      setSyncing(false);
      setTimeout(() => setSyncResult(null), 3000);
    }
  };

  const handleSave = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/settings/integrations/zoho', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          enabled: config.enabled,
          client_id: config.clientId,
          client_secret: config.clientSecret,
          refresh_token: config.refreshToken,
          organization_id: config.organizationId,
        }),
      });
      
      const data = await response.json();
      
      if (data.status === 'success') {
        setSyncResult('success');
        setTimeout(() => setSyncResult(null), 3000);
      } else {
        setSyncResult('error');
        setTimeout(() => setSyncResult(null), 3000);
      }
    } catch (error) {
      console.error('Error saving Zoho config:', error);
      setSyncResult('error');
      setTimeout(() => setSyncResult(null), 3000);
    }
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
            <div className="p-3 bg-red-500 rounded-xl">
              <Database className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-800">Zoho Integration</h1>
              <p className="text-gray-600">Sync data with Zoho CRM, Books & Inventory</p>
            </div>
          </div>
        </div>

        {/* View Tabs */}
        <div className="bg-white rounded-t-xl shadow-lg mb-0">
          <div className="flex border-b border-gray-200">
            <button
              onClick={() => setActiveView('config')}
              className={`flex-1 px-6 py-4 font-medium transition-colors ${
                activeView === 'config'
                  ? 'text-red-600 border-b-2 border-red-600 bg-red-50'
                  : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
              }`}
            >
              <div className="flex items-center justify-center gap-2">
                <Database className="w-4 h-4" />
                Configuration
              </div>
            </button>
            <button
              onClick={() => setActiveView('mappings')}
              className={`flex-1 px-6 py-4 font-medium transition-colors ${
                activeView === 'mappings'
                  ? 'text-red-600 border-b-2 border-red-600 bg-red-50'
                  : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
              }`}
            >
              <div className="flex items-center justify-center gap-2">
                <Settings className="w-4 h-4" />
                Sync Mappings
              </div>
            </button>
          </div>
        </div>

        {/* Configuration View */}
        {activeView === 'config' && (
          <>
        {/* Main Toggle */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div>
              <h3 className="font-semibold text-gray-800">Enable Zoho Integration</h3>
              <p className="text-sm text-gray-600">Activate Zoho data synchronization</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={config.enabled}
                onChange={(e) => setConfig({ ...config, enabled: e.target.checked })}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-red-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-red-500"></div>
            </label>
          </div>

          {/* OAuth Configuration */}
          <div className="mt-6 space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Client ID
              </label>
              <input
                type="text"
                value={config.clientId}
                onChange={(e) => setConfig({ ...config, clientId: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                placeholder="Enter Zoho OAuth Client ID"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Client Secret
              </label>
              <input
                type="password"
                value={config.clientSecret}
                onChange={(e) => setConfig({ ...config, clientSecret: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                placeholder="Enter Zoho OAuth Client Secret"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Refresh Token
              </label>
              <input
                type="password"
                value={config.refreshToken}
                onChange={(e) => setConfig({ ...config, refreshToken: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                placeholder="Enter Zoho Refresh Token"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Organization ID
              </label>
              <input
                type="text"
                value={config.organizationId}
                onChange={(e) => setConfig({ ...config, organizationId: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                placeholder="Enter Zoho Organization ID"
              />
            </div>
          </div>

          <button
            onClick={handleSave}
            className="w-full mt-6 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors flex items-center justify-center gap-2"
          >
            <Save className="w-4 h-4" />
            Save Configuration
          </button>
        </div>

        {/* Zoho Modules */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h3 className="text-xl font-semibold text-gray-800 mb-4">Zoho Modules</h3>
          
          {syncResult && (
            <div
              className={`mb-4 p-4 rounded-lg flex items-center gap-3 ${
                syncResult === 'success'
                  ? 'bg-green-50 text-green-800'
                  : 'bg-red-50 text-red-800'
              }`}
            >
              {syncResult === 'success' ? (
                <CheckCircle className="w-5 h-5" />
              ) : (
                <XCircle className="w-5 h-5" />
              )}
              <span>
                {syncResult === 'success'
                  ? 'Sync completed successfully!'
                  : 'Sync failed. Please try again.'}
              </span>
            </div>
          )}

          <div className="space-y-3">
            {modules.map((module, index) => (
              <div
                key={index}
                className="p-4 border border-gray-200 rounded-lg hover:border-red-300 transition-colors"
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-3">
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={module.enabled}
                        onChange={(e) => {
                          const updated = [...modules];
                          updated[index].enabled = e.target.checked;
                          setModules(updated);
                        }}
                        className="sr-only peer"
                      />
                      <div className="w-9 h-5 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-red-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-red-500"></div>
                    </label>
                    <div>
                      <h4 className="font-semibold text-gray-800">{module.name}</h4>
                      {module.lastSync && (
                        <p className="text-xs text-gray-500">
                          Last sync: {module.lastSync}
                        </p>
                      )}
                    </div>
                  </div>
                  <button
                    onClick={() => handleSync(module.name)}
                    disabled={!module.enabled || syncing}
                    className={`px-4 py-2 rounded-lg transition-colors flex items-center gap-2 ${
                      module.enabled && !syncing
                        ? 'bg-blue-500 text-white hover:bg-blue-600'
                        : 'bg-gray-200 text-gray-400 cursor-not-allowed'
                    }`}
                  >
                    {syncing ? (
                      <>
                        <RefreshCw className="w-4 h-4 animate-spin" />
                        Syncing...
                      </>
                    ) : (
                      <>
                        <RefreshCw className="w-4 h-4" />
                        Sync Now
                      </>
                    )}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Data Export */}
        <div className="mt-6 bg-white rounded-xl shadow-lg p-6">
          <h3 className="text-xl font-semibold text-gray-800 mb-4">Data Management</h3>
          <div className="flex gap-4">
            <button className="flex-1 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors flex items-center justify-center gap-2">
              <Download className="w-4 h-4" />
              Export All Zoho Data
            </button>
            <button className="flex-1 px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition-colors flex items-center justify-center gap-2">
              <RefreshCw className="w-4 h-4" />
              Full Sync All Modules
            </button>
          </div>
        </div>
        </>
        )}

        {/* Mappings View */}
        {activeView === 'mappings' && (
          <div className="bg-white rounded-b-xl shadow-lg p-6">
            <ZohoSyncMappingsAdvanced />
          </div>
        )}
      </div>
    </div>
  );
};

export default ZohoIntegrationSettings;
