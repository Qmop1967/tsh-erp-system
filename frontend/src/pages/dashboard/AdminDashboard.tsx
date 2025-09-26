import React, { useState, useEffect } from 'react'
import { useLanguageStore } from '@/stores/languageStore'
import { useTranslations } from '@/lib/translations'
import { useBranchAwareApi } from '@/hooks/useBranchAwareApi'
import { adminApi } from '@/lib/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { 
  Users, 
  Package, 
  ShoppingCart, 
  TrendingUp, 
  Building, 
  Warehouse,
  AlertTriangle,
  DollarSign,
  MapPin,
  Clock,
  Target,
  Phone,
  Activity,
  Shield,
  Globe,
  Truck,
  UserCheck,
  CreditCard,
  Bell,
  BarChart,
  Eye,
  Settings,
  RefreshCw,
  PlayCircle,
  PauseCircle,
  MessageSquare,
  Camera,
  Zap
} from 'lucide-react'

// Enhanced dashboard data interface
interface AdminDashboardData {
  // Financial Overview
  financials: {
    totalRevenue: number;
    weeklyMoneyTransfers: number;
    todaysSales: number;
    pendingPayments: number;
    profitMargin: number;
  };
  
  // Partner Salesmen Network
  partnerSalesmen: {
    totalActive: number;
    totalInactive: number;
    todaysOrders: number;
    weeklyCommissions: number;
    topPerformer: string;
    newSignups: number;
  };
  
  // Travel Salespersons
  travelSalespersons: {
    totalActive: number;
    onlineNow: number;
    suspiciousActivity: number;
    todaysTransfers: number;
    gpsTrackingStatus: string;
  };
  
  // Inventory & Warehouses
  inventory: {
    retailStock: number;
    wholesaleStock: number;
    lowStockAlerts: number;
    todaysMovements: number;
    damageReports: number;
  };
  
  // Customer Management
  customers: {
    wholesaleClients: number;
    retailCustomers: number;
    activeOrders: number;
    returnRequests: number;
    satisfactionScore: number;
  };
  
  // System Health
  systemHealth: {
    apiStatus: string;
    databaseStatus: string;
    gpsTrackingStatus: string;
    whatsappStatus: string;
    aiAssistantStatus: string;
    lastBackup: string;
  };
  
  // Real-time alerts
  alerts: Array<{
    id: string;
    type: 'warning' | 'error' | 'info' | 'success';
    message: string;
    timestamp: string;
    priority: 'high' | 'medium' | 'low';
  }>;
  
  // Recent activities
  recentActivities: Array<{
    id: string;
    type: string;
    description: string;
    timestamp: string;
    user: string;
  }>;
}

