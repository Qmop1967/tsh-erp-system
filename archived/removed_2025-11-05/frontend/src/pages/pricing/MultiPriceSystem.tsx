import React, { useState, useEffect } from 'react'
import { 
  DollarSign, Users, TrendingUp, Package, Settings, 
  Edit, Plus, Search, Filter, Download, Upload,
  MessageSquare, CheckCircle, Clock, XCircle
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useLanguageStore } from '@/stores/languageStore'
import { useDynamicTranslations } from '@/lib/dynamicTranslations'
import api from '@/lib/api'

interface PriceList {
  id: number
  name: string
  price_list_type: string
  description: string
  minimum_order_value: number
  discount_percentage: number
  is_active: boolean
  valid_from: string
  valid_to: string | null
  product_count: number
  customer_categories: string[]
  created_at: string
}

interface PriceNegotiation {
  id: number
  customer: {
    id: number
    name: string
    category: string
  }
  product: {
    id: number
    name: string
    sku: string
  }
  current_price: number
  requested_price: number
  discount_requested: number
  quantity: number
  justification: string
  status: string
  valid_until: string
  created_at: string
}

interface DashboardStats {
  total_price_lists: number
  active_price_lists: number
  pending_negotiations: number
  recent_price_changes: number
  category_breakdown: Array<{category: string, count: number}>
  price_list_usage: Array<{name: string, type: string, product_count: number}>
}

