/**
 * Money Transfer Dashboard - CRITICAL FRAUD PREVENTION
 * 
 * This is the main dashboard for monitoring $35K USD weekly transfers
 * from 12 travel salespersons. Critical for preventing fraud and losses.
 */

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { Button } from '../../components/ui/button';
import { AlertTriangle, DollarSign, Users, TrendingUp, Eye, CheckCircle } from 'lucide-react';
import { useTranslation } from '../../hooks/useTranslation';
import api from '../../lib/api';

interface MoneyTransferSummary {
  salesperson_id: number;
  salesperson_name: string;
  total_transfers: number;
  total_amount_usd: number;
  total_amount_iqd: number;
  pending_transfers: number;
  suspicious_transfers: number;
  total_commission: number;
  last_transfer_date: string | null;
}

interface DashboardStats {
  total_pending_amount: number;
  total_received_today: number;
  suspicious_transfers_count: number;
  pending_transfers_count: number;
  salesperson_summaries: MoneyTransferSummary[];
  platform_breakdown: Record<string, { count: number; total_amount: number }>;
}

interface FraudAlert {
  transfer_id: number;
  salesperson_name: string;
  alert_reason: string;
  amount_usd: number;
  created_at: string;
  priority: 'high' | 'medium' | 'low';
}

const MoneyTransferDashboard: React.FC = () => {
  const { t } = useTranslation();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [fraudAlerts, setFraudAlerts] = useState<FraudAlert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [dashboardResponse, alertsResponse] = await Promise.all([
        api.get('/money-transfers/dashboard'),
        api.get('/money-transfers/fraud-alerts')
      ]);
      
      setStats(dashboardResponse.data);
      setFraudAlerts(alertsResponse.data);
      setError(null);
    } catch (err) {
      setError('Failed to load dashboard data');
      console.error('Dashboard error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
    
    // Auto-refresh every 30 seconds for critical monitoring
    const interval = setInterval(fetchDashboardData, 30000);
    return () => clearInterval(interval);
  }, []);

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-500';
      case 'medium': return 'bg-yellow-500';
      case 'low': return 'bg-blue-500';
      default: return 'bg-gray-500';
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="border border-red-500 bg-red-50 p-4 rounded-lg flex items-center">
          <AlertTriangle className="h-4 w-4 mr-2 text-red-600" />
          <span className="text-red-700">{error}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            🚨 Money Transfer Control Center
          </h1>
          <p className="text-gray-600 mt-1">
            Emergency fraud prevention system - $35K weekly monitoring
          </p>
        </div>
        <Button onClick={fetchDashboardData} className="bg-blue-600 hover:bg-blue-700">
          <Eye className="h-4 w-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* Critical Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="border-yellow-500 bg-yellow-50">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-yellow-600">Pending Transfers</p>
                <p className="text-2xl font-bold text-yellow-900">
                  {formatCurrency(stats?.total_pending_amount || 0)}
                </p>
              </div>
              <DollarSign className="h-8 w-8 text-yellow-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-green-500 bg-green-50">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-green-600">Received Today</p>
                <p className="text-2xl font-bold text-green-900">
                  {formatCurrency(stats?.total_received_today || 0)}
                </p>
              </div>
              <CheckCircle className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-red-500 bg-red-50">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-red-600">Fraud Alerts</p>
                <p className="text-2xl font-bold text-red-900">
                  {stats?.suspicious_transfers_count || 0}
                </p>
              </div>
              <AlertTriangle className="h-8 w-8 text-red-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-blue-500 bg-blue-50">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-blue-600">Pending Count</p>
                <p className="text-2xl font-bold text-blue-900">
                  {stats?.pending_transfers_count || 0}
                </p>
              </div>
              <Users className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Fraud Alerts */}
      {fraudAlerts.length > 0 && (
        <Card className="border-red-500">
          <CardHeader>
            <CardTitle className="text-red-700 flex items-center">
              <AlertTriangle className="h-5 w-5 mr-2" />
              🚨 CRITICAL FRAUD ALERTS - IMMEDIATE ATTENTION REQUIRED
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {fraudAlerts.slice(0, 10).map((alert) => (
                <div key={alert.transfer_id} className="flex items-center justify-between p-3 bg-red-50 rounded-lg border border-red-200">
                  <div className="flex items-center space-x-3">
                    <Badge className={`${getPriorityColor(alert.priority)} text-white`}>
                      {alert.priority.toUpperCase()}
                    </Badge>
                    <div>
                      <p className="font-medium text-red-900">{alert.salesperson_name}</p>
                      <p className="text-sm text-red-600">{alert.alert_reason}</p>
                      <p className="text-xs text-red-500">Transfer #{alert.transfer_id}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-bold text-red-900">{formatCurrency(alert.amount_usd)}</p>
                    <p className="text-xs text-red-600">{formatDate(alert.created_at)}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Salesperson Summary */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Users className="h-5 w-5 mr-2" />
            Travel Salesperson Summary (12 Salespersons)
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-3">Salesperson</th>
                  <th className="text-right p-3">Total Transfers</th>
                  <th className="text-right p-3">Total Amount</th>
                  <th className="text-right p-3">Commission</th>
                  <th className="text-center p-3">Pending</th>
                  <th className="text-center p-3">Suspicious</th>
                  <th className="text-right p-3">Last Transfer</th>
                </tr>
              </thead>
              <tbody>
                {stats?.salesperson_summaries?.map((summary) => (
                  <tr key={summary.salesperson_id} className="border-b hover:bg-gray-50">
                    <td className="p-3">
                      <div className="font-medium">{summary.salesperson_name}</div>
                      <div className="text-sm text-gray-500">ID: {summary.salesperson_id}</div>
                    </td>
                    <td className="text-right p-3">{summary.total_transfers}</td>
                    <td className="text-right p-3 font-medium">
                      {formatCurrency(summary.total_amount_usd)}
                    </td>
                    <td className="text-right p-3 font-medium text-green-600">
                      {formatCurrency(summary.total_commission)}
                    </td>
                    <td className="text-center p-3">
                      {summary.pending_transfers > 0 ? (
                        <Badge className="bg-yellow-100 text-yellow-800">
                          {summary.pending_transfers}
                        </Badge>
                      ) : (
                        <span className="text-gray-400">0</span>
                      )}
                    </td>
                    <td className="text-center p-3">
                      {summary.suspicious_transfers > 0 ? (
                        <Badge className="bg-red-100 text-red-800">
                          {summary.suspicious_transfers}
                        </Badge>
                      ) : (
                        <span className="text-gray-400">0</span>
                      )}
                    </td>
                    <td className="text-right p-3 text-sm text-gray-500">
                      {summary.last_transfer_date ? 
                        formatDate(summary.last_transfer_date) : 
                        'No transfers'
                      }
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Platform Breakdown */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <TrendingUp className="h-5 w-5 mr-2" />
            Transfer Platform Breakdown
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {Object.entries(stats?.platform_breakdown || {}).map(([platform, data]) => (
              <div key={platform} className="p-4 bg-gray-50 rounded-lg">
                <h4 className="font-medium text-gray-900">{platform}</h4>
                <div className="mt-2 space-y-1">
                  <p className="text-sm text-gray-600">
                    Transfers: <span className="font-medium">{data.count}</span>
                  </p>
                  <p className="text-sm text-gray-600">
                    Total: <span className="font-medium">{formatCurrency(data.total_amount)}</span>
                  </p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default MoneyTransferDashboard; 