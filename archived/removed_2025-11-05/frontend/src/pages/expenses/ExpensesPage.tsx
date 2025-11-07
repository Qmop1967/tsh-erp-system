import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Loading } from '@/components/ui/loading'
import { useBranchAwareApi } from '@/hooks/useBranchAwareApi'
import { expensesApi } from '@/lib/api'
import { 
  Receipt, 
  Plus, 
  Search, 
  Calendar,
  DollarSign,
  TrendingUp,
  FileText
} from 'lucide-react'

interface Expense {
  id: number
  expense_number: string
  title: string
  description?: string
  category: string
  amount: number
  total_amount: number
  expense_date: string
  status: string
  created_at: string
}

export function ExpensesPage() {
  const [expenses, setExpenses] = useState<Expense[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedStatus, setSelectedStatus] = useState<string>('all')
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const { getBranchParams, useBranchChangeEffect, currentBranch } = useBranchAwareApi()

  // Fetch expenses with branch awareness
  const fetchExpenses = async () => {
    try {
      setLoading(true)
      const params = getBranchParams({ 
        search: searchTerm,
        status: selectedStatus !== 'all' ? selectedStatus : undefined,
        category_id: selectedCategory !== 'all' ? selectedCategory : undefined
      })
      
      try {
        const response = await expensesApi.getExpenses(params)
        setExpenses(response.data.data || [])
      } catch (apiError) {
        console.warn('API not available, using sample data:', apiError)
        // Fallback to sample data
        const sampleExpenses: Expense[] = [
          {
            id: 1,
            expense_number: 'EXP-001',
            title: `Office Supplies Purchase ${currentBranch ? `- ${currentBranch.nameEn}` : ''}`,
            description: 'Monthly office supplies including stationery and printer supplies',
            category: 'OFFICE_SUPPLIES',
            amount: 450.00,
            total_amount: 450.00,
            expense_date: '2024-01-15',
            status: 'APPROVED',
            created_at: '2024-01-15T10:30:00Z'
          },
          {
            id: 2,
            expense_number: 'EXP-002',
            title: `Equipment Maintenance ${currentBranch ? `- ${currentBranch.nameEn}` : ''}`,
            description: 'Monthly maintenance for office equipment and machinery',
            category: 'MAINTENANCE',
            amount: 1200.00,
            total_amount: 1200.00,
            expense_date: '2024-01-10',
            status: 'PENDING',
            created_at: '2024-01-10T14:20:00Z'
          },
          {
            id: 3,
            expense_number: 'EXP-003',
            title: `Marketing Campaign ${currentBranch ? `- ${currentBranch.nameEn}` : ''}`,
            description: 'Digital marketing campaign for product promotion',
            category: 'MARKETING',
            amount: 2500.00,
            total_amount: 2500.00,
            expense_date: '2024-01-08',
            status: 'PAID',
            created_at: '2024-01-08T16:45:00Z'
          }
        ]
        setExpenses(sampleExpenses)
      }
    } catch (error) {
      console.error('Error fetching expenses:', error)
    } finally {
      setLoading(false)
    }
  }

  // Fetch data when component mounts or branch changes
  useBranchChangeEffect(() => {
    fetchExpenses()
  }, [searchTerm, selectedStatus, selectedCategory])

  const getStatusColor = (status: string) => {
    const colors = {
      DRAFT: 'bg-gray-100 text-gray-700',
      PENDING: 'bg-yellow-100 text-yellow-700',
      APPROVED: 'bg-blue-100 text-blue-700',
      PAID: 'bg-green-100 text-green-700',
      REJECTED: 'bg-red-100 text-red-700',
      CANCELLED: 'bg-gray-100 text-gray-700',
    }
    return colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-700'
  }

  const getCategoryLabel = (category: string) => {
    return category.replace(/_/g, ' ').toLowerCase().replace(/\b\w/g, l => l.toUpperCase())
  }

  const filteredExpenses = expenses.filter(expense => {
    const matchesSearch = expense.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         expense.expense_number.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = selectedStatus === 'all' || expense.status === selectedStatus
    const matchesCategory = selectedCategory === 'all' || expense.category === selectedCategory
    return matchesSearch && matchesStatus && matchesCategory
  })

  const totalAmount = expenses.reduce((sum, expense) => sum + expense.total_amount, 0)
  const approvedAmount = expenses
    .filter(e => e.status === 'APPROVED' || e.status === 'PAID')
    .reduce((sum, expense) => sum + expense.total_amount, 0)

  if (loading) {
    return <Loading />
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Expenses Management</h1>
          <p className="text-gray-500 mt-1">Track and manage company expenses</p>
        </div>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          Add Expense
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Expenses</p>
                <p className="text-2xl font-bold text-gray-900">${totalAmount.toFixed(2)}</p>
              </div>
              <DollarSign className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Approved</p>
                <p className="text-2xl font-bold text-green-600">${approvedAmount.toFixed(2)}</p>
              </div>
              <TrendingUp className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Pending</p>
                <p className="text-2xl font-bold text-yellow-600">
                  {expenses.filter(e => e.status === 'PENDING').length}
                </p>
              </div>
              <Calendar className="h-8 w-8 text-yellow-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">This Month</p>
                <p className="text-2xl font-bold text-gray-900">{expenses.length}</p>
              </div>
              <FileText className="h-8 w-8 text-gray-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <Input
                  placeholder="Search expenses..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Status</option>
              <option value="DRAFT">Draft</option>
              <option value="PENDING">Pending</option>
              <option value="APPROVED">Approved</option>
              <option value="PAID">Paid</option>
              <option value="REJECTED">Rejected</option>
            </select>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Categories</option>
              <option value="OFFICE_SUPPLIES">Office Supplies</option>
              <option value="TRAVEL">Travel</option>
              <option value="UTILITIES">Utilities</option>
              <option value="RENT">Rent</option>
              <option value="INSURANCE">Insurance</option>
              <option value="OTHER">Other</option>
            </select>
          </div>
        </CardContent>
      </Card>

      {/* Expenses List */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Expenses</CardTitle>
          <CardDescription>
            View and manage all company expenses
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {filteredExpenses.map((expense) => (
              <div
                key={expense.id}
                className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-center space-x-4">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <Receipt className="h-5 w-5 text-blue-600" />
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-900">{expense.title}</h3>
                    <p className="text-sm text-gray-500">{expense.expense_number}</p>
                    <p className="text-sm text-gray-600 mt-1">{expense.description}</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-4">
                  <div className="text-right">
                    <p className="font-medium text-gray-900">${expense.total_amount.toFixed(2)}</p>
                    <p className="text-sm text-gray-500">{getCategoryLabel(expense.category)}</p>
                  </div>
                  <Badge className={getStatusColor(expense.status)}>
                    {expense.status}
                  </Badge>
                </div>
              </div>
            ))}
            
            {filteredExpenses.length === 0 && (
              <div className="text-center py-8">
                <Receipt className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No expenses found</h3>
                <p className="text-gray-500">Try adjusting your search or filter criteria.</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default ExpensesPage
