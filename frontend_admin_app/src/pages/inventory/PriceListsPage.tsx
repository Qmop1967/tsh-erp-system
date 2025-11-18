import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Loading } from '@/components/ui/loading'
import { 
  Tags, 
  Search, 
  Plus, 
  Eye, 
  Edit,
  Trash2,
  DollarSign
} from 'lucide-react'

interface PriceList {
  id: number
  code: string
  name: string
  currency: string
  is_default: boolean
  is_active: boolean
  items_count: number
  created_at: string
}

export function PriceListsPage() {
  const [priceLists, setPriceLists] = useState<PriceList[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    // Simulate loading data
    setTimeout(() => {
      setPriceLists([
        {
          id: 1,
          code: 'PL-IQD-01',
          name: 'قائمة الأسعار الأساسية - دينار عراقي',
          currency: 'IQD',
          is_default: true,
          is_active: true,
          items_count: 245,
          created_at: '2025-01-15'
        },
        {
          id: 2,
          code: 'PL-USD-01',
          name: 'Standard Price List - USD',
          currency: 'USD',
          is_default: false,
          is_active: true,
          items_count: 189,
          created_at: '2025-01-20'
        },
        {
          id: 3,
          code: 'PL-WHOLESALE',
          name: 'قائمة أسعار الجملة',
          currency: 'IQD',
          is_default: false,
          is_active: true,
          items_count: 156,
          created_at: '2025-02-01'
        }
      ])
      setLoading(false)
    }, 1000)
  }, [])

  const getCurrencyColor = (currency: string) => {
    switch (currency) {
      case 'IQD': return 'bg-green-100 text-green-700'
      case 'USD': return 'bg-blue-100 text-blue-700'
      case 'RMB': return 'bg-red-100 text-red-700'
      default: return 'bg-gray-100 text-gray-700'
    }
  }

  if (loading) {
    return (
      <div className="p-8">
        <div className="flex justify-center items-center h-64">
          <Loading size="lg" text="Loading price lists..." />
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
              Price Lists
            </h1>
            <p className="text-gray-600 text-lg mt-2">Manage pricing for different customer segments</p>
          </div>
          <Button className="flex items-center space-x-2 bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800">
            <Plus className="h-4 w-4" />
            <span>New Price List</span>
          </Button>
        </div>
      </div>

      {/* Search */}
      <div className="mb-6">
        <div className="relative max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
          <Input
            placeholder="Search price lists..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      {/* Price Lists Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {priceLists.map((priceList) => (
          <Card key={priceList.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Tags className="h-5 w-5 text-green-600" />
                  <CardTitle className="text-lg">{priceList.code}</CardTitle>
                </div>
                <div className="flex space-x-2">
                  {priceList.is_default && (
                    <Badge className="bg-blue-100 text-blue-700">Default</Badge>
                  )}
                  <Badge className={getCurrencyColor(priceList.currency)}>
                    {priceList.currency}
                  </Badge>
                </div>
              </div>
              <CardDescription className="mt-2">
                {priceList.name}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-500">Items Count:</span>
                  <span className="font-medium">{priceList.items_count} items</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-500">Status:</span>
                  <Badge className={priceList.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}>
                    {priceList.is_active ? 'Active' : 'Inactive'}
                  </Badge>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-500">Created:</span>
                  <span className="font-medium">{priceList.created_at}</span>
                </div>
                
                <div className="flex space-x-2 pt-4">
                  <Button variant="outline" size="sm" className="flex-1">
                    <Eye className="h-4 w-4 mr-1" />
                    View
                  </Button>
                  <Button variant="outline" size="sm" className="flex-1">
                    <Edit className="h-4 w-4 mr-1" />
                    Edit
                  </Button>
                  <Button variant="outline" size="sm" className="text-red-600 hover:text-red-700">
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Summary Stats */}
      <div className="mt-8 grid gap-6 md:grid-cols-3">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-3">
              <div className="p-3 bg-green-100 rounded-full">
                <Tags className="h-6 w-6 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-gray-500">Total Price Lists</p>
                <p className="text-2xl font-bold">{priceLists.length}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-3">
              <div className="p-3 bg-blue-100 rounded-full">
                <DollarSign className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-gray-500">Active Lists</p>
                <p className="text-2xl font-bold">{priceLists.filter(pl => pl.is_active).length}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-3">
              <div className="p-3 bg-purple-100 rounded-full">
                <Tags className="h-6 w-6 text-purple-600" />
              </div>
              <div>
                <p className="text-sm text-gray-500">Total Items</p>
                <p className="text-2xl font-bold">{priceLists.reduce((sum, pl) => sum + pl.items_count, 0)}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
