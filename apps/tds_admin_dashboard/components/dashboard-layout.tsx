'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  RefreshCw,
  BarChart3,
  AlertTriangle,
  Settings,
  Activity,
  Database,
  Webhook
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Badge } from '@/components/ui/badge';
import { useAlerts } from '@/hooks/useTDSData';

interface NavItem {
  name: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: number;
}

export function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { data: alerts } = useAlerts({ is_active: true });

  const criticalAlertsCount = alerts?.filter(a => a.severity === 'critical').length || 0;

  const navigation: NavItem[] = [
    { name: 'Overview', href: '/', icon: LayoutDashboard },
    { name: 'Sync Operations', href: '/sync', icon: RefreshCw },
    { name: 'Statistics', href: '/statistics', icon: BarChart3 },
    { name: 'Alerts', href: '/alerts', icon: AlertTriangle, badge: criticalAlertsCount },
    { name: 'System Health', href: '/health', icon: Activity },
    { name: 'Dead Letter Queue', href: '/dlq', icon: Database },
    { name: 'Webhooks', href: '/webhooks', icon: Webhook },
    { name: 'Settings', href: '/settings', icon: Settings },
  ];

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
        {/* Logo */}
        <div className="h-16 flex items-center px-6 border-b border-gray-200">
          <h1 className="text-xl font-bold text-gray-900">TDS Admin</h1>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
          {navigation.map((item) => {
            const isActive = pathname === item.href;
            const Icon = item.icon;

            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  'flex items-center justify-between px-4 py-3 text-sm font-medium rounded-lg transition-colors',
                  isActive
                    ? 'bg-blue-50 text-blue-700'
                    : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'
                )}
              >
                <div className="flex items-center gap-3">
                  <Icon className={cn('h-5 w-5', isActive ? 'text-blue-700' : 'text-gray-500')} />
                  <span>{item.name}</span>
                </div>
                {item.badge !== undefined && item.badge > 0 && (
                  <Badge variant="destructive" className="ml-auto">
                    {item.badge}
                  </Badge>
                )}
              </Link>
            );
          })}
        </nav>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200">
          <div className="text-xs text-gray-500">
            <div className="font-semibold">TSH ERP Ecosystem</div>
            <div>TDS v3.0.0</div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        {children}
      </main>
    </div>
  );
}
