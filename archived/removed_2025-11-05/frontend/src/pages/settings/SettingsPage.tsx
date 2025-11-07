import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { 
  Download, 
  Upload, 
  Trash2, 
  Database, 
  Settings as SettingsIcon,
  HardDrive,
  Shield,
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  Info
} from 'lucide-react';
import { PermissionsManagement } from '../../components/settings/PermissionsManagement';

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

const SettingsPage: React.FC = () => {
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

  const downloadBackup = async (filename: string) => {
    try {
      const response = await fetch(`${API_BASE}/backup/download/${filename}`);
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        showMessage('success', 'تم تحميل النسخة الاحتياطية / Backup downloaded successfully');
      }
    } catch (error) {
      showMessage('error', `خطأ في تحميل النسخة الاحتياطية / Error downloading backup: ${error}`);
    }
  };

  const deleteBackup = async (filename: string) => {
    if (!confirm(`هل أنت متأكد من حذف النسخة الاحتياطية؟ / Are you sure you want to delete this backup?\n${filename}`)) {
      return;
    }

    try {
      const response = await fetch(`${API_BASE}/backup/delete/${filename}`, {
        method: 'DELETE',
      });

      const data = await response.json();
      if (data.status === 'success') {
        showMessage('success', 'تم حذف النسخة الاحتياطية / Backup deleted successfully');
        await loadBackups();
        await loadSystemInfo();
      } else {
        showMessage('error', `فشل في حذف النسخة الاحتياطية / Failed to delete backup: ${data.detail}`);
      }
    } catch (error) {
      showMessage('error', `خطأ في حذف النسخة الاحتياطية / Error deleting backup: ${error}`);
    }
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
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">الإعدادات / Settings</h1>
          <p className="text-gray-600">إدارة إعدادات النظام والنسخ الاحتياطية / Manage system settings and backups</p>
        </div>
        <Button onClick={() => { loadSystemInfo(); loadBackups(); }}>
          <RefreshCw className="w-4 h-4 mr-2" />
          تحديث / Refresh
        </Button>
      </div>

      {message && (
        <div className={`p-4 rounded-lg border ${
          message.type === 'error' ? 'border-red-200 bg-red-50 text-red-800' : 
          message.type === 'success' ? 'border-green-200 bg-green-50 text-green-800' : 
          'border-blue-200 bg-blue-50 text-blue-800'
        }`}>
          <div className="flex items-center space-x-2">
            {message.type === 'error' && <AlertTriangle className="w-4 h-4" />}
            {message.type === 'success' && <CheckCircle className="w-4 h-4" />}
            {message.type === 'info' && <Info className="w-4 h-4" />}
            <span>{message.text}</span>
          </div>
        </div>
      )}

      {/* Custom Tabs */}
      <div className="border-b">
        <div className="flex space-x-4">
          {[
            { key: 'overview', label: 'نظرة عامة / Overview' },
            { key: 'backup', label: 'النسخ الاحتياطية / Backup' },
            { key: 'restore', label: 'الاستعادة / Restore' },
            { key: 'permissions', label: 'الصلاحيات / Permissions' },
            { key: 'translations', label: 'الترجمات / Translations' }
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
      {activeTab === 'overview' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {systemInfo && (
            <>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">قاعدة البيانات / Database</CardTitle>
                  <Database className="h-4 w-4 text-gray-500" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{systemInfo.database.table_count} جدول / Tables</div>
                  <p className="text-xs text-gray-500">
                    الحجم / Size: {systemInfo.database.size}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    {systemInfo.database.version.split(',')[0]}
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">النسخ الاحتياطية / Backups</CardTitle>
                  <HardDrive className="h-4 w-4 text-gray-500" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{systemInfo.backups.count}</div>
                  <p className="text-xs text-gray-500">
                    الحجم الإجمالي / Total Size: {formatFileSize(systemInfo.backups.total_size)}
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">التطبيق / Application</CardTitle>
                  <SettingsIcon className="h-4 w-4 text-gray-500" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">v{systemInfo.application.version}</div>
                  <p className="text-xs text-gray-500">
                    {systemInfo.application.name}
                  </p>
                </CardContent>
              </Card>
            </>
          )}
        </div>
      )}

      {activeTab === 'backup' && (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>إنشاء نسخة احتياطية جديدة / Create New Backup</CardTitle>
              <CardDescription>
                إنشاء نسخة احتياطية من قاعدة البيانات / Create a backup of the database
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">الوصف / Description (اختياري / Optional)</label>
                <Input
                  placeholder="مثال: نسخة احتياطية شهرية / Example: Monthly backup"
                  value={backupDescription}
                  onChange={(e) => setBackupDescription(e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">خيارات النسخ الاحتياطي / Backup Options</label>
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

              <Button onClick={createBackup} disabled={loading} className="w-full">
                {loading ? 'جاري الإنشاء... / Creating...' : 'إنشاء نسخة احتياطية / Create Backup'}
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>النسخ الاحتياطية المتاحة / Available Backups</CardTitle>
              <CardDescription>
                إدارة النسخ الاحتياطية الموجودة / Manage existing backups
              </CardDescription>
            </CardHeader>
            <CardContent>
              {backups.length === 0 ? (
                <p className="text-center text-gray-500 py-8">
                  لا توجد نسخ احتياطية / No backups available
                </p>
              ) : (
                <div className="space-y-3">
                  {backups.map((backup) => (
                    <div key={backup.filename} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex-1">
                        <div className="font-medium">{backup.filename}</div>
                        <div className="text-sm text-gray-500">
                          الحجم / Size: {formatFileSize(backup.size)} • 
                          تم الإنشاء / Created: {formatDate(backup.created_at)}
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Button
                          variant="outline"
                          onClick={() => downloadBackup(backup.filename)}
                        >
                          <Download className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="outline"
                          onClick={() => deleteBackup(backup.filename)}
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {activeTab === 'restore' && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Shield className="w-5 h-5 text-amber-500" />
              <span>استعادة قاعدة البيانات / Database Restore</span>
            </CardTitle>
            <CardDescription>
              استعادة قاعدة البيانات من نسخة احتياطية / Restore database from backup
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="p-4 mb-6 border border-amber-200 bg-amber-50 rounded-lg">
              <div className="flex items-center space-x-2">
                <AlertTriangle className="w-4 h-4 text-amber-600" />
                <strong className="text-amber-800">تحذير / Warning:</strong>
              </div>
              <p className="text-amber-700 mt-1">
                استعادة قاعدة البيانات ستحذف جميع البيانات الحالية. تأكد من إنشاء نسخة احتياطية قبل المتابعة.
                <br />
                Database restore will delete all current data. Make sure to create a backup before proceeding.
              </p>
            </div>

            {backups.length === 0 ? (
              <p className="text-center text-gray-500 py-8">
                لا توجد نسخ احتياطية للاستعادة / No backups available for restore
              </p>
            ) : (
              <div className="space-y-3">
                {backups.map((backup) => (
                  <div key={backup.filename} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex-1">
                      <div className="font-medium">{backup.filename}</div>
                      <div className="text-sm text-gray-500">
                        الحجم / Size: {formatFileSize(backup.size)} • 
                        تم الإنشاء / Created: {formatDate(backup.created_at)}
                      </div>
                    </div>
                    <Button
                      onClick={() => {
                        if (confirm(`هل أنت متأكد من استعادة هذه النسخة الاحتياطية؟ / Are you sure you want to restore this backup?\n\n${backup.filename}\n\nسيتم حذف جميع البيانات الحالية / All current data will be deleted!`)) {
                          showMessage('info', 'ميزة الاستعادة قيد التطوير / Restore feature under development');
                        }
                      }}
                      className="bg-red-600 hover:bg-red-700 text-white"
                    >
                      <Upload className="w-4 h-4 mr-2" />
                      استعادة / Restore
                    </Button>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {activeTab === 'permissions' && (
        <PermissionsManagement />
      )}

      {activeTab === 'translations' && (
        <Card>
          <CardHeader>
            <CardTitle>إدارة الترجمات / Translation Management</CardTitle>
            <CardDescription>
              إدارة ترجمات النظام / Manage system translations
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-center text-gray-500 py-8">
              ميزة إدارة الترجمات متاحة في صفحة منفصلة / Translation management available in separate page
            </p>
            <Button className="w-full">
              الانتقال إلى إدارة الترجمات / Go to Translation Management
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default SettingsPage;
