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
  Tag,
  Box,
  TrendingUp,
  X
} from 'lucide-react'

interface Category {
  id: number
  code: string
  name_ar: string
  name_en: string
  description_ar?: string
  description_en?: string
  parent_id?: number
  level: number
  sort_order: number
  is_active: boolean
  created_at: string
  updated_at: string
}

interface Item {
  id: number
  code: string
  name_ar: string
  name_en: string
  description_ar?: string
  description_en?: string
  category_id?: number
  brand?: string
  model?: string
  specifications?: string
  unit_of_measure: string
  cost_price_usd: number
  cost_price_iqd: number
  selling_price_usd: number
  selling_price_iqd: number
  track_inventory: boolean
  reorder_level: number
  reorder_quantity: number
  weight?: number
  dimensions?: string
  is_active: boolean
  is_serialized: boolean
  is_batch_tracked: boolean
  zoho_item_id?: string
  zoho_last_sync?: string
  created_at: string
  updated_at: string
  created_by?: number
}

interface ItemFormData {
  code: string
  name_ar: string
  name_en: string
  description_ar?: string
  description_en?: string
  category_id?: number
  brand?: string
  model?: string
  unit_of_measure: string
  cost_price_usd: number
  selling_price_usd: number
  track_inventory: boolean
  reorder_level: number
  reorder_quantity: number
  weight?: number
  dimensions?: string
  is_active: boolean
  is_serialized: boolean
  is_batch_tracked: boolean
}

const units = [
  { code: 'PCS', name: 'Pieces' },
  { code: 'KG', name: 'Kilogram' },
  { code: 'LTR', name: 'Liter' },
  { code: 'MTR', name: 'Meter' },
  { code: 'BOX', name: 'Box' },
  { code: 'PACK', name: 'Pack' },
  { code: 'SET', name: 'Set' }
]

