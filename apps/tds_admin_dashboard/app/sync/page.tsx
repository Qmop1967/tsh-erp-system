'use client';

import { useState } from 'react';
import { DashboardLayout } from '@/components/dashboard-layout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { useSyncRuns, useSyncRunDetail, useTriggerStockSync } from '@/hooks/useTDSData';
import {
  RefreshCw,
  ChevronLeft,
  ChevronRight,
  CheckCircle2,
  XCircle,
  Clock,
  AlertCircle,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { formatDistanceToNow, format } from 'date-fns';
import type { SyncRunSummary, EntityType } from '@/types/tds';

export default function SyncPage() {
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [entityFilter, setEntityFilter] = useState<EntityType | ''>('');
  const [selectedRunId, setSelectedRunId] = useState<number | null>(null);

  const { data: syncRuns, isLoading, error } = useSyncRuns({
    page: page - 1,
    page_size: pageSize,
    status: statusFilter || undefined,
    entity_type: entityFilter || undefined,
  });

  const { data: syncDetail } = useSyncRunDetail(selectedRunId);
  const triggerSync = useTriggerStockSync();

  const handleTriggerSync = () => {
    triggerSync.mutate(undefined, {
      onSuccess: () => {
        setPage(1); // Reset to first page to see new sync
      },
    });
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="h-4 w-4 text-green-600" />;
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-600" />;
      case 'running':
        return <RefreshCw className="h-4 w-4 text-blue-600 animate-spin" />;
      case 'pending':
        return <Clock className="h-4 w-4 text-yellow-600" />;
      default:
        return <AlertCircle className="h-4 w-4 text-gray-600" />;
    }
  };

  const getStatusBadgeVariant = (status: string): "default" | "destructive" | "secondary" => {
    switch (status) {
      case 'completed':
        return 'default';
      case 'failed':
        return 'destructive';
      default:
        return 'secondary';
    }
  };

  if (error) {
    return (
      <DashboardLayout>
        <div className="p-8">
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-800">Error loading sync runs: {error.message}</p>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  const totalPages = syncRuns ? Math.ceil(syncRuns.total / pageSize) : 0;

  return (
    <DashboardLayout>
      <div className="p-8 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Sync Operations</h1>
            <p className="text-gray-500 mt-1">Monitor and manage sync runs</p>
          </div>
          <Button onClick={handleTriggerSync} disabled={triggerSync.isPending}>
            {triggerSync.isPending ? (
              <>
                <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                Syncing...
              </>
            ) : (
              <>
                <RefreshCw className="mr-2 h-4 w-4" />
                Trigger Stock Sync
              </>
            )}
          </Button>
        </div>

        {/* Filters */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Filters</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex gap-4">
              <div className="flex-1">
                <label className="text-sm font-medium mb-2 block">Status</label>
                <select
                  value={statusFilter}
                  onChange={(e) => {
                    setStatusFilter(e.target.value);
                    setPage(1);
                  }}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                >
                  <option value="">All Statuses</option>
                  <option value="completed">Completed</option>
                  <option value="running">Running</option>
                  <option value="failed">Failed</option>
                  <option value="pending">Pending</option>
                </select>
              </div>
              <div className="flex-1">
                <label className="text-sm font-medium mb-2 block">Entity Type</label>
                <select
                  value={entityFilter}
                  onChange={(e) => {
                    setEntityFilter(e.target.value as EntityType | '');
                    setPage(1);
                  }}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                >
                  <option value="">All Types</option>
                  <option value="product">Product</option>
                  <option value="customer">Customer</option>
                  <option value="order">Order</option>
                  <option value="invoice">Invoice</option>
                  <option value="stock_adjustment">Stock Adjustment</option>
                </select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Sync Runs Table */}
        <Card>
          <CardHeader>
            <CardTitle>Sync Runs</CardTitle>
            <CardDescription>
              {syncRuns && `Showing ${syncRuns.items.length} of ${syncRuns.total} runs`}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="flex items-center justify-center py-12">
                <RefreshCw className="h-8 w-8 animate-spin text-gray-400" />
              </div>
            ) : !syncRuns || syncRuns.items.length === 0 ? (
              <div className="text-center py-12 text-gray-500">
                No sync runs found
              </div>
            ) : (
              <>
                <div className="overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Status</TableHead>
                        <TableHead>Type</TableHead>
                        <TableHead>Entity</TableHead>
                        <TableHead>Progress</TableHead>
                        <TableHead>Duration</TableHead>
                        <TableHead>Started</TableHead>
                        <TableHead>Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {syncRuns.items.map((run: SyncRunSummary) => (
                        <TableRow key={run.id} className="hover:bg-gray-50">
                          <TableCell>
                            <div className="flex items-center gap-2">
                              {getStatusIcon(run.status)}
                              <Badge
                                variant={getStatusBadgeVariant(run.status)}
                                className={cn(
                                  run.status === 'completed' && 'bg-green-500 hover:bg-green-600'
                                )}
                              >
                                {run.status}
                              </Badge>
                            </div>
                          </TableCell>
                          <TableCell className="font-medium">{run.run_type}</TableCell>
                          <TableCell>
                            {run.entity_type ? (
                              <Badge variant="outline">{run.entity_type}</Badge>
                            ) : (
                              <span className="text-gray-400">-</span>
                            )}
                          </TableCell>
                          <TableCell>
                            <div className="flex items-center gap-2">
                              <div className="text-sm">
                                {run.processed_events}/{run.total_events}
                              </div>
                              <div className="w-24 bg-gray-200 rounded-full h-2">
                                <div
                                  className={cn(
                                    "h-2 rounded-full",
                                    run.failed_events > 0 ? "bg-red-500" : "bg-green-500"
                                  )}
                                  style={{
                                    width: `${(run.processed_events / run.total_events) * 100}%`,
                                  }}
                                />
                              </div>
                            </div>
                          </TableCell>
                          <TableCell>
                            {run.duration_seconds ? (
                              <span>{run.duration_seconds.toFixed(1)}s</span>
                            ) : (
                              <span className="text-gray-400">-</span>
                            )}
                          </TableCell>
                          <TableCell className="text-sm text-gray-600">
                            {formatDistanceToNow(new Date(run.started_at), { addSuffix: true })}
                          </TableCell>
                          <TableCell>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => setSelectedRunId(run.id)}
                            >
                              Details
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>

                {/* Pagination */}
                <div className="flex items-center justify-between mt-4">
                  <div className="text-sm text-gray-600">
                    Page {page} of {totalPages}
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setPage((p) => Math.max(1, p - 1))}
                      disabled={page === 1}
                    >
                      <ChevronLeft className="h-4 w-4" />
                      Previous
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                      disabled={page === totalPages}
                    >
                      Next
                      <ChevronRight className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </>
            )}
          </CardContent>
        </Card>

        {/* Sync Run Detail Dialog */}
        <Dialog open={selectedRunId !== null} onOpenChange={() => setSelectedRunId(null)}>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Sync Run Details</DialogTitle>
              <DialogDescription>Run ID: {selectedRunId}</DialogDescription>
            </DialogHeader>
            {syncDetail && (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <div className="text-sm font-medium text-gray-500">Status</div>
                    <div className="flex items-center gap-2 mt-1">
                      {getStatusIcon(syncDetail.status)}
                      <Badge variant={getStatusBadgeVariant(syncDetail.status)}>
                        {syncDetail.status}
                      </Badge>
                    </div>
                  </div>
                  <div>
                    <div className="text-sm font-medium text-gray-500">Type</div>
                    <div className="mt-1">{syncDetail.run_type}</div>
                  </div>
                  <div>
                    <div className="text-sm font-medium text-gray-500">Entity Type</div>
                    <div className="mt-1">
                      {syncDetail.entity_type || <span className="text-gray-400">N/A</span>}
                    </div>
                  </div>
                  <div>
                    <div className="text-sm font-medium text-gray-500">Worker ID</div>
                    <div className="mt-1 font-mono text-sm">
                      {syncDetail.worker_id || <span className="text-gray-400">N/A</span>}
                    </div>
                  </div>
                </div>

                <div className="border-t pt-4">
                  <div className="text-sm font-medium text-gray-700 mb-2">Progress</div>
                  <div className="grid grid-cols-4 gap-4 text-center">
                    <div>
                      <div className="text-2xl font-bold text-blue-600">
                        {syncDetail.total_events}
                      </div>
                      <div className="text-xs text-gray-600">Total</div>
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-green-600">
                        {syncDetail.processed_events}
                      </div>
                      <div className="text-xs text-gray-600">Processed</div>
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-red-600">
                        {syncDetail.failed_events}
                      </div>
                      <div className="text-xs text-gray-600">Failed</div>
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-yellow-600">
                        {syncDetail.skipped_events}
                      </div>
                      <div className="text-xs text-gray-600">Skipped</div>
                    </div>
                  </div>
                </div>

                <div className="border-t pt-4">
                  <div className="text-sm font-medium text-gray-700 mb-2">Timing</div>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Started</span>
                      <span className="font-medium">
                        {format(new Date(syncDetail.started_at), 'PPpp')}
                      </span>
                    </div>
                    {syncDetail.completed_at && (
                      <div className="flex justify-between">
                        <span className="text-gray-600">Completed</span>
                        <span className="font-medium">
                          {format(new Date(syncDetail.completed_at), 'PPpp')}
                        </span>
                      </div>
                    )}
                    {syncDetail.duration_seconds && (
                      <div className="flex justify-between">
                        <span className="text-gray-600">Duration</span>
                        <span className="font-medium">{syncDetail.duration_seconds.toFixed(2)}s</span>
                      </div>
                    )}
                  </div>
                </div>

                {syncDetail.error_summary && (
                  <div className="border-t pt-4">
                    <div className="text-sm font-medium text-gray-700 mb-2">Errors</div>
                    <div className="bg-red-50 border border-red-200 rounded p-3">
                      <pre className="text-xs text-red-800 whitespace-pre-wrap">
                        {syncDetail.error_summary}
                      </pre>
                    </div>
                  </div>
                )}
              </div>
            )}
          </DialogContent>
        </Dialog>
      </div>
    </DashboardLayout>
  );
}
