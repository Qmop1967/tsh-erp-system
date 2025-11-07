import React, { useState, useEffect } from 'react';

interface BackupItem {
  filename: string;
  path: string;
  size: number;
  created_at: string;
  modified_at: string;
}

interface SystemInfo {
  database: {
    version: string;
    table_count: number;
    size: string;
  };
  backups: {
    count: number;
    total_size: number;
    backup_dir: string;
  };
  application: {
    name: string;
    version: string;
    last_checked: string;
  };
}

const SettingsPageMinimal: React.FC = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [backups, setBackups] = useState<BackupItem[]>([]);
  const [systemInfo, setSystemInfo] = useState<SystemInfo | null>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error' | 'info'; text: string } | null>(null);
  
  // Backup form state
  const [backupDescription, setBackupDescription] = useState('');
  const [includeData, setIncludeData] = useState(true);
  const [includeSchema, setIncludeSchema] = useState(true);

  const API_BASE = 'http://localhost:8000/api/settings';

  useEffect(() => {
    loadSystemInfo();
    loadBackups();
  }, []);

  const showMessage = (type: 'success' | 'error' | 'info', text: string) => {
    setMessage({ type, text });
    setTimeout(() => setMessage(null), 5000);
  };

  const loadSystemInfo = async () => {
    try {
      const response = await fetch(`${API_BASE}/system/info`);
      const data = await response.json();
      if (data.status === 'success') {
        setSystemInfo(data.system_info);
      }
    } catch (error) {
      console.error('Error loading system info:', error);
      showMessage('error', 'Failed to load system info');
    }
  };

  const loadBackups = async () => {
    try {
      const response = await fetch(`${API_BASE}/backups/list`);
      const data = await response.json();
      if (data.status === 'success') {
        setBackups(data.backups);
      }
    } catch (error) {
      console.error('Error loading backups:', error);
      showMessage('error', 'Failed to load backups');
    }
  };

  const createBackup = async () => {
    if (!includeData && !includeSchema) {
      showMessage('error', 'يجب تحديد البيانات أو الهيكل على الأقل / Must select at least data or schema');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/backup/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          include_data: includeData,
          include_schema: includeSchema,
          description: backupDescription || undefined,
        }),
      });

      const data = await response.json();
      if (data.status === 'success') {
        showMessage('success', 'تم إنشاء النسخة الاحتياطية بنجاح / Backup created successfully');
        setBackupDescription('');
        await loadBackups();
        await loadSystemInfo();
      } else {
        showMessage('error', `فشل في إنشاء النسخة الاحتياطية / Failed to create backup: ${data.detail}`);
      }
    } catch (error) {
      showMessage('error', `خطأ في إنشاء النسخة الاحتياطية / Error creating backup: ${error}`);
    }
    setLoading(false);
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('ar-EG', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">الإعدادات / Settings</h1>
              <p className="text-gray-600 mt-2">إدارة إعدادات النظام والنسخ الاحتياطية / Manage system settings and backups</p>
            </div>
            <button 
              onClick={() => { loadSystemInfo(); loadBackups(); }}
              className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
            >
              🔄 تحديث / Refresh
            </button>
          </div>
        </div>

        {/* Message */}
        {message && (
          <div className={`p-4 rounded-lg border ${
            message.type === 'error' ? 'border-red-200 bg-red-50 text-red-800' : 
            message.type === 'success' ? 'border-green-200 bg-green-50 text-green-800' : 
            'border-blue-200 bg-blue-50 text-blue-800'
          }`}>
            <div className="flex items-center space-x-2">
              <span>{message.type === 'error' ? '❌' : message.type === 'success' ? '✅' : 'ℹ️'}</span>
              <span>{message.text}</span>
            </div>
          </div>
        )}

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow">
          <div className="border-b">
            <div className="flex space-x-4 p-4">
              {[
                { key: 'overview', label: 'نظرة عامة / Overview' },
                { key: 'backup', label: 'النسخ الاحتياطية / Backup' },
                { key: 'restore', label: 'الاستعادة / Restore' }
              ].map((tab) => (
                <button
                  key={tab.key}
                  onClick={() => setActiveTab(tab.key)}
                  className={`px-4 py-2 font-medium border-b-2 transition-colors ${
                    activeTab === tab.key
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {activeTab === 'overview' && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {systemInfo && (
                  <>
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="font-medium">قاعدة البيانات / Database</h3>
                        <span>💾</span>
                      </div>
                      <div className="text-2xl font-bold">{systemInfo.database.table_count} جدول / Tables</div>
                      <p className="text-sm text-gray-600">الحجم / Size: {systemInfo.database.size}</p>
                    </div>

                    <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="font-medium">النسخ الاحتياطية / Backups</h3>
                        <span>🗂️</span>
                      </div>
                      <div className="text-2xl font-bold">{systemInfo.backups.count}</div>
                      <p className="text-sm text-gray-600">الحجم الإجمالي / Total Size: {formatFileSize(systemInfo.backups.total_size)}</p>
                    </div>

                    <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="font-medium">التطبيق / Application</h3>
                        <span>⚙️</span>
                      </div>
                      <div className="text-2xl font-bold">v{systemInfo.application.version}</div>
                      <p className="text-sm text-gray-600">{systemInfo.application.name}</p>
                    </div>
                  </>
                )}
              </div>
            )}

            {activeTab === 'backup' && (
              <div className="space-y-6">
                {/* Create Backup */}
                <div className="bg-gray-50 rounded-lg p-6">
                  <h3 className="text-xl font-semibold mb-4">إنشاء نسخة احتياطية جديدة / Create New Backup</h3>
                  
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium mb-2">الوصف / Description (اختياري / Optional)</label>
                      <input
                        type="text"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="مثال: نسخة احتياطية شهرية / Example: Monthly backup"
                        value={backupDescription}
                        onChange={(e) => setBackupDescription(e.target.value)}
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium mb-2">خيارات النسخ الاحتياطي / Backup Options</label>
                      <div className="flex items-center space-x-4">
                        <label className="flex items-center space-x-2">
                          <input
                            type="checkbox"
                            checked={includeSchema}
                            onChange={(e) => setIncludeSchema(e.target.checked)}
                          />
                          <span>هيكل قاعدة البيانات / Database Schema</span>
                        </label>
                        <label className="flex items-center space-x-2">
                          <input
                            type="checkbox"
                            checked={includeData}
                            onChange={(e) => setIncludeData(e.target.checked)}
                          />
                          <span>البيانات / Data</span>
                        </label>
                      </div>
                    </div>

                    <button 
                      onClick={createBackup} 
                      disabled={loading}
                      className="w-full bg-blue-500 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded disabled:opacity-50"
                    >
                      {loading ? 'جاري الإنشاء... / Creating...' : 'إنشاء نسخة احتياطية / Create Backup'}
                    </button>
                  </div>
                </div>

                {/* Backups List */}
                <div>
                  <h3 className="text-xl font-semibold mb-4">النسخ الاحتياطية المتاحة / Available Backups</h3>
                  
                  {backups.length === 0 ? (
                    <p className="text-center text-gray-500 py-8">لا توجد نسخ احتياطية / No backups available</p>
                  ) : (
                    <div className="space-y-3">
                      {backups.map((backup) => (
                        <div key={backup.filename} className="flex items-center justify-between p-4 border rounded-lg bg-white">
                          <div className="flex-1">
                            <div className="font-medium">{backup.filename}</div>
                            <div className="text-sm text-gray-500">
                              الحجم / Size: {formatFileSize(backup.size)} • 
                              تم الإنشاء / Created: {formatDate(backup.created_at)}
                            </div>
                          </div>
                          <div className="flex items-center space-x-2">
                            <button className="bg-green-500 hover:bg-green-700 text-white font-bold py-1 px-3 rounded text-sm">
                              📥 تحميل / Download
                            </button>
                            <button className="bg-red-500 hover:bg-red-700 text-white font-bold py-1 px-3 rounded text-sm">
                              🗑️ حذف / Delete
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}

            {activeTab === 'restore' && (
              <div className="bg-amber-50 border border-amber-200 rounded-lg p-6">
                <div className="flex items-center space-x-2 mb-4">
                  <span className="text-2xl">⚠️</span>
                  <h3 className="text-xl font-semibold text-amber-800">استعادة قاعدة البيانات / Database Restore</h3>
                </div>
                <p className="text-amber-700 mb-4">
                  استعادة قاعدة البيانات ستحذف جميع البيانات الحالية. تأكد من إنشاء نسخة احتياطية قبل المتابعة.
                  <br />
                  Database restore will delete all current data. Make sure to create a backup before proceeding.
                </p>
                <p className="text-center text-gray-600 py-8">
                  🔄 ميزة الاستعادة قيد التطوير / Restore feature under development
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsPageMinimal;
