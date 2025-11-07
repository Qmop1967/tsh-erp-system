import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { 
  Plus,
  Eye,
  Edit,
  Smartphone,
  AlertTriangle,
  RefreshCw,
  Search,
  DollarSign,
  Wifi,
  Shield,
  Clock
} from 'lucide-react';
import { useTranslation } from '../../hooks/useTranslation';
import api from '../../lib/api';

interface DigitalAccount {
  id: number;
  platform_name: string;
  account_identifier: string; // email, phone, username
  account_name: string;
  platform_type: 'paypal' | 'wise' | 'revolut' | 'skrill' | 'cryptocurrency' | 'local_digital' | 'other';
  currency: 'USD' | 'IQD' | 'EUR' | 'GBP' | 'BTC' | 'ETH';
  current_balance: number;
  available_balance: number;
  daily_limit?: number;
  monthly_limit?: number;
  status: 'active' | 'suspended' | 'verification_pending' | 'closed';
  verification_level: 'basic' | 'verified' | 'premium';
  fees_percentage: number;
  last_transaction_date: string | null;
  created_at: string;
  api_connected: boolean;
  two_factor_enabled: boolean;
}

interface DigitalTransaction {
  id: number;
  account_id: number;
  transaction_type: 'send' | 'receive' | 'exchange' | 'fee' | 'withdrawal' | 'deposit';
  amount: number;
  fee_amount: number;
  recipient_identifier?: string;
  sender_identifier?: string;
  reference_id?: string;
  description: string;
  balance_after: number;
  transaction_date: string;
  created_at: string;
}