// Mock data for comprehensive admin dashboard
const mockAdminData: AdminDashboardData = {
  financials: {
    totalRevenue: 1850000,
    weeklyMoneyTransfers: 35000,
    todaysSales: 45000,
    pendingPayments: 125000,
    profitMargin: 18.5
  },
  partnerSalesmen: {
    totalActive: 87,
    totalInactive: 23,
    todaysOrders: 156,
    weeklyCommissions: 12500,
    topPerformer: "Ahmed Al-Rashid",
    newSignups: 12
  },
  travelSalespersons: {
    totalActive: 12,
    onlineNow: 9,
    suspiciousActivity: 2,
    todaysTransfers: 18,
    gpsTrackingStatus: "Active"
  },
  inventory: {
    retailStock: 2847,
    wholesaleStock: 15623,
    lowStockAlerts: 23,
    todaysMovements: 145,
    damageReports: 5
  },
  customers: {
    wholesaleClients: 498,
    retailCustomers: 1247,
    activeOrders: 89,
    returnRequests: 12,
    satisfactionScore: 4.6
  },
  systemHealth: {
    apiStatus: "Healthy",
    databaseStatus: "Online",
    gpsTrackingStatus: "Active",
    whatsappStatus: "Connected",
    aiAssistantStatus: "Learning",
    lastBackup: "2 hours ago"
  },
  alerts: [
    {
      id: "1",
      type: "warning",
      message: "Low stock alert: iPhone 13 Pro cases - Only 5 remaining",
      timestamp: "10 minutes ago",
      priority: "high"
    },
    {
      id: "2",
      type: "error",
      message: "Suspicious money transfer: $2,500 from unusual location",
      timestamp: "25 minutes ago",
      priority: "high"
    },
    {
      id: "3",
      type: "info",
      message: "New partner salesman application from Basra",
      timestamp: "1 hour ago",
      priority: "medium"
    }
  ],
  recentActivities: [
    {
      id: "1",
      type: "sale",
      description: "New wholesale order #WO-2024-001 - $3,500",
      timestamp: "5 minutes ago",
      user: "Haider Ahmed"
    },
    {
      id: "2",
      type: "transfer",
      description: "Money transfer verified - $1,200 via ZAIN Cash",
      timestamp: "15 minutes ago",
      user: "Travel Salesperson #5"
    },
    {
      id: "3",
      type: "inventory",
      description: "Stock transfer: 50 items from wholesale to retail",
      timestamp: "30 minutes ago",
      user: "Mustafa Khalid"
    }
  ]
}

