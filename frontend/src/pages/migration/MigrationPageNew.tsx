import { useState, useEffect } from 'react'
import { Button } from '../../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card'
import { 
  Download, 
  Upload, 
  RefreshCw, 
  CheckCircle, 
  AlertCircle, 
  Clock,
  Database,
  FileText,
  Users,
  Package
} from 'lucide-react'

// Mock data for migration batches
const mockMigrationBatches = [
  {
    id: 1,
    batch_name: 'Initial Items Migration',
    status: 'COMPLETED',
    source_system: 'Zoho Inventory',
    total_records: 1247,
    processed_records: 1247,
    successful_records: 1235,
    failed_records: 12,
    created_at: '2024-01-15T10:30:00Z',
    completed_at: '2024-01-15T11:45:00Z'
  },
  {
    id: 2,
    batch_name: 'Customer Migration Batch 1',
    status: 'IN_PROGRESS',
    source_system: 'Zoho CRM',
    total_records: 856,
    processed_records: 623,
    successful_records: 620,
    failed_records: 3,
    created_at: '2024-01-16T09:15:00Z',
    completed_at: null
  },
  {
    id: 3,
    batch_name: 'Vendor Migration',
    status: 'PENDING',
    source_system: 'Zoho Books',
    total_records: 234,
    processed_records: 0,
    successful_records: 0,
    failed_records: 0,
    created_at: '2024-01-17T08:00:00Z',
    completed_at: null
  },
  {
    id: 4,
    batch_name: 'Price Lists Migration',
    status: 'FAILED',
    source_system: 'Zoho Inventory',
    total_records: 45,
    processed_records: 12,
    successful_records: 8,
    failed_records: 4,
    created_at: '2024-01-16T14:20:00Z',
    completed_at: '2024-01-16T14:25:00Z'
  }
]

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'COMPLETED':
      return <CheckCircle className="h-4 w-4 text-green-600" />
    case 'IN_PROGRESS':
      return <RefreshCw className="h-4 w-4 text-blue-600 animate-spin" />
    case 'FAILED':
      return <AlertCircle className="h-4 w-4 text-red-600" />
    case 'PENDING':
      return <Clock className="h-4 w-4 text-yellow-600" />
    default:
      return <Clock className="h-4 w-4 text-gray-600" />
  }
}

const getStatusBadge = (status: string) => {
  const styles = {
    'COMPLETED': 'bg-green-100 text-green-800',
    'IN_PROGRESS': 'bg-blue-100 text-blue-800',
    'FAILED': 'bg-red-100 text-red-800',
    'PENDING': 'bg-yellow-100 text-yellow-800'
  }
  
  return (
    <span className={`px-2 py-1 text-xs font-medium rounded-full ${styles[status as keyof typeof styles] || 'bg-gray-100 text-gray-800'}`}>
      {status.replace('_', ' ')}
    </span>
  )
}

