import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useAuthStore } from '@/stores/authStore'
import axios from 'axios'
import { Shield, Filter, RefreshCw, Download, AlertCircle, Info, AlertTriangle } from 'lucide-react'

interface AuditLogEntry {
  id: number
  user_id?: number
  user_email?: string
  event_type: string
  severity: 'info' | 'warning' | 'critical'
  ip_address: string
  user_agent: string
  event_metadata: any
  created_at: string
}

interface FilterOptions {
  event_type: string
  severity: string
  date_from: string
  date_to: string
  search: string
}

export function AuditLogViewer() {
  const { token } = useAuthStore()
  const [logs, setLogs] = useState<AuditLogEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [filters, setFilters] = useState<FilterOptions>({
    event_type: '',
    severity: '',
    date_from: '',
    date_to: '',
    search: ''
  })
  const [showFilters, setShowFilters] = useState(false)

  useEffect(() => {
    loadAuditLogs()
  }, [])

  const loadAuditLogs = async () => {
    try {
      setLoading(true)
      setError('')

      const params = new URLSearchParams()
      if (filters.event_type) params.append('event_type', filters.event_type)
      if (filters.severity) params.append('severity', filters.severity)
      if (filters.date_from) params.append('date_from', filters.date_from)
      if (filters.date_to) params.append('date_to', filters.date_to)
      if (filters.search) params.append('search', filters.search)

      const response = await axios.get(
        `http://localhost:8000/api/auth/audit-log?${params.toString()}`,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      )

      setLogs(response.data.events || [])
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load audit logs')
      console.error('Audit log error:', err)
    } finally {
      setLoading(false)
    }
  }

  const exportLogs = () => {
    const csvContent = [
      ['Timestamp', 'User', 'Event Type', 'Severity', 'IP Address', 'Details'].join(','),
      ...logs.map(log => [
        new Date(log.created_at).toISOString(),
        log.user_email || 'System',
        log.event_type,
        log.severity,
        log.ip_address,
        JSON.stringify(log.event_metadata || {}).replace(/,/g, ';')
      ].join(','))
    ].join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `audit-log-${new Date().toISOString().split('T')[0]}.csv`
    a.click()
  }

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return <AlertCircle className="w-4 h-4 text-red-600" />
      case 'warning':
        return <AlertTriangle className="w-4 h-4 text-yellow-600" />
      case 'info':
        return <Info className="w-4 h-4 text-blue-600" />
      default:
        return <Info className="w-4 h-4 text-gray-600" />
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-50 border-red-200 text-red-800'
      case 'warning':
        return 'bg-yellow-50 border-yellow-200 text-yellow-800'
      case 'info':
        return 'bg-blue-50 border-blue-200 text-blue-800'
      default:
        return 'bg-gray-50 border-gray-200 text-gray-800'
    }
  }

  const formatEventType = (eventType: string) => {
    return eventType
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ')
  }

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp)
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  }

  const getTimeAgo = (timestamp: string) => {
    const date = new Date(timestamp)
    const now = new Date()
    const seconds = Math.floor((now.getTime() - date.getTime()) / 1000)

    if (seconds < 60) return `${seconds}s ago`
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`
    return `${Math.floor(seconds / 86400)}d ago`
  }

  const eventTypes = [
    'successful_login',
    'failed_login',
    'logout',
    'mfa_enabled',
    'mfa_disabled',
    'mfa_verification_failed',
    'account_locked',
    'account_unlocked',
    'password_changed',
    'password_reset_requested',
    'session_created',
    'session_terminated',
    'suspicious_activity'
  ]

  return (
    <div className="container max-w-7xl mx-auto py-8 px-4">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Shield className="w-6 h-6" />
                Security Audit Log
              </CardTitle>
              <CardDescription>
                Monitor all security-related events and activities
              </CardDescription>
            </div>
            <div className="flex items-center gap-2">
              <Button
                onClick={() => setShowFilters(!showFilters)}
                variant="outline"
                size="sm"
              >
                <Filter className="w-4 h-4 mr-2" />
                {showFilters ? 'Hide' : 'Show'} Filters
              </Button>
              <Button
                onClick={loadAuditLogs}
                variant="outline"
                size="sm"
                disabled={loading}
              >
                <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
              <Button
                onClick={exportLogs}
                variant="outline"
                size="sm"
                disabled={logs.length === 0}
              >
                <Download className="w-4 h-4 mr-2" />
                Export CSV
              </Button>
            </div>
          </div>
        </CardHeader>

        <CardContent>
          {/* Filters Panel */}
          {showFilters && (
            <div className="mb-6 p-4 bg-gray-50 rounded-lg border space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="text-sm font-medium mb-1 block">Event Type</label>
                  <select
                    value={filters.event_type}
                    onChange={(e) => setFilters({ ...filters, event_type: e.target.value })}
                    className="w-full px-3 py-2 border rounded-md"
                  >
                    <option value="">All Events</option>
                    {eventTypes.map(type => (
                      <option key={type} value={type}>{formatEventType(type)}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="text-sm font-medium mb-1 block">Severity</label>
                  <select
                    value={filters.severity}
                    onChange={(e) => setFilters({ ...filters, severity: e.target.value })}
                    className="w-full px-3 py-2 border rounded-md"
                  >
                    <option value="">All Severities</option>
                    <option value="info">Info</option>
                    <option value="warning">Warning</option>
                    <option value="critical">Critical</option>
                  </select>
                </div>

                <div>
                  <label className="text-sm font-medium mb-1 block">Search</label>
                  <Input
                    type="text"
                    placeholder="Search user, IP, or details..."
                    value={filters.search}
                    onChange={(e) => setFilters({ ...filters, search: e.target.value })}
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium mb-1 block">Date From</label>
                  <Input
                    type="datetime-local"
                    value={filters.date_from}
                    onChange={(e) => setFilters({ ...filters, date_from: e.target.value })}
                  />
                </div>

                <div>
                  <label className="text-sm font-medium mb-1 block">Date To</label>
                  <Input
                    type="datetime-local"
                    value={filters.date_to}
                    onChange={(e) => setFilters({ ...filters, date_to: e.target.value })}
                  />
                </div>
              </div>

              <div className="flex justify-end gap-2">
                <Button
                  onClick={() => setFilters({
                    event_type: '',
                    severity: '',
                    date_from: '',
                    date_to: '',
                    search: ''
                  })}
                  variant="outline"
                  size="sm"
                >
                  Clear Filters
                </Button>
                <Button onClick={loadAuditLogs} size="sm">
                  Apply Filters
                </Button>
              </div>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4 text-red-800">
              {error}
            </div>
          )}

          {/* Loading State */}
          {loading && logs.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto mb-4"></div>
              Loading audit logs...
            </div>
          ) : logs.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <Shield className="w-12 h-12 mx-auto mb-4 text-gray-400" />
              <p className="text-lg font-medium">No audit logs found</p>
              <p className="text-sm">Try adjusting your filters or check back later</p>
            </div>
          ) : (
            <>
              {/* Summary Stats */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-1">
                    <Info className="w-4 h-4 text-blue-600" />
                    <span className="text-sm font-medium text-blue-900">Info</span>
                  </div>
                  <p className="text-2xl font-bold text-blue-900">
                    {logs.filter(log => log.severity === 'info').length}
                  </p>
                </div>

                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-1">
                    <AlertTriangle className="w-4 h-4 text-yellow-600" />
                    <span className="text-sm font-medium text-yellow-900">Warning</span>
                  </div>
                  <p className="text-2xl font-bold text-yellow-900">
                    {logs.filter(log => log.severity === 'warning').length}
                  </p>
                </div>

                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-1">
                    <AlertCircle className="w-4 h-4 text-red-600" />
                    <span className="text-sm font-medium text-red-900">Critical</span>
                  </div>
                  <p className="text-2xl font-bold text-red-900">
                    {logs.filter(log => log.severity === 'critical').length}
                  </p>
                </div>

                <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-1">
                    <Shield className="w-4 h-4 text-gray-600" />
                    <span className="text-sm font-medium text-gray-900">Total Events</span>
                  </div>
                  <p className="text-2xl font-bold text-gray-900">{logs.length}</p>
                </div>
              </div>

              {/* Audit Log Table */}
              <div className="space-y-2">
                {logs.map((log) => (
                  <Card
                    key={log.id}
                    className={`border ${getSeverityColor(log.severity)}`}
                  >
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between">
                        <div className="flex items-start gap-3 flex-1">
                          <div className="mt-1">
                            {getSeverityIcon(log.severity)}
                          </div>

                          <div className="flex-1 space-y-1">
                            <div className="flex items-center gap-2">
                              <h3 className="font-semibold">
                                {formatEventType(log.event_type)}
                              </h3>
                              <span className={`px-2 py-0.5 rounded text-xs font-medium ${getSeverityColor(log.severity)}`}>
                                {log.severity.toUpperCase()}
                              </span>
                            </div>

                            <div className="text-sm space-y-1">
                              <div className="flex items-center gap-4 text-gray-600">
                                <span>
                                  <span className="font-medium">User:</span>{' '}
                                  {log.user_email || 'System'}
                                </span>
                                <span>
                                  <span className="font-medium">IP:</span> {log.ip_address}
                                </span>
                                <span>
                                  <span className="font-medium">Time:</span>{' '}
                                  {getTimeAgo(log.created_at)}
                                </span>
                              </div>

                              {log.event_metadata && Object.keys(log.event_metadata).length > 0 && (
                                <details className="text-xs text-gray-600">
                                  <summary className="cursor-pointer hover:text-gray-800">
                                    View details
                                  </summary>
                                  <pre className="mt-2 p-2 bg-white rounded border">
                                    {JSON.stringify(log.event_metadata, null, 2)}
                                  </pre>
                                </details>
                              )}
                            </div>
                          </div>
                        </div>

                        <div className="text-right text-xs text-gray-500">
                          {formatTimestamp(log.created_at)}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>

              {/* Load More Button */}
              {logs.length >= 50 && (
                <div className="text-center mt-6">
                  <Button onClick={loadAuditLogs} variant="outline">
                    Load More
                  </Button>
                </div>
              )}
            </>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

export default AuditLogViewer
