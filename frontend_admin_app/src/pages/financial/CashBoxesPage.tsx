import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { 
  Plus,
  Eye,
  Edit,
  AlertTriangle,
  RefreshCw,
  Lock,
  Unlock,
  CreditCard,
  Search
} from 'lucide-react';
import { useTranslation } from '../../hooks/useTranslation';
import api from '../../lib/api';

interface CashBox {
  id: number;
  name: string;
  location: string;
  salesperson_id?: number;
  salesperson_name?: string;
  current_balance_usd: number;
  current_balance_iqd: number;
  max_capacity_usd: number;
  max_capacity_iqd: number;
  status: 'active' | 'locked' | 'maintenance';
  last_transaction_date: string | null;
  created_at: string;
  is_main_safe: boolean;
}

interface CashBoxTransaction {
  id: number;
  cash_box_id: number;
  transaction_type: 'deposit' | 'withdrawal' | 'transfer' | 'commission';
  amount_usd: number;
  amount_iqd: number;
  description: string;
  salesperson_id?: number;
  salesperson_name?: string;
  created_at: string;
}

const CashBoxesPage: React.FC = () => {
  const { t } = useTranslation();
  const [cashBoxes, setCashBoxes] = useState<CashBox[]>([]);
  const [selectedBox, setSelectedBox] = useState<CashBox | null>(null);
  const [transactions, setTransactions] = useState<CashBoxTransaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newBoxData, setNewBoxData] = useState({
    name: '',
    location: '',
    max_capacity_usd: 0,
    max_capacity_iqd: 0,
    is_main_safe: false
  });

  const fetchCashBoxes = async () => {
    try {
      setLoading(true);
      const response = await api.get('/financial/cash-boxes');
      setCashBoxes(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to load cash boxes');
      console.error('Cash boxes error:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchBoxTransactions = async (boxId: number) => {
    try {
      const response = await api.get(`/financial/cash-boxes/${boxId}/transactions`);
      setTransactions(response.data);
    } catch (err) {
      console.error('Failed to load transactions:', err);
    }
  };

  useEffect(() => {
    fetchCashBoxes();
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
      case 'locked': return <Badge className="bg-red-100 text-red-800">Locked</Badge>;
      case 'maintenance': return <Badge className="bg-yellow-100 text-yellow-800">Maintenance</Badge>;
      default: return <Badge>{status}</Badge>;
    }
  };

  const getCapacityPercentage = (current: number, max: number) => {
    if (max === 0) return 0;
    return Math.min((current / max) * 100, 100);
  };

  const getCapacityColor = (percentage: number) => {
    if (percentage >= 90) return 'bg-red-500';
    if (percentage >= 70) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  const handleCreateCashBox = async () => {
    try {
      await api.post('/financial/cash-boxes', newBoxData);
      setShowCreateModal(false);
      setNewBoxData({
        name: '',
        location: '',
        max_capacity_usd: 0,
        max_capacity_iqd: 0,
        is_main_safe: false
      });
      fetchCashBoxes();
    } catch (err) {
      console.error('Failed to create cash box:', err);
    }
  };

  const handleToggleStatus = async (boxId: number, currentStatus: string) => {
    try {
      const newStatus = currentStatus === 'active' ? 'locked' : 'active';
      await api.patch(`/financial/cash-boxes/${boxId}/status`, { status: newStatus });
      fetchCashBoxes();
    } catch (err) {
      console.error('Failed to update status:', err);
    }
  };

  const filteredCashBoxes = cashBoxes.filter(box =>
    box.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    box.location.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (box.salesperson_name && box.salesperson_name.toLowerCase().includes(searchTerm.toLowerCase()))
  );

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
            💰 {t('cashBoxes')}
          </h1>
          <p className="text-gray-600 mt-1">
            {t('manageCashBoxesAndSafes')}
          </p>
        </div>
        <div className="flex space-x-3">
          <Button onClick={fetchCashBoxes} variant="outline">
            <RefreshCw className="h-4 w-4 mr-2" />
            {t('refresh')}
          </Button>
          <Button onClick={() => setShowCreateModal(true)} className="bg-blue-600 hover:bg-blue-700">
            <Plus className="h-4 w-4 mr-2" />
            {t('addCashBox')}
          </Button>
        </div>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
        <Input
          placeholder={t('searchCashBoxes')}
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="pl-10"
        />
      </div>

      {/* Cash Boxes Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredCashBoxes.map((box) => {
          const usdPercentage = getCapacityPercentage(box.current_balance_usd, box.max_capacity_usd);
          const iqdPercentage = getCapacityPercentage(box.current_balance_iqd, box.max_capacity_iqd);
          
          return (
            <Card key={box.id} className={`${box.is_main_safe ? 'border-blue-500 bg-blue-50' : ''}`}>
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div>
                    <CardTitle className="flex items-center">
                      <CreditCard className="h-5 w-5 mr-2" />
                      {box.name}
                      {box.is_main_safe && (
                        <Badge className="ml-2 bg-blue-100 text-blue-800">Main Safe</Badge>
                      )}
                    </CardTitle>
                    <p className="text-sm text-gray-600">{box.location}</p>
                    {box.salesperson_name && (
                      <p className="text-sm text-blue-600">{box.salesperson_name}</p>
                    )}
                  </div>
                  <div className="flex space-x-2">
                    {getStatusBadge(box.status)}
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleToggleStatus(box.id, box.status)}
                    >
                      {box.status === 'active' ? <Lock className="h-4 w-4" /> : <Unlock className="h-4 w-4" />}
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {/* USD Balance */}
                  <div>
                    <div className="flex justify-between text-sm">
                      <span>USD Balance</span>
                      <span>{formatCurrency(box.current_balance_usd)} / {formatCurrency(box.max_capacity_usd)}</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                      <div
                        className={`h-2 rounded-full ${getCapacityColor(usdPercentage)}`}
                        style={{ width: `${usdPercentage}%` }}
                      ></div>
                    </div>
                  </div>

                  {/* IQD Balance */}
                  <div>
                    <div className="flex justify-between text-sm">
                      <span>IQD Balance</span>
                      <span>{formatCurrency(box.current_balance_iqd, 'IQD')} / {formatCurrency(box.max_capacity_iqd, 'IQD')}</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                      <div
                        className={`h-2 rounded-full ${getCapacityColor(iqdPercentage)}`}
                        style={{ width: `${iqdPercentage}%` }}
                      ></div>
                    </div>
                  </div>

                  {/* Last Transaction */}
                  {box.last_transaction_date && (
                    <p className="text-xs text-gray-500">
                      Last transaction: {new Date(box.last_transaction_date).toLocaleDateString()}
                    </p>
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
      {filteredCashBoxes.length === 0 && (
        <div className="text-center py-12">
          <CreditCard className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">{t('noCashBoxes')}</h3>
          <p className="text-gray-600 mb-4">{t('createFirstCashBox')}</p>
          <Button onClick={() => setShowCreateModal(true)}>
            <Plus className="h-4 w-4 mr-2" />
            {t('addCashBox')}
          </Button>
        </div>
      )}

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-4">{t('createNewCashBox')}</h3>
            <div className="space-y-4">
              <Input
                placeholder={t('cashBoxName')}
                value={newBoxData.name}
                onChange={(e) => setNewBoxData({ ...newBoxData, name: e.target.value })}
              />
              <Input
                placeholder={t('location')}
                value={newBoxData.location}
                onChange={(e) => setNewBoxData({ ...newBoxData, location: e.target.value })}
              />
              <Input
                placeholder={t('maxCapacityUSD')}
                type="number"
                value={newBoxData.max_capacity_usd}
                onChange={(e) => setNewBoxData({ ...newBoxData, max_capacity_usd: Number(e.target.value) })}
              />
              <Input
                placeholder={t('maxCapacityIQD')}
                type="number"
                value={newBoxData.max_capacity_iqd}
                onChange={(e) => setNewBoxData({ ...newBoxData, max_capacity_iqd: Number(e.target.value) })}
              />
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={newBoxData.is_main_safe}
                  onChange={(e) => setNewBoxData({ ...newBoxData, is_main_safe: e.target.checked })}
                  className="mr-2"
                />
                {t('isMainSafe')}
              </label>
            </div>
            <div className="flex justify-end space-x-3 mt-6">
              <Button variant="outline" onClick={() => setShowCreateModal(false)}>
                {t('cancel')}
              </Button>
              <Button onClick={handleCreateCashBox}>
                {t('create')}
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Transaction Modal */}
      {selectedBox && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[80vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-semibold">{selectedBox.name} - {t('transactions')}</h3>
              <Button variant="outline" onClick={() => setSelectedBox(null)}>
                ✕
              </Button>
            </div>
            
            <div className="space-y-4">
              {transactions.map((transaction) => (
                <div key={transaction.id} className="flex justify-between items-center p-4 border rounded-lg">
                  <div>
                    <p className="font-medium capitalize">{transaction.transaction_type.replace('_', ' ')}</p>
                    <p className="text-sm text-gray-600">{transaction.description}</p>
                    <p className="text-xs text-gray-500">
                      {new Date(transaction.created_at).toLocaleString()}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="font-medium">
                      USD: {formatCurrency(transaction.amount_usd)}
                    </p>
                    <p className="text-sm text-gray-600">
                      IQD: {formatCurrency(transaction.amount_iqd, 'IQD')}
                    </p>
                    {transaction.salesperson_name && (
                      <p className="text-xs text-blue-600">{transaction.salesperson_name}</p>
                    )}
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

export default CashBoxesPage;
