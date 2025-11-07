import { useState } from 'react'
import { useQuery } from 'react-query'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { migrationApi } from '@/lib/api'
import { MigrationBatch } from '@/types'
import { 
  Download, 
  Upload, 
  RefreshCw, 
  CheckCircle, 
  AlertTriangle, 
  Clock,
  Play,
  Settings
} from 'lucide-react'
import { formatDate, getStatusColor } from '@/lib/utils'

export function MigrationPage() {
  const [isExtracting, setIsExtracting] = useState(false)

  const { data: batchesData, isLoading, refetch } = useQuery(
    'migration-batches',
    () => migrationApi.getBatches({ page: 1, limit: 10 }),
    {
      staleTime: 30 * 1000,
    }
  )

  const batches = batchesData?.data?.data || []

  const handleTestConnection = async () => {
    try {
      const response = await migrationApi.testZohoConnection()
      // Handle success
      console.log('Connection test result:', response.data)
    } catch (error) {
      console.error('Connection test failed:', error)
    }
  }

  const handleExtractData = async () => {
    try {
      setIsExtracting(true)
      const response = await migrationApi.extractZohoData({
        data_types: ['items', 'customers', 'vendors'],
        batch_size: 100
      })
      // Handle success
      console.log('Data extraction result:', response.data)
      refetch()
    } catch (error) {
      console.error('Data extraction failed:', error)
    } finally {
      setIsExtracting(false)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'COMPLETED':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'IN_PROGRESS':
        return <Clock className="h-4 w-4 text-blue-500" />
      case 'FAILED':
        return <AlertTriangle className="h-4 w-4 text-red-500" />
      default:
        return <Clock className="h-4 w-4 text-gray-500" />
    }
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Data Migration</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          Import and migrate data from Zoho Books and Zoho Inventory
        </p>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Settings className="h-6 w-6 text-blue-600" />
              </div>
              <div className="flex-1">
                <p className="font-medium">Test Connection</p>
                <p className="text-sm text-gray-500">Verify Zoho API connectivity</p>
              </div>
            </div>
            <Button 
              className="w-full mt-4" 
              variant="outline"
              onClick={handleTestConnection}
            >
              Test Zoho Connection
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-green-100 rounded-lg">
                <Download className="h-6 w-6 text-green-600" />
              </div>
              <div className="flex-1">
                <p className="font-medium">Extract Data</p>
                <p className="text-sm text-gray-500">Pull data from Zoho APIs</p>
              </div>
            </div>
            <Button 
              className="w-full mt-4"
              onClick={handleExtractData}
              disabled={isExtracting}
            >
              {isExtracting ? (
                <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <Download className="h-4 w-4 mr-2" />
              )}
              {isExtracting ? 'Extracting...' : 'Extract Data'}
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Upload className="h-6 w-6 text-purple-600" />
              </div>
              <div className="flex-1">
                <p className="font-medium">Upload File</p>
                <p className="text-sm text-gray-500">Import from CSV/Excel</p>
              </div>
            </div>
            <Button className="w-full mt-4" variant="outline">
              <Upload className="h-4 w-4 mr-2" />
              Upload File
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Migration Batches */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Migration Batches</span>
            <Button variant="outline" size="sm" onClick={() => refetch()}>
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </Button>
          </CardTitle>
          <CardDescription>
            Recent data migration activities
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-4">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="animate-pulse">
                  <div className="h-16 bg-gray-200 rounded-lg"></div>
                </div>
              ))}
            </div>
          ) : batches.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-gray-500">No migration batches found</p>
              <p className="text-sm text-gray-400 mt-1">
                Start by extracting data from Zoho or uploading a file
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {batches.map((batch: MigrationBatch) => (
                <div
                  key={batch.id}
                  className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800"
                >
                  <div className="flex items-center space-x-4">
                    {getStatusIcon(batch.status)}
                    <div>
                      <p className="font-medium">{batch.batchName}</p>
                      <p className="text-sm text-gray-500">
                        {batch.description || 'No description'}
                      </p>
                      <p className="text-xs text-gray-400">
                        Created: {formatDate(batch.createdAt)}
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-4">
                    <div className="text-right">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(batch.status)}`}>
                        {batch.status}
                      </span>
                      <p className="text-xs text-gray-500 mt-1">
                        {batch.successfulRecords}/{batch.totalRecords} records
                      </p>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      {batch.status === 'PENDING' && (
                        <Button size="sm" variant="outline">
                          <Play className="h-4 w-4 mr-1" />
                          Start
                        </Button>
                      )}
                      <Button size="sm" variant="ghost">
                        View Details
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Migration Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg mr-3">
                <Clock className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">3</p>
                <p className="text-sm text-gray-500">Pending</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center">
              <div className="p-2 bg-yellow-100 rounded-lg mr-3">
                <RefreshCw className="h-5 w-5 text-yellow-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">1</p>
                <p className="text-sm text-gray-500">In Progress</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg mr-3">
                <CheckCircle className="h-5 w-5 text-green-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">12</p>
                <p className="text-sm text-gray-500">Completed</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center">
              <div className="p-2 bg-red-100 rounded-lg mr-3">
                <AlertTriangle className="h-5 w-5 text-red-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">2</p>
                <p className="text-sm text-gray-500">Failed</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
