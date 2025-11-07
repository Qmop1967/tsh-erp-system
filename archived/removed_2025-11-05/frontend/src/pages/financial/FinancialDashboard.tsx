import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { Button } from '../../components/ui/button';
import { 
  DollarSign, 
  TrendingUp, 
  TrendingDown, 
  AlertTriangle, 
  RefreshCw,
  CreditCard,
  Building,
  Smartphone,
  Users,
  Eye,
  ArrowUpRight,
  ArrowDownRight
} from 'lucide-react';
import { useTranslation } from '../../hooks/useTranslation';
import api from '../../lib/api';

interface FinancialSummary {
  total_cash_boxes: number;
  total_cash_amount: number;
  total_bank_accounts: number;
  total_bank_balance: number;
  total_digital_accounts: number;
  total_digital_balance: number;
  pending_transfers: number;
  completed_transfers_today: number;
  total_transfers_amount_today: number;
  profit_today: number;
  salesperson_active: number;
  alerts_count: number;
}

interface RecentTransaction {
  id: number;
  type: 'transfer_in' | 'transfer_out' | 'commission' | 'expense';
  amount: number;
  currency: 'USD' | 'IQD';
  from_account: string;
  to_account: string;
  salesperson_name?: string;
  status: 'completed' | 'pending' | 'failed';
  created_at: string;
}

const FinancialDashboard: React.FC = () => {
  const { t } = useTranslation();
  const [summary, setSummary] = useState<FinancialSummary | null>(null);
  const [recentTransactions, setRecentTransactions] = useState<RecentTransaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [summaryResponse, transactionsResponse] = await Promise.all([
        api.get('/financial/dashboard/summary'),
        api.get('/financial/transactions/recent')
      ]);
      
      setSummary(summaryResponse.data);
      setRecentTransactions(transactionsResponse.data);
      setError(null);
    } catch (err) {
      setError('Failed to load financial dashboard data');
      console.error('Financial dashboard error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
    
    // Auto-refresh every 60 seconds
    const interval = setInterval(fetchDashboardData, 60000);
    return () => clearInterval(interval);
  }, []);

  const formatCurrency = (amount: number, currency: 'USD' | 'IQD' = 'USD') => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: currency === 'USD' ? 2 : 0
    }).format(amount);
  };

  const getTransactionIcon = (type: string) => {
    switch (type) {
      case 'transfer_in': return <ArrowDownRight className="h-4 w-4 text-green-600" />;
      case 'transfer_out': return <ArrowUpRight className="h-4 w-4 text-red-600" />;
      case 'commission': return <DollarSign className="h-4 w-4 text-blue-600" />;
      case 'expense': return <TrendingDown className="h-4 w-4 text-orange-600" />;
      default: return <DollarSign className="h-4 w-4" />;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'completed': return <Badge className="bg-green-100 text-green-800">Completed</Badge>;
      case 'pending': return <Badge className="bg-yellow-100 text-yellow-800">Pending</Badge>;
      case 'failed': return <Badge className="bg-red-100 text-red-800">Failed</Badge>;
      default: return <Badge>{status}</Badge>;
    }
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
            💰 {t('financialDashboard')}
          </h1>
          <p className="text-gray-600 mt-1">
            {t('comprehensiveFinancialOverview')}
          </p>
        </div>
        <Button onClick={fetchDashboardData} className="bg-blue-600 hover:bg-blue-700">
          <RefreshCw className="h-4 w-4 mr-2" />
          {t('refresh')}
        </Button>
      </div>

      {/* Quick Stats */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card className="border-blue-500 bg-blue-50">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-blue-600 text-sm font-medium">{t('cashBoxes')}</p>
                  <p className="text-2xl font-bold text-blue-900">
                    {formatCurrency(summary.total_cash_amount)}
                  </p>
                  <p className="text-blue-600 text-xs">
                    {summary.total_cash_boxes} {t('boxes')}
                  </p>
                </div>
                <CreditCard className="h-8 w-8 text-blue-600" />
              </div>
            </CardContent>
          </Card>

          <Card className="border-green-500 bg-green-50">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-green-600 text-sm font-medium">{t('bankAccounts')}</p>
                  <p className="text-2xl font-bold text-green-900">
                    {formatCurrency(summary.total_bank_balance)}
                  </p>
                  <p className="text-green-600 text-xs">
                    {summary.total_bank_accounts} {t('accounts')}
                  </p>
                </div>
                <Building className="h-8 w-8 text-green-600" />
              </div>
            </CardContent>
          </Card>

          <Card className="border-purple-500 bg-purple-50">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-purple-600 text-sm font-medium">{t('digitalAccounts')}</p>
                  <p className="text-2xl font-bold text-purple-900">
                    {formatCurrency(summary.total_digital_balance)}
                  </p>
                  <p className="text-purple-600 text-xs">
                    {summary.total_digital_accounts} {t('accounts')}
                  </p>
                </div>
                <Smartphone className="h-8 w-8 text-purple-600" />
              </div>
            </CardContent>
          </Card>

          <Card className="border-orange-500 bg-orange-50">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-orange-600 text-sm font-medium">{t('todayProfit')}</p>
                  <p className="text-2xl font-bold text-orange-900">
                    {formatCurrency(summary.profit_today)}
                  </p>
                  <p className="text-orange-600 text-xs">
                    {summary.completed_transfers_today} {t('transfers')}
                  </p>
                </div>
                <TrendingUp className="h-8 w-8 text-orange-600" />
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Activity Summary */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Users className="h-5 w-5 mr-2" />
                {t('activeSalespersons')}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{summary.salesperson_active}</div>
              <p className="text-sm text-gray-600">{t('currentlyActive')}</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Eye className="h-5 w-5 mr-2" />
                {t('pendingTransfers')}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-yellow-600">{summary.pending_transfers}</div>
              <p className="text-sm text-gray-600">{t('awaitingApproval')}</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <AlertTriangle className="h-5 w-5 mr-2" />
                {t('alerts')}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-red-600">{summary.alerts_count}</div>
              <p className="text-sm text-gray-600">{t('requiresAttention')}</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Recent Transactions */}
      <Card>
        <CardHeader>
          <CardTitle>{t('recentTransactions')}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {recentTransactions.length > 0 ? (
              recentTransactions.map((transaction) => (
                <div
                  key={transaction.id}
                  className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50"
                >
                  <div className="flex items-center space-x-4">
                    {getTransactionIcon(transaction.type)}
                    <div>
                      <p className="font-medium">
                        {transaction.from_account} → {transaction.to_account}
                      </p>
                      <p className="text-sm text-gray-600">
                        {transaction.salesperson_name && `${transaction.salesperson_name} • `}
                        {new Date(transaction.created_at).toLocaleString()}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <div className="text-right">
                      <p className="font-medium">
                        {formatCurrency(transaction.amount, transaction.currency)}
                      </p>
                      <p className="text-sm text-gray-600 capitalize">{transaction.type.replace('_', ' ')}</p>
                    </div>
                    {getStatusBadge(transaction.status)}
                  </div>
                </div>
              ))
            ) : (
              <p className="text-gray-500 text-center py-8">{t('noRecentTransactions')}</p>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default FinancialDashboard;
