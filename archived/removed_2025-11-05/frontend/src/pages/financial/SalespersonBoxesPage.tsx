import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { 
  Plus,
  Eye,
  Edit,
  User,
  AlertTriangle,
  RefreshCw,
  Search,
  DollarSign,
  TrendingUp,
  Clock,
  Target,
  Award
} from 'lucide-react';
import { useTranslation } from '../../hooks/useTranslation';
import api from '../../lib/api';

interface SalespersonBox {
  id: number;
  salesperson_id: number;
  salesperson_name: string;
  box_name: string;
  current_balance_usd: number;
  current_balance_iqd: number;
  max_capacity_usd: number;
  max_capacity_iqd: number;
  daily_target_usd: number;
  weekly_target_usd: number;
  commission_rate: number;
  total_transfers_today: number;
  total_amount_today: number;
  total_commission_today: number;
  total_transfers_week: number;
  total_amount_week: number;
  status: 'active' | 'inactive' | 'maintenance';
  last_activity: string | null;
  location: string;
  created_at: string;
}

interface SalespersonTransaction {
  id: number;
  box_id: number;
  transaction_type: 'deposit' | 'withdrawal' | 'commission' | 'transfer_fee';
  amount_usd: number;
  amount_iqd: number;
  reference_transfer_id?: number;
  description: string;
  balance_after_usd: number;
  balance_after_iqd: number;
  created_at: string;
}

interface DailyStats {
  total_salespersons: number;
  active_salespersons: number;
  total_balance_usd: number;
  total_transfers_today: number;
  total_commission_today: number;
  average_commission_rate: number;
}

