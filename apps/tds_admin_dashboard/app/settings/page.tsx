'use client';

import { DashboardLayout } from '@/components/dashboard-layout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Settings as SettingsIcon,
  Cloud,
  Key,
  RefreshCw,
  CheckCircle2,
  XCircle,
  Activity,
  Shield,
} from 'lucide-react';

export default function SettingsPage() {
  // TODO: Implement actual Zoho OAuth status fetching
  const zohoConnected = true;
  const tokenExpiry = new Date(Date.now() + 3600000); // 1 hour from now
  const autoSyncEnabled = true;
  const syncInterval = 30; // minutes

  return (
    <DashboardLayout>
      <div className="p-8 space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
          <p className="text-gray-500 mt-1">Manage TDS configuration and integrations</p>
        </div>

        <Tabs defaultValue="zoho" className="space-y-6">
          <TabsList>
            <TabsTrigger value="zoho">
              <Cloud className="h-4 w-4 mr-2" />
              Zoho Integration
            </TabsTrigger>
            <TabsTrigger value="sync">
              <RefreshCw className="h-4 w-4 mr-2" />
              Sync Settings
            </TabsTrigger>
            <TabsTrigger value="system">
              <SettingsIcon className="h-4 w-4 mr-2" />
              System
            </TabsTrigger>
            <TabsTrigger value="security">
              <Shield className="h-4 w-4 mr-2" />
              Security
            </TabsTrigger>
          </TabsList>

          {/* Zoho Integration */}
          <TabsContent value="zoho" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Zoho Books OAuth Connection</CardTitle>
                <CardDescription>
                  Manage OAuth 2.0 connection to Zoho Books API
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Connection Status */}
                <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center gap-3">
                    {zohoConnected ? (
                      <CheckCircle2 className="h-6 w-6 text-green-600" />
                    ) : (
                      <XCircle className="h-6 w-6 text-red-600" />
                    )}
                    <div>
                      <div className="font-medium">
                        {zohoConnected ? 'Connected' : 'Disconnected'}
                      </div>
                      <div className="text-sm text-gray-600">
                        {zohoConnected
                          ? 'OAuth token is valid and active'
                          : 'Not connected to Zoho Books'}
                      </div>
                    </div>
                  </div>
                  <Badge variant={zohoConnected ? 'default' : 'destructive'} className={zohoConnected ? 'bg-green-500 hover:bg-green-600' : ''}>
                    {zohoConnected ? 'Active' : 'Inactive'}
                  </Badge>
                </div>

                {/* Token Information */}
                {zohoConnected && (
                  <div className="space-y-3">
                    <div className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center gap-2">
                        <Key className="h-4 w-4 text-gray-600" />
                        <span className="text-sm font-medium">Access Token</span>
                      </div>
                      <div className="text-sm text-gray-600">
                        <span className="font-mono">••••••••••••••••</span>
                      </div>
                    </div>

                    <div className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center gap-2">
                        <Activity className="h-4 w-4 text-gray-600" />
                        <span className="text-sm font-medium">Token Expires</span>
                      </div>
                      <div className="text-sm font-medium">
                        {tokenExpiry.toLocaleString()}
                      </div>
                    </div>

                    <div className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center gap-2">
                        <RefreshCw className="h-4 w-4 text-gray-600" />
                        <span className="text-sm font-medium">Auto Refresh</span>
                      </div>
                      <Badge variant="outline" className="bg-green-50 text-green-700">
                        Enabled (5 min before expiry)
                      </Badge>
                    </div>
                  </div>
                )}

                {/* Actions */}
                <div className="flex gap-2 pt-4">
                  {!zohoConnected ? (
                    <Button className="w-full">
                      <Cloud className="mr-2 h-4 w-4" />
                      Connect to Zoho Books
                    </Button>
                  ) : (
                    <>
                      <Button variant="outline" className="flex-1">
                        <RefreshCw className="mr-2 h-4 w-4" />
                        Refresh Token
                      </Button>
                      <Button variant="destructive" className="flex-1">
                        <XCircle className="mr-2 h-4 w-4" />
                        Disconnect
                      </Button>
                    </>
                  )}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>API Configuration</CardTitle>
                <CardDescription>Zoho Books API settings</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="text-sm font-medium mb-2 block">Organization ID</label>
                  <input
                    type="text"
                    value="748369814"
                    readOnly
                    className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm bg-gray-50 font-mono"
                  />
                </div>

                <div>
                  <label className="text-sm font-medium mb-2 block">API Endpoint</label>
                  <input
                    type="text"
                    value="https://www.zohoapis.com/books/v3"
                    readOnly
                    className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm bg-gray-50 font-mono"
                  />
                </div>

                <div>
                  <label className="text-sm font-medium mb-2 block">Rate Limit</label>
                  <div className="flex items-center gap-2">
                    <input
                      type="text"
                      value="200 calls/minute"
                      readOnly
                      className="flex-1 border border-gray-300 rounded-md px-3 py-2 text-sm bg-gray-50"
                    />
                    <Badge variant="outline">Default</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Sync Settings */}
          <TabsContent value="sync" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Automatic Sync Configuration</CardTitle>
                <CardDescription>
                  Configure automatic synchronization behavior
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div>
                    <div className="font-medium">Auto Sync</div>
                    <div className="text-sm text-gray-600">
                      Automatically sync data at regular intervals
                    </div>
                  </div>
                  <Badge variant={autoSyncEnabled ? 'default' : 'secondary'} className={autoSyncEnabled ? 'bg-green-500 hover:bg-green-600' : ''}>
                    {autoSyncEnabled ? 'Enabled' : 'Disabled'}
                  </Badge>
                </div>

                <div>
                  <label className="text-sm font-medium mb-2 block">Sync Interval</label>
                  <select className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm">
                    <option value="15">Every 15 minutes</option>
                    <option value="30" selected>Every 30 minutes</option>
                    <option value="60">Every hour</option>
                    <option value="120">Every 2 hours</option>
                    <option value="360">Every 6 hours</option>
                  </select>
                  <p className="text-xs text-gray-600 mt-1">
                    Current: Every {syncInterval} minutes
                  </p>
                </div>

                <div>
                  <label className="text-sm font-medium mb-2 block">Batch Size</label>
                  <select className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm">
                    <option value="50">50 items per batch</option>
                    <option value="100">100 items per batch</option>
                    <option value="200" selected>200 items per batch (default)</option>
                    <option value="500">500 items per batch</option>
                  </select>
                  <p className="text-xs text-gray-600 mt-1">
                    Larger batches are faster but use more memory
                  </p>
                </div>

                <div className="pt-4">
                  <Button className="w-full">
                    <CheckCircle2 className="mr-2 h-4 w-4" />
                    Save Sync Settings
                  </Button>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Entity Sync Preferences</CardTitle>
                <CardDescription>Choose which entities to sync</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {[
                  { name: 'Products', enabled: true },
                  { name: 'Customers', enabled: true },
                  { name: 'Orders', enabled: true },
                  { name: 'Invoices', enabled: false },
                  { name: 'Stock Adjustments', enabled: true },
                  { name: 'Price Lists', enabled: true },
                ].map((entity) => (
                  <div
                    key={entity.name}
                    className="flex items-center justify-between p-3 border rounded-lg"
                  >
                    <span className="text-sm font-medium">{entity.name}</span>
                    <Badge variant={entity.enabled ? 'default' : 'secondary'} className={entity.enabled ? 'bg-green-500 hover:bg-green-600' : ''}>
                      {entity.enabled ? 'Enabled' : 'Disabled'}
                    </Badge>
                  </div>
                ))}
              </CardContent>
            </Card>
          </TabsContent>

          {/* System Settings */}
          <TabsContent value="system" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>System Configuration</CardTitle>
                <CardDescription>General system settings</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="text-sm font-medium mb-2 block">Environment</label>
                  <input
                    type="text"
                    value="Production"
                    readOnly
                    className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm bg-gray-50"
                  />
                </div>

                <div>
                  <label className="text-sm font-medium mb-2 block">API URL</label>
                  <input
                    type="text"
                    value={process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}
                    readOnly
                    className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm bg-gray-50 font-mono"
                  />
                </div>

                <div>
                  <label className="text-sm font-medium mb-2 block">WebSocket URL</label>
                  <input
                    type="text"
                    value={process.env.NEXT_PUBLIC_SOCKET_URL || 'ws://localhost:8000'}
                    readOnly
                    className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm bg-gray-50 font-mono"
                  />
                </div>

                <div>
                  <label className="text-sm font-medium mb-2 block">Dashboard Version</label>
                  <input
                    type="text"
                    value="v1.0.0"
                    readOnly
                    className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm bg-gray-50"
                  />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Cache Settings</CardTitle>
                <CardDescription>Redis cache configuration</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="text-sm font-medium mb-2 block">Dashboard Cache TTL</label>
                  <select className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm">
                    <option value="15">15 seconds</option>
                    <option value="30" selected>30 seconds (default)</option>
                    <option value="60">60 seconds</option>
                    <option value="120">2 minutes</option>
                  </select>
                </div>

                <div>
                  <label className="text-sm font-medium mb-2 block">Statistics Cache TTL</label>
                  <select className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm">
                    <option value="30">30 seconds</option>
                    <option value="60" selected>60 seconds (default)</option>
                    <option value="300">5 minutes</option>
                    <option value="600">10 minutes</option>
                  </select>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Security Settings */}
          <TabsContent value="security" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Authentication</CardTitle>
                <CardDescription>JWT and session management</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div>
                    <div className="font-medium">JWT Authentication</div>
                    <div className="text-sm text-gray-600">
                      Token-based authentication for API and WebSocket
                    </div>
                  </div>
                  <Badge className="bg-green-500 hover:bg-green-600">Enabled</Badge>
                </div>

                <div>
                  <label className="text-sm font-medium mb-2 block">Token Expiry</label>
                  <select className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm">
                    <option value="3600">1 hour</option>
                    <option value="7200">2 hours</option>
                    <option value="14400" selected>4 hours (default)</option>
                    <option value="28800">8 hours</option>
                  </select>
                </div>

                <div>
                  <label className="text-sm font-medium mb-2 block">Auto Logout</label>
                  <select className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm">
                    <option value="1800">30 minutes</option>
                    <option value="3600" selected>1 hour (default)</option>
                    <option value="7200">2 hours</option>
                    <option value="0">Never</option>
                  </select>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Access Control</CardTitle>
                <CardDescription>Role-based access control (RBAC)</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <div className="flex items-start gap-2">
                    <Activity className="h-5 w-5 text-yellow-600 mt-0.5" />
                    <div>
                      <div className="font-medium text-yellow-800">RBAC Not Configured</div>
                      <div className="text-sm text-yellow-700 mt-1">
                        Role-based access control is not yet configured. All authenticated users have full access.
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  );
}
