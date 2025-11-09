'use client';

import { DashboardLayout } from '@/components/dashboard-layout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { useDashboard, useTriggerStockSync } from '@/hooks/useTDSData';
import {
  Activity,
  TrendingUp,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Clock,
  RefreshCw,
  Database,
  Zap,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { formatDistanceToNow } from 'date-fns';

export default function DashboardPage() {
  const { data: dashboard, isLoading, error } = useDashboard();
  const triggerSync = useTriggerStockSync();

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-full">
          <div className="flex items-center gap-2 text-gray-600">
            <RefreshCw className="h-6 w-6 animate-spin" />
            <span>Loading dashboard...</span>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  if (error) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-full">
          <Alert variant="destructive" className="max-w-md">
            <AlertTriangle className="h-4 w-4" />
            <AlertTitle>Error Loading Dashboard</AlertTitle>
            <AlertDescription>
              {error instanceof Error ? error.message : 'Failed to load dashboard data'}
            </AlertDescription>
          </Alert>
        </div>
      </DashboardLayout>
    );
  }

  const health = dashboard?.health;
  const queue = dashboard?.queue;
  const recentSyncs = dashboard?.recent_syncs || [];
  const activeAlerts = dashboard?.active_alerts || [];
  const processingRate = dashboard?.processing_rate;

  // Calculate KPIs
  const syncSuccessRate = queue
    ? (queue.completed_today / (queue.completed_today + queue.failed_today) * 100) || 0
    : 0;

  const healthScore = health?.score || 0;
  const criticalAlerts = activeAlerts.filter(a => a.severity === 'critical').length;

  return (
    <DashboardLayout>
      <div className="p-8 space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Dashboard Overview</h1>
            <p className="text-gray-500 mt-1">TSH Datasync Core Administration</p>
          </div>
          <Button
            onClick={() => triggerSync.mutate(undefined)}
            disabled={triggerSync.isPending}
          >
            {triggerSync.isPending ? (
              <>
                <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                Syncing...
              </>
            ) : (
              <>
                <RefreshCw className="mr-2 h-4 w-4" />
                Trigger Sync
              </>
            )}
          </Button>
        </div>

        {/* KPI Cards */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {/* System Health */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">System Health</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{healthScore.toFixed(0)}%</div>
              <div className="flex items-center gap-2 mt-2">
                <Badge
                  variant={health?.status === 'healthy' ? 'default' : 'destructive'}
                  className={cn(
                    health?.status === 'healthy' && 'bg-green-500 hover:bg-green-600'
                  )}
                >
                  {health?.status || 'Unknown'}
                </Badge>
              </div>
              <p className="text-xs text-muted-foreground mt-2">
                Uptime: {health?.uptime_seconds ? `${Math.floor(health.uptime_seconds / 3600)}h` : 'N/A'}
              </p>
            </CardContent>
          </Card>

          {/* Sync Success Rate */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Sync Success Rate</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{syncSuccessRate.toFixed(1)}%</div>
              <p className="text-xs text-muted-foreground mt-2">
                {queue?.completed_today || 0} completed today
              </p>
              <div className="flex items-center gap-2 mt-2">
                <div className="text-xs text-green-600 flex items-center gap-1">
                  <CheckCircle2 className="h-3 w-3" />
                  {queue?.completed_today || 0}
                </div>
                <div className="text-xs text-red-600 flex items-center gap-1">
                  <XCircle className="h-3 w-3" />
                  {queue?.failed_today || 0}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Queue Depth */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Queue Depth</CardTitle>
              <Database className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{queue?.pending || 0}</div>
              <p className="text-xs text-muted-foreground mt-2">
                {queue?.processing || 0} processing now
              </p>
              {queue?.oldest_pending_age_minutes && (
                <div className="flex items-center gap-1 text-xs text-amber-600 mt-2">
                  <Clock className="h-3 w-3" />
                  Oldest: {queue.oldest_pending_age_minutes}m
                </div>
              )}
            </CardContent>
          </Card>

          {/* Critical Alerts */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Critical Alerts</CardTitle>
              <AlertTriangle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{criticalAlerts}</div>
              <p className="text-xs text-muted-foreground mt-2">
                {activeAlerts.length} total active alerts
              </p>
              {criticalAlerts > 0 && (
                <Badge variant="destructive" className="mt-2">
                  Requires Attention
                </Badge>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Processing Rate Chart Placeholder */}
        <Card>
          <CardHeader>
            <CardTitle>Processing Rate</CardTitle>
            <CardDescription>Items processed per minute</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-3 gap-4">
              <div>
                <div className="text-xs text-muted-foreground">Current</div>
                <div className="text-2xl font-bold flex items-center gap-2">
                  <Zap className="h-5 w-5 text-yellow-500" />
                  {processingRate?.current_rate.toFixed(1) || 0}
                </div>
              </div>
              <div>
                <div className="text-xs text-muted-foreground">Avg (1h)</div>
                <div className="text-2xl font-bold">
                  {processingRate?.average_rate_1h.toFixed(1) || 0}
                </div>
              </div>
              <div>
                <div className="text-xs text-muted-foreground">Peak (24h)</div>
                <div className="text-2xl font-bold text-green-600">
                  {processingRate?.peak_rate_24h.toFixed(1) || 0}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="grid gap-6 lg:grid-cols-2">
          {/* Recent Syncs */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Sync Operations</CardTitle>
              <CardDescription>Latest sync runs</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {recentSyncs.length === 0 ? (
                  <p className="text-sm text-muted-foreground">No recent syncs</p>
                ) : (
                  recentSyncs.slice(0, 5).map((sync) => (
                    <div
                      key={sync.id}
                      className="flex items-center justify-between p-3 border rounded-lg"
                    >
                      <div className="flex-1">
                        <div className="text-sm font-medium">
                          {sync.run_type} {sync.entity_type && `- ${sync.entity_type}`}
                        </div>
                        <div className="text-xs text-muted-foreground">
                          {formatDistanceToNow(new Date(sync.started_at), { addSuffix: true })}
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <div className="text-xs text-gray-600">
                          {sync.processed_events}/{sync.total_events}
                        </div>
                        <Badge
                          variant={sync.status === 'completed' ? 'default' : sync.status === 'failed' ? 'destructive' : 'secondary'}
                          className={cn(
                            sync.status === 'completed' && 'bg-green-500 hover:bg-green-600'
                          )}
                        >
                          {sync.status}
                        </Badge>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>

          {/* Active Alerts */}
          <Card>
            <CardHeader>
              <CardTitle>Active Alerts</CardTitle>
              <CardDescription>Requires attention</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {activeAlerts.length === 0 ? (
                  <div className="flex items-center gap-2 text-green-600">
                    <CheckCircle2 className="h-5 w-5" />
                    <span className="text-sm font-medium">All systems operational</span>
                  </div>
                ) : (
                  activeAlerts.slice(0, 5).map((alert) => (
                    <Alert
                      key={alert.id}
                      variant={alert.severity === 'critical' || alert.severity === 'error' ? 'destructive' : 'default'}
                    >
                      <AlertTriangle className="h-4 w-4" />
                      <AlertTitle className="flex items-center justify-between">
                        <span>{alert.title}</span>
                        <Badge variant="outline" className="ml-2">
                          {alert.severity}
                        </Badge>
                      </AlertTitle>
                      <AlertDescription className="text-xs">
                        {alert.message}
                      </AlertDescription>
                    </Alert>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  );
}
