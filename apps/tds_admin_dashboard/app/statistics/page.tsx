'use client';

import { DashboardLayout } from '@/components/dashboard-layout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useCombinedStats } from '@/hooks/useTDSData';
import {
  TrendingUp,
  TrendingDown,
  Minus,
  Database,
  Cloud,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  RefreshCw,
} from 'lucide-react';
import { cn } from '@/lib/utils';

export default function StatisticsPage() {
  const { data: stats, isLoading, error } = useCombinedStats();

  const getMatchQualityColor = (percentage: number) => {
    if (percentage >= 95) return 'text-green-600';
    if (percentage >= 85) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getMatchQualityIcon = (percentage: number) => {
    if (percentage >= 95) return <CheckCircle2 className="h-5 w-5 text-green-600" />;
    if (percentage >= 85) return <AlertTriangle className="h-5 w-5 text-yellow-600" />;
    return <XCircle className="h-5 w-5 text-red-600" />;
  };

  const getDifferenceIcon = (zohoValue: number, localValue: number) => {
    if (zohoValue > localValue) return <TrendingUp className="h-4 w-4 text-blue-600" />;
    if (zohoValue < localValue) return <TrendingDown className="h-4 w-4 text-red-600" />;
    return <Minus className="h-4 w-4 text-gray-600" />;
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  if (error) {
    return (
      <DashboardLayout>
        <div className="p-8">
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-800">Error loading statistics: {error.message}</p>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="p-8">
          <div className="flex items-center justify-center py-12">
            <div className="flex items-center gap-2 text-gray-600">
              <RefreshCw className="h-6 w-6 animate-spin" />
              <span>Loading statistics...</span>
            </div>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  const zohoStats = stats?.zoho_stats;
  const localStats = stats?.local_stats;
  const comparison = stats?.comparison;

  return (
    <DashboardLayout>
      <div className="p-8 space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Statistics & Comparison</h1>
          <p className="text-gray-500 mt-1">Compare Zoho Books data with local database</p>
        </div>

        {/* Data Quality Score */}
        <div className="grid gap-6 md:grid-cols-3">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Match Percentage</CardTitle>
              {getMatchQualityIcon(comparison?.match_percentage || 0)}
            </CardHeader>
            <CardContent>
              <div className={cn('text-3xl font-bold', getMatchQualityColor(comparison?.match_percentage || 0))}>
                {comparison?.match_percentage.toFixed(1)}%
              </div>
              <p className="text-xs text-muted-foreground mt-2">
                Data consistency between systems
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Data Quality Score</CardTitle>
              <CheckCircle2 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className={cn('text-3xl font-bold', getMatchQualityColor(comparison?.data_quality_score || 0))}>
                {comparison?.data_quality_score.toFixed(1)}%
              </div>
              <p className="text-xs text-muted-foreground mt-2">
                Overall data integrity
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Missing Records</CardTitle>
              <AlertTriangle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">
                {(comparison?.missing_in_local || 0) + (comparison?.missing_in_zoho || 0)}
              </div>
              <div className="text-xs text-muted-foreground mt-2">
                <span className="text-red-600">{comparison?.missing_in_local || 0} in Local</span>
                {' • '}
                <span className="text-blue-600">{comparison?.missing_in_zoho || 0} in Zoho</span>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Items Comparison */}
        <Card>
          <CardHeader>
            <CardTitle>Items / Products</CardTitle>
            <CardDescription>Product inventory comparison</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="grid grid-cols-3 gap-4">
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <Cloud className="h-6 w-6 text-blue-600 mx-auto mb-2" />
                  <div className="text-sm text-gray-600 mb-1">Zoho Books</div>
                  <div className="text-2xl font-bold text-blue-600">
                    {zohoStats?.total_items.toLocaleString() || 0}
                  </div>
                  <div className="text-xs text-gray-600 mt-1">Total Items</div>
                </div>

                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <Database className="h-6 w-6 text-green-600 mx-auto mb-2" />
                  <div className="text-sm text-gray-600 mb-1">Local Database</div>
                  <div className="text-2xl font-bold text-green-600">
                    {localStats?.total_items.toLocaleString() || 0}
                  </div>
                  <div className="text-xs text-gray-600 mt-1">Total Items</div>
                </div>

                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  {getDifferenceIcon(zohoStats?.total_items || 0, localStats?.total_items || 0)}
                  <div className="text-sm text-gray-600 mb-1 mt-2">Difference</div>
                  <div className="text-2xl font-bold">
                    {Math.abs((zohoStats?.total_items || 0) - (localStats?.total_items || 0))}
                  </div>
                  <div className="text-xs text-gray-600 mt-1">Items</div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 pt-4 border-t">
                <div>
                  <div className="text-sm font-medium text-gray-700 mb-3">Zoho Breakdown</div>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Active Items</span>
                      <span className="font-medium text-green-600">
                        {zohoStats?.active_items.toLocaleString() || 0}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Inactive Items</span>
                      <span className="font-medium text-gray-500">
                        {zohoStats?.inactive_items.toLocaleString() || 0}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">With Stock</span>
                      <span className="font-medium">
                        {zohoStats?.items_with_stock.toLocaleString() || 0}
                      </span>
                    </div>
                  </div>
                </div>

                <div>
                  <div className="text-sm font-medium text-gray-700 mb-3">Local Breakdown</div>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Active Items</span>
                      <span className="font-medium text-green-600">
                        {localStats?.active_items.toLocaleString() || 0}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Inactive Items</span>
                      <span className="font-medium text-gray-500">
                        {localStats?.inactive_items.toLocaleString() || 0}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">With Stock</span>
                      <span className="font-medium">
                        {localStats?.items_with_stock.toLocaleString() || 0}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Customers & Vendors */}
        <div className="grid gap-6 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Customers</CardTitle>
              <CardDescription>Customer database comparison</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <Cloud className="h-5 w-5 text-blue-600 mx-auto mb-2" />
                  <div className="text-xs text-gray-600 mb-1">Zoho</div>
                  <div className="text-xl font-bold text-blue-600">
                    {zohoStats?.total_customers.toLocaleString() || 0}
                  </div>
                </div>
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <Database className="h-5 w-5 text-green-600 mx-auto mb-2" />
                  <div className="text-xs text-gray-600 mb-1">Local</div>
                  <div className="text-xl font-bold text-green-600">
                    {localStats?.total_customers.toLocaleString() || 0}
                  </div>
                </div>
              </div>
              <div className="mt-4 pt-4 border-t text-center">
                <div className="text-sm text-gray-600">Difference</div>
                <div className="text-lg font-bold mt-1">
                  {Math.abs((zohoStats?.total_customers || 0) - (localStats?.total_customers || 0))}
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Vendors</CardTitle>
              <CardDescription>Vendor database comparison</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <Cloud className="h-5 w-5 text-blue-600 mx-auto mb-2" />
                  <div className="text-xs text-gray-600 mb-1">Zoho</div>
                  <div className="text-xl font-bold text-blue-600">
                    {zohoStats?.total_vendors.toLocaleString() || 0}
                  </div>
                </div>
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <Database className="h-5 w-5 text-green-600 mx-auto mb-2" />
                  <div className="text-xs text-gray-600 mb-1">Local</div>
                  <div className="text-xl font-bold text-green-600">
                    {localStats?.total_vendors.toLocaleString() || 0}
                  </div>
                </div>
              </div>
              <div className="mt-4 pt-4 border-t text-center">
                <div className="text-sm text-gray-600">Difference</div>
                <div className="text-lg font-bold mt-1">
                  {Math.abs((zohoStats?.total_vendors || 0) - (localStats?.total_vendors || 0))}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Stock Value */}
        <Card>
          <CardHeader>
            <CardTitle>Inventory Stock Value</CardTitle>
            <CardDescription>Total value of inventory</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-6">
              <div className="text-center p-6 bg-blue-50 rounded-lg">
                <Cloud className="h-8 w-8 text-blue-600 mx-auto mb-3" />
                <div className="text-sm text-gray-600 mb-2">Zoho Books Total</div>
                <div className="text-3xl font-bold text-blue-600">
                  {formatCurrency(zohoStats?.total_stock_value || 0)}
                </div>
              </div>
              <div className="text-center p-6 bg-green-50 rounded-lg">
                <Database className="h-8 w-8 text-green-600 mx-auto mb-3" />
                <div className="text-sm text-gray-600 mb-2">Local Database Total</div>
                <div className="text-3xl font-bold text-green-600">
                  {formatCurrency(localStats?.total_stock_value || 0)}
                </div>
              </div>
            </div>
            <div className="mt-6 pt-6 border-t text-center">
              <div className="text-sm text-gray-600 mb-2">Value Difference</div>
              <div className="text-2xl font-bold">
                {formatCurrency(Math.abs((zohoStats?.total_stock_value || 0) - (localStats?.total_stock_value || 0)))}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Discrepancies */}
        {comparison?.discrepancies && comparison.discrepancies.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Data Discrepancies</CardTitle>
              <CardDescription>
                {comparison.discrepancies.length} discrepanc{comparison.discrepancies.length !== 1 ? 'ies' : 'y'} found
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {comparison.discrepancies.slice(0, 10).map((disc, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between p-3 border rounded-lg"
                  >
                    <div className="flex-1">
                      <div className="text-sm font-medium">
                        {disc.entity_type} - {disc.entity_id}
                      </div>
                      <div className="text-xs text-gray-600 mt-1">
                        Field: <span className="font-mono">{disc.field}</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-4 text-xs">
                      <div>
                        <div className="text-gray-600">Zoho</div>
                        <div className="font-mono font-medium">{String(disc.zoho_value)}</div>
                      </div>
                      <div>
                        <div className="text-gray-600">Local</div>
                        <div className="font-mono font-medium">{String(disc.local_value)}</div>
                      </div>
                      <Badge
                        variant={
                          disc.severity === 'high' ? 'destructive' :
                          disc.severity === 'medium' ? 'default' : 'secondary'
                        }
                      >
                        {disc.severity}
                      </Badge>
                    </div>
                  </div>
                ))}
                {comparison.discrepancies.length > 10 && (
                  <div className="text-center py-2 text-sm text-gray-500">
                    ... and {comparison.discrepancies.length - 10} more discrepancies
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Last Updated */}
        <Card>
          <CardContent className="py-4">
            <div className="text-center text-sm text-gray-600">
              Last updated: {stats && new Date(stats.last_updated).toLocaleString()}
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