const DigitalAccountsPage: React.FC = () => {
  const { t } = useTranslation();
  const [accounts, setAccounts] = useState<DigitalAccount[]>([]);
  const [selectedAccount, setSelectedAccount] = useState<DigitalAccount | null>(null);
  const [transactions, setTransactions] = useState<DigitalTransaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newAccountData, setNewAccountData] = useState({
    platform_name: '',
    account_identifier: '',
    account_name: '',
    platform_type: 'paypal' as const,
    currency: 'USD' as const,
    daily_limit: 0,
    monthly_limit: 0,
    fees_percentage: 0,
    two_factor_enabled: false
  });

  const fetchDigitalAccounts = async () => {
    try {
      setLoading(true);
      const response = await api.get('/financial/digital-accounts');
      setAccounts(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to load digital accounts');
      console.error('Digital accounts error:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchAccountTransactions = async (accountId: number) => {
    try {
      const response = await api.get(`/financial/digital-accounts/${accountId}/transactions`);
      setTransactions(response.data);
    } catch (err) {
      console.error('Failed to load transactions:', err);
    }
  };

  useEffect(() => {
    fetchDigitalAccounts();
  }, []);

  const formatCurrency = (amount: number, currency: string = 'USD') => {
    if (currency === 'BTC' || currency === 'ETH') {
      return `${amount.toFixed(8)} ${currency}`;
    }
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: currency === 'IQD' ? 0 : 2
    }).format(amount);
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active': return <Badge className="bg-green-100 text-green-800">Active</Badge>;
      case 'suspended': return <Badge className="bg-red-100 text-red-800">Suspended</Badge>;
      case 'verification_pending': return <Badge className="bg-yellow-100 text-yellow-800">Pending</Badge>;
      case 'closed': return <Badge className="bg-gray-100 text-gray-800">Closed</Badge>;
      default: return <Badge>{status}</Badge>;
    }
  };

  const getVerificationBadge = (level: string) => {
    switch (level) {
      case 'basic': return <Badge className="bg-gray-100 text-gray-800">Basic</Badge>;
      case 'verified': return <Badge className="bg-blue-100 text-blue-800">Verified</Badge>;
      case 'premium': return <Badge className="bg-purple-100 text-purple-800">Premium</Badge>;
      default: return <Badge>{level}</Badge>;
    }
  };

  const getPlatformIcon = (type: string) => {
    switch (type) {
      case 'cryptocurrency': return '₿';
      case 'paypal': return '💳';
      case 'wise': return '🌐';
      case 'revolut': return '💰';
      case 'skrill': return '📱';
      default: return '💻';
    }
  };

  const handleCreateAccount = async () => {
    try {
      await api.post('/financial/digital-accounts', newAccountData);
      setShowCreateModal(false);
      setNewAccountData({
        platform_name: '',
        account_identifier: '',
        account_name: '',
        platform_type: 'paypal',
        currency: 'USD',
        daily_limit: 0,
        monthly_limit: 0,
        fees_percentage: 0,
        two_factor_enabled: false
      });
      fetchDigitalAccounts();
    } catch (err) {
      console.error('Failed to create digital account:', err);
    }
  };

  const filteredAccounts = accounts.filter(account =>
    account.platform_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    account.account_identifier.toLowerCase().includes(searchTerm.toLowerCase()) ||
    account.account_name.toLowerCase().includes(searchTerm.toLowerCase())
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
            📱 {t('digitalAccounts')}
          </h1>
          <p className="text-gray-600 mt-1">
            {t('manageDigitalWalletsAndOnlineAccounts')}
          </p>
        </div>
        <div className="flex space-x-3">
          <Button onClick={fetchDigitalAccounts} variant="outline">
            <RefreshCw className="h-4 w-4 mr-2" />
            {t('refresh')}
          </Button>
          <Button onClick={() => setShowCreateModal(true)} className="bg-blue-600 hover:bg-blue-700">
            <Plus className="h-4 w-4 mr-2" />
            {t('addDigitalAccount')}
          </Button>
        </div>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
        <Input
          placeholder={t('searchDigitalAccounts')}
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="pl-10"
        />
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="border-purple-500 bg-purple-50">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-600 text-sm font-medium">{t('totalAccounts')}</p>
                <p className="text-2xl font-bold text-purple-900">{accounts.length}</p>
              </div>
              <Smartphone className="h-8 w-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-green-500 bg-green-50">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-green-600 text-sm font-medium">{t('totalBalance')}</p>
                <p className="text-2xl font-bold text-green-900">
                  {formatCurrency(
                    accounts.filter(acc => acc.currency === 'USD').reduce((sum, acc) => sum + acc.current_balance, 0)
                  )}
                </p>
              </div>
              <DollarSign className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-blue-500 bg-blue-50">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-600 text-sm font-medium">{t('activeAccounts')}</p>
                <p className="text-2xl font-bold text-blue-900">
                  {accounts.filter(acc => acc.status === 'active').length}
                </p>
              </div>
              <Wifi className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-orange-500 bg-orange-50">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-orange-600 text-sm font-medium">{t('verified')}</p>
                <p className="text-2xl font-bold text-orange-900">
                  {accounts.filter(acc => acc.verification_level === 'verified' || acc.verification_level === 'premium').length}
                </p>
              </div>
              <Shield className="h-8 w-8 text-orange-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Digital Accounts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {filteredAccounts.map((account) => (
          <Card key={account.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex justify-between items-start">
                <div>
                  <CardTitle className="flex items-center">
                    <span className="text-2xl mr-2">{getPlatformIcon(account.platform_type)}</span>
                    {account.platform_name}
                  </CardTitle>
                  <p className="text-sm text-gray-600">{account.account_name}</p>
                  <p className="text-xs text-gray-500">{account.account_identifier}</p>
                </div>
                <div className="flex flex-col items-end space-y-1">
                  {getStatusBadge(account.status)}
                  {getVerificationBadge(account.verification_level)}
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {/* Balance */}
                <div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">{t('currentBalance')}</span>
                    <span className="font-medium">{formatCurrency(account.current_balance, account.currency)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">{t('availableBalance')}</span>
                    <span className="font-medium text-green-600">{formatCurrency(account.available_balance, account.currency)}</span>
                  </div>
                </div>

                {/* Limits */}
                {(account.daily_limit || account.monthly_limit) && (
                  <div className="space-y-1">
                    {account.daily_limit && (
                      <div className="flex justify-between text-xs">
                        <span className="text-gray-500">{t('dailyLimit')}</span>
                        <span>{formatCurrency(account.daily_limit, account.currency)}</span>
                      </div>
                    )}
                    {account.monthly_limit && (
                      <div className="flex justify-between text-xs">
                        <span className="text-gray-500">{t('monthlyLimit')}</span>
                        <span>{formatCurrency(account.monthly_limit, account.currency)}</span>
                      </div>
                    )}
                  </div>
                )}

                {/* Features */}
                <div className="flex items-center space-x-4 text-xs">
                  {account.api_connected && (
                    <div className="flex items-center text-green-600">
                      <Wifi className="h-3 w-3 mr-1" />
                      API
                    </div>
                  )}
                  {account.two_factor_enabled && (
                    <div className="flex items-center text-blue-600">
                      <Shield className="h-3 w-3 mr-1" />
                      2FA
                    </div>
                  )}
                  {account.fees_percentage > 0 && (
                    <span className="text-gray-600">
                      {account.fees_percentage}% fees
                    </span>
                  )}
                </div>

                {/* Last Transaction */}
                {account.last_transaction_date && (
                  <div className="flex items-center text-xs text-gray-500">
                    <Clock className="h-3 w-3 mr-1" />
                    Last: {new Date(account.last_transaction_date).toLocaleDateString()}
                  </div>
                )}

                {/* Actions */}
                <div className="flex space-x-2 pt-2">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => {
                      setSelectedAccount(account);
                      fetchAccountTransactions(account.id);
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
        ))}
      </div>

      {/* Empty State */}
      {filteredAccounts.length === 0 && (
        <div className="text-center py-12">
          <Smartphone className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">{t('noDigitalAccounts')}</h3>
          <p className="text-gray-600 mb-4">{t('addFirstDigitalAccount')}</p>
          <Button onClick={() => setShowCreateModal(true)}>
            <Plus className="h-4 w-4 mr-2" />
            {t('addDigitalAccount')}
          </Button>
        </div>
      )}

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-lg max-h-[80vh] overflow-y-auto">
            <h3 className="text-lg font-semibold mb-4">{t('addNewDigitalAccount')}</h3>
            <div className="space-y-4">
              <Input
                placeholder={t('platformName')}
                value={newAccountData.platform_name}
                onChange={(e) => setNewAccountData({ ...newAccountData, platform_name: e.target.value })}
              />
              <Input
                placeholder={t('accountIdentifier')}
                value={newAccountData.account_identifier}
                onChange={(e) => setNewAccountData({ ...newAccountData, account_identifier: e.target.value })}
              />
              <Input
                placeholder={t('accountName')}
                value={newAccountData.account_name}
                onChange={(e) => setNewAccountData({ ...newAccountData, account_name: e.target.value })}
              />
              <select
                value={newAccountData.platform_type}
                onChange={(e) => setNewAccountData({ ...newAccountData, platform_type: e.target.value as any })}
                className="w-full p-2 border rounded-md"
              >
                <option value="paypal">PayPal</option>
                <option value="wise">Wise</option>
                <option value="revolut">Revolut</option>
                <option value="skrill">Skrill</option>
                <option value="cryptocurrency">Cryptocurrency</option>
                <option value="local_digital">Local Digital</option>
                <option value="other">Other</option>
              </select>
              <select
                value={newAccountData.currency}
                onChange={(e) => setNewAccountData({ ...newAccountData, currency: e.target.value as any })}
                className="w-full p-2 border rounded-md"
              >
                <option value="USD">USD</option>
                <option value="IQD">IQD</option>
                <option value="EUR">EUR</option>
                <option value="GBP">GBP</option>
                <option value="BTC">BTC</option>
                <option value="ETH">ETH</option>
              </select>
              <Input
                placeholder={t('dailyLimit')}
                type="number"
                value={newAccountData.daily_limit}
                onChange={(e) => setNewAccountData({ ...newAccountData, daily_limit: Number(e.target.value) })}
              />
              <Input
                placeholder={t('monthlyLimit')}
                type="number"
                value={newAccountData.monthly_limit}
                onChange={(e) => setNewAccountData({ ...newAccountData, monthly_limit: Number(e.target.value) })}
              />
              <Input
                placeholder={t('feesPercentage')}
                type="number"
                step="0.01"
                value={newAccountData.fees_percentage}
                onChange={(e) => setNewAccountData({ ...newAccountData, fees_percentage: Number(e.target.value) })}
              />
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={newAccountData.two_factor_enabled}
                  onChange={(e) => setNewAccountData({ ...newAccountData, two_factor_enabled: e.target.checked })}
                  className="mr-2"
                />
                {t('twoFactorEnabled')}
              </label>
            </div>
            <div className="flex justify-end space-x-3 mt-6">
              <Button variant="outline" onClick={() => setShowCreateModal(false)}>
                {t('cancel')}
              </Button>
              <Button onClick={handleCreateAccount}>
                {t('create')}
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Transaction Modal */}
      {selectedAccount && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[80vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-semibold">
                {selectedAccount.platform_name} - {selectedAccount.account_name}
              </h3>
              <Button variant="outline" onClick={() => setSelectedAccount(null)}>
                ✕
              </Button>
            </div>
            
            <div className="space-y-4">
              {transactions.map((transaction) => (
                <div key={transaction.id} className="flex justify-between items-center p-4 border rounded-lg">
                  <div>
                    <p className="font-medium capitalize">{transaction.transaction_type}</p>
                    <p className="text-sm text-gray-600">{transaction.description}</p>
                    {transaction.reference_id && (
                      <p className="text-xs text-gray-500">Ref: {transaction.reference_id}</p>
                    )}
                    {(transaction.recipient_identifier || transaction.sender_identifier) && (
                      <p className="text-xs text-blue-600">
                        {transaction.recipient_identifier ? `To: ${transaction.recipient_identifier}` : `From: ${transaction.sender_identifier}`}
                      </p>
                    )}
                    <p className="text-xs text-gray-500">
                      {new Date(transaction.transaction_date).toLocaleString()}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className={`font-medium ${
                      transaction.transaction_type === 'receive' || transaction.transaction_type === 'deposit'
                        ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {transaction.transaction_type === 'receive' || transaction.transaction_type === 'deposit' ? '+' : '-'}
                      {formatCurrency(transaction.amount, selectedAccount.currency)}
                    </p>
                    {transaction.fee_amount > 0 && (
                      <p className="text-xs text-red-600">
                        Fee: {formatCurrency(transaction.fee_amount, selectedAccount.currency)}
                      </p>
                    )}
                    <p className="text-sm text-gray-600">
                      Balance: {formatCurrency(transaction.balance_after, selectedAccount.currency)}
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

export default DigitalAccountsPage;
