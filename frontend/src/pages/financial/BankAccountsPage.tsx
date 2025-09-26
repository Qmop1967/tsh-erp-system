import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { 
  Plus,
  Eye,
  Edit,
  Building,
  AlertTriangle,
  RefreshCw,
  Search,
  Download,
  DollarSign,
  CreditCard
} from 'lucide-react';
import { useTranslation } from '../../hooks/useTranslation';
import api from '../../lib/api';

interface BankAccount {
  id: number;
  bank_name: string;
  account_number: string;
  account_name: string;
  account_type: 'checking' | 'savings' | 'business' | 'foreign_currency';
  currency: 'USD' | 'IQD' | 'EUR' | 'GBP';
  current_balance: number;
  available_balance: number;
  branch_name?: string;
  branch_code?: string;
  swift_code?: string;
  iban?: string;
  status: 'active' | 'frozen' | 'closed';
  is_main_account: boolean;
  last_transaction_date: string | null;
  created_at: string;
}

interface BankTransaction {
  id: number;
  account_id: number;
  transaction_type: 'deposit' | 'withdrawal' | 'transfer_in' | 'transfer_out' | 'fee' | 'interest';
  amount: number;
  reference_number?: string;
  description: string;
  balance_after: number;
  transaction_date: string;
  created_at: string;
}

