import React, { useState } from 'react';
import { ArrowLeft, Smartphone, Monitor, Tablet, Trash2, Shield, MapPin, Clock } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface Device {
  id: string;
  name: string;
  type: 'mobile' | 'desktop' | 'tablet';
  os: string;
  browser: string;
  location: string;
  lastActive: string;
  trusted: boolean;
  ipAddress: string;
}

const DevicesManagement: React.FC = () => {
  const navigate = useNavigate();
  const [devices, setDevices] = useState<Device[]>([
    {
      id: '1',
      name: 'iPhone 14 Pro',
      type: 'mobile',
      os: 'iOS 17.0',
      browser: 'Safari',
      location: 'Dubai, UAE',
      lastActive: '2 minutes ago',
      trusted: true,
      ipAddress: '192.168.1.100',
    },
    {
      id: '2',
      name: 'MacBook Pro',
      type: 'desktop',
      os: 'macOS Sonoma',
      browser: 'Chrome 118',
      location: 'Dubai, UAE',
      lastActive: 'Active now',
      trusted: true,
      ipAddress: '192.168.1.101',
    },
    {
      id: '3',
      name: 'Windows PC',
      type: 'desktop',
      os: 'Windows 11',
      browser: 'Edge 118',
      location: 'Abu Dhabi, UAE',
      lastActive: '1 hour ago',
      trusted: false,
      ipAddress: '192.168.2.50',
    },
  ]);

  const getDeviceIcon = (type: string) => {
    switch (type) {
      case 'mobile':
        return Smartphone;
      case 'tablet':
        return Tablet;
      default:
        return Monitor;
    }
  };

  const handleRemoveDevice = (deviceId: string) => {
    setDevices(devices.filter(d => d.id !== deviceId));
  };

  const handleTrustToggle = (deviceId: string) => {
    setDevices(devices.map(d => 
      d.id === deviceId ? { ...d, trusted: !d.trusted } : d
    ));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-6">
      <div className="max-w-6xl mx-auto">
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
              <Smartphone className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-800">Devices Management</h1>
              <p className="text-gray-600">View and manage authorized devices</p>
            </div>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Total Devices</p>
                <p className="text-3xl font-bold text-gray-800">{devices.length}</p>
              </div>
              <div className="p-3 bg-blue-100 rounded-lg">
                <Smartphone className="w-6 h-6 text-blue-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Trusted Devices</p>
                <p className="text-3xl font-bold text-gray-800">
                  {devices.filter(d => d.trusted).length}
                </p>
              </div>
              <div className="p-3 bg-green-100 rounded-lg">
                <Shield className="w-6 h-6 text-green-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Active Sessions</p>
                <p className="text-3xl font-bold text-gray-800">
                  {devices.filter(d => d.lastActive.includes('now')).length}
                </p>
              </div>
              <div className="p-3 bg-purple-100 rounded-lg">
                <Clock className="w-6 h-6 text-purple-600" />
              </div>
            </div>
          </div>
        </div>

        {/* Devices List */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h3 className="text-xl font-semibold text-gray-800 mb-4">Connected Devices</h3>
          
          <div className="space-y-4">
            {devices.map((device) => {
              const DeviceIcon = getDeviceIcon(device.type);
              return (
                <div
                  key={device.id}
                  className="p-4 border border-gray-200 rounded-lg hover:border-purple-300 transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex gap-4 flex-1">
                      <div className={`p-3 rounded-lg ${device.trusted ? 'bg-green-100' : 'bg-gray-100'}`}>
                        <DeviceIcon className={`w-6 h-6 ${device.trusted ? 'text-green-600' : 'text-gray-600'}`} />
                      </div>
                      
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h4 className="font-semibold text-gray-800">{device.name}</h4>
                          {device.trusted && (
                            <span className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full flex items-center gap-1">
                              <Shield className="w-3 h-3" />
                              Trusted
                            </span>
                          )}
                          {device.lastActive.includes('now') && (
                            <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full">
                              Active
                            </span>
                          )}
                        </div>
                        
                        <div className="text-sm text-gray-600 space-y-1">
                          <p>{device.os} • {device.browser}</p>
                          <div className="flex items-center gap-4">
                            <span className="flex items-center gap-1">
                              <MapPin className="w-3 h-3" />
                              {device.location}
                            </span>
                            <span className="flex items-center gap-1">
                              <Clock className="w-3 h-3" />
                              {device.lastActive}
                            </span>
                          </div>
                          <p className="text-xs text-gray-500">IP: {device.ipAddress}</p>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => handleTrustToggle(device.id)}
                        className={`px-3 py-2 rounded-lg transition-colors text-sm ${
                          device.trusted
                            ? 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                            : 'bg-green-500 text-white hover:bg-green-600'
                        }`}
                      >
                        {device.trusted ? 'Untrust' : 'Trust'}
                      </button>
                      
                      <button
                        onClick={() => handleRemoveDevice(device.id)}
                        className="px-3 py-2 bg-red-100 text-red-600 rounded-lg hover:bg-red-200 transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Security Notice */}
        <div className="mt-6 bg-yellow-50 border border-yellow-200 rounded-xl p-6">
          <div className="flex gap-3">
            <Shield className="w-6 h-6 text-yellow-600 flex-shrink-0" />
            <div>
              <h4 className="font-semibold text-yellow-900 mb-2">Security Notice</h4>
              <p className="text-sm text-yellow-800">
                Trusted devices can access your account without additional verification. 
                Remove any devices you don't recognize or no longer use to keep your account secure.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DevicesManagement;
