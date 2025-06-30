import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Loading } from '@/components/ui/loading'
import axios from 'axios'
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
      const response = await axios.get<ModelsResponse>('http://localhost:8000/api/models')
      setModels(response.data.models || [])
    } catch (err) {
      console.error('Error fetching models:', err)
      setError('Failed to load database models. Please ensure the backend server is running.')
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
              className="flex items-center space-x-2"
            >
              <span>{category.label}</span>
              <Badge variant="secondary" className="ml-1">
                {category.count}
              </Badge>
            </Button>
          ))}
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <Card className="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
          <CardContent className="p-6">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-blue-500 rounded-xl flex items-center justify-center">
                <Database className="h-6 w-6 text-white" />
              </div>
              <div>
                <p className="text-2xl font-bold text-blue-900">{models.length}</p>
                <p className="text-sm text-blue-700">Total Models</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-gradient-to-br from-green-50 to-green-100 border-green-200">
          <CardContent className="p-6">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-green-500 rounded-xl flex items-center justify-center">
                <Table className="h-6 w-6 text-white" />
              </div>
              <div>
                <p className="text-2xl font-bold text-green-900">
                  {models.reduce((sum, model) => sum + model.columns.length, 0)}
                </p>
                <p className="text-sm text-green-700">Total Fields</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200">
          <CardContent className="p-6">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-purple-500 rounded-xl flex items-center justify-center">
                <Link className="h-6 w-6 text-white" />
              </div>
              <div>
                <p className="text-2xl font-bold text-purple-900">
                  {models.reduce((sum, model) => sum + model.relationships.length, 0)}
                </p>
                <p className="text-sm text-purple-700">Relationships</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-gradient-to-br from-orange-50 to-orange-100 border-orange-200">
          <CardContent className="p-6">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-orange-500 rounded-xl flex items-center justify-center">
                <Layers className="h-6 w-6 text-white" />
              </div>
              <div>
                <p className="text-2xl font-bold text-orange-900">
                  {models.reduce((sum, model) => sum + (model.record_count || 0), 0).toLocaleString()}
                </p>
                <p className="text-sm text-orange-700">Total Records</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Models Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredModels.map((model) => (
          <Card key={model.name} className="hover:shadow-lg transition-all duration-200 hover:scale-105 cursor-pointer border-l-4 border-l-blue-500">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                    <Table className="h-5 w-5 text-white" />
                  </div>
                  <div>
                    <CardTitle className="text-lg">{model.name}</CardTitle>
                    <p className="text-sm text-gray-500">{model.table_name}</p>
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
                  <Badge variant="outline">{model.columns.length}</Badge>
                </div>
                
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">Relationships:</span>
                  <Badge variant="outline">{model.relationships.length}</Badge>
                </div>
                
                {model.record_count !== undefined && (
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Records:</span>
                    <Badge variant="outline">{model.record_count.toLocaleString()}</Badge>
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

      {filteredModels.length === 0 && (
        <div className="text-center py-12">
          <Database className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-500 text-lg">No models found matching your search criteria</p>
        </div>
      )}

      {/* Model Detail Modal */}
      {selectedModel && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden">
            <div className="p-6 border-b">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-bold">{selectedModel.name}</h2>
                  <CardDescription>Table: {selectedModel.table_name}</CardDescription>
                </div>
                <Button variant="outline" onClick={() => setSelectedModel(null)}>
                  Close
                </Button>
              </div>
            </div>
            
            <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Fields */}
                <div>
                  <h3 className="text-lg font-semibold mb-4 flex items-center">
                    <Key className="h-5 w-5 mr-2" />
                    Fields ({selectedModel.columns.length})
                  </h3>
                  <div className="space-y-3">
                    {selectedModel.columns.map((field) => (
                      <div key={field.name} className="border rounded-lg p-3 bg-gray-50">
                        <div className="flex items-center justify-between mb-1">
                          <span className="font-medium">{field.name}</span>
                          <div className="flex gap-1">
                            {field.primary_key && (
                              <Badge variant="destructive" className="text-xs">PK</Badge>
                            )}
                            {field.foreign_keys && field.foreign_keys.length > 0 && (
                              <Badge variant="secondary" className="text-xs">FK</Badge>
                            )}
                            {!field.nullable && (
                              <Badge variant="outline" className="text-xs">Required</Badge>
                            )}
                          </div>
                        </div>
                        <p className="text-sm text-gray-600">{field.type}</p>
                        {field.foreign_keys && field.foreign_keys.length > 0 && (
                          <p className="text-xs text-blue-600 mt-1">→ {field.foreign_keys.join(', ')}</p>
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
                  <div className="space-y-3">
                    {selectedModel.relationships.map((relationship) => (
                      <div key={relationship.name} className="border rounded-lg p-3 bg-gray-50">
                        <div className="flex items-center justify-between">
                          <span className="font-medium">{relationship.name}</span>
                          <Badge variant="outline" className="text-xs">{relationship.type}</Badge>
                        </div>
                        <p className="text-sm text-gray-600">→ {relationship.target}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
