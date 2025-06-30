import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Loading } from '@/components/ui/loading'
import api from '@/lib/api'
import { 
  Database, 
  Table, 
  Search, 
  Eye, 
  Layers,
  Key,
  Link,
  FileText,
  Settings,
  RefreshCw,
  AlertCircle
} from 'lucide-react'

interface ModelField {
  name: string
  type: string
  nullable: boolean
  primary_key?: boolean
  foreign_keys?: string[]
  default?: string
  description?: string
}

interface DatabaseModel {
  name: string
  table_name: string
  description: string
  columns: ModelField[]
  relationships: Array<{
    name: string
    target: string
    type: string
  }>
  record_count?: number
  category: 'core' | 'inventory' | 'sales' | 'purchasing' | 'accounting' | 'pos' | 'cashflow' | 'other'
}

interface ModelsResponse {
  models: DatabaseModel[]
  total_models: number
  total_records: number
}

const mockModels: DatabaseModel[] = [
  // Core Models
  {
    name: 'User',
    tableName: 'users',
    description: 'System users and authentication',
    category: 'core',
    recordCount: 24,
    fields: [
      { name: 'id', type: 'Integer', nullable: false, primaryKey: true },
      { name: 'name', type: 'String(100)', nullable: false },
      { name: 'email', type: 'String(255)', nullable: false },
      { name: 'password_hash', type: 'String(255)', nullable: false },
      { name: 'role_id', type: 'Integer', nullable: false, foreignKey: 'roles.id' },
      { name: 'is_active', type: 'Boolean', nullable: false },
      { name: 'created_at', type: 'DateTime', nullable: false },
      { name: 'updated_at', type: 'DateTime', nullable: false },
    ],
    relationships: ['Role', 'Branch', 'SalesOrder', 'PurchaseOrder']
  },
  {
    name: 'Role',
    tableName: 'roles',
    description: 'User roles and permissions',
    category: 'core',
    recordCount: 5,
    fields: [
      { name: 'id', type: 'Integer', nullable: false, primaryKey: true },
      { name: 'name', type: 'String(50)', nullable: false },
      { name: 'description', type: 'Text', nullable: true },
      { name: 'permissions', type: 'JSON', nullable: true },
    ],
    relationships: ['User']
  },
  {
    name: 'Branch',
    tableName: 'branches',
    description: 'Company branches and locations',
    category: 'core',
    recordCount: 5,
    fields: [
      { name: 'id', type: 'Integer', nullable: false, primaryKey: true },
      { name: 'name', type: 'String(100)', nullable: false },
      { name: 'code', type: 'String(10)', nullable: false },
      { name: 'address', type: 'Text', nullable: true },
      { name: 'phone', type: 'String(20)', nullable: true },
      { name: 'email', type: 'String(255)', nullable: true },
      { name: 'manager_id', type: 'Integer', nullable: true, foreignKey: 'users.id' },
    ],
    relationships: ['User', 'Warehouse', 'SalesOrder']
  },
  // Inventory Models
  {
    name: 'Product',
    tableName: 'products',
    description: 'Product catalog and information',
    category: 'inventory',
    recordCount: 1247,
    fields: [
      { name: 'id', type: 'Integer', nullable: false, primaryKey: true },
      { name: 'name', type: 'String(200)', nullable: false },
      { name: 'sku', type: 'String(50)', nullable: false },
      { name: 'barcode', type: 'String(50)', nullable: true },
      { name: 'category_id', type: 'Integer', nullable: false, foreignKey: 'categories.id' },
      { name: 'description', type: 'Text', nullable: true },
      { name: 'unit_price', type: 'Decimal(10,2)', nullable: false },
      { name: 'cost_price', type: 'Decimal(10,2)', nullable: false },
      { name: 'is_active', type: 'Boolean', nullable: false },
    ],
    relationships: ['Category', 'InventoryItem', 'SalesItem', 'PurchaseItem']
  },
  {
    name: 'Category',
    tableName: 'categories',
    description: 'Product categories and classification',
    category: 'inventory',
    recordCount: 45,
    fields: [
      { name: 'id', type: 'Integer', nullable: false, primaryKey: true },
      { name: 'name', type: 'String(100)', nullable: false },
      { name: 'description', type: 'Text', nullable: true },
      { name: 'parent_id', type: 'Integer', nullable: true, foreignKey: 'categories.id' },
    ],
    relationships: ['Product', 'Category (parent/child)']
  },
  {
    name: 'InventoryItem',
    tableName: 'inventory_items',
    description: 'Current stock levels and inventory tracking',
    category: 'inventory',
    recordCount: 856,
    fields: [
      { name: 'id', type: 'Integer', nullable: false, primaryKey: true },
      { name: 'product_id', type: 'Integer', nullable: false, foreignKey: 'products.id' },
      { name: 'warehouse_id', type: 'Integer', nullable: false, foreignKey: 'warehouses.id' },
      { name: 'quantity', type: 'Integer', nullable: false },
      { name: 'reserved_quantity', type: 'Integer', nullable: false },
      { name: 'reorder_level', type: 'Integer', nullable: true },
      { name: 'last_updated', type: 'DateTime', nullable: false },
    ],
    relationships: ['Product', 'Warehouse', 'StockMovement']
  },
  // Sales Models
  {
    name: 'Customer',
    tableName: 'customers',
    description: 'Customer information and contacts',
    category: 'sales',
    recordCount: 342,
    fields: [
      { name: 'id', type: 'Integer', nullable: false, primaryKey: true },
      { name: 'name', type: 'String(200)', nullable: false },
      { name: 'email', type: 'String(255)', nullable: true },
      { name: 'phone', type: 'String(20)', nullable: true },
      { name: 'address', type: 'Text', nullable: true },
      { name: 'tax_number', type: 'String(50)', nullable: true },
      { name: 'credit_limit', type: 'Decimal(12,2)', nullable: true },
    ],
    relationships: ['SalesOrder']
  },
  {
    name: 'SalesOrder',
    tableName: 'sales_orders',
    description: 'Sales orders and transactions',
    category: 'sales',
    recordCount: 156,
    fields: [
      { name: 'id', type: 'Integer', nullable: false, primaryKey: true },
      { name: 'order_number', type: 'String(50)', nullable: false },
      { name: 'customer_id', type: 'Integer', nullable: false, foreignKey: 'customers.id' },
      { name: 'branch_id', type: 'Integer', nullable: false, foreignKey: 'branches.id' },
      { name: 'user_id', type: 'Integer', nullable: false, foreignKey: 'users.id' },
      { name: 'order_date', type: 'DateTime', nullable: false },
      { name: 'total_amount', type: 'Decimal(12,2)', nullable: false },
      { name: 'status', type: 'String(20)', nullable: false },
    ],
    relationships: ['Customer', 'Branch', 'User', 'SalesItem']
  },
  // Accounting Models
  {
    name: 'Account',
    tableName: 'accounts',
    description: 'Chart of accounts for financial tracking',
    category: 'accounting',
    recordCount: 89,
    fields: [
      { name: 'id', type: 'Integer', nullable: false, primaryKey: true },
      { name: 'code', type: 'String(20)', nullable: false },
      { name: 'name', type: 'String(200)', nullable: false },
      { name: 'type', type: 'String(20)', nullable: false },
      { name: 'parent_id', type: 'Integer', nullable: true, foreignKey: 'accounts.id' },
      { name: 'balance', type: 'Decimal(15,2)', nullable: false },
    ],
    relationships: ['JournalEntry', 'Account (parent/child)']
  },
  {
    name: 'JournalEntry',
    tableName: 'journal_entries',
    description: 'Financial journal entries and transactions',
    category: 'accounting',
    recordCount: 1234,
    fields: [
      { name: 'id', type: 'Integer', nullable: false, primaryKey: true },
      { name: 'entry_number', type: 'String(50)', nullable: false },
      { name: 'entry_date', type: 'Date', nullable: false },
      { name: 'description', type: 'Text', nullable: false },
      { name: 'total_debit', type: 'Decimal(15,2)', nullable: false },
      { name: 'total_credit', type: 'Decimal(15,2)', nullable: false },
      { name: 'created_by', type: 'Integer', nullable: false, foreignKey: 'users.id' },
    ],
    relationships: ['User', 'JournalLine']
  }
]

