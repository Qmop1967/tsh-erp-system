import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Activity, RefreshCw } from 'lucide-react';
import { SystemHealth } from './components/SystemHealth';
import { QueueMonitor } from './components/QueueMonitor';
import { EntityDistribution } from './components/EntityDistribution';
import { ProcessingRate } from './components/ProcessingRate';
import './App.css';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      staleTime: 3000,
    },
  },
});

function Dashboard() {
  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Activity className="h-8 w-8 text-blue-600" />
              <div>
                <h1 className="text-3xl font-bold text-gray-900">TDS Dashboard</h1>
                <p className="text-sm text-gray-500">TSH DataSync Core Monitoring</p>
              </div>
            </div>
            <div className="flex items-center gap-2 rounded-lg bg-blue-50 px-4 py-2">
              <RefreshCw className="h-4 w-4 animate-spin text-blue-600" />
              <span className="text-sm font-medium text-blue-900">Live</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="space-y-8">
          {/* System Health Section */}
          <SystemHealth />

          {/* Queue Monitor Section */}
          <QueueMonitor />

          {/* Charts Section */}
          <div className="grid gap-6 lg:grid-cols-2">
            <EntityDistribution />
            <ProcessingRate />
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-12 border-t border-gray-200 bg-white">
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
          <p className="text-center text-sm text-gray-500">
            TDS Core Dashboard © 2024 TSH ERP System
          </p>
        </div>
      </footer>
    </div>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Dashboard />
    </QueryClientProvider>
  );
}

export default App;
