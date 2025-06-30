import { useState } from 'react'
import { useLanguageStore } from '@/stores/languageStore'
import { useTranslations } from '@/lib/translations'
import { useBranchAwareApi } from '@/hooks/useBranchAwareApi'
import { dashboardApi } from '@/lib/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card'
import { 
  Users, 
  Package, 
  ShoppingCart, 
  TrendingUp, 
  Building, 
  Warehouse,
  AlertTriangle,
  DollarSign,
  RefreshCw
} from 'lucide-react'

// Define dashboard stats type
interface DashboardStats {
  totalUsers: number;
  totalItems: number;
  totalOrders: number;
  totalRevenue: number;
  totalBranches: number;
  totalWarehouses: number;
  lowStockItems: number;
  pendingOrders: number;
  monthlyRevenue: number[];
  recentActivities: string[];
}

// Mock data for dashboard (fallback)
const mockStats: DashboardStats = {
  totalUsers: 24,
  totalItems: 1247,
  totalOrders: 156,
  totalRevenue: 89450,
  totalBranches: 5,
  totalWarehouses: 12,
  lowStockItems: 8,
  pendingOrders: 23,
  monthlyRevenue: [65000, 72000, 68000, 81000, 89450],
  recentActivities: [
    'New user registered: John Doe',
    'Item added to inventory: Dell Laptop',
    'Order completed: #ORD-001',
    'Low stock alert: iPhone 13 Pro',
    'New vendor added: Tech Supplier Co.'
  ]
}

export function DashboardPage() {
  const [stats, setStats] = useState(mockStats)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const { language } = useLanguageStore()
  const t = useTranslations(language)
  const { currentBranch, getBranchParams, useBranchChangeEffect } = useBranchAwareApi()

  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      setError(null)
      
      // Get branch-aware parameters
      const params = getBranchParams()
      
      // Try to fetch real data, fallback to mock data
      try {
        const response = await dashboardApi.getStats(params)
        setStats(response.data)
      } catch (apiError) {
        console.warn('API not available, using mock data:', apiError)
        // Use mock data but filter by branch if available
        setStats({
          ...mockStats,
          // Adjust some stats based on current branch for demo
          totalBranches: currentBranch ? 1 : mockStats.totalBranches,
          totalWarehouses: currentBranch ? Math.floor(mockStats.totalWarehouses / 3) : mockStats.totalWarehouses,
        })
      }
    } catch (err) {
      console.error('Error fetching dashboard data:', err)
      setError('Failed to fetch dashboard data')
      setStats(mockStats)
    } finally {
      setLoading(false)
    }
  }

  // Fetch data when component mounts or branch changes
  useBranchChangeEffect(() => {
    fetchDashboardData()
  })

  const statCards = [
    {
      titleKey: 'totalUsers',
      value: stats.totalUsers,
      icon: Users,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      change: '+12%'
    },
    {
      titleKey: 'totalItems',
      value: stats.totalItems,
      icon: Package,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
      change: '+5%'
    },
    {
      titleKey: 'totalOrders',
      value: stats.totalOrders,
      icon: ShoppingCart,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
      change: '+18%'
    },
    {
      titleKey: 'revenue',
      value: `$${stats.totalRevenue.toLocaleString()}`,
      icon: DollarSign,
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-50',
      change: '+22%'
    },
    {
      titleKey: 'branches',
      value: stats.totalBranches,
      icon: Building,
      color: 'text-indigo-600',
      bgColor: 'bg-indigo-50',
      change: t.noChange
    },
    {
      titleKey: 'warehouses',
      value: stats.totalWarehouses,
      icon: Warehouse,
      color: 'text-teal-600',
      bgColor: 'bg-teal-50',
      change: '+1'
    },
    {
      titleKey: 'lowStockItems',
      value: stats.lowStockItems,
      icon: AlertTriangle,
      color: 'text-red-600',
      bgColor: 'bg-red-50',
      change: t.needsAttention
    },
    {
      titleKey: 'pendingOrders',
      value: stats.pendingOrders,
      icon: TrendingUp,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
      change: '+7%'
    }
  ] as const

  if (loading) {
    return (
      <div className="p-8">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-64 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[...Array(8)].map((_, i) => (
              <div key={i} className="bg-gray-200 h-32 rounded-lg"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="p-8 bg-gradient-to-br from-gray-50 to-white min-h-full">
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
              {t.dashboard}
            </h1>
            <p className="text-gray-600 text-lg mt-2">
              {currentBranch 
                ? `${t.welcomeToSystem} - ${currentBranch.nameEn}`
                : t.welcomeToSystem
              }
            </p>
          </div>
          {error && (
            <div className="flex items-center space-x-2 text-red-600 bg-red-100 px-4 py-2 rounded-lg">
              <AlertTriangle className="h-4 w-4" />
              <span className="text-sm">{error}</span>
            </div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {statCards.map((card, index) => (
          <Card key={index} className="group hover:shadow-xl transition-all duration-300 hover:scale-105 border-0 shadow-md bg-white">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-600 group-hover:text-gray-800 transition-colors">
                {t[card.titleKey]}
              </CardTitle>
              <div className={`p-3 rounded-xl ${card.bgColor} group-hover:scale-110 transition-transform shadow-sm`}>
                <card.icon className={`h-5 w-5 ${card.color}`} />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-gray-900 mb-2">{card.value}</div>
              <div className="flex items-center space-x-2">
                <span className={`text-xs px-2 py-1 rounded-full ${
                  card.change.includes('+') ? 'bg-green-100 text-green-700' : 
                  card.change.includes('-') ? 'bg-red-100 text-red-700' : 
                  'bg-gray-100 text-gray-700'
                }`}>
                  {card.change}
                </span>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>{t.recentActivity}</CardTitle>
            <CardDescription>{t.latestSystemActivities}</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {stats.recentActivities.map((activity, index) => (
                <div key={index} className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                  <span className="text-sm text-gray-700">{activity}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>{t.systemStatus}</CardTitle>
            <CardDescription>{t.currentSystemHealth}</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-700">{t.database}</span>
                <span className="text-sm text-green-600 font-medium">{t.online}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-700">{t.apiServer}</span>
                <span className="text-sm text-green-600 font-medium">{t.running}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-700">{t.zohoIntegration}</span>
                <span className="text-sm text-green-600 font-medium">{t.connected}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-700">{t.backupStatus}</span>
                <span className="text-sm text-green-600 font-medium">{t.upToDate}</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
