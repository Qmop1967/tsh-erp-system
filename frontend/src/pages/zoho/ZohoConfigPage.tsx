import { useState } from 'react'
import { Button } from '../../components/ui/button'
import { Input } from '../../components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card'
import { 
  Settings, 
  Cloud, 
  RefreshCw, 
  CheckCircle, 
  AlertCircle,
  XCircle,
  Eye,
  EyeOff,
  Save,
  TestTube
} from 'lucide-react'

interface ZohoConfig {
  organization_id: string
  client_id: string
  client_secret: string
  access_token: string
  refresh_token: string
  books_api_base: string
  inventory_api_base: string
}

export function ZohoConfigPage() {
  const [config, setConfig] = useState<ZohoConfig>({
    organization_id: '',
    client_id: '',
    client_secret: '',
    access_token: '',
    refresh_token: '',
    books_api_base: 'https://www.zohoapis.com/books/v3',
    inventory_api_base: 'https://www.zohoapis.com/inventory/v1'
  })
  
  const [showSecrets, setShowSecrets] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [connectionStatus, setConnectionStatus] = useState<'disconnected' | 'connected' | 'error'>('disconnected')

  const handleInputChange = (field: keyof ZohoConfig, value: string) => {
    setConfig(prev => ({ ...prev, [field]: value }))
  }

  const handleSaveConfig = async () => {
    setIsLoading(true)
    try {
      // Simulate API call to save configuration
      await new Promise(resolve => setTimeout(resolve, 1000))
      setConnectionStatus('connected')
    } catch (error) {
      setConnectionStatus('error')
    } finally {
      setIsLoading(false)
    }
  }

  const handleTestConnection = async () => {
    setIsLoading(true)
    try {
      // Simulate API call to test connection
      await new Promise(resolve => setTimeout(resolve, 2000))
      setConnectionStatus('connected')
    } catch (error) {
      setConnectionStatus('error')
    } finally {
      setIsLoading(false)
    }
  }

  const getStatusIcon = () => {
    switch (connectionStatus) {
      case 'connected':
        return <CheckCircle className="h-5 w-5 text-green-500" />
      case 'error':
        return <XCircle className="h-5 w-5 text-red-500" />
      default:
        return <AlertCircle className="h-5 w-5 text-yellow-500" />
    }
  }

  const getStatusColor = () => {
    switch (connectionStatus) {
      case 'connected':
        return 'border-green-200 bg-green-50 text-green-800'
      case 'error':
        return 'border-red-200 bg-red-50 text-red-800'
      default:
        return 'border-yellow-200 bg-yellow-50 text-yellow-800'
    }
  }

  const getStatusText = () => {
    switch (connectionStatus) {
      case 'connected':
        return 'Connected successfully'
      case 'error':
        return 'Connection failed'
      default:
        return 'Not connected'
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Zoho Integration Configuration</h1>
          <p className="text-gray-600 dark:text-gray-300">
            Configure your Zoho API credentials for Books and Inventory integration
          </p>
        </div>
        <div className="flex items-center gap-2">
          <div className={`flex items-center gap-2 px-3 py-2 rounded-lg border ${getStatusColor()}`}>
            {getStatusIcon()}
            <span className="text-sm font-medium">{getStatusText()}</span>
          </div>
        </div>
      </div>

      {/* Configuration Form */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Basic Configuration */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Settings className="h-5 w-5" />
              Basic Configuration
            </CardTitle>
            <CardDescription>
              Enter your Zoho organization and API credentials
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Organization ID
              </label>
              <Input
                placeholder="Enter your Zoho Organization ID"
                value={config.organization_id}
                onChange={(e) => handleInputChange('organization_id', e.target.value)}
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Client ID
              </label>
              <Input
                placeholder="Enter your Zoho Client ID"
                value={config.client_id}
                onChange={(e) => handleInputChange('client_id', e.target.value)}
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Client Secret
              </label>
              <div className="relative">
                <Input
                  type={showSecrets ? 'text' : 'password'}
                  placeholder="Enter your Zoho Client Secret"
                  value={config.client_secret}
                  onChange={(e) => handleInputChange('client_secret', e.target.value)}
                />
                <button
                  type="button"
                  onClick={() => setShowSecrets(!showSecrets)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
                >
                  {showSecrets ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Token Configuration */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Cloud className="h-5 w-5" />
              Authentication Tokens
            </CardTitle>
            <CardDescription>
              Enter your access and refresh tokens for API authentication
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Access Token
              </label>
              <Input
                type={showSecrets ? 'text' : 'password'}
                placeholder="Enter your Zoho Access Token"
                value={config.access_token}
                onChange={(e) => handleInputChange('access_token', e.target.value)}
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Refresh Token
              </label>
              <Input
                type={showSecrets ? 'text' : 'password'}
                placeholder="Enter your Zoho Refresh Token"
                value={config.refresh_token}
                onChange={(e) => handleInputChange('refresh_token', e.target.value)}
              />
            </div>
            
            <div className="pt-2">
              <Button 
                onClick={handleTestConnection}
                disabled={isLoading}
                className="w-full flex items-center gap-2"
              >
                {isLoading ? (
                  <RefreshCw className="h-4 w-4 animate-spin" />
                ) : (
                  <TestTube className="h-4 w-4" />
                )}
                Test Connection
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* API Endpoints */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <RefreshCw className="h-5 w-5" />
            API Endpoints
          </CardTitle>
          <CardDescription>
            Configure the base URLs for Zoho Books and Inventory APIs
          </CardDescription>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Books API Base URL
            </label>
            <Input
              placeholder="Zoho Books API URL"
              value={config.books_api_base}
              onChange={(e) => handleInputChange('books_api_base', e.target.value)}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Inventory API Base URL
            </label>
            <Input
              placeholder="Zoho Inventory API URL"
              value={config.inventory_api_base}
              onChange={(e) => handleInputChange('inventory_api_base', e.target.value)}
            />
          </div>
        </CardContent>
      </Card>

      {/* Actions */}
      <div className="flex items-center justify-end gap-4">
        <Button variant="outline">
          Reset to Defaults
        </Button>
        <Button 
          onClick={handleSaveConfig}
          disabled={isLoading}
          className="flex items-center gap-2"
        >
          {isLoading ? (
            <RefreshCw className="h-4 w-4 animate-spin" />
          ) : (
            <Save className="h-4 w-4" />
          )}
          Save Configuration
        </Button>
      </div>

      {/* Help Section */}
      <Card className="border-blue-200 bg-blue-50 dark:bg-blue-900/20">
        <CardHeader>
          <CardTitle className="text-blue-800 dark:text-blue-300">
            Need Help?
          </CardTitle>
        </CardHeader>
        <CardContent className="text-blue-700 dark:text-blue-400">
          <p className="mb-2">To get your Zoho API credentials:</p>
          <ol className="list-decimal list-inside space-y-1 text-sm">
            <li>Visit the Zoho Developer Console</li>
            <li>Create a new application or use an existing one</li>
            <li>Generate your Client ID and Client Secret</li>
            <li>Set up OAuth authentication to get Access and Refresh tokens</li>
            <li>Copy your Organization ID from your Zoho account</li>
          </ol>
        </CardContent>
      </Card>
    </div>
  )
}
