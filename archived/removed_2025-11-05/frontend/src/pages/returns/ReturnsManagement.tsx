import React, { useState, useEffect, useRef } from 'react'
import { 
  Package, ArrowLeft, Camera, CheckCircle, XCircle, Clock, 
  DollarSign, RotateCcw, FileImage, AlertTriangle, Search,
  Filter, Download, Plus, Eye, Edit, Trash2
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { useLanguageStore } from '@/stores/languageStore'
import { useDynamicTranslations } from '@/lib/dynamicTranslations'
import api from '@/lib/api'

interface ReturnItem {
  product_id: number
  product_name: string
  quantity: number
  original_price: number
  return_amount: number
  condition: string
  notes: string
}

interface ReturnRequest {
  id?: number
  return_number?: string
  transaction_id?: number
  customer_id?: number
  return_items: ReturnItem[]
  return_reason: string
  return_description: string
  refund_method: string
  photos?: string[]
  customer_notes?: string
  status?: string
  created_at?: string
  total_amount?: number
}

interface Customer {
  id: number
  name: string
  phone: string
  email?: string
}

export default function ReturnsManagement() {
  const { language } = useLanguageStore()
  const { t } = useDynamicTranslations(language)
  
  // State Management
  const [returns, setReturns] = useState<ReturnRequest[]>([])
  const [selectedReturn, setSelectedReturn] = useState<ReturnRequest | null>(null)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showDetailsModal, setShowDetailsModal] = useState(false)
  const [showApprovalModal, setShowApprovalModal] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  // Filters
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [reasonFilter, setReasonFilter] = useState<string>('all')
  const [dateFromFilter, setDateFromFilter] = useState<string>('')
  const [dateToFilter, setDateToFilter] = useState<string>('')
  const [searchTerm, setSearchTerm] = useState<string>('')
  
  // Create Return Form
  const [newReturn, setNewReturn] = useState<ReturnRequest>({
    return_items: [],
    return_reason: 'defective',
    return_description: '',
    refund_method: 'cash',
    photos: []
  })
  const [customers, setCustomers] = useState<Customer[]>([])
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null)
  const [photosToUpload, setPhotosToUpload] = useState<File[]>([])
  const fileInputRef = useRef<HTMLInputElement>(null)
  
  // Dashboard Stats
  const [dashboardStats, setDashboardStats] = useState({
    today_returns: 0,
    pending_returns: 0,
    weekly_returns: 0,
    monthly_refunds: 0,
    reasons_breakdown: {},
    return_rate: 0
  })

  const returnReasons = [
    { value: 'defective', label: language === 'ar' ? 'معيب' : 'Defective' },
    { value: 'wrong_item', label: language === 'ar' ? 'صنف خاطئ' : 'Wrong Item' },
    { value: 'damage', label: language === 'ar' ? 'تلف' : 'Damage' },
    { value: 'customer_changed_mind', label: language === 'ar' ? 'غير رأيه' : 'Changed Mind' },
    { value: 'size_issue', label: language === 'ar' ? 'مشكلة الحجم' : 'Size Issue' },
    { value: 'quality_issue', label: language === 'ar' ? 'مشكلة الجودة' : 'Quality Issue' },
    { value: 'other', label: language === 'ar' ? 'أخرى' : 'Other' }
  ]

  const refundMethods = [
    { value: 'cash', label: language === 'ar' ? 'نقداً' : 'Cash' },
    { value: 'store_credit', label: language === 'ar' ? 'رصيد المتجر' : 'Store Credit' },
    { value: 'original_payment', label: language === 'ar' ? 'الدفعة الأصلية' : 'Original Payment' },
    { value: 'bank_transfer', label: language === 'ar' ? 'تحويل بنكي' : 'Bank Transfer' }
  ]

  const statusOptions = [
    { value: 'all', label: language === 'ar' ? 'الكل' : 'All' },
    { value: 'pending', label: language === 'ar' ? 'قيد الانتظار' : 'Pending' },
    { value: 'approved', label: language === 'ar' ? 'معتمد' : 'Approved' },
    { value: 'rejected', label: language === 'ar' ? 'مرفوض' : 'Rejected' },
    { value: 'processed', label: language === 'ar' ? 'تم المعالجة' : 'Processed' },
    { value: 'refunded', label: language === 'ar' ? 'تم الاسترداد' : 'Refunded' }
  ]

  useEffect(() => {
    loadReturns()
    loadDashboardStats()
    loadCustomers()
  }, [statusFilter, reasonFilter, dateFromFilter, dateToFilter])

  const loadReturns = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams()
      
      if (statusFilter !== 'all') params.append('status', statusFilter)
      if (reasonFilter !== 'all') params.append('return_reason', reasonFilter)
      if (dateFromFilter) params.append('date_from', dateFromFilter)
      if (dateToFilter) params.append('date_to', dateToFilter)
      
      const response = await api.get(`/api/returns/returns?${params.toString()}`)
      setReturns(response.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load returns')
    } finally {
      setLoading(false)
    }
  }

  const loadDashboardStats = async () => {
    try {
      const response = await api.get('/api/returns/returns/dashboard/stats')
      setDashboardStats(response.data)
    } catch (err) {
      console.error('Failed to load dashboard stats:', err)
    }
  }

  const loadCustomers = async () => {
    try {
      const response = await api.get('/api/customers')
      setCustomers(response.data)
    } catch (err) {
      console.error('Failed to load customers:', err)
    }
  }

  const handlePhotoUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || [])
    setPhotosToUpload([...photosToUpload, ...files])
  }

  const convertPhotosToBase64 = async (files: File[]): Promise<string[]> => {
    const base64Photos: string[] = []
    
    for (const file of files) {
      const reader = new FileReader()
      const base64 = await new Promise<string>((resolve) => {
        reader.onload = () => {
          const result = reader.result as string
          resolve(result.split(',')[1]) // Remove data:image prefix
        }
        reader.readAsDataURL(file)
      })
      base64Photos.push(base64)
    }
    
    return base64Photos
  }

  const createReturnRequest = async () => {
    try {
      setLoading(true)
      
      // Convert photos to base64
      const photoBase64 = await convertPhotosToBase64(photosToUpload)
      
      const returnData = {
        ...newReturn,
        customer_id: selectedCustomer?.id,
        photos: photoBase64
      }
      
      const response = await api.post('/api/returns/returns/create', returnData)
      
      // Reset form
      setNewReturn({
        return_items: [],
        return_reason: 'defective',
        return_description: '',
        refund_method: 'cash',
        photos: []
      })
      setSelectedCustomer(null)
      setPhotosToUpload([])
      setShowCreateModal(false)
      
      // Reload returns
      loadReturns()
      loadDashboardStats()
      
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create return request')
    } finally {
      setLoading(false)
    }
  }

  const approveReturn = async (returnId: number, approved: boolean, approvalData: any) => {
    try {
      setLoading(true)
      
      const response = await api.post(`/api/returns/returns/${returnId}/approve`, {
        return_id: returnId,
        approved,
        ...approvalData
      })
      
      setShowApprovalModal(false)
      loadReturns()
      loadDashboardStats()
      
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to process return approval')
    } finally {
      setLoading(false)
    }
  }

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      pending: { color: 'bg-yellow-100 text-yellow-800', icon: Clock },
      approved: { color: 'bg-green-100 text-green-800', icon: CheckCircle },
      rejected: { color: 'bg-red-100 text-red-800', icon: XCircle },
      processed: { color: 'bg-blue-100 text-blue-800', icon: Package },
      refunded: { color: 'bg-purple-100 text-purple-800', icon: DollarSign }
    }
    
    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.pending
    const IconComponent = config.icon
    
    return (
      <Badge className={`${config.color} border-0`}>
        <IconComponent className="w-3 h-3 mr-1" />
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    )
  }

  const filteredReturns = returns.filter(returnItem => {
    const matchesSearch = searchTerm === '' || 
      returnItem.return_number?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      returnItem.return_description.toLowerCase().includes(searchTerm.toLowerCase())
    
    return matchesSearch
  })

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center">
              <Package className="w-8 h-8 mr-3 text-blue-600" />
              {language === 'ar' ? 'إدارة المرتجعات والاستبدال' : 'Returns & Exchange Management'}
            </h1>
            <p className="text-gray-600 mt-2">
              {language === 'ar' 
                ? 'إدارة شاملة للمرتجعات والاستبدالات مع تتبع الأسباب والموافقات'
                : 'Comprehensive returns and exchange management with reason tracking and approvals'
              }
            </p>
          </div>
          <Button 
            onClick={() => setShowCreateModal(true)}
            className="bg-blue-600 hover:bg-blue-700"
          >
            <Plus className="w-4 h-4 mr-2" />
            {language === 'ar' ? 'طلب إرجاع جديد' : 'New Return Request'}
          </Button>
        </div>
      </div>

      {/* Dashboard Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">
                  {language === 'ar' ? 'مرتجعات اليوم' : "Today's Returns"}
                </p>
                <p className="text-2xl font-bold text-gray-900">{dashboardStats.today_returns}</p>
              </div>
              <Package className="w-8 h-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">
                  {language === 'ar' ? 'قيد الانتظار' : 'Pending Returns'}
                </p>
                <p className="text-2xl font-bold text-yellow-600">{dashboardStats.pending_returns}</p>
              </div>
              <Clock className="w-8 h-8 text-yellow-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">
                  {language === 'ar' ? 'مرتجعات الأسبوع' : 'Weekly Returns'}
                </p>
                <p className="text-2xl font-bold text-gray-900">{dashboardStats.weekly_returns}</p>
              </div>
              <RotateCcw className="w-8 h-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">
                  {language === 'ar' ? 'استردادات الشهر' : 'Monthly Refunds'}
                </p>
                <p className="text-2xl font-bold text-purple-600">
                  {dashboardStats.monthly_refunds.toLocaleString()} IQD
                </p>
              </div>
              <DollarSign className="w-8 h-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center">
            <Filter className="w-5 h-5 mr-2" />
            {language === 'ar' ? 'المرشحات' : 'Filters'}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">
                {language === 'ar' ? 'البحث' : 'Search'}
              </label>
              <div className="relative">
                <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <Input
                  placeholder={language === 'ar' ? 'رقم الإرجاع أو الوصف' : 'Return number or description'}
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                {language === 'ar' ? 'الحالة' : 'Status'}
              </label>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="w-full p-2 border rounded-lg bg-white"
              >
                {statusOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                {language === 'ar' ? 'السبب' : 'Reason'}
              </label>
              <select
                value={reasonFilter}
                onChange={(e) => setReasonFilter(e.target.value)}
                className="w-full p-2 border rounded-lg bg-white"
              >
                <option value="all">{language === 'ar' ? 'الكل' : 'All'}</option>
                {returnReasons.map(reason => (
                  <option key={reason.value} value={reason.value}>
                    {reason.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                {language === 'ar' ? 'من تاريخ' : 'From Date'}
              </label>
              <Input
                type="date"
                value={dateFromFilter}
                onChange={(e) => setDateFromFilter(e.target.value)}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                {language === 'ar' ? 'إلى تاريخ' : 'To Date'}
              </label>
              <Input
                type="date"
                value={dateToFilter}
                onChange={(e) => setDateToFilter(e.target.value)}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Returns List */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>
              {language === 'ar' ? 'قائمة المرتجعات' : 'Returns List'}
              <Badge className="ml-2 bg-blue-100 text-blue-800">
                {filteredReturns.length}
              </Badge>
            </span>
            <Button variant="outline" size="sm">
              <Download className="w-4 h-4 mr-2" />
              {language === 'ar' ? 'تصدير' : 'Export'}
            </Button>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-4 text-gray-600">
                {language === 'ar' ? 'جاري التحميل...' : 'Loading...'}
              </p>
            </div>
          ) : filteredReturns.length === 0 ? (
            <div className="text-center py-8">
              <Package className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">
                {language === 'ar' ? 'لا توجد مرتجعات' : 'No returns found'}
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {filteredReturns.map((returnItem) => (
                <div 
                  key={returnItem.id}
                  className="border rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
                  onClick={() => {
                    setSelectedReturn(returnItem)
                    setShowDetailsModal(true)
                  }}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-4">
                        <div>
                          <h3 className="font-semibold text-lg">
                            {returnItem.return_number}
                          </h3>
                          <p className="text-gray-600 text-sm">
                            {returnItem.return_description}
                          </p>
                        </div>
                        {getStatusBadge(returnItem.status || 'pending')}
                      </div>
                      
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
                        <div>
                          <p className="text-xs text-gray-500">
                            {language === 'ar' ? 'السبب' : 'Reason'}
                          </p>
                          <p className="font-medium">
                            {returnReasons.find(r => r.value === returnItem.return_reason)?.label}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500">
                            {language === 'ar' ? 'المبلغ' : 'Amount'}
                          </p>
                          <p className="font-medium text-blue-600">
                            {returnItem.total_amount?.toLocaleString()} IQD
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500">
                            {language === 'ar' ? 'الأصناف' : 'Items'}
                          </p>
                          <p className="font-medium">
                            {returnItem.return_items.length}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500">
                            {language === 'ar' ? 'التاريخ' : 'Date'}
                          </p>
                          <p className="font-medium">
                            {returnItem.created_at ? new Date(returnItem.created_at).toLocaleDateString() : '-'}
                          </p>
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      {returnItem.photos && returnItem.photos.length > 0 && (
                        <Badge variant="outline">
                          <FileImage className="w-3 h-3 mr-1" />
                          {returnItem.photos.length}
                        </Badge>
                      )}
                      
                      {returnItem.status === 'pending' && (
                        <Button
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation()
                            setSelectedReturn(returnItem)
                            setShowApprovalModal(true)
                          }}
                        >
                          {language === 'ar' ? 'مراجعة' : 'Review'}
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Error Display */}
      {error && (
        <div className="fixed bottom-4 right-4 bg-red-50 border border-red-200 p-4 rounded-lg shadow-lg">
          <div className="flex items-center">
            <AlertTriangle className="w-5 h-5 text-red-600 mr-2" />
            <span className="text-red-800">{error}</span>
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={() => setError(null)}
              className="ml-2"
            >
              ×
            </Button>
          </div>
        </div>
      )}
    </div>
  )
} 