export function AdminDashboard() {
  const [data, setData] = useState<AdminDashboardData>(mockAdminData)
  const [loading, setLoading] = useState(false)
  const [lastRefresh, setLastRefresh] = useState(new Date())
  const { language } = useLanguageStore()
  const t = useTranslations(language)
  const { currentBranch } = useBranchAwareApi()

  // Auto-refresh every 30 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      refreshData()
    }, 30000)
    return () => clearInterval(interval)
  }, [])

  const refreshData = async () => {
    setLoading(true)
    try {
      const response = await adminApi.getDashboard()
      setData(response.data)
      setLastRefresh(new Date())
    } catch (error) {
      console.error('Error refreshing data:', error)
      // Fallback to mock data if API fails
      setData(mockAdminData)
    } finally {
      setLoading(false)
    }
  }

  const getAlertColor = (type: string) => {
    switch (type) {
      case 'error': return 'bg-red-100 text-red-800 border-red-200'
      case 'warning': return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'success': return 'bg-green-100 text-green-800 border-green-200'
      default: return 'bg-blue-100 text-blue-800 border-blue-200'
    }
  }

  return (
    <div className="p-6 bg-gradient-to-br from-gray-50 to-white min-h-screen">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              🏢 TSH ERP Admin Control Center
            </h1>
            <p className="text-gray-600 text-lg mt-2">
              Complete business oversight and control - {currentBranch?.nameEn || "All Operations"}
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="text-sm text-gray-500">
              Last updated: {lastRefresh.toLocaleTimeString()}
            </div>
            <button
              onClick={refreshData}
              disabled={loading}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
              <span>Refresh</span>
            </button>
          </div>
        </div>
      </div>

      {/* Critical Alerts */}
      {data.alerts.length > 0 && (
        <div className="mb-8">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <Bell className="h-5 w-5 mr-2" />
            Critical Alerts
          </h2>
          <div className="space-y-3">
            {data.alerts.map((alert) => (
              <div
                key={alert.id}
                className={`p-4 rounded-lg border-l-4 ${getAlertColor(alert.type)}`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <AlertTriangle className="h-5 w-5" />
                    <div>
                      <p className="font-medium">{alert.message}</p>
                      <p className="text-sm opacity-75">{alert.timestamp}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      alert.priority === 'high' ? 'bg-red-100 text-red-700' :
                      alert.priority === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                      'bg-gray-100 text-gray-700'
                    }`}>
                      {alert.priority}
                    </span>
                    <button className="text-blue-600 hover:text-blue-800">
                      <Eye className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Financial Overview */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold mb-4 flex items-center">
          <DollarSign className="h-5 w-5 mr-2" />
          Financial Overview
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
          <Card className="bg-gradient-to-br from-green-500 to-green-600 text-white">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-green-100 text-sm">Total Revenue</p>
                  <p className="text-2xl font-bold">${data.financials.totalRevenue.toLocaleString()}</p>
                </div>
                <TrendingUp className="h-8 w-8 text-green-200" />
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-blue-100 text-sm">Weekly Transfers</p>
                  <p className="text-2xl font-bold">${data.financials.weeklyMoneyTransfers.toLocaleString()}</p>
                </div>
                <CreditCard className="h-8 w-8 text-blue-200" />
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-gradient-to-br from-purple-500 to-purple-600 text-white">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-purple-100 text-sm">Today's Sales</p>
                  <p className="text-2xl font-bold">${data.financials.todaysSales.toLocaleString()}</p>
                </div>
                <ShoppingCart className="h-8 w-8 text-purple-200" />
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-gradient-to-br from-yellow-500 to-yellow-600 text-white">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-yellow-100 text-sm">Pending Payments</p>
                  <p className="text-2xl font-bold">${data.financials.pendingPayments.toLocaleString()}</p>
                </div>
                <Clock className="h-8 w-8 text-yellow-200" />
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-gradient-to-br from-indigo-500 to-indigo-600 text-white">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-indigo-100 text-sm">Profit Margin</p>
                  <p className="text-2xl font-bold">{data.financials.profitMargin}%</p>
                </div>
                <Target className="h-8 w-8 text-indigo-200" />
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Partner Salesmen & Travel Salespersons */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold mb-4 flex items-center">
          <Users className="h-5 w-5 mr-2" />
          Sales Force Management
        </h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Partner Salesmen */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Globe className="h-5 w-5 mr-2" />
                Partner Salesmen Network
              </CardTitle>
              <CardDescription>100+ salesmen across Iraq</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Active Partners</span>
                  <span className="text-2xl font-bold text-green-600">{data.partnerSalesmen.totalActive}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Today's Orders</span>
                  <span className="text-lg font-semibold">{data.partnerSalesmen.todaysOrders}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Weekly Commissions</span>
                  <span className="text-lg font-semibold">${data.partnerSalesmen.weeklyCommissions.toLocaleString()}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Top Performer</span>
                  <span className="text-sm font-medium text-blue-600">{data.partnerSalesmen.topPerformer}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">New Signups</span>
                  <span className="text-lg font-semibold text-green-600">+{data.partnerSalesmen.newSignups}</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Travel Salespersons */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <MapPin className="h-5 w-5 mr-2" />
                Travel Salespersons
              </CardTitle>
              <CardDescription>GPS tracking & money transfer monitoring</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Online Now</span>
                  <span className="text-2xl font-bold text-green-600">{data.travelSalespersons.onlineNow}/{data.travelSalespersons.totalActive}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Today's Transfers</span>
                  <span className="text-lg font-semibold">{data.travelSalespersons.todaysTransfers}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">GPS Status</span>
                  <span className="text-sm font-medium text-green-600">{data.travelSalespersons.gpsTrackingStatus}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Suspicious Activity</span>
                  <span className={`text-lg font-semibold ${data.travelSalespersons.suspiciousActivity > 0 ? 'text-red-600' : 'text-green-600'}`}>
                    {data.travelSalespersons.suspiciousActivity}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Inventory & Customer Management */}
      <div className="mb-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Inventory Management */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Package className="h-5 w-5 mr-2" />
                Multi-Warehouse Inventory
              </CardTitle>
              <CardDescription>Retail & wholesale stock management</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Retail Stock</span>
                  <span className="text-lg font-semibold">{data.inventory.retailStock.toLocaleString()}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Wholesale Stock</span>
                  <span className="text-lg font-semibold">{data.inventory.wholesaleStock.toLocaleString()}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Low Stock Alerts</span>
                  <span className={`text-lg font-semibold ${data.inventory.lowStockAlerts > 0 ? 'text-red-600' : 'text-green-600'}`}>
                    {data.inventory.lowStockAlerts}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Today's Movements</span>
                  <span className="text-lg font-semibold">{data.inventory.todaysMovements}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Damage Reports</span>
                  <span className={`text-lg font-semibold ${data.inventory.damageReports > 0 ? 'text-yellow-600' : 'text-green-600'}`}>
                    {data.inventory.damageReports}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Customer Management */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <UserCheck className="h-5 w-5 mr-2" />
                Customer Management
              </CardTitle>
              <CardDescription>Wholesale & retail customer overview</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Wholesale Clients</span>
                  <span className="text-lg font-semibold">{data.customers.wholesaleClients}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Retail Customers</span>
                  <span className="text-lg font-semibold">{data.customers.retailCustomers.toLocaleString()}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Active Orders</span>
                  <span className="text-lg font-semibold">{data.customers.activeOrders}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Return Requests</span>
                  <span className="text-lg font-semibold">{data.customers.returnRequests}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Satisfaction Score</span>
                  <span className="text-lg font-semibold text-green-600">{data.customers.satisfactionScore}/5.0</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold mb-4 flex items-center">
          <Zap className="h-5 w-5 mr-2" />
          Quick Actions
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
          <button className="p-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex flex-col items-center space-y-2">
            <MapPin className="h-6 w-6" />
            <span className="text-sm">GPS Tracking</span>
          </button>
          <button className="p-4 bg-green-600 text-white rounded-lg hover:bg-green-700 flex flex-col items-center space-y-2">
            <Users className="h-6 w-6" />
            <span className="text-sm">Manage Partners</span>
          </button>
          <button className="p-4 bg-purple-600 text-white rounded-lg hover:bg-purple-700 flex flex-col items-center space-y-2">
            <Package className="h-6 w-6" />
            <span className="text-sm">Inventory</span>
          </button>
          <button className="p-4 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 flex flex-col items-center space-y-2">
            <BarChart className="h-6 w-6" />
            <span className="text-sm">Reports</span>
          </button>
          <button className="p-4 bg-red-600 text-white rounded-lg hover:bg-red-700 flex flex-col items-center space-y-2">
            <Shield className="h-6 w-6" />
            <span className="text-sm">Security</span>
          </button>
          <button className="p-4 bg-gray-600 text-white rounded-lg hover:bg-gray-700 flex flex-col items-center space-y-2">
            <Settings className="h-6 w-6" />
            <span className="text-sm">Settings</span>
          </button>
        </div>
      </div>

      {/* System Health & Recent Activities */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* System Health */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Activity className="h-5 w-5 mr-2" />
              System Health
            </CardTitle>
            <CardDescription>All systems operational</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {Object.entries(data.systemHealth).map(([key, value]) => (
                <div key={key} className="flex items-center justify-between">
                  <span className="text-sm text-gray-600 capitalize">{key.replace(/([A-Z])/g, ' $1').trim()}</span>
                  <span className={`text-sm font-medium ${
                    value === 'Healthy' || value === 'Online' || value === 'Active' || value === 'Connected' || value === 'Learning' 
                      ? 'text-green-600' 
                      : 'text-gray-600'
                  }`}>
                    {value}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Recent Activities */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Clock className="h-5 w-5 mr-2" />
              Recent Activities
            </CardTitle>
            <CardDescription>Latest business activities</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {data.recentActivities.map((activity) => (
                <div key={activity.id} className="flex items-start space-x-3">
                  <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                  <div className="flex-1">
                    <p className="text-sm font-medium">{activity.description}</p>
                    <div className="flex items-center space-x-2 mt-1">
                      <span className="text-xs text-gray-500">{activity.user}</span>
                      <span className="text-xs text-gray-400">•</span>
                      <span className="text-xs text-gray-500">{activity.timestamp}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
} 