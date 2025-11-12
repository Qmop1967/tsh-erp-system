'use client';

import { useState } from 'react';
import { DashboardLayout } from '@/components/dashboard-layout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { useAlerts, useAcknowledgeAlert } from '@/hooks/useTDSData';
import {
  AlertTriangle,
  Info,
  AlertCircle,
  XCircle,
  CheckCircle2,
  RefreshCw,
  Bell,
  BellOff,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { formatDistanceToNow, format } from 'date-fns';
import type { AlertSeverity } from '@/types/tds';

export default function AlertsPage() {
  const [severityFilter, setSeverityFilter] = useState<AlertSeverity | ''>('');
  const [showResolved, setShowResolved] = useState(false);

  const { data: alerts, isLoading } = useAlerts({
    severity: severityFilter || undefined,
    is_active: !showResolved ? true : undefined,
  });

  const acknowledgeAlert = useAcknowledgeAlert();

  const getSeverityIcon = (severity: AlertSeverity) => {
    switch (severity) {
      case 'critical':
        return <XCircle className="h-5 w-5" />;
      case 'error':
        return <AlertCircle className="h-5 w-5" />;
      case 'warning':
        return <AlertTriangle className="h-5 w-5" />;
      case 'info':
        return <Info className="h-5 w-5" />;
    }
  };

  const getSeverityColor = (severity: AlertSeverity) => {
    switch (severity) {
      case 'critical':
        return 'text-red-600 bg-red-50 border-red-200';
      case 'error':
        return 'text-red-500 bg-red-50 border-red-100';
      case 'warning':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'info':
        return 'text-blue-600 bg-blue-50 border-blue-200';
    }
  };

  const getSeverityBadgeColor = (severity: AlertSeverity) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-600 text-white hover:bg-red-700';
      case 'error':
        return 'bg-red-500 text-white hover:bg-red-600';
      case 'warning':
        return 'bg-yellow-500 text-white hover:bg-yellow-600';
      case 'info':
        return 'bg-blue-500 text-white hover:bg-blue-600';
    }
  };

  const handleAcknowledge = (alertId: number) => {
    acknowledgeAlert.mutate(alertId);
  };

  const activeAlerts = alerts?.filter(a => a.is_active && !a.acknowledged) || [];
  const acknowledgedAlerts = alerts?.filter(a => a.acknowledged) || [];
  const criticalCount = activeAlerts.filter(a => a.severity === 'critical').length;
  const errorCount = activeAlerts.filter(a => a.severity === 'error').length;
  const warningCount = activeAlerts.filter(a => a.severity === 'warning').length;

  return (
    <DashboardLayout>
      <div className="p-8 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Alerts & Notifications</h1>
            <p className="text-gray-500 mt-1">Monitor system alerts and notifications</p>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="text-lg px-4 py-2">
              <Bell className="h-4 w-4 mr-2" />
              {activeAlerts.length} Active
            </Badge>
          </div>
        </div>

        {/* Summary Cards */}
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Critical</CardTitle>
              <XCircle className="h-4 w-4 text-red-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">{criticalCount}</div>
              <p className="text-xs text-muted-foreground mt-1">Immediate action required</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Errors</CardTitle>
              <AlertCircle className="h-4 w-4 text-red-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-500">{errorCount}</div>
              <p className="text-xs text-muted-foreground mt-1">Action recommended</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Warnings</CardTitle>
              <AlertTriangle className="h-4 w-4 text-yellow-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-yellow-600">{warningCount}</div>
              <p className="text-xs text-muted-foreground mt-1">Review suggested</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Acknowledged</CardTitle>
              <CheckCircle2 className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{acknowledgedAlerts.length}</div>
              <p className="text-xs text-muted-foreground mt-1">Handled alerts</p>
            </CardContent>
          </Card>
        </div>

        {/* Filters */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Filters</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex gap-4">
              <div className="flex-1">
                <label className="text-sm font-medium mb-2 block">Severity</label>
                <select
                  value={severityFilter}
                  onChange={(e) => setSeverityFilter(e.target.value as AlertSeverity | '')}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                >
                  <option value="">All Severities</option>
                  <option value="critical">Critical</option>
                  <option value="error">Error</option>
                  <option value="warning">Warning</option>
                  <option value="info">Info</option>
                </select>
              </div>
              <div className="flex-1 flex items-end">
                <Button
                  variant={showResolved ? 'default' : 'outline'}
                  onClick={() => setShowResolved(!showResolved)}
                  className="w-full"
                >
                  {showResolved ? (
                    <>
                      <BellOff className="mr-2 h-4 w-4" />
                      Hide Resolved
                    </>
                  ) : (
                    <>
                      <Bell className="mr-2 h-4 w-4" />
                      Show All
                    </>
                  )}
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Alerts List */}
        <Card>
          <CardHeader>
            <CardTitle>Active Alerts</CardTitle>
            <CardDescription>
              {isLoading ? 'Loading...' : `${activeAlerts.length} active alert${activeAlerts.length !== 1 ? 's' : ''}`}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="flex items-center justify-center py-12">
                <RefreshCw className="h-8 w-8 animate-spin text-gray-400" />
              </div>
            ) : activeAlerts.length === 0 ? (
              <div className="text-center py-12">
                <CheckCircle2 className="h-12 w-12 text-green-500 mx-auto mb-3" />
                <p className="text-lg font-medium text-gray-900">All Clear!</p>
                <p className="text-gray-500 mt-1">No active alerts at the moment</p>
              </div>
            ) : (
              <div className="space-y-3">
                {activeAlerts.map((alert) => (
                  <Alert
                    key={alert.id}
                    className={cn(
                      'border-2',
                      getSeverityColor(alert.severity)
                    )}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-3 flex-1">
                        {getSeverityIcon(alert.severity)}
                        <div className="flex-1">
                          <AlertTitle className="flex items-center gap-2 mb-1">
                            <span>{alert.title}</span>
                            <Badge className={getSeverityBadgeColor(alert.severity)}>
                              {alert.severity}
                            </Badge>
                          </AlertTitle>
                          <AlertDescription className="text-sm mb-2">
                            {alert.message}
                          </AlertDescription>
                          <div className="flex items-center gap-4 text-xs text-gray-600">
                            <span>
                              {formatDistanceToNow(new Date(alert.triggered_at), { addSuffix: true })}
                            </span>
                            <span>•</span>
                            <span>{format(new Date(alert.triggered_at), 'PPpp')}</span>
                          </div>
                        </div>
                      </div>
                      <div className="flex gap-2 ml-4">
                        {!alert.acknowledged && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleAcknowledge(alert.id)}
                            disabled={acknowledgeAlert.isPending}
                          >
                            {acknowledgeAlert.isPending ? (
                              <RefreshCw className="h-4 w-4 animate-spin" />
                            ) : (
                              <>Acknowledge</>
                            )}
                          </Button>
                        )}
                        {alert.acknowledged && (
                          <Badge variant="outline" className="bg-green-50 text-green-700 border-green-300">
                            <CheckCircle2 className="h-3 w-3 mr-1" />
                            Acknowledged
                          </Badge>
                        )}
                      </div>
                    </div>
                  </Alert>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Acknowledged Alerts */}
        {showResolved && acknowledgedAlerts.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Acknowledged Alerts</CardTitle>
              <CardDescription>
                {acknowledgedAlerts.length} acknowledged alert{acknowledgedAlerts.length !== 1 ? 's' : ''}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {acknowledgedAlerts.map((alert) => (
                  <Alert
                    key={alert.id}
                    className="border bg-gray-50 opacity-75"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-3 flex-1">
                        <CheckCircle2 className="h-5 w-5 text-green-600" />
                        <div className="flex-1">
                          <AlertTitle className="flex items-center gap-2 mb-1">
                            <span>{alert.title}</span>
                            <Badge variant="outline">{alert.severity}</Badge>
                          </AlertTitle>
                          <AlertDescription className="text-sm mb-2">
                            {alert.message}
                          </AlertDescription>
                          <div className="flex items-center gap-4 text-xs text-gray-600">
                            <span>
                              Triggered {formatDistanceToNow(new Date(alert.triggered_at), { addSuffix: true })}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </Alert>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  );
}