export default function MultiPriceSystem() {
  const { language } = useLanguageStore()
  const { t } = useDynamicTranslations(language)
  
  // State Management
  const [priceLists, setPriceLists] = useState<PriceList[]>([])
  const [negotiations, setNegotiations] = useState<PriceNegotiation[]>([])
  const [dashboardStats, setDashboardStats] = useState<DashboardStats>({
    total_price_lists: 0,
    active_price_lists: 0,
    pending_negotiations: 0,
    recent_price_changes: 0,
    category_breakdown: [],
    price_list_usage: []
  })
  
  const [selectedView, setSelectedView] = useState<'overview' | 'price-lists' | 'negotiations' | 'customers'>('overview')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  // Filters
  const [priceListFilter, setPriceListFilter] = useState<string>('all')
  const [negotiationFilter, setNegotiationFilter] = useState<string>('all')
  const [searchTerm, setSearchTerm] = useState<string>('')

  const priceListTypes = [
    { value: 'wholesale_a', label: language === 'ar' ? 'جملة أ' : 'Wholesale A', color: 'bg-blue-600' },
    { value: 'wholesale_b', label: language === 'ar' ? 'جملة ب' : 'Wholesale B', color: 'bg-blue-500' },
    { value: 'retailer_shop', label: language === 'ar' ? 'متاجر التجزئة' : 'Retailer Shop', color: 'bg-green-600' },
    { value: 'technical', label: language === 'ar' ? 'فني' : 'Technical', color: 'bg-purple-600' },
    { value: 'consumer', label: language === 'ar' ? 'مستهلك' : 'Consumer', color: 'bg-orange-600' },
    { value: 'partner_salesmen', label: language === 'ar' ? 'شركاء البيع' : 'Partner Salesmen', color: 'bg-red-600' }
  ]

  const negotiationStatuses = [
    { value: 'pending', label: language === 'ar' ? 'قيد الانتظار' : 'Pending', icon: Clock, color: 'text-yellow-600' },
    { value: 'approved', label: language === 'ar' ? 'موافق' : 'Approved', icon: CheckCircle, color: 'text-green-600' },
    { value: 'rejected', label: language === 'ar' ? 'مرفوض' : 'Rejected', icon: XCircle, color: 'text-red-600' },
    { value: 'counter_offer', label: language === 'ar' ? 'عرض مضاد' : 'Counter Offer', icon: MessageSquare, color: 'text-blue-600' }
  ]

  useEffect(() => {
    loadDashboardData()
    loadPriceLists()
    loadNegotiations()
  }, [])

  const loadDashboardData = async () => {
    try {
      const response = await api.get('/api/pricing/pricing/dashboard/overview')
      setDashboardStats(response.data)
    } catch (err) {
      console.error('Failed to load dashboard data:', err)
    }
  }

  const loadPriceLists = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams()
      if (priceListFilter !== 'all') params.append('price_list_type', priceListFilter)
      
      const response = await api.get(`/api/pricing/price-lists?${params.toString()}`)
      setPriceLists(response.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load price lists')
    } finally {
      setLoading(false)
    }
  }

  const loadNegotiations = async () => {
    try {
      const params = new URLSearchParams()
      if (negotiationFilter !== 'all') params.append('status', negotiationFilter)
      
      const response = await api.get(`/api/pricing/price-negotiations?${params.toString()}`)
      setNegotiations(response.data)
    } catch (err) {
      console.error('Failed to load negotiations:', err)
    }
  }

  const getPriceListTypeInfo = (type: string) => {
    return priceListTypes.find(t => t.value === type) || priceListTypes[0]
  }

  const getNegotiationStatusInfo = (status: string) => {
    return negotiationStatuses.find(s => s.value === status) || negotiationStatuses[0]
  }

  const filteredPriceLists = priceLists.filter(list => {
    if (searchTerm === '') return true
    return list.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
           list.description.toLowerCase().includes(searchTerm.toLowerCase())
  })

  const filteredNegotiations = negotiations.filter(negotiation => {
    if (searchTerm === '') return true
    return negotiation.customer.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
           negotiation.product.name.toLowerCase().includes(searchTerm.toLowerCase())
  })

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center">
              <DollarSign className="w-8 h-8 mr-3 text-blue-600" />
              {language === 'ar' ? 'نظام التسعير المتعدد' : 'Multi-Price System'}
            </h1>
            <p className="text-gray-600 mt-2">
              {language === 'ar' 
                ? 'إدارة 5 قوائم أسعار مختلفة لفئات العملاء المتنوعة مع نظام التفاوض'
                : 'Manage 5 different price lists for various customer categories with negotiation system'
              }
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <Button 
              variant="outline"
              onClick={() => loadDashboardData()}
            >
              <TrendingUp className="w-4 h-4 mr-2" />
              {language === 'ar' ? 'تحديث' : 'Refresh'}
            </Button>
            <Button className="bg-blue-600 hover:bg-blue-700">
              <Plus className="w-4 h-4 mr-2" />
              {language === 'ar' ? 'قائمة أسعار جديدة' : 'New Price List'}
            </Button>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="mb-8">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            {[
              { id: 'overview', label: language === 'ar' ? 'نظرة عامة' : 'Overview', icon: TrendingUp },
              { id: 'price-lists', label: language === 'ar' ? 'قوائم الأسعار' : 'Price Lists', icon: Package },
              { id: 'negotiations', label: language === 'ar' ? 'المفاوضات' : 'Negotiations', icon: MessageSquare },
              { id: 'customers', label: language === 'ar' ? 'العملاء' : 'Customers', icon: Users }
            ].map((tab) => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setSelectedView(tab.id as any)}
                  className={`group inline-flex items-center py-4 px-1 border-b-2 font-medium text-sm ${
                    selectedView === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="w-5 h-5 mr-2" />
                  {tab.label}
                </button>
              )
            })}
          </nav>
        </div>
      </div>

      {/* Overview Tab */}
      {selectedView === 'overview' && (
        <div className="space-y-8">
          {/* Dashboard Stats */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">
                      {language === 'ar' ? 'قوائم الأسعار النشطة' : 'Active Price Lists'}
                    </p>
                    <p className="text-2xl font-bold text-blue-600">
                      {dashboardStats.active_price_lists}/{dashboardStats.total_price_lists}
                    </p>
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
                      {language === 'ar' ? 'المفاوضات المعلقة' : 'Pending Negotiations'}
                    </p>
                    <p className="text-2xl font-bold text-yellow-600">{dashboardStats.pending_negotiations}</p>
                  </div>
                  <MessageSquare className="w-8 h-8 text-yellow-600" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">
                      {language === 'ar' ? 'تغييرات الأسعار الأخيرة' : 'Recent Price Changes'}
                    </p>
                    <p className="text-2xl font-bold text-green-600">{dashboardStats.recent_price_changes}</p>
                  </div>
                  <TrendingUp className="w-8 h-8 text-green-600" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">
                      {language === 'ar' ? 'فئات العملاء' : 'Customer Categories'}
                    </p>
                    <p className="text-2xl font-bold text-purple-600">{dashboardStats.category_breakdown.length}</p>
                  </div>
                  <Users className="w-8 h-8 text-purple-600" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Price List Types Overview */}
          <Card>
            <CardHeader>
              <CardTitle>
                {language === 'ar' ? 'نظرة عامة على أنواع قوائم الأسعار' : 'Price List Types Overview'}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {priceListTypes.map((type) => {
                  const usage = dashboardStats.price_list_usage.find(u => u.type === type.value)
                  return (
                    <div key={type.value} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-3">
                        <div className={`w-4 h-4 rounded-full ${type.color}`}></div>
                        <Badge variant="outline">
                          {usage?.product_count || 0} {language === 'ar' ? 'منتج' : 'products'}
                        </Badge>
                      </div>
                      <h3 className="font-semibold text-lg mb-2">{type.label}</h3>
                      <p className="text-sm text-gray-600">
                        {usage ? usage.name : language === 'ar' ? 'لا توجد قائمة نشطة' : 'No active list'}
                      </p>
                    </div>
                  )
                })}
              </div>
            </CardContent>
          </Card>

          {/* Customer Category Breakdown */}
          <Card>
            <CardHeader>
              <CardTitle>
                {language === 'ar' ? 'توزيع فئات العملاء' : 'Customer Category Breakdown'}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {dashboardStats.category_breakdown.map((category) => {
                  const typeInfo = getPriceListTypeInfo(category.category)
                  const total = dashboardStats.category_breakdown.reduce((sum, c) => sum + c.count, 0)
                  const percentage = total > 0 ? (category.count / total * 100) : 0
                  
                  return (
                    <div key={category.category} className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className={`w-3 h-3 rounded-full ${typeInfo.color}`}></div>
                        <span className="font-medium">{typeInfo.label}</span>
                      </div>
                      <div className="flex items-center space-x-4">
                        <div className="flex-1 bg-gray-200 rounded-full h-2 w-32">
                          <div 
                            className={`h-2 rounded-full ${typeInfo.color}`}
                            style={{ width: `${percentage}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-medium w-12 text-right">
                          {category.count}
                        </span>
                        <span className="text-sm text-gray-500 w-12 text-right">
                          {percentage.toFixed(1)}%
                        </span>
                      </div>
                    </div>
                  )
                })}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Price Lists Tab */}
      {selectedView === 'price-lists' && (
        <div className="space-y-6">
          {/* Filters */}
          <Card>
            <CardContent className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">
                    {language === 'ar' ? 'البحث' : 'Search'}
                  </label>
                  <div className="relative">
                    <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                    <Input
                      placeholder={language === 'ar' ? 'اسم القائمة أو الوصف' : 'List name or description'}
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-2">
                    {language === 'ar' ? 'نوع القائمة' : 'List Type'}
                  </label>
                  <select
                    value={priceListFilter}
                    onChange={(e) => setPriceListFilter(e.target.value)}
                    className="w-full p-2 border rounded-lg bg-white"
                  >
                    <option value="all">{language === 'ar' ? 'جميع الأنواع' : 'All Types'}</option>
                    {priceListTypes.map(type => (
                      <option key={type.value} value={type.value}>
                        {type.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="flex items-end space-x-2">
                  <Button 
                    onClick={loadPriceLists}
                    variant="outline"
                  >
                    <Filter className="w-4 h-4 mr-2" />
                    {language === 'ar' ? 'تطبيق المرشحات' : 'Apply Filters'}
                  </Button>
                  <Button variant="outline">
                    <Download className="w-4 h-4 mr-2" />
                    {language === 'ar' ? 'تصدير' : 'Export'}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Price Lists Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
            {filteredPriceLists.map((priceList) => {
              const typeInfo = getPriceListTypeInfo(priceList.price_list_type)
              return (
                <Card key={priceList.id} className="relative overflow-hidden">
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <div className={`w-3 h-3 rounded-full ${typeInfo.color}`}></div>
                        <Badge variant={priceList.is_active ? "default" : "secondary"}>
                          {priceList.is_active 
                            ? (language === 'ar' ? 'نشط' : 'Active')
                            : (language === 'ar' ? 'غير نشط' : 'Inactive')
                          }
                        </Badge>
                      </div>
                      <Button size="sm" variant="outline">
                        <Edit className="w-4 h-4" />
                      </Button>
                    </div>
                    <div>
                      <h3 className="font-semibold text-lg">{priceList.name}</h3>
                      <p className="text-sm text-gray-600">{typeInfo.label}</p>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <p className="text-sm text-gray-600">{priceList.description}</p>
                      
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <p className="text-xs text-gray-500">
                            {language === 'ar' ? 'الحد الأدنى للطلب' : 'Min Order'}
                          </p>
                          <p className="font-medium">
                            {priceList.minimum_order_value.toLocaleString()} IQD
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500">
                            {language === 'ar' ? 'نسبة الخصم' : 'Discount'}
                          </p>
                          <p className="font-medium">{priceList.discount_percentage}%</p>
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <p className="text-xs text-gray-500">
                            {language === 'ar' ? 'عدد المنتجات' : 'Products'}
                          </p>
                          <p className="font-medium">{priceList.product_count}</p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500">
                            {language === 'ar' ? 'فئات العملاء' : 'Categories'}
                          </p>
                          <p className="font-medium">{priceList.customer_categories.length}</p>
                        </div>
                      </div>

                      <div className="flex items-center justify-between pt-2">
                        <span className="text-xs text-gray-500">
                          {language === 'ar' ? 'تاريخ الإنشاء:' : 'Created:'} {new Date(priceList.created_at).toLocaleDateString()}
                        </span>
                        <div className="flex space-x-2">
                          <Button size="sm" variant="outline">
                            {language === 'ar' ? 'تحرير' : 'Edit'}
                          </Button>
                          <Button size="sm">
                            {language === 'ar' ? 'عرض المنتجات' : 'View Products'}
                          </Button>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        </div>
      )}

      {/* Negotiations Tab */}
      {selectedView === 'negotiations' && (
        <div className="space-y-6">
          {/* Filters */}
          <Card>
            <CardContent className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">
                    {language === 'ar' ? 'البحث' : 'Search'}
                  </label>
                  <div className="relative">
                    <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                    <Input
                      placeholder={language === 'ar' ? 'اسم العميل أو المنتج' : 'Customer or product name'}
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-2">
                    {language === 'ar' ? 'حالة المفاوضة' : 'Status'}
                  </label>
                  <select
                    value={negotiationFilter}
                    onChange={(e) => setNegotiationFilter(e.target.value)}
                    className="w-full p-2 border rounded-lg bg-white"
                  >
                    <option value="all">{language === 'ar' ? 'جميع الحالات' : 'All Statuses'}</option>
                    {negotiationStatuses.map(status => (
                      <option key={status.value} value={status.value}>
                        {status.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="flex items-end">
                  <Button 
                    onClick={loadNegotiations}
                    variant="outline"
                  >
                    <Filter className="w-4 h-4 mr-2" />
                    {language === 'ar' ? 'تطبيق المرشحات' : 'Apply Filters'}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Negotiations List */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>
                  {language === 'ar' ? 'طلبات التفاوض على الأسعار' : 'Price Negotiation Requests'}
                  <Badge className="ml-2 bg-blue-100 text-blue-800">
                    {filteredNegotiations.length}
                  </Badge>
                </span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {filteredNegotiations.map((negotiation) => {
                  const statusInfo = getNegotiationStatusInfo(negotiation.status)
                  const StatusIcon = statusInfo.icon
                  
                  return (
                    <div key={negotiation.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-4 mb-3">
                            <div>
                              <h3 className="font-semibold text-lg">
                                {negotiation.customer.name}
                              </h3>
                              <p className="text-sm text-gray-600">
                                {negotiation.product.name} ({negotiation.product.sku})
                              </p>
                            </div>
                            <Badge className={`${statusInfo.color} border-0`}>
                              <StatusIcon className="w-3 h-3 mr-1" />
                              {statusInfo.label}
                            </Badge>
                          </div>
                          
                          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                            <div>
                              <p className="text-xs text-gray-500">
                                {language === 'ar' ? 'السعر الحالي' : 'Current Price'}
                              </p>
                              <p className="font-medium">
                                {negotiation.current_price.toLocaleString()} IQD
                              </p>
                            </div>
                            <div>
                              <p className="text-xs text-gray-500">
                                {language === 'ar' ? 'السعر المطلوب' : 'Requested Price'}
                              </p>
                              <p className="font-medium text-blue-600">
                                {negotiation.requested_price.toLocaleString()} IQD
                              </p>
                            </div>
                            <div>
                              <p className="text-xs text-gray-500">
                                {language === 'ar' ? 'نسبة الخصم' : 'Discount'}
                              </p>
                              <p className="font-medium text-green-600">
                                {negotiation.discount_requested.toFixed(1)}%
                              </p>
                            </div>
                            <div>
                              <p className="text-xs text-gray-500">
                                {language === 'ar' ? 'الكمية' : 'Quantity'}
                              </p>
                              <p className="font-medium">{negotiation.quantity}</p>
                            </div>
                            <div>
                              <p className="text-xs text-gray-500">
                                {language === 'ar' ? 'تاريخ الانتهاء' : 'Valid Until'}
                              </p>
                              <p className="font-medium">
                                {new Date(negotiation.valid_until).toLocaleDateString()}
                              </p>
                            </div>
                          </div>
                          
                          {negotiation.justification && (
                            <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                              <p className="text-sm text-gray-700">
                                <strong>{language === 'ar' ? 'المبرر:' : 'Justification:'}</strong> {negotiation.justification}
                              </p>
                            </div>
                          )}
                        </div>
                        
                        <div className="flex items-center space-x-2 ml-4">
                          {negotiation.status === 'pending' && (
                            <>
                              <Button size="sm" variant="outline" className="text-green-600 border-green-600">
                                {language === 'ar' ? 'قبول' : 'Approve'}
                              </Button>
                              <Button size="sm" variant="outline" className="text-red-600 border-red-600">
                                {language === 'ar' ? 'رفض' : 'Reject'}
                              </Button>
                            </>
                          )}
                          <Button size="sm" variant="outline">
                            {language === 'ar' ? 'التفاصيل' : 'Details'}
                          </Button>
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="fixed bottom-4 right-4 bg-red-50 border border-red-200 p-4 rounded-lg shadow-lg">
          <div className="flex items-center">
            <XCircle className="w-5 h-5 text-red-600 mr-2" />
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