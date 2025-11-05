import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import {
  Download,
  Upload,
  Trash2,
  Database,
  HardDrive,
  Shield,
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  Info,
  Clock,
  Archive,
  Image as ImageIcon,
  Settings
} from 'lucide-react';

interface BackupInfo {
  type: string;
  filename: string;
  size: number;
  size_human: string;
  created_at: string;
  path: string;
}

interface BackupList {
  database: BackupInfo[];
  images: BackupInfo[];
  env: BackupInfo[];
  full: BackupInfo[];
}

interface Message {
  type: 'success' | 'error' | 'info' | 'warning';
  text: string;
}

const API_BASE = 'http://192.168.68.66:8000/api/backup';

export const BackupRestoreModule: React.FC = () => {
  const [backups, setBackups] = useState<BackupList>({
    database: [],
    images: [],
    env: [],
    full: []
  });
  const [latestBackups, setLatestBackups] = useState<any>({});
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<Message | null>(null);
  const [activeTab, setActiveTab] = useState<'database' | 'images' | 'env' | 'full'>('full');
  const [selectedBackup, setSelectedBackup] = useState<BackupInfo | null>(null);
  const [showRestoreConfirm, setShowRestoreConfirm] = useState(false);

  useEffect(() => {
    loadBackups();
    loadLatestBackups();
  }, []);

  const showMessage = (type: Message['type'], text: string) => {
    setMessage({ type, text });
    setTimeout(() => setMessage(null), 5000);
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

  const loadLatestBackups = async () => {
    try {
      const response = await fetch(`${API_BASE}/backups/latest`);
      const data = await response.json();
      if (data.status === 'success') {
        setLatestBackups(data.latest_backups);
      }
    } catch (error) {
      console.error('Error loading latest backups:', error);
    }
  };

  const createBackup = async (type: string) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/backup/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type })
      });
      const data = await response.json();

      if (data.status === 'success') {
        showMessage('success', `${type} backup created successfully!`);
        await loadBackups();
        await loadLatestBackups();
      } else {
        showMessage('error', data.detail || 'Backup failed');
      }
    } catch (error) {
      showMessage('error', 'Error creating backup');
    } finally {
      setLoading(false);
    }
  };

  const restoreBackup = async () => {
    if (!selectedBackup) return;

    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/backup/restore`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          backup_file: selectedBackup.path,
          type: selectedBackup.type
        })
      });
      const data = await response.json();

      if (data.status === 'success') {
        showMessage('success', `${selectedBackup.type} restored successfully!`);
        setShowRestoreConfirm(false);
        setSelectedBackup(null);
      } else {
        showMessage('error', data.detail || 'Restore failed');
      }
    } catch (error) {
      showMessage('error', 'Error restoring backup');
    } finally {
      setLoading(false);
    }
  };

  const downloadBackup = async (backup: BackupInfo) => {
    try {
      window.open(`${API_BASE}/backup/download/${backup.type}/${backup.filename}`, '_blank');
      showMessage('success', 'Download started');
    } catch (error) {
      showMessage('error', 'Error downloading backup');
    }
  };

  const deleteBackup = async (backup: BackupInfo) => {
    if (!confirm(`Are you sure you want to delete ${backup.filename}?`)) return;

    try {
      const response = await fetch(`${API_BASE}/backup/delete/${backup.type}/${backup.filename}`, {
        method: 'DELETE'
      });
      const data = await response.json();

      if (data.status === 'success') {
        showMessage('success', 'Backup deleted');
        await loadBackups();
      } else {
        showMessage('error', data.detail || 'Delete failed');
      }
    } catch (error) {
      showMessage('error', 'Error deleting backup');
    }
  };

  const getBackupIcon = (type: string) => {
    switch (type) {
      case 'database': return <Database className="w-5 h-5" />;
      case 'images': return <ImageIcon className="w-5 h-5" />;
      case 'env': return <Settings className="w-5 h-5" />;
      case 'full': return <Archive className="w-5 h-5" />;
      default: return <HardDrive className="w-5 h-5" />;
    }
  };

  const getMessageIcon = () => {
    switch (message?.type) {
      case 'success': return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'error': return <AlertTriangle className="w-5 h-5 text-red-500" />;
      case 'warning': return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
      case 'info': return <Info className="w-5 h-5 text-blue-500" />;
      default: return null;
    }
  };

  return (
    <div className="space-y-6">
      {/* Message Banner */}
      {message && (
        <div className={`flex items-center gap-3 p-4 rounded-lg ${
          message.type === 'success' ? 'bg-green-50 text-green-800' :
          message.type === 'error' ? 'bg-red-50 text-red-800' :
          message.type === 'warning' ? 'bg-yellow-50 text-yellow-800' :
          'bg-blue-50 text-blue-800'
        }`}>
          {getMessageIcon()}
          <span>{message.text}</span>
        </div>
      )}

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="w-6 h-6" />
            Backup & Restore System
          </CardTitle>
          <CardDescription>
            Protect your data with automated backups for database, images, and configuration files
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Button
              onClick={() => createBackup('full')}
              disabled={loading}
              className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700"
            >
              <Archive className="w-4 h-4" />
              {loading ? 'Creating...' : 'Full Backup'}
            </Button>

            <Button
              onClick={() => createBackup('database')}
              disabled={loading}
              variant="outline"
              className="flex items-center gap-2"
            >
              <Database className="w-4 h-4" />
              Database Only
            </Button>

            <Button
              onClick={() => createBackup('images')}
              disabled={loading}
              variant="outline"
              className="flex items-center gap-2"
            >
              <ImageIcon className="w-4 h-4" />
              Images Only
            </Button>

            <Button
              onClick={() => createBackup('env')}
              disabled={loading}
              variant="outline"
              className="flex items-center gap-2"
            >
              <Settings className="w-4 h-4" />
              Config Only
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Latest Backups */}
      <Card>
        <CardHeader>
          <CardTitle>Latest Backups</CardTitle>
          <CardDescription>Most recent backup for each type</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {['database', 'images', 'env', 'full'].map((type) => (
              <div key={type} className="border rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  {getBackupIcon(type)}
                  <h3 className="font-semibold capitalize">{type}</h3>
                </div>
                {latestBackups[type] ? (
                  <>
                    <p className="text-sm text-gray-600 mb-1">{latestBackups[type].size_human}</p>
                    <p className="text-xs text-gray-400">
                      {new Date(latestBackups[type].created_at).toLocaleString()}
                    </p>
                    <Button
                      size="sm"
                      variant="outline"
                      className="mt-2 w-full"
                      onClick={() => downloadBackup({ ...latestBackups[type], type })}
                    >
                      <Download className="w-3 h-3 mr-1" />
                      Download
                    </Button>
                  </>
                ) : (
                  <p className="text-sm text-gray-400">No backup available</p>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Backup History */}
      <Card>
        <CardHeader>
          <CardTitle>Backup History</CardTitle>
          <CardDescription>Browse and manage all backups</CardDescription>
        </CardHeader>
        <CardContent>
          {/* Tabs */}
          <div className="flex gap-2 mb-4">
            {(['full', 'database', 'images', 'env'] as const).map((tab) => (
              <Button
                key={tab}
                variant={activeTab === tab ? 'default' : 'outline'}
                size="sm"
                onClick={() => setActiveTab(tab)}
                className="capitalize"
              >
                {getBackupIcon(tab)}
                <span className="ml-2">{tab}</span>
                <span className="ml-1 text-xs">({backups[tab].length})</span>
              </Button>
            ))}
          </div>

          {/* Backup List */}
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {backups[activeTab].length === 0 ? (
              <p className="text-center text-gray-400 py-8">No {activeTab} backups found</p>
            ) : (
              backups[activeTab].map((backup) => (
                <div key={backup.filename} className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50">
                  <div className="flex-1">
                    <p className="font-medium">{backup.filename}</p>
                    <div className="flex items-center gap-4 text-sm text-gray-600 mt-1">
                      <span className="flex items-center gap-1">
                        <HardDrive className="w-3 h-3" />
                        {backup.size_human}
                      </span>
                      <span className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {new Date(backup.created_at).toLocaleString()}
                      </span>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => downloadBackup(backup)}
                    >
                      <Download className="w-4 h-4" />
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => {
                        setSelectedBackup(backup);
                        setShowRestoreConfirm(true);
                      }}
                    >
                      <Upload className="w-4 h-4" />
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => deleteBackup(backup)}
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              ))
            )}
          </div>
        </CardContent>
      </Card>

      {/* Restore Confirmation Modal */}
      {showRestoreConfirm && selectedBackup && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <Card className="max-w-md w-full mx-4">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-red-600">
                <AlertTriangle className="w-6 h-6" />
                Confirm Restore
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <p className="text-yellow-800 font-semibold mb-2">⚠️ Warning</p>
                <p className="text-sm text-yellow-700">
                  This will restore {selectedBackup.type} from backup: <strong>{selectedBackup.filename}</strong>
                </p>
                <p className="text-sm text-yellow-700 mt-2">
                  Current data will be overwritten. This action cannot be undone!
                </p>
              </div>

              <div className="flex gap-3">
                <Button
                  variant="outline"
                  className="flex-1"
                  onClick={() => {
                    setShowRestoreConfirm(false);
                    setSelectedBackup(null);
                  }}
                >
                  Cancel
                </Button>
                <Button
                  className="flex-1 bg-red-600 hover:bg-red-700"
                  onClick={restoreBackup}
                  disabled={loading}
                >
                  {loading ? 'Restoring...' : 'Yes, Restore'}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};
