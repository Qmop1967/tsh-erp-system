import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card'
import { 
  Users, 
  Package, 
  ShoppingCart, 
  TrendingUp, 
  Building, 
  Warehouse,
  AlertTriangle,
  DollarSign
} from 'lucide-react'

// Mock data for dashboard
const mockStats = {
  totalUsers: 24,
  totalItems: 1247,
  totalOrders: 156,
  totalRevenue: 89450,
  totalBranches: 5,
  totalWarehouses: 12,
  lowStockItems: 8,
  pendingOrders: 23
}

export function DashboardPage() {
  const [stats] = useState(mockStats)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Simulate loading
    const timer = setTimeout(() => {
      setLoading(false)
    }, 1000)
    return () => clearTimeout(timer)
  }, [])

  const statCards = [
    {
      title: 'Total Users',
      value: stats.totalUsers,
      icon: Users,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      change: '+12%'
    },
    {
      title: 'Total Items',
      value: stats.totalItems,
      icon: Package,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
      change: '+5%'
    },
    {
      title: 'Total Orders',
      value: stats.totalOrders,
      icon: ShoppingCart,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
      change: '+18%'
    },
    {
      title: 'Revenue (USD)',
      value: `$${stats.totalRevenue.toLocaleString()}`,
      icon: DollarSign,
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-50',
      change: '+22%'
    },
    {
      title: 'Branches',
      value: stats.totalBranches,
      icon: Building,
      color: 'text-indigo-600',
      bgColor: 'bg-indigo-50',
      change: 'No change'
    },
    {
      title: 'Warehouses',
      value: stats.totalWarehouses,
      icon: Warehouse,
      color: 'text-teal-600',
      bgColor: 'bg-teal-50',
      change: '+1'
    },
    {
      title: 'Low Stock Items',
      value: stats.lowStockItems,
      icon: AlertTriangle,
      color: 'text-red-600',
      bgColor: 'bg-red-50',
      change: 'Needs attention'
    },
    {
      title: 'Pending Orders',
      value: stats.pendingOrders,
      icon: TrendingUp,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
      change: '+7%'
    }
  ]

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
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600">Welcome to TSH ERP System</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {statCards.map((card, index) => (
          <Card key={index} className="hover:shadow-md transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                {card.title}
              </CardTitle>
              <div className={`p-2 rounded-lg ${card.bgColor}`}>
                <card.icon className={`h-4 w-4 ${card.color}`} />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-gray-900">{card.value}</div>
              <p className="text-xs text-gray-500 mt-1">{card.change}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>Latest system activities</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[
                'New user registered: John Doe',
                'Item added to inventory: Dell Laptop',
                'Order completed: #ORD-001',
                'Low stock alert: iPhone 13 Pro',
                'New vendor added: Tech Supplier Co.'
              ].map((activity, index) => (
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
            <CardTitle>System Status</CardTitle>
            <CardDescription>Current system health</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-700">Database</span>
                <span className="text-sm text-green-600 font-medium">Online</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-700">API Server</span>
                <span className="text-sm text-green-600 font-medium">Running</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-700">Zoho Integration</span>
                <span className="text-sm text-green-600 font-medium">Connected</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-700">Backup Status</span>
                <span className="text-sm text-green-600 font-medium">Up to date</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
