// System Health Component
import { Activity, Database, Clock, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import { useHealth } from '../hooks/useTDSData';
import { formatDuration, getStatusColor, cn } from '../lib/utils';
import { StatusCard } from './StatusCard';

export function SystemHealth() {
  const { data: health, isLoading, isError, error } = useHealth();

  if (isLoading) {
    return (
      <div className="rounded-lg bg-white p-8 shadow-md">
        <div className="animate-pulse">
          <div className="h-6 w-48 rounded bg-gray-200"></div>
          <div className="mt-4 space-y-3">
            <div className="h-4 w-full rounded bg-gray-200"></div>
            <div className="h-4 w-3/4 rounded bg-gray-200"></div>
          </div>
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-6 shadow-md">
        <div className="flex items-center gap-3">
          <XCircle className="h-6 w-6 text-red-600" />
          <div>
            <h3 className="font-semibold text-red-900">Unable to Connect</h3>
            <p className="mt-1 text-sm text-red-700">
              {error instanceof Error ? error.message : 'Failed to fetch health status'}
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (!health) return null;

  const statusIcon = {
    healthy: <CheckCircle className="h-6 w-6 text-green-600" />,
    degraded: <AlertCircle className="h-6 w-6 text-yellow-600" />,
    unhealthy: <XCircle className="h-6 w-6 text-red-600" />,
  };

  const getCardStatus = (status: string) => {
    if (status === 'healthy' || status === 'connected') return 'success';
    if (status === 'degraded') return 'warning';
    return 'error';
  };

  return (
    <div className="space-y-6">
      <div className="rounded-lg bg-white p-6 shadow-md">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">System Health</h2>
            <p className="mt-1 text-sm text-gray-500">
              Last updated: {new Date(health.timestamp).toLocaleTimeString()}
            </p>
          </div>
          <div className="flex items-center gap-3">
            {statusIcon[health.status]}
            <span
              className={cn(
                'rounded-full px-4 py-2 text-sm font-semibold',
                getStatusColor(health.status)
              )}
            >
              {health.status.toUpperCase()}
            </span>
          </div>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <StatusCard
          title="System Uptime"
          value={formatDuration(health.uptime_seconds)}
          subtitle={`Version ${health.version}`}
          icon={<Clock className="h-8 w-8" />}
          status="info"
        />

        <StatusCard
          title="Database"
          value={health.database.status === 'connected' ? 'Connected' : 'Disconnected'}
          subtitle={
            health.database.response_time_ms
              ? `${health.database.response_time_ms}ms response`
              : undefined
          }
          icon={<Database className="h-8 w-8" />}
          status={getCardStatus(health.database.status)}
        />

        <StatusCard
          title="Processing Rate"
          value={health.queue.completed_last_hour}
          subtitle="Completed last hour"
          icon={<Activity className="h-8 w-8" />}
          status="success"
        />

        <StatusCard
          title="Failed Events"
          value={health.queue.failed}
          subtitle="Require attention"
          icon={<AlertCircle className="h-8 w-8" />}
          status={health.queue.failed > 0 ? 'warning' : 'success'}
        />
      </div>
    </div>
  );
}
