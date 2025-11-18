import React, { useState, useEffect, useRef } from 'react'
import { 
  MapPin, Users, AlertTriangle, Shield, Navigation, 
  Clock, DollarSign, Phone, Battery, Zap, Target,
  TrendingUp, Activity, AlertCircle, CheckCircle
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { useLanguageStore } from '@/stores/languageStore'
import { useDynamicTranslations } from '@/lib/dynamicTranslations'
import api from '@/lib/api'

interface SalespersonTracking {
  salesperson_id: number
  name: string
  phone: string
  current_location: {
    latitude: number | null
    longitude: number | null
    accuracy: number | null
    speed: number
    timestamp: string | null
  }
  status: string
  battery_level: number
  time_since_update: number | null
  active_transfers: number
  today_amount: number
  recent_alerts: number
  route_efficiency: number
  is_moving: boolean
}

interface GPSAlert {
  id: number
  salesperson_id: number
  salesperson_name: string
  alert_type: string
  severity: string
  description: string
  location: {
    latitude: number
    longitude: number
  }
  created_at: string
  time_ago: number
}

export default function GPSTracking() {
  const { language } = useLanguageStore()
  const { t } = useDynamicTranslations(language)
  
  // State Management
  const [trackingData, setTrackingData] = useState<SalespersonTracking[]>([])
  const [alerts, setAlerts] = useState<GPSAlert[]>([])
  const [selectedSalesperson, setSelectedSalesperson] = useState<SalespersonTracking | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [showMap, setShowMap] = useState(false)
  
  // Dashboard Stats
  const [dashboardStats, setDashboardStats] = useState({
    total_salespersons: 0,
    active_count: 0,
    offline_count: 0,
    total_today_amount: 0,
    total_active_transfers: 0,
    last_updated: ''
  })
  
  const refreshIntervalRef = useRef<NodeJS.Timeout | null>(null)

  useEffect(() => {
    loadTrackingData()
    loadAlerts()
    
    if (autoRefresh) {
      refreshIntervalRef.current = setInterval(() => {
        loadTrackingData()
        loadAlerts()
      }, 30000) // Update every 30 seconds
    }
    
    return () => {
      if (refreshIntervalRef.current) {
        clearInterval(refreshIntervalRef.current)
      }
    }
  }, [autoRefresh])

  const loadTrackingData = async () => {
    try {
      setLoading(true)
      const response = await api.get('/api/gps/gps/tracking/live')
      setTrackingData(response.data.tracking_data || [])
      setDashboardStats({
        total_salespersons: response.data.total_salespersons || 0,
        active_count: response.data.active_count || 0,
        offline_count: response.data.offline_count || 0,
        total_today_amount: response.data.total_today_amount || 0,
        total_active_transfers: response.data.total_active_transfers || 0,
        last_updated: response.data.last_updated || ''
      })
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load tracking data')
    } finally {
      setLoading(false)
    }
  }

  const loadAlerts = async () => {
    try {
      const response = await api.get('/api/gps/gps/alerts/active')
      setAlerts(response.data.alerts || [])
    } catch (err) {
      console.error('Failed to load alerts:', err)
    }
  }

  const triggerEmergencyAlert = async (salespersonId: number) => {
    try {
      const salesperson = trackingData.find(s => s.salesperson_id === salespersonId)
      if (!salesperson || !salesperson.current_location.latitude) {
        throw new Error('Location not available')
      }
      
      const response = await api.post('/api/gps/gps/emergency/trigger', {
        salesperson_id: salespersonId,
        location: {
          latitude: salesperson.current_location.latitude,
          longitude: salesperson.current_location.longitude
        },
        message: `Emergency alert triggered for ${salesperson.name}`
      })
      
      // Reload data to reflect emergency status
      loadTrackingData()
      loadAlerts()
      
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to trigger emergency alert')
    }
  }

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active':
        return 'bg-green-100 text-green-800'
      case 'inactive':
        return 'bg-yellow-100 text-yellow-800'
      case 'offline':
        return 'bg-red-100 text-red-800'
      case 'suspicious':
        return 'bg-orange-100 text-orange-800'
      case 'emergency':
        return 'bg-red-100 text-red-800 animate-pulse'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active':
        return <CheckCircle className="w-4 h-4" />
      case 'inactive':
        return <Clock className="w-4 h-4" />
      case 'offline':
        return <AlertCircle className="w-4 h-4" />
      case 'suspicious':
        return <AlertTriangle className="w-4 h-4" />
      case 'emergency':
        return <Shield className="w-4 h-4" />
      default:
        return <Activity className="w-4 h-4" />
    }
  }

  const getAlertSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical':
        return 'bg-red-500 text-white'
      case 'high':
        return 'bg-orange-500 text-white'
      case 'medium':
        return 'bg-yellow-500 text-white'
      case 'low':
        return 'bg-blue-500 text-white'
      default:
        return 'bg-gray-500 text-white'
    }
  }

  const formatTimeAgo = (timeInMinutes: number) => {
    if (timeInMinutes < 1) return language === 'ar' ? 'الآن' : 'Now'
    if (timeInMinutes < 60) return `${Math.floor(timeInMinutes)}${language === 'ar' ? 'د' : 'm'}`
    const hours = Math.floor(timeInMinutes / 60)
    return `${hours}${language === 'ar' ? 'س' : 'h'}`
  }

  const criticalAlerts = alerts.filter(a => a.severity === 'critical')
  const highAlerts = alerts.filter(a => a.severity === 'high')

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center">
              <MapPin className="w-8 h-8 mr-3 text-blue-600" />
              {language === 'ar' ? 'تتبع GPS للمسافرين' : 'GPS Tracking - Travel Salespersons'}
            </h1>
            <p className="text-gray-600 mt-2">
              {language === 'ar' 
                ? 'تتبع مباشر لـ 12 بائع متنقل يتعاملون مع 35,000 دولار أسبوعياً'
                : 'Real-time tracking for 12 travel salespersons handling $35K weekly'
              }
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${autoRefresh ? 'bg-green-500' : 'bg-gray-400'}`}></div>
              <span className="text-sm text-gray-600">
                {autoRefresh ? (language === 'ar' ? 'تحديث تلقائي' : 'Auto Refresh') : (language === 'ar' ? 'يدوي' : 'Manual')}
              </span>
            </div>
            <Button
              variant="outline"
              onClick={() => setAutoRefresh(!autoRefresh)}
            >
              {autoRefresh ? (language === 'ar' ? 'إيقاف التحديث' : 'Stop Auto') : (language === 'ar' ? 'تشغيل التحديث' : 'Start Auto')}
            </Button>
            <Button
              onClick={() => setShowMap(!showMap)}
              className="bg-blue-600 hover:bg-blue-700"
            >
              <MapPin className="w-4 h-4 mr-2" />
              {showMap ? (language === 'ar' ? 'إخفاء الخريطة' : 'Hide Map') : (language === 'ar' ? 'عرض الخريطة' : 'Show Map')}
            </Button>
          </div>
        </div>
      </div>

      {/* Critical Alerts Bar */}
      {criticalAlerts.length > 0 && (
        <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <Shield className="w-5 h-5 text-red-600 mr-2" />
            <span className="font-semibold text-red-800">
              {language === 'ar' ? 'تنبيهات حرجة' : 'Critical Alerts'}
            </span>
            <Badge className="ml-2 bg-red-500 text-white">
              {criticalAlerts.length}
            </Badge>
          </div>
          <div className="mt-2 space-y-1">
            {criticalAlerts.slice(0, 3).map(alert => (
              <div key={alert.id} className="text-sm text-red-700">
                <strong>{alert.salesperson_name}:</strong> {alert.description}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Dashboard Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">
                  {language === 'ar' ? 'إجمالي البائعين' : 'Total Salespersons'}
                </p>
                <p className="text-2xl font-bold text-gray-900">{dashboardStats.total_salespersons}</p>
              </div>
              <Users className="w-8 h-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">
                  {language === 'ar' ? 'نشط' : 'Active'}
                </p>
                <p className="text-2xl font-bold text-green-600">{dashboardStats.active_count}</p>
              </div>
              <CheckCircle className="w-8 h-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">
                  {language === 'ar' ? 'غير متصل' : 'Offline'}
                </p>
                <p className="text-2xl font-bold text-red-600">{dashboardStats.offline_count}</p>
              </div>
              <AlertCircle className="w-8 h-8 text-red-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">
                  {language === 'ar' ? 'مبلغ اليوم' : "Today's Amount"}
                </p>
                <p className="text-2xl font-bold text-purple-600">
                  ${dashboardStats.total_today_amount.toLocaleString()}
                </p>
              </div>
              <DollarSign className="w-8 h-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">
                  {language === 'ar' ? 'حوالات نشطة' : 'Active Transfers'}
                </p>
                <p className="text-2xl font-bold text-orange-600">{dashboardStats.total_active_transfers}</p>
              </div>
              <TrendingUp className="w-8 h-8 text-orange-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Live Tracking Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6 mb-8">
        {trackingData.map((salesperson) => (
          <Card key={salesperson.salesperson_id} className="relative overflow-hidden">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-semibold text-lg">{salesperson.name}</h3>
                  <p className="text-sm text-gray-600">{salesperson.phone}</p>
                </div>
                <div className="flex items-center space-x-2">
                  <Badge className={getStatusColor(salesperson.status)}>
                    {getStatusIcon(salesperson.status)}
                    <span className="ml-1 capitalize">{salesperson.status}</span>
                  </Badge>
                  {salesperson.recent_alerts > 0 && (
                    <Badge variant="destructive">
                      {salesperson.recent_alerts}
                    </Badge>
                  )}
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {/* Location & Status */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-xs text-gray-500">
                      {language === 'ar' ? 'آخر تحديث' : 'Last Update'}
                    </p>
                    <p className="font-medium">
                      {salesperson.time_since_update !== null 
                        ? formatTimeAgo(salesperson.time_since_update)
                        : language === 'ar' ? 'غير متاح' : 'N/A'
                      }
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">
                      {language === 'ar' ? 'البطارية' : 'Battery'}
                    </p>
                    <div className="flex items-center space-x-2">
                      <Battery className={`w-4 h-4 ${salesperson.battery_level < 20 ? 'text-red-500' : 'text-green-500'}`} />
                      <span className="font-medium">{salesperson.battery_level}%</span>
                    </div>
                  </div>
                </div>

                {/* Movement & Performance */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-xs text-gray-500">
                      {language === 'ar' ? 'الحركة' : 'Movement'}
                    </p>
                    <div className="flex items-center space-x-2">
                      <Activity className={`w-4 h-4 ${salesperson.is_moving ? 'text-green-500' : 'text-gray-400'}`} />
                      <span className="font-medium">
                        {salesperson.is_moving 
                          ? `${salesperson.current_location.speed} km/h`
                          : language === 'ar' ? 'متوقف' : 'Stopped'
                        }
                      </span>
                    </div>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">
                      {language === 'ar' ? 'الكفاءة' : 'Efficiency'}
                    </p>
                    <div className="flex items-center space-x-2">
                      <Target className="w-4 h-4 text-blue-500" />
                      <span className="font-medium">{salesperson.route_efficiency.toFixed(1)}%</span>
                    </div>
                  </div>
                </div>

                {/* Today's Performance */}
                <div className="bg-gray-50 rounded-lg p-3">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-xs text-gray-500">
                        {language === 'ar' ? 'مبلغ اليوم' : "Today's Amount"}
                      </p>
                      <p className="font-bold text-green-600">
                        ${salesperson.today_amount.toLocaleString()}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">
                        {language === 'ar' ? 'حوالات نشطة' : 'Active Transfers'}
                      </p>
                      <p className="font-bold text-blue-600">
                        {salesperson.active_transfers}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex items-center space-x-2 pt-2">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => setSelectedSalesperson(salesperson)}
                  >
                    <Navigation className="w-4 h-4 mr-1" />
                    {language === 'ar' ? 'التفاصيل' : 'Details'}
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => {
                      if (salesperson.phone) {
                        window.open(`tel:${salesperson.phone}`, '_blank')
                      }
                    }}
                  >
                    <Phone className="w-4 h-4 mr-1" />
                    {language === 'ar' ? 'اتصال' : 'Call'}
                  </Button>
                  {salesperson.status !== 'emergency' && (
                    <Button
                      size="sm"
                      variant="destructive"
                      onClick={() => triggerEmergencyAlert(salesperson.salesperson_id)}
                    >
                      <Shield className="w-4 h-4 mr-1" />
                      {language === 'ar' ? 'طوارئ' : 'Emergency'}
                    </Button>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Active Alerts */}
      {alerts.length > 0 && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center">
              <AlertTriangle className="w-5 h-5 mr-2 text-orange-500" />
              {language === 'ar' ? 'التنبيهات النشطة' : 'Active Alerts'}
              <Badge className="ml-2 bg-orange-100 text-orange-800">
                {alerts.length}
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {alerts.slice(0, 10).map((alert) => (
                <div key={alert.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <Badge className={getAlertSeverityColor(alert.severity)}>
                      {alert.severity.toUpperCase()}
                    </Badge>
                    <div>
                      <p className="font-medium">{alert.salesperson_name}</p>
                      <p className="text-sm text-gray-600">{alert.description}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium text-gray-900">
                      {alert.alert_type.replace('_', ' ').toUpperCase()}
                    </p>
                    <p className="text-xs text-gray-500">
                      {formatTimeAgo(alert.time_ago)} {language === 'ar' ? 'مضت' : 'ago'}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Loading State */}
      {loading && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-xl">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-center text-gray-600">
              {language === 'ar' ? 'جاري التحميل...' : 'Loading GPS data...'}
            </p>
          </div>
        </div>
      )}

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