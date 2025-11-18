import { useQuery } from 'react-query'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { 
  Users, 
  Building, 
  Package, 
  DollarSign,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  Clock
} from 'lucide-react'
import { formatCurrency } from '@/lib/utils'

// Mock data - replace with actual API calls
const dashboardStats = {
  totalUsers: 45,
  totalBranches: 8,
  totalItems: 1250,
  totalRevenue: 125000,
  recentMigrations: [
    { id: 1, name: 'Items Migration', status: 'COMPLETED', date: '2024-01-15' },
    { id: 2, name: 'Customers Migration', status: 'IN_PROGRESS', date: '2024-01-16' },
    { id: 3, name: 'Vendors Migration', status: 'PENDING', date: '2024-01-17' },
  ],
  lowStockItems: [
    { id: 1, name: 'Laptop Dell XPS', currentStock: 5, reorderLevel: 10 },
    { id: 2, name: 'iPhone 15 Pro', currentStock: 2, reorderLevel: 5 },
    { id: 3, name: 'Samsung Monitor', currentStock: 1, reorderLevel: 3 },
  ]
}

export function DashboardPage() {
  // In a real app, you would fetch this data from your API
  const { data: stats, isLoading } = useQuery('dashboard-stats', 
    () => Promise.resolve(dashboardStats),
    { staleTime: 5 * 60 * 1000 }
  )

  if (isLoading) {
    return (
      <div className="animate-pulse">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="bg-gray-200 rounded-lg h-32"></div>
          ))}
        </div>
      </div>
    )
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'COMPLETED':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'IN_PROGRESS':
        return <Clock className="h-4 w-4 text-blue-500" />
      case 'PENDING':
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />
      default:
        return <Clock className="h-4 w-4 text-gray-500" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'COMPLETED':
        return 'bg-green-100 text-green-800'
      case 'IN_PROGRESS':
        return 'bg-blue-100 text-blue-800'
      case 'PENDING':
        return 'bg-yellow-100 text-yellow-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          Welcome back! Here's an overview of your TSH ERP system.
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Users</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.totalUsers}</div>
            <p className="text-xs text-muted-foreground">
              +2 from last month
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Branches</CardTitle>
            <Building className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.totalBranches}</div>
            <p className="text-xs text-muted-foreground">
              Across Iraq
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Inventory Items</CardTitle>
            <Package className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.totalItems}</div>
            <p className="text-xs text-muted-foreground">
              +15% from last month
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Revenue</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatCurrency(stats?.totalRevenue || 0, 'USD')}
            </div>
            <p className="text-xs text-muted-foreground">
              <TrendingUp className="inline h-3 w-3 mr-1" />
              +8% from last month
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Migrations */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Migrations</CardTitle>
            <CardDescription>
              Latest data migration activities
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {stats?.recentMigrations.map((migration) => (
                <div
                  key={migration.id}
                  className="flex items-center justify-between p-3 border rounded-lg"
                >
                  <div className="flex items-center space-x-3">
                    {getStatusIcon(migration.status)}
                    <div>
                      <p className="font-medium text-sm">{migration.name}</p>
                      <p className="text-xs text-gray-500">{migration.date}</p>
                    </div>
                  </div>
                  <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor(migration.status)}`}>
                    {migration.status}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Low Stock Alert */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <AlertTriangle className="h-5 w-5 text-yellow-500 mr-2" />
              Low Stock Items
            </CardTitle>
            <CardDescription>
              Items that need restocking
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {stats?.lowStockItems.map((item) => (
                <div
                  key={item.id}
                  className="flex items-center justify-between p-3 border rounded-lg"
                >
                  <div>
                    <p className="font-medium text-sm">{item.name}</p>
                    <p className="text-xs text-gray-500">
                      Current: {item.currentStock} | Reorder: {item.reorderLevel}
                    </p>
                  </div>
                  <div className="text-right">
                    <span className="text-sm font-medium text-red-600">
                      {item.currentStock} left
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>
            Common tasks and shortcuts
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button className="p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors text-center">
              <Users className="h-8 w-8 mx-auto mb-2 text-gray-400" />
              <p className="font-medium">Add New User</p>
              <p className="text-sm text-gray-500">Create user account</p>
            </button>
            
            <button className="p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-green-500 hover:bg-green-50 transition-colors text-center">
              <Package className="h-8 w-8 mx-auto mb-2 text-gray-400" />
              <p className="font-medium">Add New Item</p>
              <p className="text-sm text-gray-500">Add inventory item</p>
            </button>
            
            <button className="p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-purple-500 hover:bg-purple-50 transition-colors text-center">
              <Building className="h-8 w-8 mx-auto mb-2 text-gray-400" />
              <p className="font-medium">Start Migration</p>
              <p className="text-sm text-gray-500">Import from Zoho</p>
            </button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
