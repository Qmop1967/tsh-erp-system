import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card'
import { Button } from '../../components/ui/button'
import { 
  Package,
  DollarSign,
  TrendingUp,
  Tag,
  BarChart3,
  Plus,
  Eye,
  Edit,
  Filter,
  Search,
  ArrowUpRight,
  Zap,
  Target,
  Globe,
  Clock,
  Star
} from 'lucide-react'

interface Category {
  id: number
  code: string
  name_ar: string
  name_en: string
  is_active: boolean
  item_count?: number
}

interface Item {
  id: number
  code: string
  name_ar: string
  name_en: string
  category_id?: number
  brand?: string
  cost_price_usd: number
  selling_price_usd: number
  reorder_level: number
  is_active: boolean
}

interface DashboardStats {
  totalItems: number
  totalCategories: number
  totalValue: number
  averageMargin: number
  lowStockItems: number
  topCategories: Array<{category: string, count: number, value: number}>
  recentItems: Item[]
  profitableItems: Item[]
}

export function ItemsDashboard() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState<DashboardStats>({
    totalItems: 0,
    totalCategories: 0,
    totalValue: 0,
    averageMargin: 0,
    lowStockItems: 0,
    topCategories: [],
    recentItems: [],
    profitableItems: []
  })

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      // Fetch items and categories data
      const [itemsResponse, categoriesResponse] = await Promise.all([
        fetch('/api/migration/items/'),
        fetch('/api/migration/categories/')
      ])

      let itemsData = []
      let categoriesData = []

      if (itemsResponse.ok) {
        itemsData = await itemsResponse.json()
      }

      if (categoriesResponse.ok) {
        categoriesData = await categoriesResponse.json()
      }

      // Calculate dashboard statistics
      const totalItems = itemsData.filter((item: Item) => item.is_active).length
      const totalCategories = categoriesData.filter((cat: Category) => cat.is_active).length
      const totalValue = itemsData.reduce((sum: number, item: Item) => sum + item.cost_price_usd, 0)
      const averageMargin = itemsData.length > 0 
        ? itemsData.reduce((sum: number, item: Item) => sum + (item.selling_price_usd - item.cost_price_usd), 0) / itemsData.length 
        : 0
      const lowStockItems = itemsData.filter((item: Item) => item.reorder_level > 0).length

      // Calculate category statistics
      const categoryStats = categoriesData.map((cat: Category) => {
        const categoryItems = itemsData.filter((item: Item) => item.category_id === cat.id)
        return {
          category: cat.name_en,
          count: categoryItems.length,
          value: categoryItems.reduce((sum: number, item: Item) => sum + item.cost_price_usd, 0)
        }
      }).sort((a: {category: string, count: number, value: number}, b: {category: string, count: number, value: number}) => b.count - a.count).slice(0, 5)

      // Get most profitable items
      const profitableItems = itemsData
        .map((item: Item) => ({
          ...item,
          margin: item.selling_price_usd - item.cost_price_usd
        }))
        .sort((a: Item & { margin: number }, b: Item & { margin: number }) => b.margin - a.margin)
        .slice(0, 5)

      setStats({
        totalItems,
        totalCategories,
        totalValue,
        averageMargin,
        lowStockItems,
        topCategories: categoryStats,
        recentItems: itemsData.slice(0, 5),
        profitableItems: profitableItems
      })

    } catch (error) {
      console.error('Error fetching dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="p-8">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-64 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="bg-gray-200 dark:bg-gray-700 h-32 rounded-lg"></div>
            ))}
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="bg-gray-200 dark:bg-gray-700 h-64 rounded-lg"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="p-8 space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Items Dashboard</h1>
          <p className="text-gray-600 dark:text-gray-400">Overview of your product catalog and inventory</p>
        </div>
        <div className="flex items-center space-x-3">
          <Button
            variant="outline"
            onClick={() => navigate('/inventory/items')}
            className="flex items-center space-x-2"
          >
            <Eye className="h-4 w-4" />
            <span>View All Items</span>
          </Button>
          <Button
            onClick={() => navigate('/inventory/items')}
            className="flex items-center space-x-2 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800"
          >
            <Plus className="h-4 w-4" />
            <span>Add New Item</span>
          </Button>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="relative overflow-hidden">
          <div className="absolute top-0 right-0 w-20 h-20 bg-gradient-to-br from-blue-500/20 to-purple-500/20 rounded-full -translate-y-10 translate-x-10"></div>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-600 dark:text-gray-300">
              Total Items
            </CardTitle>
            <div className="p-2 rounded-lg bg-blue-50 dark:bg-blue-900/20">
              <Package className="h-4 w-4 text-blue-600 dark:text-blue-400" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-900 dark:text-white">{stats.totalItems}</div>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 flex items-center">
              <TrendingUp className="h-3 w-3 mr-1 text-green-500" />
              Active items in catalog
            </p>
          </CardContent>
        </Card>

        <Card className="relative overflow-hidden">
          <div className="absolute top-0 right-0 w-20 h-20 bg-gradient-to-br from-purple-500/20 to-pink-500/20 rounded-full -translate-y-10 translate-x-10"></div>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-600 dark:text-gray-300">
              Categories
            </CardTitle>
            <div className="p-2 rounded-lg bg-purple-50 dark:bg-purple-900/20">
              <Tag className="h-4 w-4 text-purple-600 dark:text-purple-400" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-900 dark:text-white">{stats.totalCategories}</div>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 flex items-center">
              <Target className="h-3 w-3 mr-1 text-purple-500" />
              Product categories
            </p>
          </CardContent>
        </Card>

        <Card className="relative overflow-hidden">
          <div className="absolute top-0 right-0 w-20 h-20 bg-gradient-to-br from-green-500/20 to-emerald-500/20 rounded-full -translate-y-10 translate-x-10"></div>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-600 dark:text-gray-300">
              Total Value
            </CardTitle>
            <div className="p-2 rounded-lg bg-green-50 dark:bg-green-900/20">
              <DollarSign className="h-4 w-4 text-green-600 dark:text-green-400" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-900 dark:text-white">
              ${stats.totalValue.toLocaleString()}
            </div>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 flex items-center">
              <ArrowUpRight className="h-3 w-3 mr-1 text-green-500" />
              Total cost value
            </p>
          </CardContent>
        </Card>

        <Card className="relative overflow-hidden">
          <div className="absolute top-0 right-0 w-20 h-20 bg-gradient-to-br from-orange-500/20 to-red-500/20 rounded-full -translate-y-10 translate-x-10"></div>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-600 dark:text-gray-300">
              Avg. Margin
            </CardTitle>
            <div className="p-2 rounded-lg bg-orange-50 dark:bg-orange-900/20">
              <TrendingUp className="h-4 w-4 text-orange-600 dark:text-orange-400" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-900 dark:text-white">
              ${stats.averageMargin.toFixed(2)}
            </div>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 flex items-center">
              <Star className="h-3 w-3 mr-1 text-orange-500" />
              Average profit margin
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Charts and Analytics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Categories */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <BarChart3 className="h-5 w-5 text-blue-600" />
              <span>Top Categories</span>
            </CardTitle>
            <CardDescription>Categories with most items</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {stats.topCategories.map((category, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-bold ${
                      index === 0 ? 'bg-yellow-500' : 
                      index === 1 ? 'bg-gray-400' : 
                      index === 2 ? 'bg-orange-500' : 'bg-blue-500'
                    }`}>
                      {index + 1}
                    </div>
                    <div>
                      <p className="font-medium text-gray-900 dark:text-white">{category.category}</p>
                      <p className="text-sm text-gray-500 dark:text-gray-400">{category.count} items</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold text-gray-900 dark:text-white">${category.value.toFixed(0)}</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">Total value</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Most Profitable Items */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <TrendingUp className="h-5 w-5 text-green-600" />
              <span>Most Profitable Items</span>
            </CardTitle>
            <CardDescription>Items with highest profit margins</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {stats.profitableItems.map((item, index) => {
                const margin = item.selling_price_usd - item.cost_price_usd
                const marginPercent = item.cost_price_usd > 0 ? (margin / item.cost_price_usd) * 100 : 0
                
                return (
                  <div key={item.id} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center">
                        <span className="text-green-600 dark:text-green-400 text-xs font-bold">{index + 1}</span>
                      </div>
                      <div>
                        <p className="font-medium text-gray-900 dark:text-white">{item.name_en}</p>
                        <p className="text-sm text-gray-500 dark:text-gray-400">{item.code}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold text-green-600 dark:text-green-400">${margin.toFixed(2)}</p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">{marginPercent.toFixed(1)}%</p>
                    </div>
                  </div>
                )
              })}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Items & Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Items */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Clock className="h-5 w-5 text-blue-600" />
              <span>Recent Items</span>
            </CardTitle>
            <CardDescription>Latest items added to your catalog</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {stats.recentItems.map((item) => (
                <div key={item.id} className="flex items-center justify-between p-3 hover:bg-gray-50 dark:hover:bg-gray-800 rounded-lg transition-colors">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                      <Package className="h-5 w-5 text-white" />
                    </div>
                    <div>
                      <p className="font-medium text-gray-900 dark:text-white">{item.name_en}</p>
                      <p className="text-sm text-gray-500 dark:text-gray-400">{item.code} • {item.brand}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-medium text-gray-900 dark:text-white">
                      ${item.selling_price_usd.toFixed(2)}
                    </span>
                    <Button size="sm" variant="outline" className="h-8 w-8 p-0">
                      <Eye className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
              <Button 
                variant="outline" 
                className="w-full"
                onClick={() => navigate('/inventory/items')}
              >
                View All Items
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Zap className="h-5 w-5 text-orange-600" />
              <span>Quick Actions</span>
            </CardTitle>
            <CardDescription>Common tasks and shortcuts</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button 
              className="w-full justify-start h-12"
              onClick={() => navigate('/inventory/items')}
            >
              <Plus className="h-4 w-4 mr-2" />
              Add New Item
            </Button>
            <Button 
              variant="outline" 
              className="w-full justify-start h-12"
              onClick={() => navigate('/inventory/items')}
            >
              <Search className="h-4 w-4 mr-2" />
              Search Items
            </Button>
            <Button 
              variant="outline" 
              className="w-full justify-start h-12"
              onClick={() => navigate('/inventory/items')}
            >
              <Filter className="h-4 w-4 mr-2" />
              Filter by Category
            </Button>
            <Button 
              variant="outline" 
              className="w-full justify-start h-12"
              onClick={() => navigate('/inventory/price-lists')}
            >
              <DollarSign className="h-4 w-4 mr-2" />
              Manage Pricing
            </Button>
            <Button 
              variant="outline" 
              className="w-full justify-start h-12"
              onClick={() => navigate('/inventory/adjustments')}
            >
              <Edit className="h-4 w-4 mr-2" />
              Stock Adjustments
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* System Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Globe className="h-5 w-5 text-green-600" />
            <span>Items System Status</span>
          </CardTitle>
          <CardDescription>Current status of your items management system</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
              <div className="w-8 h-8 bg-green-500 rounded-full mx-auto mb-2 flex items-center justify-center">
                <Package className="h-4 w-4 text-white" />
              </div>
              <p className="font-semibold text-green-700 dark:text-green-400">Items Management</p>
              <p className="text-sm text-green-600 dark:text-green-500">Online</p>
            </div>
            <div className="text-center p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
              <div className="w-8 h-8 bg-blue-500 rounded-full mx-auto mb-2 flex items-center justify-center">
                <Tag className="h-4 w-4 text-white" />
              </div>
              <p className="font-semibold text-blue-700 dark:text-blue-400">Categories</p>
              <p className="text-sm text-blue-600 dark:text-blue-500">Active</p>
            </div>
            <div className="text-center p-4 bg-orange-50 dark:bg-orange-900/20 rounded-lg">
              <div className="w-8 h-8 bg-orange-500 rounded-full mx-auto mb-2 flex items-center justify-center">
                <DollarSign className="h-4 w-4 text-white" />
              </div>
              <p className="font-semibold text-orange-700 dark:text-orange-400">Pricing Engine</p>
              <p className="text-sm text-orange-600 dark:text-orange-500">Running</p>
            </div>
            <div className="text-center p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
              <div className="w-8 h-8 bg-purple-500 rounded-full mx-auto mb-2 flex items-center justify-center">
                <BarChart3 className="h-4 w-4 text-white" />
              </div>
              <p className="font-semibold text-purple-700 dark:text-purple-400">Analytics</p>
              <p className="text-sm text-purple-600 dark:text-purple-500">Updated</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
