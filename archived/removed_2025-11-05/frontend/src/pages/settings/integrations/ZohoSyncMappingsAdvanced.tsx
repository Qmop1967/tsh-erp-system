import React, { useState, useEffect } from 'react';
import { 
  RefreshCw, 
  Database, 
  CheckCircle,
  BarChart3,
  ArrowRight,
  Download,
  TrendingUp,
  Activity,
  GitCompare,
  Search,
  FileText,
  Settings as SettingsIcon,
  Eye,
  Save,
  XCircle,
  ArrowLeftRight,
  Play,
  Zap,
  AlertTriangle
} from 'lucide-react';

interface FieldMapping {
  zoho_field: string;
  tsh_field: string;
  field_type: string;
  is_required: boolean;
  transformation_rule?: string;
}

interface EntityMapping {
  entity_type: string;
  zoho_module: string;
  tsh_table: string;
  enabled: boolean;
  sync_direction: string;
  sync_mode: string;
  sync_frequency: number;
  conflict_resolution: string;
  field_mappings: FieldMapping[];
  sync_images: boolean;
  auto_create: boolean;
  auto_update: boolean;
  last_sync: string | null;
  total_synced: number;
  total_errors: number;
}

interface AnalysisReport {
  total_records: number;
  new_records: number;
  updated_records: number;
  matched_records: number;
  error_records: number;
  last_analyzed: string;
}

interface ComparisonData {
  zoho_only: number;
  tsh_only: number;
  matched: number;
  conflicts: number;
  ready_to_sync: number;
}

