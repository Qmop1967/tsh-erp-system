import React, { useState, useEffect } from 'react';
import { 
  RefreshCw, 
  Play, 
  Pause,
  Database, 
  AlertCircle,
  CheckCircle,
  Clock,
  BarChart3,
  ArrowRight,
  Download,
  Upload,
  Zap,
  TrendingUp,
  Activity,
  GitCompare,
  Search,
  FileText,
  Settings,
  Eye,
  Save,
  XCircle,
  ArrowLeftRight
} from 'lucide-react';

interface FieldMapping {
  zoho_field: string;
  tsh_field: string;
  field_type: string;
  is_required: boolean;
  default_value?: string;
  transformation_rule?: string;
}

interface SyncMapping {
  entity_type: string;
  enabled: boolean;
  sync_direction: string;
  sync_mode: string;
  sync_frequency?: number;
  field_mappings: FieldMapping[];
  sync_images: boolean;
  sync_attachments: boolean;
  conflict_resolution: string;
  auto_create: boolean;
  auto_update: boolean;
  delete_sync: boolean;
  last_sync?: string;
  last_sync_status?: string;
  total_synced: number;
  total_errors: number;
}

interface SyncLog {
  sync_id: string;
  entity_type: string;
  operation: string;
  status: string;
  error_message?: string;
  timestamp: string;
}

interface DataAnalysis {
  entity_type: string;
  total_records: number;
  new_records: number;
  updated_records: number;
  matched_records: number;
  error_records: number;
  last_analyzed: string;
  field_statistics: any;
}