const SalespersonBoxesPage: React.FC = () => {
  const { t } = useTranslation();
  const [boxes, setBoxes] = useState<SalespersonBox[]>([]);
  const [selectedBox, setSelectedBox] = useState<SalespersonBox | null>(null);
  const [transactions, setTransactions] = useState<SalespersonTransaction[]>([]);
  const [dailyStats, setDailyStats] = useState<DailyStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');

  const fetchSalespersonBoxes = async () => {
    try {
      setLoading(true);
      const [boxesResponse, statsResponse] = await Promise.all([
        api.get('/financial/salesperson-boxes'),
        api.get('/financial/salesperson-boxes/stats')
      ]);
      setBoxes(boxesResponse.data);
      setDailyStats(statsResponse.data);
      setError(null);
    } catch (err) {
      setError('Failed to load salesperson boxes');
      console.error('Salesperson boxes error:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchBoxTransactions = async (boxId: number) => {
    try {
      const response = await api.get(`/financial/salesperson-boxes/${boxId}/transactions`);
      setTransactions(response.data);
    } catch (err) {
      console.error('Failed to load transactions:', err);
    }
  };

  useEffect(() => {
    fetchSalespersonBoxes();
    
    // Auto-refresh every 60 seconds
    const interval = setInterval(fetchSalespersonBoxes, 60000);
    return () => clearInterval(interval);
  }, []);

  const formatCurrency = (amount: number, currency: 'USD' | 'IQD' = 'USD') => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: currency === 'USD' ? 2 : 0
    }).format(amount);
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active': return <Badge className="bg-green-100 text-green-800">Active</Badge>;
      case 'inactive': return <Badge className="bg-gray-100 text-gray-800">Inactive</Badge>;
      case 'maintenance': return <Badge className="bg-yellow-100 text-yellow-800">Maintenance</Badge>;
      default: return <Badge>{status}</Badge>;
    }
  };

  const getCapacityPercentage = (current: number, max: number) => {
    if (max === 0) return 0;
    return Math.min((current / max) * 100, 100);
  };

  const getTargetProgress = (current: number, target: number) => {
    if (target === 0) return 0;
    return Math.min((current / target) * 100, 100);
  };

  const getProgressColor = (percentage: number) => {
    if (percentage >= 100) return 'bg-green-500';
    if (percentage >= 75) return 'bg-blue-500';
    if (percentage >= 50) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const filteredBoxes = boxes.filter(box => {
    const matchesSearch = 
      box.salesperson_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      box.box_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      box.location.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = statusFilter === 'all' || box.status === statusFilter;
    
    return matchesSearch && matchesStatus;
  });

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
            👤 {t('salespersonBoxes')}
          </h1>
          <p className="text-gray-600 mt-1">
            {t('manageSalespersonCashBoxesAndPerformance')}
          </p>
        </div>
        <div className="flex space-x-3">
          <Button onClick={fetchSalespersonBoxes} variant="outline">
            <RefreshCw className="h-4 w-4 mr-2" />
            {t('refresh')}
          </Button>
          <Button className="bg-blue-600 hover:bg-blue-700">
            <Plus className="h-4 w-4 mr-2" />
            {t('addSalespersonBox')}
          </Button>
        </div>
      </div>

      {/* Filters */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
          <Input
            placeholder={t('searchSalesperson')}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="p-2 border rounded-md"
        >
          <option value="all">{t('allStatuses')}</option>
          <option value="active">{t('active')}</option>
          <option value="inactive">{t('inactive')}</option>
          <option value="maintenance">{t('maintenance')}</option>
        </select>

        <div></div> {/* Empty space for grid alignment */}
      </div>

      {/* Daily Stats */}
      {dailyStats && (
        <div className="grid grid-cols-1 md:grid-cols-6 gap-6">
          <Card className="border-blue-500 bg-blue-50">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-blue-600 text-sm font-medium">{t('totalSalespersons')}</p>
                  <p className="text-2xl font-bold text-blue-900">{dailyStats.total_salespersons}</p>
                </div>
                <User className="h-6 w-6 text-blue-600" />
              </div>
            </CardContent>
          </Card>

          <Card className="border-green-500 bg-green-50">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-green-600 text-sm font-medium">{t('activeSalespersons')}</p>
                  <p className="text-2xl font-bold text-green-900">{dailyStats.active_salespersons}</p>
                </div>
                <TrendingUp className="h-6 w-6 text-green-600" />
              </div>
            </CardContent>
          </Card>

          <Card className="border-purple-500 bg-purple-50">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-purple-600 text-sm font-medium">{t('totalBalance')}</p>
                  <p className="text-xl font-bold text-purple-900">
                    {formatCurrency(dailyStats.total_balance_usd)}
                  </p>
                </div>
                <DollarSign className="h-6 w-6 text-purple-600" />
              </div>
            </CardContent>
          </Card>

          <Card className="border-orange-500 bg-orange-50">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-orange-600 text-sm font-medium">{t('todayTransfers')}</p>
                  <p className="text-2xl font-bold text-orange-900">{dailyStats.total_transfers_today}</p>
                </div>
                <Target className="h-6 w-6 text-orange-600" />
              </div>
            </CardContent>
          </Card>

          <Card className="border-yellow-500 bg-yellow-50">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-yellow-600 text-sm font-medium">{t('todayCommission')}</p>
                  <p className="text-xl font-bold text-yellow-900">
                    {formatCurrency(dailyStats.total_commission_today)}
                  </p>
                </div>
                <Award className="h-6 w-6 text-yellow-600" />
              </div>
            </CardContent>
          </Card>

          <Card className="border-gray-500 bg-gray-50">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm font-medium">{t('avgCommission')}</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {dailyStats.average_commission_rate.toFixed(1)}%
                  </p>
                </div>
                <TrendingUp className="h-6 w-6 text-gray-600" />
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Salesperson Boxes Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {filteredBoxes.map((box) => {
          const usdCapacity = getCapacityPercentage(box.current_balance_usd, box.max_capacity_usd);
          const iqdCapacity = getCapacityPercentage(box.current_balance_iqd, box.max_capacity_iqd);
          const dailyProgress = getTargetProgress(box.total_amount_today, box.daily_target_usd);
          const weeklyProgress = getTargetProgress(box.total_amount_week, box.weekly_target_usd);
          
          return (
            <Card key={box.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div>
                    <CardTitle className="flex items-center">
                      <User className="h-5 w-5 mr-2" />
                      {box.salesperson_name}
                    </CardTitle>
                    <p className="text-sm text-gray-600">{box.box_name}</p>
                    <p className="text-xs text-gray-500">{box.location}</p>
                  </div>
                  <div className="flex flex-col items-end space-y-1">
                    {getStatusBadge(box.status)}
                    <Badge className="text-xs">{box.commission_rate}% Commission</Badge>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {/* Current Balance */}
                  <div>
                    <h4 className="text-sm font-medium mb-2">{t('currentBalance')}</h4>
                    <div className="space-y-2">
                      <div>
                        <div className="flex justify-between text-sm">
                          <span>USD</span>
                          <span>{formatCurrency(box.current_balance_usd)} / {formatCurrency(box.max_capacity_usd)}</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                          <div
                            className={`h-2 rounded-full ${usdCapacity >= 90 ? 'bg-red-500' : usdCapacity >= 70 ? 'bg-yellow-500' : 'bg-green-500'}`}
                            style={{ width: `${usdCapacity}%` }}
                          ></div>
                        </div>
                      </div>
                      <div>
                        <div className="flex justify-between text-sm">
                          <span>IQD</span>
                          <span>{formatCurrency(box.current_balance_iqd, 'IQD')} / {formatCurrency(box.max_capacity_iqd, 'IQD')}</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                          <div
                            className={`h-2 rounded-full ${iqdCapacity >= 90 ? 'bg-red-500' : iqdCapacity >= 70 ? 'bg-yellow-500' : 'bg-green-500'}`}
                            style={{ width: `${iqdCapacity}%` }}
                          ></div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Daily Performance */}
                  <div>
                    <h4 className="text-sm font-medium mb-2">{t('todayPerformance')}</h4>
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <div>
                        <p className="text-gray-600">{t('transfers')}</p>
                        <p className="font-medium">{box.total_transfers_today}</p>
                      </div>
                      <div>
                        <p className="text-gray-600">{t('amount')}</p>
                        <p className="font-medium">{formatCurrency(box.total_amount_today)}</p>
                      </div>
                      <div>
                        <p className="text-gray-600">{t('commission')}</p>
                        <p className="font-medium text-green-600">{formatCurrency(box.total_commission_today)}</p>
                      </div>
                      <div>
                        <p className="text-gray-600">{t('target')}</p>
                        <p className="font-medium">{dailyProgress.toFixed(0)}%</p>
                      </div>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                      <div
                        className={`h-2 rounded-full ${getProgressColor(dailyProgress)}`}
                        style={{ width: `${Math.min(dailyProgress, 100)}%` }}
                      ></div>
                    </div>
                  </div>

                  {/* Weekly Performance */}
                  <div>
                    <h4 className="text-sm font-medium mb-2">{t('weeklyPerformance')}</h4>
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <div>
                        <p className="text-gray-600">{t('transfers')}</p>
                        <p className="font-medium">{box.total_transfers_week}</p>
                      </div>
                      <div>
                        <p className="text-gray-600">{t('amount')}</p>
                        <p className="font-medium">{formatCurrency(box.total_amount_week)}</p>
                      </div>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                      <div
                        className={`h-2 rounded-full ${getProgressColor(weeklyProgress)}`}
                        style={{ width: `${Math.min(weeklyProgress, 100)}%` }}
                      ></div>
                    </div>
                    <p className="text-xs text-gray-600 mt-1">
                      {formatCurrency(box.total_amount_week)} / {formatCurrency(box.weekly_target_usd)} weekly target
                    </p>
                  </div>

                  {/* Last Activity */}
                  {box.last_activity && (
                    <div className="flex items-center text-xs text-gray-500">
                      <Clock className="h-3 w-3 mr-1" />
                      Last activity: {new Date(box.last_activity).toLocaleString()}
                    </div>
                  )}

                  {/* Actions */}
                  <div className="flex space-x-2 pt-2">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => {
                        setSelectedBox(box);
                        fetchBoxTransactions(box.id);
                      }}
                    >
                      <Eye className="h-4 w-4 mr-1" />
                      {t('view')}
                    </Button>
                    <Button size="sm" variant="outline">
                      <Edit className="h-4 w-4 mr-1" />
                      {t('edit')}
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Empty State */}
      {filteredBoxes.length === 0 && (
        <div className="text-center py-12">
          <User className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">{t('noSalespersonBoxes')}</h3>
          <p className="text-gray-600 mb-4">{t('addFirstSalespersonBox')}</p>
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            {t('addSalespersonBox')}
          </Button>
        </div>
      )}

      {/* Transaction Modal */}
      {selectedBox && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[80vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-semibold">
                {selectedBox.salesperson_name} - {selectedBox.box_name}
              </h3>
              <Button variant="outline" onClick={() => setSelectedBox(null)}>
                ✕
              </Button>
            </div>

            {/* Box Summary */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <Card>
                <CardContent className="p-4">
                  <h4 className="font-medium mb-2">{t('currentBalance')}</h4>
                  <p className="text-lg font-bold">{formatCurrency(selectedBox.current_balance_usd)}</p>
                  <p className="text-sm text-gray-600">{formatCurrency(selectedBox.current_balance_iqd, 'IQD')}</p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4">
                  <h4 className="font-medium mb-2">{t('todayActivity')}</h4>
                  <p className="text-lg font-bold">{selectedBox.total_transfers_today} transfers</p>
                  <p className="text-sm text-gray-600">{formatCurrency(selectedBox.total_amount_today)}</p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4">
                  <h4 className="font-medium mb-2">{t('commission')}</h4>
                  <p className="text-lg font-bold text-green-600">{formatCurrency(selectedBox.total_commission_today)}</p>
                  <p className="text-sm text-gray-600">{selectedBox.commission_rate}% rate</p>
                </CardContent>
              </Card>
            </div>
            
            {/* Transactions */}
            <div className="space-y-4">
              <h4 className="text-lg font-semibold">{t('recentTransactions')}</h4>
              {transactions.map((transaction) => (
                <div key={transaction.id} className="flex justify-between items-center p-4 border rounded-lg">
                  <div>
                    <p className="font-medium capitalize">{transaction.transaction_type.replace('_', ' ')}</p>
                    <p className="text-sm text-gray-600">{transaction.description}</p>
                    {transaction.reference_transfer_id && (
                      <p className="text-xs text-blue-600">Transfer ID: {transaction.reference_transfer_id}</p>
                    )}
                    <p className="text-xs text-gray-500">
                      {new Date(transaction.created_at).toLocaleString()}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className={`font-medium ${
                      transaction.transaction_type === 'deposit' || transaction.transaction_type === 'commission'
                        ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {transaction.transaction_type === 'deposit' || transaction.transaction_type === 'commission' ? '+' : '-'}
                      {formatCurrency(transaction.amount_usd)}
                    </p>
                    <p className="text-sm text-gray-600">
                      IQD: {formatCurrency(transaction.amount_iqd, 'IQD')}
                    </p>
                    <p className="text-xs text-gray-500">
                      Balance: {formatCurrency(transaction.balance_after_usd)}
                    </p>
                  </div>
                </div>
              ))}
              
              {transactions.length === 0 && (
                <p className="text-center text-gray-500 py-8">{t('noTransactions')}</p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SalespersonBoxesPage;
