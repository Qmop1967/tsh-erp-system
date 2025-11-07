// Status Card Component
import { cn } from '../lib/utils';

interface StatusCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: React.ReactNode;
  status?: 'success' | 'warning' | 'error' | 'info';
  className?: string;
}

export function StatusCard({
  title,
  value,
  subtitle,
  icon,
  status = 'info',
  className,
}: StatusCardProps) {
  const statusColors = {
    success: 'border-green-500 bg-green-50',
    warning: 'border-yellow-500 bg-yellow-50',
    error: 'border-red-500 bg-red-50',
    info: 'border-blue-500 bg-blue-50',
  };

  return (
    <div
      className={cn(
        'rounded-lg border-l-4 bg-white p-6 shadow-md',
        statusColors[status],
        className
      )}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="mt-2 text-3xl font-bold text-gray-900">{value}</p>
          {subtitle && (
            <p className="mt-1 text-sm text-gray-500">{subtitle}</p>
          )}
        </div>
        {icon && <div className="ml-4 text-gray-400">{icon}</div>}
      </div>
    </div>
  );
}
