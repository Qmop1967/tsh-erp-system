import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { 
  Search,
  Eye,
  RefreshCw,
  AlertTriangle,
  ArrowRight,
  Clock,
  CheckCircle,
  XCircle,
  Pause,
  Filter,
  Download,
  MapPin,
  DollarSign
} from 'lucide-react';
import { useTranslation } from '../../hooks/useTranslation';
import api from '../../lib/api';

interface Transfer {
  id: number;
  transfer_number: string;
  salesperson_id: number;
  salesperson_name: string;
  amount_usd: number;
  amount_iqd: number;
  exchange_rate: number;
  commission_rate: number;
  commission_amount: number;
  source_account: string;
  destination_account: string;
  source_type: 'cash_box' | 'bank_account' | 'digital_account';
  destination_type: 'cash_box' | 'bank_account' | 'digital_account';
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';
  priority: 'low' | 'normal' | 'high' | 'urgent';
  recipient_name: string;
  recipient_contact: string;
  recipient_location?: string;
  purpose: string;
  notes?: string;
  tracking_stages: TransferStage[];
  estimated_completion: string;
  actual_completion?: string;
  created_at: string;
  updated_at: string;
}

interface TransferStage {
  id: number;
  stage_name: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  started_at?: string;
  completed_at?: string;
  notes?: string;
  responsible_person?: string;
}

