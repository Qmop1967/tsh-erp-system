import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Loading } from '@/components/ui/loading'
import { 
  FileText, 
  Search, 
  Plus, 
  Eye, 
  Edit,
  Trash2,
  Filter
} from 'lucide-react'

interface SalesOrder {
  id: number
  order_number: string
  customer_name: string
  order_date: string
  status: string
  total_amount: number
  currency: string
}

export function SalesOrdersPage() {
  const [orders, setOrders] = useState<SalesOrder[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    // Simulate loading data
    setTimeout(() => {
      setOrders([
        {
          id: 1,
          order_number: 'SO-2025-001',
          customer_name: 'أحمد محمد العراقي',
          order_date: '2025-06-26',
          status: 'pending',
          total_amount: 1250000,
          currency: 'IQD'
        },
        {
          id: 2,
          order_number: 'SO-2025-002',
          customer_name: 'شركة التجارة العامة',
          order_date: '2025-06-25',
          status: 'confirmed',
          total_amount: 850,
          currency: 'USD'
        }
      ])
      setLoading(false)
    }, 1000)
  }, [])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'bg-yellow-100 text-yellow-700'
      case 'confirmed': return 'bg-green-100 text-green-700'
      case 'shipped': return 'bg-blue-100 text-blue-700'
      case 'delivered': return 'bg-purple-100 text-purple-700'
      case 'cancelled': return 'bg-red-100 text-red-700'
      default: return 'bg-gray-100 text-gray-700'
    }
  }

  const formatCurrency = (amount: number, currency: string) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency === 'IQD' ? 'USD' : currency,
      minimumFractionDigits: 0
    }).format(amount).replace('$', currency === 'IQD' ? 'IQD ' : '$')
  }

  if (loading) {
    return (
      <div className="p-8">
        <div className="flex justify-center items-center h-64">
          <Loading size="lg" text="Loading sales orders..." />
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
              Sales Orders
            </h1>
            <p className="text-gray-600 text-lg mt-2">Manage and track sales orders</p>
          </div>
          <Button className="flex items-center space-x-2 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800">
            <Plus className="h-4 w-4" />
            <span>New Sales Order</span>
          </Button>
        </div>
      </div>

      {/* Filters */}
      <div className="mb-6 flex flex-wrap gap-4">
        <div className="relative flex-1 min-w-[300px]">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
          <Input
            placeholder="Search orders by number, customer..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        <Button variant="outline" className="flex items-center space-x-2">
          <Filter className="h-4 w-4" />
          <span>Filter</span>
        </Button>
      </div>

      {/* Orders Grid */}
      <div className="grid gap-6">
        {orders.map((order) => (
          <Card key={order.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center space-x-2">
                    <FileText className="h-5 w-5 text-blue-600" />
                    <span>{order.order_number}</span>
                  </CardTitle>
                  <CardDescription>{order.customer_name}</CardDescription>
                </div>
                <Badge className={getStatusColor(order.status)}>
                  {order.status.charAt(0).toUpperCase() + order.status.slice(1)}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-500">Order Date:</span>
                    <p className="font-medium">{order.order_date}</p>
                  </div>
                  <div>
                    <span className="text-gray-500">Total Amount:</span>
                    <p className="font-medium text-green-600">
                      {formatCurrency(order.total_amount, order.currency)}
                    </p>
                  </div>
                </div>
                <div className="flex space-x-2">
                  <Button variant="outline" size="sm">
                    <Eye className="h-4 w-4" />
                  </Button>
                  <Button variant="outline" size="sm">
                    <Edit className="h-4 w-4" />
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
    </div>
  )
}