export function ModelsPage() {
  const [models, setModels] = useState<DatabaseModel[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [selectedModel, setSelectedModel] = useState<DatabaseModel | null>(null)

  const fetchModels = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await api.get('/api/models')
      setModels(response.data.models || [])
    } catch (err) {
      console.error('Error fetching models:', err)
      setError('Failed to load database models. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchModels()
  }, [])

  const categories = [
    { value: 'all', label: 'All Models', count: models.length },
    { value: 'core', label: 'Core System', count: models.filter(m => m.category === 'core').length },
    { value: 'inventory', label: 'Inventory', count: models.filter(m => m.category === 'inventory').length },
    { value: 'sales', label: 'Sales', count: models.filter(m => m.category === 'sales').length },
    { value: 'purchasing', label: 'Purchasing', count: models.filter(m => m.category === 'purchasing').length },
    { value: 'accounting', label: 'Accounting', count: models.filter(m => m.category === 'accounting').length },
    { value: 'pos', label: 'Point of Sale', count: models.filter(m => m.category === 'pos').length },
    { value: 'cashflow', label: 'Cash Flow', count: models.filter(m => m.category === 'cashflow').length },
    { value: 'other', label: 'Other', count: models.filter(m => m.category === 'other').length },
  ]

  const filteredModels = models.filter(model => {
    const matchesSearch = model.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         model.description.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesCategory = selectedCategory === 'all' || model.category === selectedCategory
    return matchesSearch && matchesCategory
  })

  const getCategoryColor = (category: string) => {
    const colors = {
      core: 'bg-blue-100 text-blue-700',
      inventory: 'bg-green-100 text-green-700',
      sales: 'bg-purple-100 text-purple-700',
      purchasing: 'bg-indigo-100 text-indigo-700',
      accounting: 'bg-yellow-100 text-yellow-700',
      pos: 'bg-orange-100 text-orange-700',
      cashflow: 'bg-teal-100 text-teal-700',
      other: 'bg-gray-100 text-gray-700',
    }
    return colors[category as keyof typeof colors] || 'bg-gray-100 text-gray-700'
  }

  if (loading) {
    return (
      <div className="p-8 bg-gradient-to-br from-gray-50 to-white min-h-full">
        <div className="mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
            Database Models & Schema
          </h1>
          <p className="text-gray-600 text-lg mt-2">Explore and manage your database structure</p>
        </div>
        <div className="flex justify-center items-center h-64">
          <Loading size="lg" text="Loading database models..." />
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-8 bg-gradient-to-br from-gray-50 to-white min-h-full">
        <div className="mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
            Database Models & Schema
          </h1>
          <p className="text-gray-600 text-lg mt-2">Explore and manage your database structure</p>
        </div>
        <div className="flex flex-col items-center justify-center h-64 space-y-4">
          <AlertCircle className="h-12 w-12 text-red-500" />
          <p className="text-red-600 text-center">{error}</p>
          <Button onClick={fetchModels} className="flex items-center space-x-2">
            <RefreshCw className="h-4 w-4" />
            <span>Retry</span>
          </Button>
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
              Database Models & Schema
            </h1>
            <p className="text-gray-600 text-lg mt-2">Explore and manage your database structure</p>
          </div>
          <Button onClick={fetchModels} variant="outline" className="flex items-center space-x-2">
            <RefreshCw className="h-4 w-4" />
            <span>Refresh</span>
          </Button>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="mb-6 flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-3.5 h-4 w-4 text-gray-400" />
          <Input
            placeholder="Search models..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        <div className="flex gap-2 flex-wrap">
          {categories.map((category) => (
            <Button
              key={category.value}
              variant={selectedCategory === category.value ? "default" : "outline"}
              size="sm"
              onClick={() => setSelectedCategory(category.value)}
              className="whitespace-nowrap"
            >
              {category.label} ({category.count})
            </Button>
          ))}
        </div>
      </div>

      {/* Models Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        {filteredModels.map((model) => (
          <Card key={model.name} className="group hover:shadow-xl transition-all duration-300 hover:scale-105 cursor-pointer">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                    <Table className="h-5 w-5 text-white" />
                  </div>
                  <div>
                    <CardTitle className="text-lg">{model.name}</CardTitle>
                    <p className="text-sm text-gray-500">{model.tableName}</p>
                  </div>
                </div>
                <Badge className={getCategoryColor(model.category)}>
                  {model.category}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <CardDescription className="mb-4">{model.description}</CardDescription>
              
              <div className="space-y-3">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">Fields:</span>
                  <Badge variant="outline">{model.fields.length}</Badge>
                </div>
                
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">Relationships:</span>
                  <Badge variant="outline">{model.relationships.length}</Badge>
                </div>
                
                {model.recordCount !== undefined && (
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Records:</span>
                    <Badge variant="outline">{model.recordCount.toLocaleString()}</Badge>
                  </div>
                )}
              </div>

              <div className="mt-4 flex gap-2">
                <Button 
                  size="sm" 
                  variant="outline" 
                  className="flex-1"
                  onClick={() => setSelectedModel(model)}
                >
                  <Eye className="h-4 w-4 mr-1" />
                  View Schema
                </Button>
                <Button size="sm" variant="outline">
                  <Settings className="h-4 w-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Model Detail Modal/Panel */}
      {selectedModel && (
        <Card className="mt-8 border-2 border-blue-200">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-2xl">{selectedModel.name} Schema</CardTitle>
                <CardDescription>Table: {selectedModel.tableName}</CardDescription>
              </div>
              <Button variant="outline" onClick={() => setSelectedModel(null)}>
                Close
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Fields */}
              <div>
                <h3 className="text-lg font-semibold mb-4 flex items-center">
                  <Layers className="h-5 w-5 mr-2" />
                  Fields ({selectedModel.fields.length})
                </h3>
                <div className="space-y-2">
                  {selectedModel.fields.map((field) => (
                    <div key={field.name} className="border rounded-lg p-3 bg-gray-50">
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-medium flex items-center">
                          {field.primaryKey && <Key className="h-4 w-4 mr-1 text-yellow-500" />}
                          {field.foreignKey && <Link className="h-4 w-4 mr-1 text-blue-500" />}
                          {field.name}
                        </span>
                        <Badge variant={field.nullable ? "secondary" : "default"}>
                          {field.type}
                        </Badge>
                      </div>
                      {field.foreignKey && (
                        <p className="text-xs text-blue-600">→ {field.foreignKey}</p>
                      )}
                      {field.description && (
                        <p className="text-xs text-gray-600 mt-1">{field.description}</p>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* Relationships */}
              <div>
                <h3 className="text-lg font-semibold mb-4 flex items-center">
                  <Link className="h-5 w-5 mr-2" />
                  Relationships ({selectedModel.relationships.length})
                </h3>
                <div className="space-y-2">
                  {selectedModel.relationships.map((relationship) => (
                    <div key={relationship} className="border rounded-lg p-3 bg-gray-50">
                      <span className="font-medium">{relationship}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-8">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Models</p>
                <p className="text-2xl font-bold">{models.length}</p>
              </div>
              <Database className="h-8 w-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Records</p>
                <p className="text-2xl font-bold">
                  {models.reduce((sum, model) => sum + (model.recordCount || 0), 0).toLocaleString()}
                </p>
              </div>
              <FileText className="h-8 w-8 text-green-500" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Categories</p>
                <p className="text-2xl font-bold">{categories.length - 1}</p>
              </div>
              <Layers className="h-8 w-8 text-purple-500" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Active Tables</p>
                <p className="text-2xl font-bold">{models.length}</p>
              </div>
              <Table className="h-8 w-8 text-orange-500" />
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