const TransferTrackingPage: React.FC = () => {
  const { t } = useTranslation();
  const [transfers, setTransfers] = useState<Transfer[]>([]);
  const [selectedTransfer, setSelectedTransfer] = useState<Transfer | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [priorityFilter, setPriorityFilter] = useState<string>('all');

  const fetchTransfers = async () => {
    try {
      setLoading(true);
      const response = await api.get('/financial/transfers/tracking');
      setTransfers(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to load transfer tracking data');
      console.error('Transfer tracking error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTransfers();
    
    // Auto-refresh every 30 seconds for real-time tracking
    const interval = setInterval(fetchTransfers, 30000);
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
      case 'pending': return <Badge className="bg-yellow-100 text-yellow-800"><Clock className="h-3 w-3 mr-1" />Pending</Badge>;
      case 'processing': return <Badge className="bg-blue-100 text-blue-800"><Pause className="h-3 w-3 mr-1" />Processing</Badge>;
      case 'completed': return <Badge className="bg-green-100 text-green-800"><CheckCircle className="h-3 w-3 mr-1" />Completed</Badge>;
      case 'failed': return <Badge className="bg-red-100 text-red-800"><XCircle className="h-3 w-3 mr-1" />Failed</Badge>;
      case 'cancelled': return <Badge className="bg-gray-100 text-gray-800"><XCircle className="h-3 w-3 mr-1" />Cancelled</Badge>;
      default: return <Badge>{status}</Badge>;
    }
  };

  const getPriorityBadge = (priority: string) => {
    switch (priority) {
      case 'urgent': return <Badge className="bg-red-500 text-white">🚨 Urgent</Badge>;
      case 'high': return <Badge className="bg-orange-100 text-orange-800">⚡ High</Badge>;
      case 'normal': return <Badge className="bg-blue-100 text-blue-800">📋 Normal</Badge>;
      case 'low': return <Badge className="bg-gray-100 text-gray-800">⏳ Low</Badge>;
      default: return <Badge>{priority}</Badge>;
    }
  };

  const getStageIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'in_progress': return <Pause className="h-4 w-4 text-blue-600 animate-pulse" />;
      case 'failed': return <XCircle className="h-4 w-4 text-red-600" />;
      default: return <Clock className="h-4 w-4 text-gray-400" />;
    }
  };

  const getProgressPercentage = (stages: TransferStage[]) => {
    const completedStages = stages.filter(stage => stage.status === 'completed').length;
    return Math.round((completedStages / stages.length) * 100);
  };

  const filteredTransfers = transfers.filter(transfer => {
    const matchesSearch = 
      transfer.transfer_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
      transfer.salesperson_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      transfer.recipient_name.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = statusFilter === 'all' || transfer.status === statusFilter;
    const matchesPriority = priorityFilter === 'all' || transfer.priority === priorityFilter;
    
    return matchesSearch && matchesStatus && matchesPriority;
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
            📍 {t('transferTracking')}
          </h1>
          <p className="text-gray-600 mt-1">
            {t('realTimeTransferMonitoring')}
          </p>
        </div>
        <div className="flex space-x-3">
          <Button onClick={fetchTransfers} variant="outline">
            <RefreshCw className="h-4 w-4 mr-2" />
            {t('refresh')}
          </Button>
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            {t('export')}
          </Button>
        </div>
      </div>

      {/* Filters */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
          <Input
            placeholder={t('searchTransfers')}
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
          <option value="pending">{t('pending')}</option>
          <option value="processing">{t('processing')}</option>
          <option value="completed">{t('completed')}</option>
          <option value="failed">{t('failed')}</option>
          <option value="cancelled">{t('cancelled')}</option>
        </select>

        <select
          value={priorityFilter}
          onChange={(e) => setPriorityFilter(e.target.value)}
          className="p-2 border rounded-md"
        >
          <option value="all">{t('allPriorities')}</option>
          <option value="urgent">{t('urgent')}</option>
          <option value="high">{t('high')}</option>
          <option value="normal">{t('normal')}</option>
          <option value="low">{t('low')}</option>
        </select>

        <Button variant="outline">
          <Filter className="h-4 w-4 mr-2" />
          {t('moreFilters')}
        </Button>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
        <Card className="border-yellow-500 bg-yellow-50">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-yellow-600 text-sm font-medium">{t('pending')}</p>
                <p className="text-2xl font-bold text-yellow-900">
                  {transfers.filter(t => t.status === 'pending').length}
                </p>
              </div>
              <Clock className="h-6 w-6 text-yellow-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-blue-500 bg-blue-50">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-600 text-sm font-medium">{t('processing')}</p>
                <p className="text-2xl font-bold text-blue-900">
                  {transfers.filter(t => t.status === 'processing').length}
                </p>
              </div>
              <Pause className="h-6 w-6 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-green-500 bg-green-50">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-green-600 text-sm font-medium">{t('completed')}</p>
                <p className="text-2xl font-bold text-green-900">
                  {transfers.filter(t => t.status === 'completed').length}
                </p>
              </div>
              <CheckCircle className="h-6 w-6 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-red-500 bg-red-50">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-red-600 text-sm font-medium">{t('failed')}</p>
                <p className="text-2xl font-bold text-red-900">
                  {transfers.filter(t => t.status === 'failed').length}
                </p>
              </div>
              <XCircle className="h-6 w-6 text-red-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-purple-500 bg-purple-50">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-600 text-sm font-medium">{t('totalAmount')}</p>
                <p className="text-xl font-bold text-purple-900">
                  {formatCurrency(
                    transfers.reduce((sum, t) => sum + t.amount_usd, 0)
                  )}
                </p>
              </div>
              <DollarSign className="h-6 w-6 text-purple-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Transfers List */}
      <div className="space-y-4">
        {filteredTransfers.map((transfer) => {
          const progress = getProgressPercentage(transfer.tracking_stages);
          
          return (
            <Card key={transfer.id} className="hover:shadow-lg transition-shadow">
              <CardContent className="p-6">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-lg font-semibold">{transfer.transfer_number}</h3>
                      {getStatusBadge(transfer.status)}
                      {getPriorityBadge(transfer.priority)}
                    </div>
                    <div className="flex items-center space-x-4 text-sm text-gray-600">
                      <span>{transfer.salesperson_name}</span>
                      <ArrowRight className="h-4 w-4" />
                      <span>{transfer.recipient_name}</span>
                      {transfer.recipient_location && (
                        <>
                          <MapPin className="h-4 w-4" />
                          <span>{transfer.recipient_location}</span>
                        </>
                      )}
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-xl font-bold">{formatCurrency(transfer.amount_usd)}</p>
                    <p className="text-sm text-gray-600">{formatCurrency(transfer.amount_iqd, 'IQD')}</p>
                    <p className="text-xs text-gray-500">Rate: {transfer.exchange_rate}</p>
                  </div>
                </div>

                {/* Progress Bar */}
                <div className="mb-4">
                  <div className="flex justify-between text-sm mb-1">
                    <span>{t('progress')}</span>
                    <span>{progress}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${progress}%` }}
                    ></div>
                  </div>
                </div>

                {/* Transfer Route */}
                <div className="flex items-center justify-between mb-4 p-3 bg-gray-50 rounded-lg">
                  <div className="text-center">
                    <p className="text-xs text-gray-500">{t('from')}</p>
                    <p className="font-medium">{transfer.source_account}</p>
                    <p className="text-xs text-blue-600">{transfer.source_type.replace('_', ' ')}</p>
                  </div>
                  <ArrowRight className="h-6 w-6 text-gray-400" />
                  <div className="text-center">
                    <p className="text-xs text-gray-500">{t('to')}</p>
                    <p className="font-medium">{transfer.destination_account}</p>
                    <p className="text-xs text-blue-600">{transfer.destination_type.replace('_', ' ')}</p>
                  </div>
                </div>

                {/* Timing */}
                <div className="flex justify-between items-center text-sm text-gray-600 mb-4">
                  <div>
                    <span>{t('created')}: {new Date(transfer.created_at).toLocaleString()}</span>
                  </div>
                  <div>
                    <span>{t('estimated')}: {new Date(transfer.estimated_completion).toLocaleString()}</span>
                  </div>
                  {transfer.actual_completion && (
                    <div>
                      <span className="text-green-600">{t('completed')}: {new Date(transfer.actual_completion).toLocaleString()}</span>
                    </div>
                  )}
                </div>

                {/* Actions */}
                <div className="flex justify-between items-center">
                  <div>
                    <p className="text-sm text-gray-600">
                      {t('purpose')}: {transfer.purpose}
                    </p>
                    {transfer.commission_amount > 0 && (
                      <p className="text-xs text-green-600">
                        {t('commission')}: {formatCurrency(transfer.commission_amount)} ({transfer.commission_rate}%)
                      </p>
                    )}
                  </div>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => setSelectedTransfer(transfer)}
                  >
                    <Eye className="h-4 w-4 mr-2" />
                    {t('trackDetails')}
                  </Button>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Empty State */}
      {filteredTransfers.length === 0 && (
        <div className="text-center py-12">
          <MapPin className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">{t('noTransfersFound')}</h3>
          <p className="text-gray-600">{t('adjustFiltersOrCreateNewTransfer')}</p>
        </div>
      )}

      {/* Detailed Tracking Modal */}
      {selectedTransfer && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[80vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-2xl font-semibold">
                {t('transferDetails')} - {selectedTransfer.transfer_number}
              </h3>
              <Button variant="outline" onClick={() => setSelectedTransfer(null)}>
                ✕
              </Button>
            </div>

            {/* Transfer Summary */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
              <Card>
                <CardHeader>
                  <CardTitle>{t('transferInfo')}</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <p><strong>{t('amount')}:</strong> {formatCurrency(selectedTransfer.amount_usd)} / {formatCurrency(selectedTransfer.amount_iqd, 'IQD')}</p>
                    <p><strong>{t('salesperson')}:</strong> {selectedTransfer.salesperson_name}</p>
                    <p><strong>{t('recipient')}:</strong> {selectedTransfer.recipient_name}</p>
                    <p><strong>{t('contact')}:</strong> {selectedTransfer.recipient_contact}</p>
                    <p><strong>{t('purpose')}:</strong> {selectedTransfer.purpose}</p>
                    {selectedTransfer.notes && (
                      <p><strong>{t('notes')}:</strong> {selectedTransfer.notes}</p>
                    )}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>{t('statusAndTiming')}</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex items-center space-x-2">
                      <strong>{t('status')}:</strong> {getStatusBadge(selectedTransfer.status)}
                    </div>
                    <div className="flex items-center space-x-2">
                      <strong>{t('priority')}:</strong> {getPriorityBadge(selectedTransfer.priority)}
                    </div>
                    <p><strong>{t('created')}:</strong> {new Date(selectedTransfer.created_at).toLocaleString()}</p>
                    <p><strong>{t('estimated')}:</strong> {new Date(selectedTransfer.estimated_completion).toLocaleString()}</p>
                    {selectedTransfer.actual_completion && (
                      <p><strong>{t('completed')}:</strong> {new Date(selectedTransfer.actual_completion).toLocaleString()}</p>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Tracking Stages */}
            <Card>
              <CardHeader>
                <CardTitle>{t('trackingStages')}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {selectedTransfer.tracking_stages.map((stage) => (
                    <div key={stage.id} className="flex items-start space-x-4 p-4 border rounded-lg">
                      <div className="flex-shrink-0 mt-1">
                        {getStageIcon(stage.status)}
                      </div>
                      <div className="flex-grow">
                        <div className="flex justify-between items-start">
                          <div>
                            <h4 className="font-medium">{stage.stage_name}</h4>
                            {stage.responsible_person && (
                              <p className="text-sm text-gray-600">{t('responsible')}: {stage.responsible_person}</p>
                            )}
                            {stage.notes && (
                              <p className="text-sm text-gray-700 mt-1">{stage.notes}</p>
                            )}
                          </div>
                          <div className="text-right text-sm">
                            {stage.started_at && (
                              <p className="text-gray-600">{t('started')}: {new Date(stage.started_at).toLocaleString()}</p>
                            )}
                            {stage.completed_at && (
                              <p className="text-green-600">{t('completed')}: {new Date(stage.completed_at).toLocaleString()}</p>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      )}
    </div>
  );
};

export default TransferTrackingPage;