const ZohoSyncMappings: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'item' | 'customer' | 'vendor'>('item');
  const [mappings, setMappings] = useState<Record<string, SyncMapping>>({});
  const [logs, setLogs] = useState<SyncLog[]>([]);
  const [analysis, setAnalysis] = useState<DataAnalysis | null>(null);
  const [statistics, setStatistics] = useState<any>(null);
  const [syncing, setSyncing] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);

  const API_BASE = 'http://localhost:8000/api/settings';

  useEffect(() => {
    loadMappings();
    loadStatistics();
    loadLogs();
  }, []);

  const loadMappings = async () => {
    try {
      const response = await fetch(`${API_BASE}/integrations/zoho/sync/mappings`);
      const data = await response.json();
      if (data.status === 'success') {
        setMappings(data.mappings);
      }
    } catch (error) {
      console.error('Failed to load mappings:', error);
    }
  };

  const loadStatistics = async () => {
    try {
      const response = await fetch(`${API_BASE}/integrations/zoho/sync/statistics`);
      const data = await response.json();
      if (data.status === 'success') {
        setStatistics(data.statistics);
      }
    } catch (error) {
      console.error('Failed to load statistics:', error);
    }
  };

  const loadLogs = async (entityType?: string) => {
    try {
      const url = entityType 
        ? `${API_BASE}/integrations/zoho/sync/logs?entity_type=${entityType}&limit=10`
        : `${API_BASE}/integrations/zoho/sync/logs?limit=20`;
      const response = await fetch(url);
      const data = await response.json();
      if (data.status === 'success') {
        setLogs(data.logs);
      }
    } catch (error) {
      console.error('Failed to load logs:', error);
    }
  };

  const toggleSync = async (entityType: string, enabled: boolean) => {
    try {
      const response = await fetch(
        `${API_BASE}/integrations/zoho/sync/${entityType}/toggle`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ enabled })
        }
      );
      const data = await response.json();
      if (data.status === 'success') {
        loadMappings();
        loadStatistics();
      }
    } catch (error) {
      console.error('Failed to toggle sync:', error);
    }
  };

  const analyzeData = async (entityType: string) => {
    setAnalyzing(true);
    try {
      const response = await fetch(
        `${API_BASE}/integrations/zoho/sync/${entityType}/analyze`,
        { method: 'POST' }
      );
      const data = await response.json();
      if (data.status === 'success') {
        setAnalysis(data.analysis);
      }
    } catch (error) {
      console.error('Failed to analyze data:', error);
    } finally {
      setAnalyzing(false);
    }
  };

  const executeSync = async (entityType: string) => {
    setSyncing(true);
    try {
      const response = await fetch(
        `${API_BASE}/integrations/zoho/sync/${entityType}/execute`,
        { method: 'POST' }
      );
      const data = await response.json();
      if (data.status === 'success') {
        alert(`Sync initiated: ${data.sync_id}`);
        loadMappings();
        loadStatistics();
        loadLogs(entityType);
      }
    } catch (error) {
      console.error('Failed to execute sync:', error);
      alert('Sync failed. Check console for details.');
    } finally {
      setSyncing(false);
    }
  };

  const resetMapping = async (entityType: string) => {
    if (!confirm(`Reset ${entityType} mapping to default configuration?`)) return;
    
    try {
      const response = await fetch(
        `${API_BASE}/integrations/zoho/sync/mappings/${entityType}/reset`,
        { method: 'POST' }
      );
      const data = await response.json();
      if (data.status === 'success') {
        loadMappings();
        alert('Mapping reset to default configuration');
      }
    } catch (error) {
      console.error('Failed to reset mapping:', error);
    }
  };

  const currentMapping = mappings[activeTab];

  const getStatusColor = (status?: string) => {
    switch (status) {
      case 'success': return 'text-green-600';
      case 'error': return 'text-red-600';
      case 'in_progress': return 'text-yellow-600';
      default: return 'text-gray-600';
    }
  };

  const getEntityIcon = (entityType: string) => {
    switch (entityType) {
      case 'item': return <Database className="w-5 h-5" />;
      case 'customer': return <Upload className="w-5 h-5" />;
      case 'vendor': return <Download className="w-5 h-5" />;
      default: return <Database className="w-5 h-5" />;
    }
  };

  const getEntityLabel = (entityType: string) => {
    switch (entityType) {
      case 'item': return 'Items (Products)';
      case 'customer': return 'Customers';
      case 'vendor': return 'Vendors';
      default: return entityType;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
                <Zap className="w-8 h-8 text-blue-600" />
                Zoho Sync Mappings
              </h1>
              <p className="text-gray-600 mt-2">
                Configure real-time synchronization from Zoho to TSH ERP System
              </p>
            </div>
            <button
              onClick={loadStatistics}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
              Refresh
            </button>
          </div>

          {/* Statistics Cards */}
          {statistics && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-6">
              <div className="bg-white rounded-lg shadow-sm p-4 border border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Total Synced</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {statistics.total_synced}
                    </p>
                  </div>
                  <CheckCircle className="w-8 h-8 text-green-600" />
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-sm p-4 border border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Total Errors</p>
                    <p className="text-2xl font-bold text-red-600">
                      {statistics.total_errors}
                    </p>
                  </div>
                  <AlertCircle className="w-8 h-8 text-red-600" />
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-sm p-4 border border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Active Syncs</p>
                    <p className="text-2xl font-bold text-blue-600">
                      {statistics.enabled_entities}
                    </p>
                  </div>
                  <Play className="w-8 h-8 text-blue-600" />
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-sm p-4 border border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Total Logs</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {statistics.total_logs}
                    </p>
                  </div>
                  <BarChart3 className="w-8 h-8 text-purple-600" />
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Entity Tabs */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-6">
          <div className="flex border-b border-gray-200">
            {(['item', 'customer', 'vendor'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => {
                  setActiveTab(tab);
                  setAnalysis(null);
                  loadLogs(tab);
                }}
                className={`flex-1 px-6 py-4 text-center font-medium transition-colors ${
                  activeTab === tab
                    ? 'bg-blue-50 text-blue-600 border-b-2 border-blue-600'
                    : 'text-gray-600 hover:bg-gray-50'
                }`}
              >
                <div className="flex items-center justify-center gap-2">
                  {getEntityIcon(tab)}
                  {getEntityLabel(tab)}
                  {mappings[tab]?.enabled && (
                    <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                  )}
                </div>
              </button>
            ))}
          </div>

          {/* Mapping Details */}
          {currentMapping && (
            <div className="p-6">
              {/* Sync Control */}
              <div className="flex items-center justify-between mb-6 pb-6 border-b border-gray-200">
                <div className="flex items-center gap-4">
                  <div>
                    <h3 className="text-xl font-semibold text-gray-900 mb-1">
                      {getEntityLabel(activeTab)}
                    </h3>
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <ArrowRight className="w-4 h-4" />
                      <span>Zoho → TSH ERP</span>
                      <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs font-medium">
                        {currentMapping.sync_mode}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <button
                    onClick={() => analyzeData(activeTab)}
                    disabled={analyzing}
                    className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-400 transition-colors"
                  >
                    <BarChart3 className="w-4 h-4" />
                    {analyzing ? 'Analyzing...' : 'Analyze'}
                  </button>

                  <button
                    onClick={() => executeSync(activeTab)}
                    disabled={syncing || !currentMapping.enabled}
                    className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 transition-colors"
                  >
                    <Play className="w-4 h-4" />
                    {syncing ? 'Syncing...' : 'Sync Now'}
                  </button>

                  <button
                    onClick={() => toggleSync(activeTab, !currentMapping.enabled)}
                    className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                      currentMapping.enabled
                        ? 'bg-yellow-600 text-white hover:bg-yellow-700'
                        : 'bg-gray-600 text-white hover:bg-gray-700'
                    }`}
                  >
                    {currentMapping.enabled ? (
                      <>
                        <Pause className="w-4 h-4" />
                        Disable
                      </>
                    ) : (
                      <>
                        <Play className="w-4 h-4" />
                        Enable
                      </>
                    )}
                  </button>

                  <button
                    onClick={() => resetMapping(activeTab)}
                    className="flex items-center gap-2 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
                  >
                    <RefreshCw className="w-4 h-4" />
                    Reset
                  </button>
                </div>
              </div>

              {/* Sync Statistics */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm text-gray-600 mb-1">Status</p>
                  <p className={`font-semibold ${getStatusColor(currentMapping.last_sync_status)}`}>
                    {currentMapping.enabled ? 'Active' : 'Disabled'}
                  </p>
                </div>

                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm text-gray-600 mb-1">Last Sync</p>
                  <p className="font-semibold text-gray-900">
                    {currentMapping.last_sync 
                      ? new Date(currentMapping.last_sync).toLocaleString()
                      : 'Never'
                    }
                  </p>
                </div>

                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm text-gray-600 mb-1">Total Synced</p>
                  <p className="font-semibold text-green-600">
                    {currentMapping.total_synced}
                  </p>
                </div>

                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm text-gray-600 mb-1">Total Errors</p>
                  <p className="font-semibold text-red-600">
                    {currentMapping.total_errors}
                  </p>
                </div>
              </div>

              {/* Data Analysis */}
              {analysis && (
                <div className="mb-6 p-4 bg-purple-50 rounded-lg border border-purple-200">
                  <h4 className="text-lg font-semibold text-purple-900 mb-4">
                    Data Analysis Results
                  </h4>
                  <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                    <div>
                      <p className="text-sm text-purple-700">Total Records</p>
                      <p className="text-2xl font-bold text-purple-900">
                        {analysis.total_records}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-purple-700">New</p>
                      <p className="text-2xl font-bold text-green-600">
                        {analysis.new_records}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-purple-700">Updated</p>
                      <p className="text-2xl font-bold text-yellow-600">
                        {analysis.updated_records}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-purple-700">Matched</p>
                      <p className="text-2xl font-bold text-blue-600">
                        {analysis.matched_records}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-purple-700">Errors</p>
                      <p className="text-2xl font-bold text-red-600">
                        {analysis.error_records}
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Field Mappings Table */}
              <div className="mb-6">
                <h4 className="text-lg font-semibold text-gray-900 mb-4">
                  Field Mappings ({currentMapping.field_mappings.length} fields)
                </h4>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead className="bg-gray-50 border-b border-gray-200">
                      <tr>
                        <th className="text-left px-4 py-3 font-medium text-gray-700">Zoho Field</th>
                        <th className="text-center px-4 py-3 font-medium text-gray-700">→</th>
                        <th className="text-left px-4 py-3 font-medium text-gray-700">TSH Field</th>
                        <th className="text-left px-4 py-3 font-medium text-gray-700">Type</th>
                        <th className="text-center px-4 py-3 font-medium text-gray-700">Required</th>
                        <th className="text-left px-4 py-3 font-medium text-gray-700">Transformation</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {currentMapping.field_mappings.map((mapping, index) => (
                        <tr key={index} className="hover:bg-gray-50">
                          <td className="px-4 py-3 font-mono text-xs text-blue-600">
                            {mapping.zoho_field}
                          </td>
                          <td className="px-4 py-3 text-center">
                            <ArrowRight className="w-4 h-4 text-gray-400 mx-auto" />
                          </td>
                          <td className="px-4 py-3 font-mono text-xs text-green-600">
                            {mapping.tsh_field}
                          </td>
                          <td className="px-4 py-3">
                            <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs">
                              {mapping.field_type}
                            </span>
                          </td>
                          <td className="px-4 py-3 text-center">
                            {mapping.is_required ? (
                              <CheckCircle className="w-4 h-4 text-green-600 mx-auto" />
                            ) : (
                              <span className="text-gray-400">—</span>
                            )}
                          </td>
                          <td className="px-4 py-3 text-xs text-gray-600">
                            {mapping.transformation_rule || '—'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Sync Settings */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                <div className="bg-gray-50 rounded-lg p-4">
                  <h5 className="font-medium text-gray-900 mb-3">Sync Options</h5>
                  <div className="space-y-2 text-sm">
                    <div className="flex items-center justify-between">
                      <span className="text-gray-600">Sync Images</span>
                      <span className={`font-medium ${currentMapping.sync_images ? 'text-green-600' : 'text-gray-400'}`}>
                        {currentMapping.sync_images ? 'Enabled' : 'Disabled'}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-gray-600">Auto Create</span>
                      <span className={`font-medium ${currentMapping.auto_create ? 'text-green-600' : 'text-gray-400'}`}>
                        {currentMapping.auto_create ? 'Enabled' : 'Disabled'}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-gray-600">Auto Update</span>
                      <span className={`font-medium ${currentMapping.auto_update ? 'text-green-600' : 'text-gray-400'}`}>
                        {currentMapping.auto_update ? 'Enabled' : 'Disabled'}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="bg-gray-50 rounded-lg p-4">
                  <h5 className="font-medium text-gray-900 mb-3">Conflict Resolution</h5>
                  <div className="space-y-2 text-sm">
                    <div className="flex items-center justify-between">
                      <span className="text-gray-600">Strategy</span>
                      <span className="font-medium text-blue-600">
                        {currentMapping.conflict_resolution}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-gray-600">Delete Sync</span>
                      <span className={`font-medium ${currentMapping.delete_sync ? 'text-red-600' : 'text-gray-400'}`}>
                        {currentMapping.delete_sync ? 'Enabled' : 'Disabled'}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-gray-600">Sync Frequency</span>
                      <span className="font-medium text-gray-900">
                        {currentMapping.sync_frequency ? `${currentMapping.sync_frequency} min` : 'Real-time'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Recent Logs */}
              <div>
                <h4 className="text-lg font-semibold text-gray-900 mb-4">
                  Recent Sync Logs
                </h4>
                <div className="space-y-2">
                  {logs.length > 0 ? (
                    logs.map((log, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div className="flex items-center gap-3">
                          <div className={`w-2 h-2 rounded-full ${
                            log.status === 'success' ? 'bg-green-500' :
                            log.status === 'error' ? 'bg-red-500' :
                            'bg-yellow-500'
                          }`}></div>
                          <div>
                            <p className="text-sm font-medium text-gray-900">
                              {log.operation} - {log.sync_id}
                            </p>
                            {log.error_message && (
                              <p className="text-xs text-red-600">{log.error_message}</p>
                            )}
                          </div>
                        </div>
                        <div className="flex items-center gap-2 text-xs text-gray-600">
                          <Clock className="w-3 h-3" />
                          {new Date(log.timestamp).toLocaleString()}
                        </div>
                      </div>
                    ))
                  ) : (
                    <p className="text-center text-gray-500 py-8">No sync logs available</p>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ZohoSyncMappings;
