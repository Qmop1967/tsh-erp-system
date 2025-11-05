// Queue Monitor Component
import { Inbox, Clock, CheckCircle, XCircle, RotateCw, Archive } from 'lucide-react';
import { useQueueStats } from '../hooks/useTDSData';
import { formatNumber, getStatusColor, cn } from '../lib/utils';
import { EventStatus } from '../types/tds';

export function QueueMonitor() {
  const { data: queueData, isLoading, isError } = useQueueStats();

  if (isLoading) {
    return (
      <div className="rounded-lg bg-white p-8 shadow-md">
        <div className="animate-pulse space-y-4">
          <div className="h-6 w-48 rounded bg-gray-200"></div>
          <div className="grid gap-4 md:grid-cols-3">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="h-24 rounded bg-gray-200"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (isError || !queueData) {
    return (
      <div className="rounded-lg border border-yellow-200 bg-yellow-50 p-6 shadow-md">
        <p className="text-yellow-800">Unable to load queue statistics</p>
      </div>
    );
  }

  const stats = queueData;

  const statusCards = [
    {
      status: EventStatus.PENDING,
      icon: Inbox,
      label: 'Pending',
      value: stats.by_status[EventStatus.PENDING] || 0,
      color: 'blue',
    },
    {
      status: EventStatus.PROCESSING,
      icon: RotateCw,
      label: 'Processing',
      value: stats.by_status[EventStatus.PROCESSING] || 0,
      color: 'purple',
    },
    {
      status: EventStatus.COMPLETED,
      icon: CheckCircle,
      label: 'Completed',
      value: stats.by_status[EventStatus.COMPLETED] || 0,
      color: 'green',
    },
    {
      status: EventStatus.FAILED,
      icon: XCircle,
      label: 'Failed',
      value: stats.by_status[EventStatus.FAILED] || 0,
      color: 'red',
    },
    {
      status: EventStatus.RETRY,
      icon: RotateCw,
      label: 'Retry',
      value: stats.by_status[EventStatus.RETRY] || 0,
      color: 'orange',
    },
    {
      status: EventStatus.DEAD_LETTER,
      icon: Archive,
      label: 'Dead Letter',
      value: stats.by_status[EventStatus.DEAD_LETTER] || 0,
      color: 'gray',
    },
  ];

  return (
    <div className="space-y-6">
      <div className="rounded-lg bg-white p-6 shadow-md">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Queue Monitor</h2>
            <p className="mt-1 text-sm text-gray-500">
              Total events: {formatNumber(stats.total_events)}
            </p>
          </div>
          <div className="text-right">
            <p className="text-sm font-medium text-gray-600">Processing Rate</p>
            <p className="text-2xl font-bold text-gray-900">
              {stats.processing_rate?.last_minute || 0}/min
            </p>
          </div>
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {statusCards.map(({ status, icon: Icon, label, value, color }) => (
          <div
            key={status}
            className={cn(
              'rounded-lg border-l-4 bg-white p-6 shadow-md transition-all hover:shadow-lg',
              `border-${color}-500`
            )}
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">{label}</p>
                <p className="mt-2 text-3xl font-bold text-gray-900">
                  {formatNumber(value)}
                </p>
                <span
                  className={cn(
                    'mt-2 inline-block rounded-full px-2 py-1 text-xs font-semibold',
                    getStatusColor(status)
                  )}
                >
                  {status}
                </span>
              </div>
              <Icon className={`h-12 w-12 text-${color}-400`} />
            </div>
          </div>
        ))}
      </div>

      {stats.oldest_pending && (
        <div className="rounded-lg border border-yellow-200 bg-yellow-50 p-6 shadow-md">
          <div className="flex items-center gap-3">
            <Clock className="h-6 w-6 text-yellow-600" />
            <div>
              <h3 className="font-semibold text-yellow-900">Oldest Pending Event</h3>
              <p className="mt-1 text-sm text-yellow-700">
                {stats.oldest_pending.entity_type} - Age: {stats.oldest_pending.age_minutes} minutes
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
