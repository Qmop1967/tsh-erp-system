import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Shield } from 'lucide-react';
import { Button } from '../../../components/ui/button';
import { BackupRestoreModule } from '../../../components/settings/BackupRestoreModule';

const BackupRestorePage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <Button
            variant="ghost"
            onClick={() => navigate('/settings')}
            className="mb-4"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Settings
          </Button>

          <div className="flex items-center gap-3">
            <div className="p-3 bg-blue-100 rounded-lg">
              <Shield className="w-8 h-8 text-blue-600" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Backup & Restore</h1>
              <p className="text-gray-600 mt-1">
                Protect your data with automated backups and restore capabilities
              </p>
            </div>
          </div>
        </div>

        {/* Backup & Restore Module */}
        <BackupRestoreModule />

        {/* Info Section */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white rounded-lg p-6 border">
            <h3 className="font-semibold text-gray-900 mb-2">🔄 Automated Protection</h3>
            <p className="text-sm text-gray-600">
              Schedule automatic backups to run daily, weekly, or at custom intervals
            </p>
          </div>

          <div className="bg-white rounded-lg p-6 border">
            <h3 className="font-semibold text-gray-900 mb-2">💾 What's Backed Up</h3>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Database (PostgreSQL)</li>
              <li>• Product Images</li>
              <li>• Configuration Files</li>
            </ul>
          </div>

          <div className="bg-white rounded-lg p-6 border">
            <h3 className="font-semibold text-gray-900 mb-2">🛡️ 3-2-1 Strategy</h3>
            <p className="text-sm text-gray-600">
              3 copies, 2 media types, 1 offsite location for maximum protection
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BackupRestorePage;