const BankAccountsPage: React.FC = () => {
  const { t } = useTranslation();
  const [accounts, setAccounts] = useState<BankAccount[]>([]);
  const [selectedAccount, setSelectedAccount] = useState<BankAccount | null>(null);
  const [transactions, setTransactions] = useState<BankTransaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newAccountData, setNewAccountData] = useState({
    bank_name: '',
    account_number: '',
    account_name: '',
    account_type: 'checking' as const,
    currency: 'USD' as const,
    branch_name: '',
    swift_code: '',
    iban: '',
    is_main_account: false
  });

  const fetchBankAccounts = async () => {
    try {
      setLoading(true);
      const response = await api.get('/financial/bank-accounts');
      setAccounts(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to load bank accounts');
      console.error('Bank accounts error:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchAccountTransactions = async (accountId: number) => {
    try {
      const response = await api.get(`/financial/bank-accounts/${accountId}/transactions`);
      setTransactions(response.data);
    } catch (err) {
      console.error('Failed to load transactions:', err);
    }
  };

  useEffect(() => {
    fetchBankAccounts();
  }, []);

  const formatCurrency = (amount: number, currency: string = 'USD') => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: currency === 'IQD' ? 0 : 2
    }).format(amount);
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active': return <Badge className="bg-green-100 text-green-800">Active</Badge>;
      case 'frozen': return <Badge className="bg-yellow-100 text-yellow-800">Frozen</Badge>;
      case 'closed': return <Badge className="bg-red-100 text-red-800">Closed</Badge>;
      default: return <Badge>{status}</Badge>;
    }
  };

  const getAccountTypeColor = (type: string) => {
    switch (type) {
      case 'checking': return 'text-blue-600';
      case 'savings': return 'text-green-600';
      case 'business': return 'text-purple-600';
      case 'foreign_currency': return 'text-orange-600';
      default: return 'text-gray-600';
    }
  };

  const handleCreateAccount = async () => {
    try {
      await api.post('/financial/bank-accounts', newAccountData);
      setShowCreateModal(false);
      setNewAccountData({
        bank_name: '',
        account_number: '',
        account_name: '',
        account_type: 'checking',
        currency: 'USD',
        branch_name: '',
        swift_code: '',
        iban: '',
        is_main_account: false
      });
      fetchBankAccounts();
    } catch (err) {
      console.error('Failed to create bank account:', err);
    }
  };

  const filteredAccounts = accounts.filter(account =>
    account.bank_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    account.account_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
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
            🏦 {t('bankAccounts')}
          </h1>
          <p className="text-gray-600 mt-1">
            {t('manageBankAccountsAndTransactions')}
          </p>
        </div>
        <div className="flex space-x-3">
          <Button onClick={fetchBankAccounts} variant="outline">
            <RefreshCw className="h-4 w-4 mr-2" />
            {t('refresh')}
          </Button>
          <Button onClick={() => setShowCreateModal(true)} className="bg-blue-600 hover:bg-blue-700">
            <Plus className="h-4 w-4 mr-2" />
            {t('addBankAccount')}
          </Button>
        </div>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
        <Input
          placeholder={t('searchBankAccounts')}
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="pl-10"
        />
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="border-blue-500 bg-blue-50">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-600 text-sm font-medium">{t('totalAccounts')}</p>
                <p className="text-2xl font-bold text-blue-900">{accounts.length}</p>
              </div>
              <Building className="h-8 w-8 text-blue-600" />
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
                    accounts.reduce((sum, acc) => sum + acc.current_balance, 0)
                  )}
                </p>
              </div>
              <DollarSign className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-yellow-500 bg-yellow-50">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-yellow-600 text-sm font-medium">{t('activeAccounts')}</p>
                <p className="text-2xl font-bold text-yellow-900">
                  {accounts.filter(acc => acc.status === 'active').length}
                </p>
              </div>
              <CreditCard className="h-8 w-8 text-yellow-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-purple-500 bg-purple-50">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-600 text-sm font-medium">{t('currencies')}</p>
                <p className="text-2xl font-bold text-purple-900">
                  {new Set(accounts.map(acc => acc.currency)).size}
                </p>
              </div>
              <Building className="h-8 w-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Bank Accounts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {filteredAccounts.map((account) => (
          <Card key={account.id} className={`${account.is_main_account ? 'border-blue-500 bg-blue-50' : ''}`}>
            <CardHeader>
              <div className="flex justify-between items-start">
                <div>
                  <CardTitle className="flex items-center">
                    <Building className="h-5 w-5 mr-2" />
                    {account.bank_name}
                    {account.is_main_account && (
                      <Badge className="ml-2 bg-blue-100 text-blue-800">Main</Badge>
                    )}
                  </CardTitle>
                  <p className="text-sm text-gray-600">{account.account_name}</p>
                  <p className="text-xs text-gray-500">***{account.account_number.slice(-4)}</p>
                </div>
                <div className="flex flex-col items-end space-y-1">
                  {getStatusBadge(account.status)}
                  <Badge className={getAccountTypeColor(account.account_type)}>
                    {account.account_type.replace('_', ' ')}
                  </Badge>
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

                {/* Account Details */}
                <div className="space-y-1">
                  {account.branch_name && (
                    <p className="text-xs text-gray-500">Branch: {account.branch_name}</p>
                  )}
                  {account.swift_code && (
                    <p className="text-xs text-gray-500">SWIFT: {account.swift_code}</p>
                  )}
                  {account.iban && (
                    <p className="text-xs text-gray-500">IBAN: {account.iban}</p>
                  )}
                </div>

                {/* Last Transaction */}
                {account.last_transaction_date && (
                  <p className="text-xs text-gray-500">
                    Last transaction: {new Date(account.last_transaction_date).toLocaleDateString()}
                  </p>
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
                    <Download className="h-4 w-4 mr-1" />
                    {t('export')}
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
          <Building className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">{t('noBankAccounts')}</h3>
          <p className="text-gray-600 mb-4">{t('addFirstBankAccount')}</p>
          <Button onClick={() => setShowCreateModal(true)}>
            <Plus className="h-4 w-4 mr-2" />
            {t('addBankAccount')}
          </Button>
        </div>
      )}

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-lg max-h-[80vh] overflow-y-auto">
            <h3 className="text-lg font-semibold mb-4">{t('addNewBankAccount')}</h3>
            <div className="space-y-4">
              <Input
                placeholder={t('bankName')}
                value={newAccountData.bank_name}
                onChange={(e) => setNewAccountData({ ...newAccountData, bank_name: e.target.value })}
              />
              <Input
                placeholder={t('accountNumber')}
                value={newAccountData.account_number}
                onChange={(e) => setNewAccountData({ ...newAccountData, account_number: e.target.value })}
              />
              <Input
                placeholder={t('accountName')}
                value={newAccountData.account_name}
                onChange={(e) => setNewAccountData({ ...newAccountData, account_name: e.target.value })}
              />
              <select
                value={newAccountData.account_type}
                onChange={(e) => setNewAccountData({ ...newAccountData, account_type: e.target.value as any })}
                className="w-full p-2 border rounded-md"
              >
                <option value="checking">{t('checking')}</option>
                <option value="savings">{t('savings')}</option>
                <option value="business">{t('business')}</option>
                <option value="foreign_currency">{t('foreignCurrency')}</option>
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
              </select>
              <Input
                placeholder={t('branchName')}
                value={newAccountData.branch_name}
                onChange={(e) => setNewAccountData({ ...newAccountData, branch_name: e.target.value })}
              />
              <Input
                placeholder={t('swiftCode')}
                value={newAccountData.swift_code}
                onChange={(e) => setNewAccountData({ ...newAccountData, swift_code: e.target.value })}
              />
              <Input
                placeholder={t('iban')}
                value={newAccountData.iban}
                onChange={(e) => setNewAccountData({ ...newAccountData, iban: e.target.value })}
              />
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={newAccountData.is_main_account}
                  onChange={(e) => setNewAccountData({ ...newAccountData, is_main_account: e.target.checked })}
                  className="mr-2"
                />
                {t('isMainAccount')}
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
                {selectedAccount.bank_name} - {selectedAccount.account_name}
              </h3>
              <Button variant="outline" onClick={() => setSelectedAccount(null)}>
                ✕
              </Button>
            </div>
            
            <div className="space-y-4">
              {transactions.map((transaction) => (
                <div key={transaction.id} className="flex justify-between items-center p-4 border rounded-lg">
                  <div>
                    <p className="font-medium capitalize">{transaction.transaction_type.replace('_', ' ')}</p>
                    <p className="text-sm text-gray-600">{transaction.description}</p>
                    {transaction.reference_number && (
                      <p className="text-xs text-gray-500">Ref: {transaction.reference_number}</p>
                    )}
                    <p className="text-xs text-gray-500">
                      {new Date(transaction.transaction_date).toLocaleString()}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className={`font-medium ${
                      transaction.transaction_type.includes('in') || transaction.transaction_type === 'deposit' || transaction.transaction_type === 'interest'
                        ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {transaction.transaction_type.includes('in') || transaction.transaction_type === 'deposit' || transaction.transaction_type === 'interest' ? '+' : '-'}
                      {formatCurrency(transaction.amount, selectedAccount.currency)}
                    </p>
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

export default BankAccountsPage;