const ZohoSyncMappingsAdvanced: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'item' | 'customer' | 'vendor'>('item');
  const [activeSection, setActiveSection] = useState<'config' | 'analysis' | 'comparison'>('config');
  const [mappings, setMappings] = useState<Record<string, EntityMapping>>({});
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [editMode, setEditMode] = useState(false);
  
  // Statistics states
  const [zohoStats, setZohoStats] = useState<Record<string, AnalysisReport>>({});
  const [tshStats, setTshStats] = useState<Record<string, AnalysisReport>>({});
  const [comparisonData, setComparisonData] = useState<Record<string, ComparisonData>>({});
  
  const [statusMessage, setStatusMessage] = useState<{type: 'success' | 'error' | 'info', text: string} | null>(null);

  useEffect(() => {
    fetchMappings();
    // Auto-load statistics for all entities on mount
    loadAllStatistics();
  }, []);

  // Auto-fetch statistics when switching tabs
  useEffect(() => {
    if (activeSection === 'analysis' && !zohoStats[activeTab]) {
      analyzeData(activeTab);
      getTSHStatistics(activeTab);
    }
  }, [activeTab, activeSection]);

  const loadAllStatistics = async () => {
    // Load statistics for all entity types
    const entities = ['item', 'customer', 'vendor'] as const;
    for (const entity of entities) {
      await getTSHStatistics(entity);
    }
  };

  const fetchMappings = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/settings/integrations/zoho/sync/mappings');
      const data = await response.json();
      setMappings(data.mappings);
    } catch (error) {
      console.error('Error fetching mappings:', error);
      showStatus('error', 'Failed to load mappings');
    } finally {
      setLoading(false);
    }
  };

  const analyzeData = async (entityType: string) => {
    try {
      setAnalyzing(true);
      showStatus('info', `Analyzing ${entityType} data from Zoho...`);
      
      const response = await fetch(`http://localhost:8000/api/settings/integrations/zoho/sync/${entityType}/analyze`, {
        method: 'POST',
      });
      
      const data = await response.json();
      
      if (data.status === 'success') {
        setZohoStats(prev => ({
          ...prev,
          [entityType]: data.analysis
        }));
        showStatus('success', `Analysis completed for ${entityType}`);
      } else {
        showStatus('error', 'Analysis failed');
      }
    } catch (error) {
      console.error('Error analyzing data:', error);
      showStatus('error', 'Analysis failed');
    } finally {
      setAnalyzing(false);
    }
  };

  const getTSHStatistics = async (entityType: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/settings/integrations/zoho/sync/${entityType}/status`);
      const data = await response.json();
      
      if (data.status === 'success') {
        setTshStats(prev => ({
          ...prev,
          [entityType]: {
            total_records: data.sync_status.total_synced,
            new_records: 0,
            updated_records: 0,
            matched_records: data.sync_status.total_synced,
            error_records: data.sync_status.total_errors,
            last_analyzed: new Date().toISOString()
          }
        }));
      }
    } catch (error) {
      console.error('Error fetching TSH stats:', error);
    }
  };

  const compareData = async (entityType: string) => {
    try {
      showStatus('info', 'Comparing data between systems...');
      
      // Get both Zoho and TSH data
      await Promise.all([
        analyzeData(entityType),
        getTSHStatistics(entityType)
      ]);
      
      // Calculate comparison
      const zoho = zohoStats[entityType];
      const tsh = tshStats[entityType];
      
      if (zoho && tsh) {
        setComparisonData(prev => ({
          ...prev,
          [entityType]: {
            zoho_only: zoho.new_records,
            tsh_only: Math.max(0, tsh.total_records - zoho.matched_records),
            matched: zoho.matched_records,
            conflicts: zoho.updated_records,
            ready_to_sync: zoho.new_records + zoho.updated_records
          }
        }));
        showStatus('success', 'Comparison completed');
      }
    } catch (error) {
      console.error('Error comparing data:', error);
      showStatus('error', 'Comparison failed');
    }
  };

  const executeSync = async (entityType: string) => {
    try {
      setSyncing(true);
      showStatus('info', `Starting sync for ${entityType}...`);
      
      const response = await fetch(`http://localhost:8000/api/settings/integrations/zoho/sync/${entityType}/execute`, {
        method: 'POST',
      });
      
      const data = await response.json();
      
      if (data.status === 'success') {
        showStatus('success', `Sync completed for ${entityType}`);
        await fetchMappings();
        await getTSHStatistics(entityType);
      } else {
        showStatus('error', 'Sync failed');
      }
    } catch (error) {
      console.error('Error executing sync:', error);
      showStatus('error', 'Sync failed');
    } finally {
      setSyncing(false);
    }
  };

  const updateMapping = async (entityType: string, updates: Partial<EntityMapping>) => {
    try {
      const response = await fetch(`http://localhost:8000/api/settings/integrations/zoho/sync/mappings/${entityType}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates),
      });
      
      if (response.ok) {
        showStatus('success', 'Mapping updated successfully');
        await fetchMappings();
      }
    } catch (error) {
      console.error('Error updating mapping:', error);
      showStatus('error', 'Failed to update mapping');
    }
  };

  const showStatus = (type: 'success' | 'error' | 'info', text: string) => {
    setStatusMessage({ type, text });
    setTimeout(() => setStatusMessage(null), 5000);
  };

  const currentMapping = mappings[activeTab];
  const currentZohoStats = zohoStats[activeTab];
  const currentTshStats = tshStats[activeTab];
  const currentComparison = comparisonData[activeTab];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="w-8 h-8 animate-spin text-red-500" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with Status */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
            <BarChart3 className="w-7 h-7 text-red-500" />
            Advanced Sync Mappings Control
          </h2>
          <p className="text-gray-600">Real-time analysis, comparison & synchronization management</p>
        </div>
        <button
          onClick={() => fetchMappings()}
          className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors flex items-center gap-2"
        >
          <RefreshCw className="w-4 h-4" />
          Refresh
        </button>
      </div>

      {/* Status Message */}
      {statusMessage && (
        <div
          className={`p-4 rounded-lg flex items-center gap-3 ${
            statusMessage.type === 'success'
              ? 'bg-green-50 text-green-800 border border-green-200'
              : statusMessage.type === 'error'
              ? 'bg-red-50 text-red-800 border border-red-200'
              : 'bg-blue-50 text-blue-800 border border-blue-200'
          }`}
        >
          {statusMessage.type === 'success' && <CheckCircle className="w-5 h-5" />}
          {statusMessage.type === 'error' && <XCircle className="w-5 h-5" />}
          {statusMessage.type === 'info' && <Activity className="w-5 h-5 animate-pulse" />}
          <span className="font-medium">{statusMessage.text}</span>
        </div>
      )}

      {/* Entity Tabs */}
      <div className="bg-white rounded-xl shadow-lg overflow-hidden">
        <div className="flex border-b border-gray-200">
          {(['item', 'customer', 'vendor'] as const).map((tab) => {
            const mapping = mappings[tab];
            const stats = zohoStats[tab];
            return (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`flex-1 px-6 py-4 font-medium transition-colors relative ${
                  activeTab === tab
                    ? 'text-red-600 border-b-2 border-red-600 bg-red-50'
                    : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                }`}
              >
                <div className="flex flex-col items-center gap-1">
                  <div className="flex items-center gap-2">
                    {tab.charAt(0).toUpperCase() + tab.slice(1)}s
                    {mapping?.enabled && (
                      <CheckCircle className="w-4 h-4 text-green-500" />
                    )}
                  </div>
                  {stats && (
                    <span className="text-xs text-gray-500">
                      {stats.total_records.toLocaleString()} records
                    </span>
                  )}
                </div>
              </button>
            );
          })}
        </div>

        {/* Section Tabs */}
        <div className="flex border-b border-gray-200 bg-gray-50">
          <button
            onClick={() => setActiveSection('config')}
            className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
              activeSection === 'config'
                ? 'text-red-600 border-b-2 border-red-600 bg-white'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            <div className="flex items-center justify-center gap-2">
              <SettingsIcon className="w-4 h-4" />
              Configuration
            </div>
          </button>
          <button
            onClick={() => setActiveSection('analysis')}
            className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
              activeSection === 'analysis'
                ? 'text-red-600 border-b-2 border-red-600 bg-white'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            <div className="flex items-center justify-center gap-2">
              <TrendingUp className="w-4 h-4" />
              Data Analysis
            </div>
          </button>
          <button
            onClick={() => setActiveSection('comparison')}
            className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
              activeSection === 'comparison'
                ? 'text-red-600 border-b-2 border-red-600 bg-white'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            <div className="flex items-center justify-center gap-2">
              <GitCompare className="w-4 h-4" />
              Comparison
            </div>
          </button>
        </div>

        {/* Content Area */}
        <div className="p-6">
          {/* Configuration Section */}
          {activeSection === 'config' && currentMapping && (
            <div className="space-y-6">
              {/* Quick Actions */}
              <div className="flex gap-3">
                <button
                  onClick={() => analyzeData(activeTab)}
                  disabled={analyzing}
                  className="flex-1 px-4 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  {analyzing ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <Search className="w-4 h-4" />
                      Analyze Data
                    </>
                  )}
                </button>
                <button
                  onClick={() => executeSync(activeTab)}
                  disabled={!currentMapping.enabled || syncing}
                  className="flex-1 px-4 py-3 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {syncing ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      Syncing...
                    </>
                  ) : (
                    <>
                      <Play className="w-4 h-4" />
                      Execute Sync
                    </>
                  )}
                </button>
                <button
                  onClick={() => compareData(activeTab)}
                  className="flex-1 px-4 py-3 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition-colors flex items-center justify-center gap-2"
                >
                  <GitCompare className="w-4 h-4" />
                  Compare Systems
                </button>
              </div>

              {/* Enable/Disable Toggle */}
              <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <label className="font-semibold text-gray-800">Enable Synchronization</label>
                    <p className="text-sm text-gray-600">Activate sync for {activeTab}s</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={currentMapping.enabled}
                      onChange={(e) => updateMapping(activeTab, { enabled: e.target.checked })}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-red-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-red-500"></div>
                  </label>
                </div>
              </div>

              {/* Sync Configuration Grid */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <ArrowLeftRight className="w-4 h-4 inline mr-1" />
                    Sync Direction
                  </label>
                  <select
                    value={currentMapping.sync_direction}
                    onChange={(e) => updateMapping(activeTab, { sync_direction: e.target.value })}
                    disabled={!editMode}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent disabled:bg-gray-100"
                  >
                    <option value="zoho_to_tsh">Zoho → TSH</option>
                    <option value="tsh_to_zoho">TSH → Zoho</option>
                    <option value="bidirectional">↔ Bidirectional</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <Zap className="w-4 h-4 inline mr-1" />
                    Sync Mode
                  </label>
                  <select
                    value={currentMapping.sync_mode}
                    onChange={(e) => updateMapping(activeTab, { sync_mode: e.target.value })}
                    disabled={!editMode}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent disabled:bg-gray-100"
                  >
                    <option value="manual">Manual</option>
                    <option value="automatic">Automatic</option>
                    <option value="scheduled">Scheduled</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Frequency (minutes)
                  </label>
                  <input
                    type="number"
                    value={currentMapping.sync_frequency}
                    onChange={(e) => updateMapping(activeTab, { sync_frequency: parseInt(e.target.value) })}
                    disabled={!editMode}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent disabled:bg-gray-100"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Conflict Resolution
                  </label>
                  <select
                    value={currentMapping.conflict_resolution}
                    onChange={(e) => updateMapping(activeTab, { conflict_resolution: e.target.value })}
                    disabled={!editMode}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent disabled:bg-gray-100"
                  >
                    <option value="zoho_wins">Zoho Wins</option>
                    <option value="tsh_wins">TSH Wins</option>
                    <option value="latest_wins">Latest Wins</option>
                    <option value="manual_review">Manual Review</option>
                  </select>
                </div>
              </div>

              {/* Options */}
              <div className="grid grid-cols-2 gap-3">
                <label className="flex items-center gap-2 p-3 bg-gray-50 rounded-lg border border-gray-200 cursor-pointer hover:bg-gray-100">
                  <input
                    type="checkbox"
                    checked={currentMapping.sync_images}
                    onChange={(e) => updateMapping(activeTab, { sync_images: e.target.checked })}
                    disabled={!editMode}
                    className="w-4 h-4 text-red-600 border-gray-300 rounded focus:ring-red-500"
                  />
                  <span className="text-sm font-medium text-gray-700">Sync Images</span>
                </label>
                <label className="flex items-center gap-2 p-3 bg-gray-50 rounded-lg border border-gray-200 cursor-pointer hover:bg-gray-100">
                  <input
                    type="checkbox"
                    checked={currentMapping.auto_create}
                    onChange={(e) => updateMapping(activeTab, { auto_create: e.target.checked })}
                    disabled={!editMode}
                    className="w-4 h-4 text-red-600 border-gray-300 rounded focus:ring-red-500"
                  />
                  <span className="text-sm font-medium text-gray-700">Auto Create</span>
                </label>
                <label className="flex items-center gap-2 p-3 bg-gray-50 rounded-lg border border-gray-200 cursor-pointer hover:bg-gray-100">
                  <input
                    type="checkbox"
                    checked={currentMapping.auto_update}
                    onChange={(e) => updateMapping(activeTab, { auto_update: e.target.checked })}
                    disabled={!editMode}
                    className="w-4 h-4 text-red-600 border-gray-300 rounded focus:ring-red-500"
                  />
                  <span className="text-sm font-medium text-gray-700">Auto Update</span>
                </label>
              </div>

              {/* Field Mappings Table */}
              <div className="border border-gray-200 rounded-lg overflow-hidden">
                <div className="bg-gray-50 px-4 py-3 border-b border-gray-200">
                  <h3 className="font-semibold text-gray-800 flex items-center gap-2">
                    <FileText className="w-4 h-4" />
                    Field Mappings ({currentMapping.field_mappings.length} fields)
                  </h3>
                </div>
                <div className="overflow-x-auto max-h-96 overflow-y-auto">
                  <table className="w-full">
                    <thead className="bg-gray-50 border-b border-gray-200 sticky top-0">
                      <tr>
                        <th className="px-4 py-2 text-left text-xs font-semibold text-gray-700">Zoho Field</th>
                        <th className="px-4 py-2 text-center text-xs font-semibold text-gray-700">→</th>
                        <th className="px-4 py-2 text-left text-xs font-semibold text-gray-700">TSH Field</th>
                        <th className="px-4 py-2 text-left text-xs font-semibold text-gray-700">Type</th>
                        <th className="px-4 py-2 text-center text-xs font-semibold text-gray-700">Required</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {currentMapping.field_mappings.map((field, index) => (
                        <tr key={index} className="hover:bg-gray-50">
                          <td className="px-4 py-2 text-xs text-gray-900 font-mono">{field.zoho_field}</td>
                          <td className="px-4 py-2 text-center">
                            <ArrowRight className="w-3 h-3 text-red-500 mx-auto" />
                          </td>
                          <td className="px-4 py-2 text-xs text-gray-900 font-mono">{field.tsh_field}</td>
                          <td className="px-4 py-2 text-xs text-gray-600">{field.field_type}</td>
                          <td className="px-4 py-2 text-center">
                            {field.is_required ? (
                              <CheckCircle className="w-3 h-3 text-green-500 mx-auto" />
                            ) : (
                              <span className="text-gray-400">—</span>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Edit Mode Controls */}
              <div className="flex justify-between items-center pt-4 border-t border-gray-200">
                <button
                  onClick={() => setEditMode(!editMode)}
                  className={`px-4 py-2 rounded-lg flex items-center gap-2 transition-colors ${
                    editMode 
                      ? 'bg-gray-200 text-gray-700 hover:bg-gray-300' 
                      : 'bg-red-500 text-white hover:bg-red-600'
                  }`}
                >
                  {editMode ? (
                    <>
                      <Eye className="w-4 h-4" />
                      View Mode
                    </>
                  ) : (
                    <>
                      <SettingsIcon className="w-4 h-4" />
                      Edit Mode
                    </>
                  )}
                </button>
                {editMode && (
                  <button
                    onClick={() => {
                      setEditMode(false);
                      fetchMappings();
                    }}
                    className="px-6 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors flex items-center gap-2"
                  >
                    <Save className="w-4 h-4" />
                    Save Changes
                  </button>
                )}
              </div>
            </div>
          )}

          {/* Analysis Section */}
          {activeSection === 'analysis' && (
            <div className="space-y-6">
              {/* Info Banner */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex items-start gap-3">
                <Activity className="w-5 h-5 text-blue-600 mt-0.5" />
                <div className="flex-1">
                  <p className="text-sm font-medium text-blue-900">Real-time Data Analysis</p>
                  <p className="text-xs text-blue-700 mt-1">
                    Statistics are automatically loaded. Click buttons below to refresh or analyze specific data.
                  </p>
                </div>
              </div>

              <div className="flex gap-3 mb-6">
                <button
                  onClick={() => analyzeData(activeTab)}
                  disabled={analyzing}
                  className="flex-1 px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  {analyzing ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      Analyzing Zoho Data...
                    </>
                  ) : (
                    <>
                      <Search className="w-4 h-4" />
                      Analyze Zoho Data
                    </>
                  )}
                </button>
                <button
                  onClick={() => getTSHStatistics(activeTab)}
                  className="flex-1 px-6 py-3 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition-colors flex items-center justify-center gap-2"
                >
                  <Database className="w-4 h-4" />
                  Refresh TSH Stats
                </button>
                <button
                  onClick={() => {
                    analyzeData(activeTab);
                    getTSHStatistics(activeTab);
                  }}
                  disabled={analyzing}
                  className="flex-1 px-6 py-3 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  <RefreshCw className="w-4 h-4" />
                  Refresh All
                </button>
              </div>

              {/* Zoho Statistics */}
              <div className="border border-gray-200 rounded-lg overflow-hidden">
                <div className="bg-gradient-to-r from-red-500 to-red-600 px-4 py-3 text-white flex items-center justify-between">
                  <h3 className="font-semibold flex items-center gap-2">
                    <Database className="w-5 h-5" />
                    Zoho Data Statistics Report
                  </h3>
                  {analyzing && (
                    <RefreshCw className="w-4 h-4 animate-spin" />
                  )}
                </div>
                <div className="p-6">
                  {analyzing && !currentZohoStats ? (
                    <div className="text-center py-12">
                      <RefreshCw className="w-12 h-12 mx-auto mb-3 text-blue-500 animate-spin" />
                      <p className="text-gray-600 font-medium">Analyzing Zoho data...</p>
                      <p className="text-sm text-gray-500 mt-1">Please wait while we fetch the latest statistics</p>
                    </div>
                  ) : currentZohoStats ? (
                    <>
                      <div className="grid grid-cols-5 gap-4">
                        <div className="p-4 bg-blue-50 rounded-lg border border-blue-200 hover:shadow-md transition-shadow">
                          <p className="text-xs text-blue-600 font-medium mb-1">Total Records</p>
                          <p className="text-2xl font-bold text-blue-900">{currentZohoStats.total_records.toLocaleString()}</p>
                          <p className="text-xs text-blue-600 mt-1">In Zoho System</p>
                        </div>
                        <div className="p-4 bg-green-50 rounded-lg border border-green-200 hover:shadow-md transition-shadow">
                          <p className="text-xs text-green-600 font-medium mb-1">New Records</p>
                          <p className="text-2xl font-bold text-green-900">{currentZohoStats.new_records.toLocaleString()}</p>
                          <p className="text-xs text-green-600 mt-1">Not in TSH</p>
                        </div>
                        <div className="p-4 bg-yellow-50 rounded-lg border border-yellow-200 hover:shadow-md transition-shadow">
                          <p className="text-xs text-yellow-600 font-medium mb-1">Updated</p>
                          <p className="text-2xl font-bold text-yellow-900">{currentZohoStats.updated_records.toLocaleString()}</p>
                          <p className="text-xs text-yellow-600 mt-1">Modified Recently</p>
                        </div>
                        <div className="p-4 bg-purple-50 rounded-lg border border-purple-200 hover:shadow-md transition-shadow">
                          <p className="text-xs text-purple-600 font-medium mb-1">Matched</p>
                          <p className="text-2xl font-bold text-purple-900">{currentZohoStats.matched_records.toLocaleString()}</p>
                          <p className="text-xs text-purple-600 mt-1">In Both Systems</p>
                        </div>
                        <div className="p-4 bg-red-50 rounded-lg border border-red-200 hover:shadow-md transition-shadow">
                          <p className="text-xs text-red-600 font-medium mb-1">Errors</p>
                          <p className="text-2xl font-bold text-red-900">{currentZohoStats.error_records.toLocaleString()}</p>
                          <p className="text-xs text-red-600 mt-1">Need Attention</p>
                        </div>
                      </div>
                      <div className="mt-4 p-3 bg-gray-50 rounded-lg border border-gray-200">
                        <p className="text-xs text-gray-600">
                          <span className="font-semibold">Last Analyzed:</span> {new Date(currentZohoStats.last_analyzed).toLocaleString()}
                        </p>
                      </div>
                    </>
                  ) : (
                    <div className="text-center py-12 text-gray-500">
                      <Activity className="w-12 h-12 mx-auto mb-3 text-gray-400" />
                      <p className="font-medium text-lg mb-2">No analysis data available</p>
                      <p className="text-sm mb-4">Click "Analyze Zoho Data" to fetch real-time statistics from Zoho</p>
                      <button
                        onClick={() => analyzeData(activeTab)}
                        className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors inline-flex items-center gap-2"
                      >
                        <Search className="w-4 h-4" />
                        Analyze Now
                      </button>
                    </div>
                  )}
                </div>
              </div>

              {/* TSH ERP Statistics */}
              <div className="border border-gray-200 rounded-lg overflow-hidden">
                <div className="bg-gradient-to-r from-indigo-500 to-indigo-600 px-4 py-3 text-white flex items-center justify-between">
                  <h3 className="font-semibold flex items-center gap-2">
                    <Database className="w-5 h-5" />
                    TSH ERP Data Statistics Report
                  </h3>
                  <span className="text-xs bg-white/20 px-2 py-1 rounded">Local System</span>
                </div>
                <div className="p-6">
                  {currentTshStats ? (
                    <>
                      <div className="grid grid-cols-4 gap-4">
                        <div className="p-4 bg-indigo-50 rounded-lg border border-indigo-200 hover:shadow-md transition-shadow">
                          <p className="text-xs text-indigo-600 font-medium mb-1">Total Records</p>
                          <p className="text-2xl font-bold text-indigo-900">{currentTshStats.total_records.toLocaleString()}</p>
                          <p className="text-xs text-indigo-600 mt-1">In TSH Database</p>
                        </div>
                        <div className="p-4 bg-teal-50 rounded-lg border border-teal-200 hover:shadow-md transition-shadow">
                          <p className="text-xs text-teal-600 font-medium mb-1">Synced</p>
                          <p className="text-2xl font-bold text-teal-900">{currentTshStats.matched_records.toLocaleString()}</p>
                          <p className="text-xs text-teal-600 mt-1">From Zoho</p>
                        </div>
                        <div className="p-4 bg-orange-50 rounded-lg border border-orange-200 hover:shadow-md transition-shadow">
                          <p className="text-xs text-orange-600 font-medium mb-1">Errors</p>
                          <p className="text-2xl font-bold text-orange-900">{currentTshStats.error_records.toLocaleString()}</p>
                          <p className="text-xs text-orange-600 mt-1">Sync Failures</p>
                        </div>
                        <div className="p-4 bg-emerald-50 rounded-lg border border-emerald-200 hover:shadow-md transition-shadow">
                          <p className="text-xs text-emerald-600 font-medium mb-1">Success Rate</p>
                          <p className="text-2xl font-bold text-emerald-900">
                            {currentTshStats.total_records > 0 
                              ? ((currentTshStats.matched_records / currentTshStats.total_records) * 100).toFixed(1)
                              : '0'}%
                          </p>
                          <p className="text-xs text-emerald-600 mt-1">Sync Quality</p>
                        </div>
                      </div>
                      <div className="mt-4 grid grid-cols-2 gap-4">
                        <div className="p-3 bg-gray-50 rounded-lg border border-gray-200">
                          <p className="text-xs text-gray-600 mb-1">
                            <span className="font-semibold">Last Sync:</span>
                          </p>
                          <p className="text-sm text-gray-900 font-medium">
                            {new Date(currentTshStats.last_analyzed).toLocaleString()}
                          </p>
                        </div>
                        <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
                          <p className="text-xs text-blue-600 mb-1">
                            <span className="font-semibold">System Status:</span>
                          </p>
                          <p className="text-sm text-blue-900 font-medium flex items-center gap-1">
                            <CheckCircle className="w-4 h-4 text-green-500" />
                            Operational & Ready
                          </p>
                        </div>
                      </div>
                    </>
                  ) : (
                    <div className="text-center py-12 text-gray-500">
                      <Database className="w-12 h-12 mx-auto mb-3 text-gray-400" />
                      <p className="font-medium text-lg mb-2">No TSH data available</p>
                      <p className="text-sm mb-4">Click "Refresh TSH Stats" to load current system statistics</p>
                      <button
                        onClick={() => getTSHStatistics(activeTab)}
                        className="px-6 py-2 bg-indigo-500 text-white rounded-lg hover:bg-indigo-600 transition-colors inline-flex items-center gap-2"
                      >
                        <Database className="w-4 h-4" />
                        Load Stats
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Comparison Section */}
          {activeSection === 'comparison' && (
            <div className="space-y-6">
              <div className="flex gap-3 mb-6">
                <button
                  onClick={() => compareData(activeTab)}
                  disabled={analyzing}
                  className="px-6 py-3 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition-colors flex items-center gap-2 disabled:opacity-50"
                >
                  {analyzing ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      Comparing...
                    </>
                  ) : (
                    <>
                      <GitCompare className="w-4 h-4" />
                      Run Comparison
                    </>
                  )}
                </button>
                <button
                  onClick={() => executeSync(activeTab)}
                  disabled={!currentMapping?.enabled || syncing || !currentComparison}
                  className="px-6 py-3 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Play className="w-4 h-4" />
                  Sync Now
                </button>
              </div>

              {/* Comparison Results */}
              <div className="border border-gray-200 rounded-lg overflow-hidden">
                <div className="bg-gradient-to-r from-purple-500 to-purple-600 px-4 py-3 text-white">
                  <h3 className="font-semibold flex items-center gap-2">
                    <GitCompare className="w-5 h-5" />
                    System Comparison & Matching Report
                  </h3>
                </div>
                <div className="p-6">
                  {currentComparison ? (
                    <>
                      <div className="grid grid-cols-5 gap-4 mb-6">
                        <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                          <p className="text-xs text-blue-600 font-medium mb-1">Zoho Only</p>
                          <p className="text-2xl font-bold text-blue-900">{currentComparison.zoho_only.toLocaleString()}</p>
                          <p className="text-xs text-blue-600 mt-1">In Zoho, not in TSH</p>
                        </div>
                        <div className="p-4 bg-indigo-50 rounded-lg border border-indigo-200">
                          <p className="text-xs text-indigo-600 font-medium mb-1">TSH Only</p>
                          <p className="text-2xl font-bold text-indigo-900">{currentComparison.tsh_only.toLocaleString()}</p>
                          <p className="text-xs text-indigo-600 mt-1">In TSH, not in Zoho</p>
                        </div>
                        <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                          <p className="text-xs text-green-600 font-medium mb-1">Matched</p>
                          <p className="text-2xl font-bold text-green-900">{currentComparison.matched.toLocaleString()}</p>
                          <p className="text-xs text-green-600 mt-1">In sync</p>
                        </div>
                        <div className="p-4 bg-yellow-50 rounded-lg border border-yellow-200">
                          <p className="text-xs text-yellow-600 font-medium mb-1">Conflicts</p>
                          <p className="text-2xl font-bold text-yellow-900">{currentComparison.conflicts.toLocaleString()}</p>
                          <p className="text-xs text-yellow-600 mt-1">Need resolution</p>
                        </div>
                        <div className="p-4 bg-purple-50 rounded-lg border border-purple-200">
                          <p className="text-xs text-purple-600 font-medium mb-1">Ready to Sync</p>
                          <p className="text-2xl font-bold text-purple-900">{currentComparison.ready_to_sync.toLocaleString()}</p>
                          <p className="text-xs text-purple-600 mt-1">Can sync now</p>
                        </div>
                      </div>

                      {/* Visual Comparison */}
                      <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
                        <h4 className="font-semibold text-gray-800 mb-4 flex items-center gap-2">
                          <BarChart3 className="w-4 h-4" />
                          Visual Comparison
                        </h4>
                        <div className="space-y-3">
                          {/* Matched Progress */}
                          <div>
                            <div className="flex justify-between text-sm mb-1">
                              <span className="text-green-600 font-medium">Matched Records</span>
                              <span className="text-green-600 font-bold">
                                {((currentComparison.matched / (currentComparison.matched + currentComparison.conflicts + currentComparison.zoho_only)) * 100).toFixed(1)}%
                              </span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-3">
                              <div 
                                className="bg-green-500 h-3 rounded-full transition-all"
                                style={{ 
                                  width: `${((currentComparison.matched / (currentComparison.matched + currentComparison.conflicts + currentComparison.zoho_only)) * 100)}%` 
                                }}
                              />
                            </div>
                          </div>

                          {/* Conflicts Progress */}
                          <div>
                            <div className="flex justify-between text-sm mb-1">
                              <span className="text-yellow-600 font-medium">Conflicts</span>
                              <span className="text-yellow-600 font-bold">
                                {((currentComparison.conflicts / (currentComparison.matched + currentComparison.conflicts + currentComparison.zoho_only)) * 100).toFixed(1)}%
                              </span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-3">
                              <div 
                                className="bg-yellow-500 h-3 rounded-full transition-all"
                                style={{ 
                                  width: `${((currentComparison.conflicts / (currentComparison.matched + currentComparison.conflicts + currentComparison.zoho_only)) * 100)}%` 
                                }}
                              />
                            </div>
                          </div>

                          {/* New Records Progress */}
                          <div>
                            <div className="flex justify-between text-sm mb-1">
                              <span className="text-blue-600 font-medium">New from Zoho</span>
                              <span className="text-blue-600 font-bold">
                                {((currentComparison.zoho_only / (currentComparison.matched + currentComparison.conflicts + currentComparison.zoho_only)) * 100).toFixed(1)}%
                              </span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-3">
                              <div 
                                className="bg-blue-500 h-3 rounded-full transition-all"
                                style={{ 
                                  width: `${((currentComparison.zoho_only / (currentComparison.matched + currentComparison.conflicts + currentComparison.zoho_only)) * 100)}%` 
                                }}
                              />
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Recommendations */}
                      {currentComparison.ready_to_sync > 0 && (
                        <div className="mt-4 p-4 bg-green-50 rounded-lg border border-green-200">
                          <div className="flex items-start gap-3">
                            <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
                            <div>
                              <p className="font-semibold text-green-800">Ready for Synchronization</p>
                              <p className="text-sm text-green-700 mt-1">
                                {currentComparison.ready_to_sync} records are ready to be synchronized. Click "Sync Now" to proceed.
                              </p>
                            </div>
                          </div>
                        </div>
                      )}

                      {currentComparison.conflicts > 0 && (
                        <div className="mt-4 p-4 bg-yellow-50 rounded-lg border border-yellow-200">
                          <div className="flex items-start gap-3">
                            <AlertTriangle className="w-5 h-5 text-yellow-600 mt-0.5" />
                            <div>
                              <p className="font-semibold text-yellow-800">Conflicts Detected</p>
                              <p className="text-sm text-yellow-700 mt-1">
                                {currentComparison.conflicts} records have conflicts. Review your conflict resolution settings before syncing.
                              </p>
                            </div>
                          </div>
                        </div>
                      )}
                    </>
                  ) : (
                    <div className="text-center py-12 text-gray-500">
                      <GitCompare className="w-16 h-16 mx-auto mb-4 text-gray-400" />
                      <p className="text-lg font-medium">No comparison data available</p>
                      <p className="text-sm mt-2">Click "Run Comparison" to analyze differences between systems</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Export Button */}
      <div className="flex justify-end">
        <button
          onClick={() => {
            const reportData = {
              entity: activeTab,
              zoho_stats: currentZohoStats,
              tsh_stats: currentTshStats,
              comparison: currentComparison,
              mapping: currentMapping,
              generated_at: new Date().toISOString()
            };
            const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `zoho-sync-report-${activeTab}-${Date.now()}.json`;
            a.click();
          }}
          className="px-6 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-800 transition-colors flex items-center gap-2"
        >
          <Download className="w-4 h-4" />
          Export Report
        </button>
      </div>
    </div>
  );
};

export default ZohoSyncMappingsAdvanced;