export function ItemsPageEnhanced() {
  const [items, setItems] = useState<Item[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [editingItem, setEditingItem] = useState<Item | null>(null)
  const [formData, setFormData] = useState<ItemFormData>({
    code: '',
    name_ar: '',
    name_en: '',
    description_ar: '',
    description_en: '',
    category_id: undefined,
    brand: '',
    model: '',
    unit_of_measure: 'PCS',
    cost_price_usd: 0,
    selling_price_usd: 0,
    track_inventory: true,
    reorder_level: 0,
    reorder_quantity: 0,
    weight: undefined,
    dimensions: '',
    is_active: true,
    is_serialized: false,
    is_batch_tracked: false
  })

  // Fetch data
  useEffect(() => {
    fetchItems()
    fetchCategories()
  }, [])

  const fetchItems = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('http://localhost:8000/api/items/', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setItems(data)
        console.log('✅ Fetched items:', data.length)
      } else {
        console.error('❌ Failed to fetch items:', response.status)
      }
    } catch (error) {
      console.error('❌ Error fetching items:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchCategories = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/migration/categories/')
      if (response.ok) {
        const data = await response.json()
        setCategories(data)
        console.log('✅ Fetched categories:', data.length)
      }
    } catch (error) {
      console.error('❌ Error fetching categories:', error)
    }
  }

  // Reset form
  const resetForm = () => {
    setFormData({
      code: '',
      name_ar: '',
      name_en: '',
      description_ar: '',
      description_en: '',
      category_id: undefined,
      brand: '',
      model: '',
      unit_of_measure: 'PCS',
      cost_price_usd: 0,
      selling_price_usd: 0,
      track_inventory: true,
      reorder_level: 0,
      reorder_quantity: 0,
      weight: undefined,
      dimensions: '',
      is_active: true,
      is_serialized: false,
      is_batch_tracked: false
    })
    setEditingItem(null)
    setShowForm(false)
  }

  // Handle create/update
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    try {
      const token = localStorage.getItem('token')
      const url = editingItem 
        ? `http://localhost:8000/api/items/${editingItem.id}`
        : 'http://localhost:8000/api/items/'
      
      const method = editingItem ? 'PUT' : 'POST'
      
      const response = await fetch(url, {
        method,
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      })
      
      if (response.ok) {
        await fetchItems() // Refresh list
        resetForm()
        console.log(`✅ ${editingItem ? 'Updated' : 'Created'} item successfully`)
      } else {
        const error = await response.json()
        console.error('❌ Error saving item:', error)
      }
    } catch (error) {
      console.error('❌ Error saving item:', error)
    }
  }

  // Handle edit
  const handleEdit = (item: Item) => {
    setFormData({
      code: item.code,
      name_ar: item.name_ar,
      name_en: item.name_en,
      description_ar: item.description_ar || '',
      description_en: item.description_en || '',
      category_id: item.category_id,
      brand: item.brand || '',
      model: item.model || '',
      unit_of_measure: item.unit_of_measure,
      cost_price_usd: item.cost_price_usd,
      selling_price_usd: item.selling_price_usd,
      track_inventory: item.track_inventory,
      reorder_level: item.reorder_level,
      reorder_quantity: item.reorder_quantity,
      weight: item.weight,
      dimensions: item.dimensions || '',
      is_active: item.is_active,
      is_serialized: item.is_serialized,
      is_batch_tracked: item.is_batch_tracked
    })
    setEditingItem(item)
    setShowForm(true)
  }

  // Handle delete
  const handleDelete = async (item: Item) => {
    if (!confirm(`Are you sure you want to delete "${item.name_en}"?`)) return
    
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`http://localhost:8000/api/items/${item.id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        await fetchItems() // Refresh list
        console.log('✅ Deleted item successfully')
      } else {
        console.error('❌ Failed to delete item')
      }
    } catch (error) {
      console.error('❌ Error deleting item:', error)
    }
  }

  // Filter items
  const filteredItems = items.filter(item => {
    const matchesSearch = item.name_en.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         item.name_ar.includes(searchTerm) ||
                         item.code.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         (item.brand && item.brand.toLowerCase().includes(searchTerm.toLowerCase()))
    
    const matchesCategory = selectedCategory === '' || item.category_id?.toString() === selectedCategory
    
    return matchesSearch && matchesCategory && item.is_active
  })

  // Calculate stats
  const totalItems = items.filter(item => item.is_active).length
  const totalValue = items.reduce((sum, item) => sum + item.cost_price_usd, 0)
  const averageMargin = items.length > 0 
    ? items.reduce((sum, item) => sum + (item.selling_price_usd - item.cost_price_usd), 0) / items.length 
    : 0

  if (loading) {
    return (
      <div className="p-8">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-64 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
            {[...Array(4)].map((_, i) => (
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
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Items Management</h1>
          <p className="text-gray-600 dark:text-gray-400">Manage your product catalog and inventory items</p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            className="group relative overflow-hidden"
          >
            <span className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-500 opacity-0 group-hover:opacity-10 transition-opacity"></span>
            <Package className="h-4 w-4 mr-2" />
            Export
          </Button>
          <Button
            size="sm"
            onClick={() => setShowForm(true)}
            className="bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 shadow-md hover:shadow-lg transition-all"
          >
            <Plus className="h-4 w-4 mr-2" />
            Add Item
          </Button>
        </div>
      </div>

      {/* Enhanced Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-600 dark:text-gray-300">
              Total Items
            </CardTitle>
            <div className="p-2 rounded-lg bg-blue-50 dark:bg-blue-900/20">
              <Package className="h-4 w-4 text-blue-600 dark:text-blue-400" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-900 dark:text-white">{totalItems}</div>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Active items in catalog</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-600 dark:text-gray-300">
              Categories
            </CardTitle>
            <div className="p-2 rounded-lg bg-purple-50 dark:bg-purple-900/20">
              <Tag className="h-4 w-4 text-purple-600 dark:text-purple-400" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-900 dark:text-white">{categories.length}</div>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Product categories</p>
          </CardContent>
        </Card>

        <Card>
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
              ${totalValue.toLocaleString()}
            </div>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Total cost value</p>
          </CardContent>
        </Card>

        <Card>
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
              ${averageMargin.toFixed(2)}
            </div>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Average profit margin</p>
          </CardContent>
        </Card>
      </div>

      {/* Filters and Search */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="h-5 w-5" />
            Filters & Search
          </CardTitle>
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
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Categories</option>
                {categories.map(category => (
                  <option key={category.id} value={category.id.toString()}>
                    {category.name_en}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Items Table */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Box className="h-5 w-5" />
            Items ({filteredItems.length})
          </CardTitle>
          <CardDescription>
            {searchTerm || selectedCategory ? 'Filtered results' : 'All active items in your catalog'}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b dark:border-gray-700">
                  <th className="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">Code</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">Item Name</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">Category</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">Brand</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">Unit</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">Cost Price</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">Selling Price</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">Margin</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredItems.map((item) => {
                  const category = categories.find(c => c.id === item.category_id)
                  const margin = item.selling_price_usd - item.cost_price_usd
                  const marginPercent = item.cost_price_usd > 0 ? (margin / item.cost_price_usd) * 100 : 0
                  
                  return (
                    <tr key={item.id} className="border-b dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800">
                      <td className="py-3 px-4 font-mono text-sm text-blue-600 dark:text-blue-400">{item.code}</td>
                      <td className="py-3 px-4">
                        <div>
                          <div className="font-medium text-gray-900 dark:text-white">{item.name_en}</div>
                          <div className="text-sm text-gray-500 dark:text-gray-400">{item.name_ar}</div>
                          {item.model && (
                            <div className="text-xs text-gray-400 dark:text-gray-500">Model: {item.model}</div>
                          )}
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <span className="text-sm bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-300 px-2 py-1 rounded">
                          {category?.name_en || 'No Category'}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-sm text-gray-700 dark:text-gray-300">{item.brand || '-'}</td>
                      <td className="py-3 px-4 text-sm text-gray-700 dark:text-gray-300">{item.unit_of_measure}</td>
                      <td className="py-3 px-4 text-sm text-gray-700 dark:text-gray-300">
                        ${item.cost_price_usd.toFixed(2)}
                      </td>
                      <td className="py-3 px-4 text-sm text-gray-700 dark:text-gray-300">
                        ${item.selling_price_usd.toFixed(2)}
                      </td>
                      <td className="py-3 px-4">
                        <div className="text-sm">
                          <span className={`font-medium ${margin >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
                            ${margin.toFixed(2)}
                          </span>
                          <div className="text-xs text-gray-500 dark:text-gray-400">
                            {marginPercent.toFixed(1)}%
                          </div>
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2">
                          <Button 
                            size="sm" 
                            variant="outline" 
                            className="h-8 w-8 p-0"
                            onClick={() => handleEdit(item)}
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button 
                            size="sm" 
                            variant="outline" 
                            className="h-8 w-8 p-0 text-red-600 hover:text-red-700"
                            onClick={() => handleDelete(item)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Add/Edit Item Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-6 border-b dark:border-gray-700">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                {editingItem ? 'Edit Item' : 'Add New Item'}
              </h2>
              <Button
                variant="outline"
                size="sm"
                onClick={resetForm}
                className="h-8 w-8 p-0"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
            
            <form onSubmit={handleSubmit} className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Basic Information */}
                <div className="space-y-4">
                  <h3 className="font-medium text-gray-900 dark:text-white mb-4">Basic Information</h3>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Item Code *
                    </label>
                    <Input
                      value={formData.code}
                      onChange={(e) => setFormData({...formData, code: e.target.value})}
                      placeholder="e.g., LAP-001"
                      required
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      English Name *
                    </label>
                    <Input
                      value={formData.name_en}
                      onChange={(e) => setFormData({...formData, name_en: e.target.value})}
                      placeholder="Item name in English"
                      required
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Arabic Name *
                    </label>
                    <Input
                      value={formData.name_ar}
                      onChange={(e) => setFormData({...formData, name_ar: e.target.value})}
                      placeholder="اسم الصنف بالعربية"
                      required
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Category
                    </label>
                    <select
                      value={formData.category_id || ''}
                      onChange={(e) => setFormData({...formData, category_id: e.target.value ? parseInt(e.target.value) : undefined})}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">Select Category</option>
                      {categories.map(category => (
                        <option key={category.id} value={category.id}>
                          {category.name_en}
                        </option>
                      ))}
                    </select>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Brand
                      </label>
                      <Input
                        value={formData.brand}
                        onChange={(e) => setFormData({...formData, brand: e.target.value})}
                        placeholder="e.g., Dell, Apple"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Model
                      </label>
                      <Input
                        value={formData.model}
                        onChange={(e) => setFormData({...formData, model: e.target.value})}
                        placeholder="e.g., XPS 13"
                      />
                    </div>
                  </div>
                </div>

                {/* Pricing & Inventory */}
                <div className="space-y-4">
                  <h3 className="font-medium text-gray-900 dark:text-white mb-4">Pricing & Inventory</h3>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Unit of Measure
                    </label>
                    <select
                      value={formData.unit_of_measure}
                      onChange={(e) => setFormData({...formData, unit_of_measure: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      {units.map(unit => (
                        <option key={unit.code} value={unit.code}>
                          {unit.name} ({unit.code})
                        </option>
                      ))}
                    </select>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Cost Price (USD) *
                      </label>
                      <Input
                        type="number"
                        step="0.01"
                        min="0"
                        value={formData.cost_price_usd}
                        onChange={(e) => setFormData({...formData, cost_price_usd: parseFloat(e.target.value) || 0})}
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Selling Price (USD) *
                      </label>
                      <Input
                        type="number"
                        step="0.01"
                        min="0"
                        value={formData.selling_price_usd}
                        onChange={(e) => setFormData({...formData, selling_price_usd: parseFloat(e.target.value) || 0})}
                        required
                      />
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Reorder Level
                      </label>
                      <Input
                        type="number"
                        min="0"
                        value={formData.reorder_level}
                        onChange={(e) => setFormData({...formData, reorder_level: parseFloat(e.target.value) || 0})}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Reorder Quantity
                      </label>
                      <Input
                        type="number"
                        min="0"
                        value={formData.reorder_quantity}
                        onChange={(e) => setFormData({...formData, reorder_quantity: parseFloat(e.target.value) || 0})}
                      />
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Weight (kg)
                      </label>
                      <Input
                        type="number"
                        step="0.001"
                        min="0"
                        value={formData.weight || ''}
                        onChange={(e) => setFormData({...formData, weight: parseFloat(e.target.value) || undefined})}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Dimensions
                      </label>
                      <Input
                        value={formData.dimensions}
                        onChange={(e) => setFormData({...formData, dimensions: e.target.value})}
                        placeholder="L x W x H"
                      />
                    </div>
                  </div>
                  
                  {/* Checkboxes */}
                  <div className="space-y-3">
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={formData.track_inventory}
                        onChange={(e) => setFormData({...formData, track_inventory: e.target.checked})}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">Track Inventory</span>
                    </label>
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={formData.is_serialized}
                        onChange={(e) => setFormData({...formData, is_serialized: e.target.checked})}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">Serialized Item</span>
                    </label>
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={formData.is_batch_tracked}
                        onChange={(e) => setFormData({...formData, is_batch_tracked: e.target.checked})}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">Batch Tracked</span>
                    </label>
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={formData.is_active}
                        onChange={(e) => setFormData({...formData, is_active: e.target.checked})}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">Active</span>
                    </label>
                  </div>
                </div>
              </div>
              
              {/* Description */}
              <div className="mt-6">
                <h3 className="font-medium text-gray-900 dark:text-white mb-4">Description</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      English Description
                    </label>
                    <textarea
                      value={formData.description_en}
                      onChange={(e) => setFormData({...formData, description_en: e.target.value})}
                      rows={3}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Item description in English"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Arabic Description
                    </label>
                    <textarea
                      value={formData.description_ar}
                      onChange={(e) => setFormData({...formData, description_ar: e.target.value})}
                      rows={3}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="وصف الصنف بالعربية"
                    />
                  </div>
                </div>
              </div>
              
              {/* Form Actions */}
              <div className="flex items-center justify-end gap-4 mt-8 pt-6 border-t dark:border-gray-700">
                <Button
                  type="button"
                  variant="outline"
                  onClick={resetForm}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  className="bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700"
                >
                  {editingItem ? 'Update Item' : 'Create Item'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
