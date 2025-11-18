import React, { useState } from 'react';
import { ArrowLeft, Fingerprint, Smartphone, Key, Shield, CheckCircle, Copy } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const MFASettings: React.FC = () => {
  const navigate = useNavigate();
  const [mfaEnabled, setMfaEnabled] = useState(false);
  const [authMethod, setAuthMethod] = useState<'app' | 'sms' | 'email'>('app');
  const [showQR, setShowQR] = useState(false);
  const [backupCodes] = useState([
    'ABC123-DEF456',
    'GHI789-JKL012',
    'MNO345-PQR678',
    'STU901-VWX234',
    'YZA567-BCD890',
  ]);

  const handleEnableMFA = () => {
    setShowQR(true);
  };

  const copyCode = (code: string) => {
    navigator.clipboard.writeText(code);
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
            <div className="p-3 bg-purple-500 rounded-xl">
              <Fingerprint className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-800">Multi-Factor Authentication</h1>
              <p className="text-gray-600">Add an extra layer of security to your account</p>
            </div>
          </div>
        </div>

        {/* Main Toggle */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div>
              <h3 className="font-semibold text-gray-800">Enable Two-Factor Authentication</h3>
              <p className="text-sm text-gray-600">Require a second verification step when logging in</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={mfaEnabled}
                onChange={(e) => {
                  setMfaEnabled(e.target.checked);
                  if (e.target.checked) handleEnableMFA();
                }}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-500"></div>
            </label>
          </div>

          {mfaEnabled && (
            <div className="mt-6 space-y-6">
              {/* Authentication Method */}
              <div>
                <h4 className="font-semibold text-gray-800 mb-3">Choose Authentication Method</h4>
                <div className="space-y-3">
                  <label className="flex items-center p-4 border-2 border-gray-200 rounded-lg cursor-pointer hover:border-purple-300 transition-colors">
                    <input
                      type="radio"
                      name="auth-method"
                      value="app"
                      checked={authMethod === 'app'}
                      onChange={() => setAuthMethod('app')}
                      className="w-4 h-4 text-purple-600"
                    />
                    <div className="ml-3 flex items-center gap-3 flex-1">
                      <Smartphone className="w-5 h-5 text-purple-600" />
                      <div>
                        <p className="font-medium text-gray-800">Authenticator App</p>
                        <p className="text-sm text-gray-600">Use an app like Google Authenticator or Authy</p>
                      </div>
                    </div>
                  </label>

                  <label className="flex items-center p-4 border-2 border-gray-200 rounded-lg cursor-pointer hover:border-purple-300 transition-colors">
                    <input
                      type="radio"
                      name="auth-method"
                      value="sms"
                      checked={authMethod === 'sms'}
                      onChange={() => setAuthMethod('sms')}
                      className="w-4 h-4 text-purple-600"
                    />
                    <div className="ml-3 flex items-center gap-3 flex-1">
                      <Smartphone className="w-5 h-5 text-blue-600" />
                      <div>
                        <p className="font-medium text-gray-800">SMS Text Message</p>
                        <p className="text-sm text-gray-600">Receive codes via text message</p>
                      </div>
                    </div>
                  </label>

                  <label className="flex items-center p-4 border-2 border-gray-200 rounded-lg cursor-pointer hover:border-purple-300 transition-colors">
                    <input
                      type="radio"
                      name="auth-method"
                      value="email"
                      checked={authMethod === 'email'}
                      onChange={() => setAuthMethod('email')}
                      className="w-4 h-4 text-purple-600"
                    />
                    <div className="ml-3 flex items-center gap-3 flex-1">
                      <Key className="w-5 h-5 text-green-600" />
                      <div>
                        <p className="font-medium text-gray-800">Email</p>
                        <p className="text-sm text-gray-600">Receive codes via email</p>
                      </div>
                    </div>
                  </label>
                </div>
              </div>

              {/* QR Code Section */}
              {showQR && authMethod === 'app' && (
                <div className="p-6 bg-purple-50 rounded-lg">
                  <h4 className="font-semibold text-gray-800 mb-3">Scan QR Code</h4>
                  <div className="flex flex-col items-center gap-4">
                    <div className="w-48 h-48 bg-white p-4 rounded-lg shadow-md">
                      <div className="w-full h-full bg-gray-200 rounded flex items-center justify-center">
                        <p className="text-gray-500 text-sm text-center">QR Code Placeholder</p>
                      </div>
                    </div>
                    <div className="text-center">
                      <p className="text-sm text-gray-600 mb-2">Or enter this code manually:</p>
                      <code className="px-4 py-2 bg-white rounded-lg text-purple-600 font-mono">
                        ABCD-EFGH-IJKL-MNOP
                      </code>
                    </div>
                  </div>
                </div>
              )}

              {/* Backup Codes */}
              <div className="p-6 bg-yellow-50 border border-yellow-200 rounded-lg">
                <div className="flex items-start gap-3 mb-4">
                  <Shield className="w-6 h-6 text-yellow-600 flex-shrink-0" />
                  <div>
                    <h4 className="font-semibold text-yellow-900 mb-2">Backup Recovery Codes</h4>
                    <p className="text-sm text-yellow-800 mb-4">
                      Save these codes in a secure location. You can use them to access your account if you lose your authentication device.
                    </p>
                    <div className="grid grid-cols-2 gap-2">
                      {backupCodes.map((code, index) => (
                        <div
                          key={index}
                          className="flex items-center justify-between px-3 py-2 bg-white rounded-lg"
                        >
                          <code className="text-sm font-mono text-gray-800">{code}</code>
                          <button
                            onClick={() => copyCode(code)}
                            className="p-1 hover:bg-gray-100 rounded"
                          >
                            <Copy className="w-4 h-4 text-gray-600" />
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Active 2FA Methods */}
        {mfaEnabled && (
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-xl font-semibold text-gray-800 mb-4">Active Authentication Methods</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-4 bg-green-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <CheckCircle className="w-5 h-5 text-green-600" />
                  <div>
                    <p className="font-medium text-gray-800">Authenticator App</p>
                    <p className="text-sm text-gray-600">Last used: 2 hours ago</p>
                  </div>
                </div>
                <button className="px-3 py-1 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors">
                  Remove
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MFASettings;
