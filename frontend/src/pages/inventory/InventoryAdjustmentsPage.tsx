import { useState, useEffect } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Loading } from '@/components/ui/loading'
import { 
  ClipboardList, 
  Search, 
  Plus, 
  Eye, 
  Edit,
  PlusCircle,
  MinusCircle,
  Package
} from 'lucide-react'

interface InventoryAdjustment {
  id: number
  adjustment_number: string
  warehouse: string
  type: 'increase' | 'decrease' | 'recount'
  reason: string
  items_count: number
  total_value: number
  status: 'draft' | 'pending' | 'approved' | 'rejected'
  created_by: string
  created_at: string
}

export function InventoryAdjustmentsPage() {
  const [adjustments, setAdjustments] = useState<InventoryAdjustment[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    // Simulate loading data
    setTimeout(() => {
      setAdjustments([
        {
          id: 1,
          adjustment_number: 'ADJ-2025-001',
          warehouse: 'المستودع الرئيسي - بغداد',
          type: 'increase',
          reason: 'إضافة مخزون جديد',
          items_count: 15,
          total_value: 2500000,
          status: 'approved',
          created_by: 'أحمد محمد',
          created_at: '2025-06-26'
        },
        {
          id: 2,
          adjustment_number: 'ADJ-2025-002',
          warehouse: 'مستودع البصرة',
          type: 'decrease',
          reason: 'تلف بضاعة',
          items_count: 8,
          total_value: -450000,
          status: 'pending',
          created_by: 'فاطمة علي',
          created_at: '2025-06-25'
        },
        {
          id: 3,
          adjustment_number: 'ADJ-2025-003',
          warehouse: 'المستودع الرئيسي - بغداد',
          type: 'recount',
          reason: 'جرد دوري',
          items_count: 45,
          total_value: -125000,
          status: 'draft',
          created_by: 'محمد حسن',
          created_at: '2025-06-24'
        }
      ])
      setLoading(false)
    }, 1000)
  }, [])

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'increase': return <PlusCircle className="h-5 w-5 text-green-600" />
      case 'decrease': return <MinusCircle className="h-5 w-5 text-red-600" />
      case 'recount': return <ClipboardList className="h-5 w-5 text-blue-600" />
      default: return <Package className="h-5 w-5 text-gray-600" />
    }
  }

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'increase': return 'bg-green-100 text-green-700'
      case 'decrease': return 'bg-red-100 text-red-700'
      case 'recount': return 'bg-blue-100 text-blue-700'
      default: return 'bg-gray-100 text-gray-700'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'draft': return 'bg-gray-100 text-gray-700'
      case 'pending': return 'bg-yellow-100 text-yellow-700'
      case 'approved': return 'bg-green-100 text-green-700'
      case 'rejected': return 'bg-red-100 text-red-700'
      default: return 'bg-gray-100 text-gray-700'
    }
  }

  const formatCurrency = (amount: number) => {
    const isNegative = amount < 0
    const absAmount = Math.abs(amount)
    const formatted = new Intl.NumberFormat('en-US').format(absAmount)
    return `${isNegative ? '-' : ''}${formatted} IQD`
  }

  if (loading) {
    return (
      <div className="p-8">
        <div className="flex justify-center items-center h-64">
          <Loading size="lg" text="Loading inventory adjustments..." />
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
              Inventory Adjustments
            </h1>
            <p className="text-gray-600 text-lg mt-2">Manage stock adjustments and corrections</p>
          </div>
          <Button className="flex items-center space-x-2 bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800">
            <Plus className="h-4 w-4" />
            <span>New Adjustment</span>
          </Button>
        </div>
      </div>

      {/* Search */}
      <div className="mb-6">
        <div className="relative max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
          <Input
            placeholder="Search adjustments..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      {/* Adjustments List */}
      <div className="space-y-4">
        {adjustments.map((adjustment) => (
          <Card key={adjustment.id} className="hover:shadow-lg transition-shadow">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  {getTypeIcon(adjustment.type)}
                  <div>
                    <h3 className="text-lg font-semibold">{adjustment.adjustment_number}</h3>
                    <p className="text-gray-600">{adjustment.warehouse}</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-4">
                  <div className="text-right">
                    <div className="flex items-center space-x-2">
                      <Badge className={getTypeColor(adjustment.type)}>
                        {adjustment.type.charAt(0).toUpperCase() + adjustment.type.slice(1)}
                      </Badge>
                      <Badge className={getStatusColor(adjustment.status)}>
                        {adjustment.status.charAt(0).toUpperCase() + adjustment.status.slice(1)}
                      </Badge>
                    </div>
                    <p className={`text-lg font-bold mt-1 ${adjustment.total_value >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {formatCurrency(adjustment.total_value)}
                    </p>
                  </div>
                  
                  <div className="flex space-x-2">
                    <Button variant="outline" size="sm">
                      <Eye className="h-4 w-4" />
                    </Button>
                    <Button variant="outline" size="sm">
                      <Edit className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
              
              <div className="mt-4 grid grid-cols-4 gap-4 text-sm">
                <div>
                  <span className="text-gray-500">Reason:</span>
                  <p className="font-medium">{adjustment.reason}</p>
                </div>
                <div>
                  <span className="text-gray-500">Items Count:</span>
                  <p className="font-medium">{adjustment.items_count} items</p>
                </div>
                <div>
                  <span className="text-gray-500">Created By:</span>
                  <p className="font-medium">{adjustment.created_by}</p>
                </div>
                <div>
                  <span className="text-gray-500">Date:</span>
                  <p className="font-medium">{adjustment.created_at}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Summary Stats */}
      <div className="mt-8 grid gap-6 md:grid-cols-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-3">
              <div className="p-3 bg-green-100 rounded-full">
                <PlusCircle className="h-6 w-6 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-gray-500">Increases</p>
                <p className="text-2xl font-bold">{adjustments.filter(adj => adj.type === 'increase').length}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-3">
              <div className="p-3 bg-red-100 rounded-full">
                <MinusCircle className="h-6 w-6 text-red-600" />
              </div>
              <div>
                <p className="text-sm text-gray-500">Decreases</p>
                <p className="text-2xl font-bold">{adjustments.filter(adj => adj.type === 'decrease').length}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-3">
              <div className="p-3 bg-blue-100 rounded-full">
                <ClipboardList className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-gray-500">Recounts</p>
                <p className="text-2xl font-bold">{adjustments.filter(adj => adj.type === 'recount').length}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-3">
              <div className="p-3 bg-yellow-100 rounded-full">
                <ClipboardList className="h-6 w-6 text-yellow-600" />
              </div>
              <div>
                <p className="text-sm text-gray-500">Pending</p>
                <p className="text-2xl font-bold">{adjustments.filter(adj => adj.status === 'pending').length}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
