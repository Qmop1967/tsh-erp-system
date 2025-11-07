import { useState, useEffect } from 'react'
import { Button } from '../../components/ui/button'
import { Input } from '../../components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card'
import { 
  Plus, 
  Search, 
  Filter, 
  Edit, 
  Trash2,
  Package,
  DollarSign,
  BarChart3
} from 'lucide-react'

// Mock data for items
const mockItems = [
  {
    id: 1,
    code: 'ITM-001',
    name_en: 'Dell Laptop XPS 13',
    name_ar: 'لاب توب ديل XPS 13',
    category: 'Laptops',
    brand: 'Dell',
    cost_price_usd: 800.00,
    selling_price_usd: 1200.00,
    stock_quantity: 25,
    reorder_level: 10,
    is_active: true,
    created_at: '2024-01-15'
  },
  {
    id: 2,
    code: 'ITM-002',
    name_en: 'iPhone 15 Pro',
    name_ar: 'آيفون 15 برو',
    category: 'Mobile Phones',
    brand: 'Apple',
    cost_price_usd: 900.00,
    selling_price_usd: 1399.00,
    stock_quantity: 5,
    reorder_level: 10,
    is_active: true,
    created_at: '2024-01-16'
  },
  {
    id: 3,
    code: 'ITM-003',
    name_en: 'Samsung Monitor 27"',
    name_ar: 'شاشة سامسونج 27 بوصة',
    category: 'Monitors',
    brand: 'Samsung',
    cost_price_usd: 250.00,
    selling_price_usd: 399.00,
    stock_quantity: 15,
    reorder_level: 5,
    is_active: true,
    created_at: '2024-01-17'
  },
  {
    id: 4,
    code: 'ITM-004',
    name_en: 'Logitech Wireless Mouse',
    name_ar: 'ماوس لاسلكي لوجيتك',
    category: 'Accessories',
    brand: 'Logitech',
    cost_price_usd: 15.00,
    selling_price_usd: 29.99,
    stock_quantity: 50,
    reorder_level: 20,
    is_active: true,
    created_at: '2024-01-18'
  },
  {
    id: 5,
    code: 'ITM-005',
    name_en: 'HP Printer LaserJet',
    name_ar: 'طابعة ليزر HP',
    category: 'Printers',
    brand: 'HP',
    cost_price_usd: 200.00,
    selling_price_usd: 349.00,
    stock_quantity: 8,
    reorder_level: 3,
    is_active: true,
    created_at: '2024-01-19'
  }
]

export function ItemsPage() {
  const [items] = useState(mockItems)
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('')

  // Simulate loading
  useEffect(() => {
    const timer = setTimeout(() => {
      setLoading(false)
    }, 1000)
    return () => clearTimeout(timer)
  }, [])

  // Filter items based on search and category
  const filteredItems = items.filter(item => {
    const matchesSearch = item.name_en.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         item.name_ar.includes(searchTerm) ||
                         item.code.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         item.brand.toLowerCase().includes(searchTerm.toLowerCase())
    
    const matchesCategory = selectedCategory === '' || item.category === selectedCategory
    
    return matchesSearch && matchesCategory
  })

  // Get unique categories
  const categories = [...new Set(items.map(item => item.category))]

  // Calculate summary stats
  const totalItems = items.length
  const lowStockItems = items.filter(item => item.stock_quantity <= item.reorder_level).length
  const totalValue = items.reduce((sum, item) => sum + (item.stock_quantity * item.cost_price_usd), 0)

  if (loading) {
    return (
      <div className="p-8">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-64 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="bg-gray-200 h-24 rounded-lg"></div>
            ))}
          </div>
          <div className="bg-gray-200 h-96 rounded-lg"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Inventory Management</h1>
          <p className="text-gray-600">Manage your items and stock levels</p>
        </div>
        <Button className="flex items-center gap-2">
          <Plus className="h-4 w-4" />
          Add New Item
        </Button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">
              Total Items
            </CardTitle>
            <div className="p-2 rounded-lg bg-blue-50">
              <Package className="h-4 w-4 text-blue-600" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-900">{totalItems}</div>
            <p className="text-xs text-gray-500 mt-1">Active items in inventory</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">
              Low Stock Items
            </CardTitle>
            <div className="p-2 rounded-lg bg-red-50">
              <BarChart3 className="h-4 w-4 text-red-600" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-900">{lowStockItems}</div>
            <p className="text-xs text-gray-500 mt-1">Items need reordering</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">
              Total Inventory Value
            </CardTitle>
            <div className="p-2 rounded-lg bg-green-50">
              <DollarSign className="h-4 w-4 text-green-600" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-900">
              ${totalValue.toLocaleString()}
            </div>
            <p className="text-xs text-gray-500 mt-1">Total cost value</p>
          </CardContent>
        </Card>
      </div>

      {/* Filters and Search */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Filters</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Search items by name, code, or brand..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <div className="w-full md:w-48">
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Categories</option>
                {categories.map(category => (
                  <option key={category} value={category}>{category}</option>
                ))}
              </select>
            </div>
            <Button variant="outline" className="flex items-center gap-2">
              <Filter className="h-4 w-4" />
              More Filters
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Items Table */}
      <Card>
        <CardHeader>
          <CardTitle>Items ({filteredItems.length})</CardTitle>
          <CardDescription>
            {searchTerm || selectedCategory ? 'Filtered results' : 'All items in your inventory'}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3 px-4 font-medium text-gray-700">Code</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700">Item Name</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700">Category</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700">Brand</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700">Stock</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700">Cost Price</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700">Selling Price</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700">Status</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredItems.map((item) => (
                  <tr key={item.id} className="border-b hover:bg-gray-50">
                    <td className="py-3 px-4 font-mono text-sm">{item.code}</td>
                    <td className="py-3 px-4">
                      <div>
                        <div className="font-medium text-gray-900">{item.name_en}</div>
                        <div className="text-sm text-gray-500">{item.name_ar}</div>
                      </div>
                    </td>
                    <td className="py-3 px-4 text-sm text-gray-700">{item.category}</td>
                    <td className="py-3 px-4 text-sm text-gray-700">{item.brand}</td>
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        <span className={`text-sm font-medium ${
                          item.stock_quantity <= item.reorder_level 
                            ? 'text-red-600' 
                            : 'text-gray-900'
                        }`}>
                          {item.stock_quantity}
                        </span>
                        {item.stock_quantity <= item.reorder_level && (
                          <span className="text-xs bg-red-100 text-red-600 px-2 py-1 rounded">
                            Low Stock
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="py-3 px-4 text-sm text-gray-700">
                      ${item.cost_price_usd.toFixed(2)}
                    </td>
                    <td className="py-3 px-4 text-sm text-gray-700">
                      ${item.selling_price_usd.toFixed(2)}
                    </td>
                    <td className="py-3 px-4">
                      <span className={`text-xs px-2 py-1 rounded-full ${
                        item.is_active 
                          ? 'bg-green-100 text-green-600' 
                          : 'bg-gray-100 text-gray-600'
                      }`}>
                        {item.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        <Button size="sm" variant="outline" className="h-8 w-8 p-0">
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button size="sm" variant="outline" className="h-8 w-8 p-0">
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