export function MigrationPage() {
  const [batches, setBatches] = useState(mockMigrationBatches)
  const [loading, setLoading] = useState(true)
  const [extracting, setExtracting] = useState(false)

  useEffect(() => {
    // Simulate loading
    const timer = setTimeout(() => {
      setLoading(false)
    }, 1000)
    return () => clearTimeout(timer)
  }, [])

  const handleStartExtraction = async (dataType: string) => {
    setExtracting(true)
    // Simulate API call
    setTimeout(() => {
      const newBatch = {
        id: batches.length + 1,
        batch_name: `${dataType} Migration`,
        status: 'IN_PROGRESS',
        source_system: 'Zoho Books/Inventory',
        total_records: Math.floor(Math.random() * 1000) + 100,
        processed_records: 0,
        successful_records: 0,
        failed_records: 0,
        created_at: new Date().toISOString(),
        completed_at: null
      }
      setBatches([newBatch, ...batches])
      setExtracting(false)
    }, 2000)
  }

  // Calculate summary statistics
  const totalBatches = batches.length
  const completedBatches = batches.filter(b => b.status === 'COMPLETED').length
  const inProgressBatches = batches.filter(b => b.status === 'IN_PROGRESS').length
  const totalRecords = batches.reduce((sum, batch) => sum + batch.total_records, 0)
  const successfulRecords = batches.reduce((sum, batch) => sum + batch.successful_records, 0)

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
          <h1 className="text-3xl font-bold text-gray-900">Migration Dashboard</h1>
          <p className="text-gray-600">Manage data migration from Zoho to TSH ERP</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" className="flex items-center gap-2">
            <RefreshCw className="h-4 w-4" />
            Refresh Status
          </Button>
          <Button className="flex items-center gap-2">
            <Download className="h-4 w-4" />
            Export Report
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">
              Total Batches
            </CardTitle>
            <Database className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-900">{totalBatches}</div>
            <p className="text-xs text-gray-500 mt-1">Migration batches created</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">
              Completed
            </CardTitle>
            <CheckCircle className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-900">{completedBatches}</div>
            <p className="text-xs text-gray-500 mt-1">Successfully completed</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">
              In Progress
            </CardTitle>
            <RefreshCw className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-900">{inProgressBatches}</div>
            <p className="text-xs text-gray-500 mt-1">Currently running</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">
              Success Rate
            </CardTitle>
            <FileText className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-900">
              {totalRecords > 0 ? Math.round((successfulRecords / totalRecords) * 100) : 0}%
            </div>
            <p className="text-xs text-gray-500 mt-1">Overall success rate</p>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Quick Migration Actions</CardTitle>
          <CardDescription>Start new data extractions from Zoho systems</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Button 
              onClick={() => handleStartExtraction('Items')}
              disabled={extracting}
              className="flex items-center gap-2 h-auto py-4 flex-col"
            >
              <Package className="h-6 w-6" />
              <span>Extract Items</span>
              <span className="text-xs opacity-75">from Zoho Inventory</span>
            </Button>
            
            <Button 
              onClick={() => handleStartExtraction('Customers')}
              disabled={extracting}
              variant="outline"
              className="flex items-center gap-2 h-auto py-4 flex-col"
            >
              <Users className="h-6 w-6" />
              <span>Extract Customers</span>
              <span className="text-xs opacity-75">from Zoho CRM</span>
            </Button>
            
            <Button 
              onClick={() => handleStartExtraction('Vendors')}
              disabled={extracting}
              variant="outline"
              className="flex items-center gap-2 h-auto py-4 flex-col"
            >
              <Upload className="h-6 w-6" />
              <span>Extract Vendors</span>
              <span className="text-xs opacity-75">from Zoho Books</span>
            </Button>
            
            <Button 
              onClick={() => handleStartExtraction('Price Lists')}
              disabled={extracting}
              variant="outline"
              className="flex items-center gap-2 h-auto py-4 flex-col"
            >
              <FileText className="h-6 w-6" />
              <span>Extract Price Lists</span>
              <span className="text-xs opacity-75">from Zoho Inventory</span>
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Migration Batches */}
      <Card>
        <CardHeader>
          <CardTitle>Migration Batches</CardTitle>
          <CardDescription>Track the progress of your data migration batches</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {batches.map((batch) => (
              <div key={batch.id} className="border rounded-lg p-4 hover:bg-gray-50">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-3">
                    {getStatusIcon(batch.status)}
                    <h3 className="font-medium text-gray-900">{batch.batch_name}</h3>
                    {getStatusBadge(batch.status)}
                  </div>
                  <div className="text-sm text-gray-500">
                    {new Date(batch.created_at).toLocaleDateString()}
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-5 gap-4 text-sm">
                  <div>
                    <span className="text-gray-500">Source:</span>
                    <div className="font-medium">{batch.source_system}</div>
                  </div>
                  <div>
                    <span className="text-gray-500">Total Records:</span>
                    <div className="font-medium">{batch.total_records.toLocaleString()}</div>
                  </div>
                  <div>
                    <span className="text-gray-500">Processed:</span>
                    <div className="font-medium">{batch.processed_records.toLocaleString()}</div>
                  </div>
                  <div>
                    <span className="text-gray-500">Successful:</span>
                    <div className="font-medium text-green-600">{batch.successful_records.toLocaleString()}</div>
                  </div>
                  <div>
                    <span className="text-gray-500">Failed:</span>
                    <div className="font-medium text-red-600">{batch.failed_records.toLocaleString()}</div>
                  </div>
                </div>
                
                {batch.status === 'IN_PROGRESS' && batch.total_records > 0 && (
                  <div className="mt-3">
                    <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
                      <span>Progress</span>
                      <span>{Math.round((batch.processed_records / batch.total_records) * 100)}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full transition-all duration-300" 
                        style={{ width: `${(batch.processed_records / batch.total_records) * 100}%` }}
                      ></div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
