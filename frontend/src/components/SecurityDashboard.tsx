import { useState, useCallback } from 'react'
import { useQuery, useQueryClient, useMutation } from 'react-query'
import axios from 'axios'
import { toast } from 'react-hot-toast'
import { Button } from './ui/button'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import {
  Shield,
  Users,
  AlertTriangle,
  Smartphone,
  Activity,
  Clock,
  CheckCircle,
  XCircle,
  RefreshCw,
  Download
} from 'lucide-react'

// Types
interface SecurityDashboardData {
  active_sessions: number
  failed_logins_24h: number
  open_incidents: number
  mfa_devices: number
  high_risk_sessions: number
  policy_violations_7d: number
  recent_audits: AuditLog[]
  system_health: string
}

interface AuditLog {
  id: number
  user_email: string
  action: string
  resource_type: string
  timestamp: string
  success: boolean
  risk_level: string
  ip_address: string
  location_info?: {
    city: string
    country: string
  }
}

interface SecurityIncident {
  id: number
  title: string
  severity: string
  status: string
  created_at: string
  affected_user_id?: number
  description: string
}

interface UserSession {
  id: string
  user_id: number
  user_email: string
  device_info: any
  location_info: any
  risk_score: number
  last_activity: string
  created_at: string
  expires_at: string
}

interface MFADevice {
  id: number
  user_id: number
  device_name: string
  device_type: string
  last_used: string
  is_active: boolean
  created_at: string
}

// API functions
const securityAPI = {
  getDashboard: () => axios.get('/api/v1/admin/security/dashboard').then(res => res.data),
  getIncidents: () => axios.get('/api/v1/admin/security/incidents').then(res => res.data),
  getSessions: () => axios.get('/api/v1/admin/security/sessions').then(res => res.data),
  getMFADevices: () => axios.get('/api/v1/mfa/devices').then(res => res.data),
  getAuditLogs: (params?: any) => axios.get('/api/v1/admin/security/audit-logs', { params }).then(res => res.data),
  terminateSession: (sessionId: string) => axios.delete(`/api/v1/admin/security/sessions/${sessionId}`),
  updateIncidentStatus: (incidentId: number, status: string, notes?: string) => 
    axios.put(`/api/v1/admin/security/incidents/${incidentId}/status`, { status, notes }),
  exportAuditLogs: (format: string) => axios.get(`/api/v1/admin/security/audit-logs/export?format=${format}`)
}

export function SecurityDashboard() {
  const [activeTab, setActiveTab] = useState('overview')
  const [refreshInterval, setRefreshInterval] = useState(30000) // 30 seconds
  const queryClient = useQueryClient()

  // Queries
  const { data: dashboardData, isLoading: dashboardLoading } = useQuery(
    'security-dashboard',
    securityAPI.getDashboard,
    { 
      refetchInterval: refreshInterval,
      onError: (error) => {
        console.error('Dashboard fetch error:', error)
        toast.error('Failed to load security dashboard')
      }
    }
  )

  const { data: incidents, isLoading: incidentsLoading } = useQuery(
    'security-incidents',
    securityAPI.getIncidents,
    { refetchInterval: refreshInterval }
  )

  const { data: sessions, isLoading: sessionsLoading } = useQuery(
    'security-sessions',
    securityAPI.getSessions,
    { refetchInterval: refreshInterval }
  )

  const { data: mfaDevices, isLoading: mfaLoading } = useQuery(
    'mfa-devices',
    securityAPI.getMFADevices,
    { refetchInterval: refreshInterval }
  )

  const { data: auditLogs, isLoading: auditLoading } = useQuery(
    'audit-logs',
    () => securityAPI.getAuditLogs({ limit: 50 }),
    { refetchInterval: refreshInterval }
  )

  // Mutations
  const terminateSessionMutation = useMutation(securityAPI.terminateSession, {
    onSuccess: () => {
      toast.success('Session terminated successfully')
      queryClient.invalidateQueries('security-sessions')
    },
    onError: () => toast.error('Failed to terminate session')
  })

  const updateIncidentMutation = useMutation(
    ({ incidentId, status, notes }: { incidentId: number, status: string, notes?: string }) =>
      securityAPI.updateIncidentStatus(incidentId, status, notes),
    {
      onSuccess: () => {
        toast.success('Incident updated successfully')
        queryClient.invalidateQueries('security-incidents')
      },
      onError: () => toast.error('Failed to update incident')
    }
  )

  // Auto-refresh control
  const handleRefreshToggle = useCallback(() => {
    if (refreshInterval > 0) {
      setRefreshInterval(0)
      toast.success('Auto-refresh disabled')
    } else {
      setRefreshInterval(30000)
      toast.success('Auto-refresh enabled (30s)')
    }
  }, [refreshInterval])

  const handleManualRefresh = useCallback(() => {
    queryClient.invalidateQueries()
    toast.success('Data refreshed')
  }, [queryClient])

  // Helper functions
  const getRiskColor = (score: number) => {
    if (score >= 0.8) return 'text-red-600'
    if (score >= 0.6) return 'text-orange-600'
    if (score >= 0.3) return 'text-yellow-600'
    return 'text-green-600'
  }

  const getRiskBadgeVariant = (level: string) => {
    switch (level?.toLowerCase()) {
      case 'critical': return 'destructive'
      case 'high': return 'destructive'
      case 'medium': return 'secondary'
      case 'low': return 'outline'
      default: return 'outline'
    }
  }

  const formatTimeAgo = (timestamp: string) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
    const diffMins = Math.floor(diffMs / (1000 * 60))
    
    if (diffHours > 24) {
      return `${Math.floor(diffHours / 24)}d ago`
    } else if (diffHours > 0) {
      return `${diffHours}h ago`
    } else if (diffMins > 0) {
      return `${diffMins}m ago`
    } else {
      return 'Just now'
    }
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Shield className="h-8 w-8 text-blue-600" />
            Security Dashboard
          </h1>
          <p className="text-muted-foreground">
            Monitor and manage system security in real-time
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleRefreshToggle}
            className={refreshInterval > 0 ? 'text-green-600' : 'text-gray-600'}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${refreshInterval > 0 ? 'animate-spin' : ''}`} />
            Auto-refresh {refreshInterval > 0 ? 'On' : 'Off'}
          </Button>
          <Button variant="outline" size="sm" onClick={handleManualRefresh}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Sessions</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboardData?.active_sessions || 0}</div>
            <p className="text-xs text-muted-foreground">Currently logged in</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Failed Logins (24h)</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">
              {dashboardData?.failed_logins_24h || 0}
            </div>
            <p className="text-xs text-muted-foreground">Security attempts blocked</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Open Incidents</CardTitle>
            <Shield className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              {dashboardData?.open_incidents || 0}
            </div>
            <p className="text-xs text-muted-foreground">Require attention</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">MFA Devices</CardTitle>
            <Smartphone className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {dashboardData?.mfa_devices || 0}
            </div>
            <p className="text-xs text-muted-foreground">Registered devices</p>
          </CardContent>
        </Card>
      </div>

      {/* System Health Alert */}
      {dashboardData?.system_health !== 'healthy' && (
        <Alert className="border-orange-200 bg-orange-50">
          <AlertTriangle className="h-4 w-4 text-orange-600" />
          <AlertDescription className="text-orange-800">
            System health status: <strong>{dashboardData?.system_health}</strong>. 
            Please review security incidents and high-risk sessions.
          </AlertDescription>
        </Alert>
      )}

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="sessions">Active Sessions</TabsTrigger>
          <TabsTrigger value="incidents">Security Incidents</TabsTrigger>
          <TabsTrigger value="devices">MFA Devices</TabsTrigger>
          <TabsTrigger value="audit">Audit Logs</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Risk Assessment */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="h-5 w-5" />
                  Risk Assessment
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>High Risk Sessions</span>
                    <span className="font-medium text-red-600">
                      {dashboardData?.high_risk_sessions || 0}
                    </span>
                  </div>
                  <Progress 
                    value={(dashboardData?.high_risk_sessions || 0) * 10} 
                    className="h-2" 
                  />
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Policy Violations (7d)</span>
                    <span className="font-medium text-orange-600">
                      {dashboardData?.policy_violations_7d || 0}
                    </span>
                  </div>
                  <Progress 
                    value={(dashboardData?.policy_violations_7d || 0) * 5} 
                    className="h-2" 
                  />
                </div>
              </CardContent>
            </Card>

            {/* Recent Activity */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Clock className="h-5 w-5" />
                  Recent Activity
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-48">
                  <div className="space-y-2">
                    {dashboardData?.recent_audits?.slice(0, 5).map((log: AuditLog) => (
                      <div key={log.id} className="flex items-center justify-between py-2">
                        <div className="flex items-center gap-2">
                          {log.success ? (
                            <CheckCircle className="h-4 w-4 text-green-600" />
                          ) : (
                            <XCircle className="h-4 w-4 text-red-600" />
                          )}
                          <div>
                            <p className="text-sm font-medium">{log.action}</p>
                            <p className="text-xs text-muted-foreground">
                              {log.user_email} • {formatTimeAgo(log.timestamp)}
                            </p>
                          </div>
                        </div>
                        <Badge variant={getRiskBadgeVariant(log.risk_level)}>
                          {log.risk_level}
                        </Badge>
                      </div>
                    )) || (
                      <p className="text-sm text-muted-foreground">No recent activity</p>
                    )}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Active Sessions Tab */}
        <TabsContent value="sessions" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Active User Sessions</CardTitle>
              <CardDescription>
                Monitor and manage active user sessions across the system
              </CardDescription>
            </CardHeader>
            <CardContent>
              {sessionsLoading ? (
                <div className="flex items-center justify-center py-8">
                  <RefreshCw className="h-6 w-6 animate-spin" />
                </div>
              ) : (
                <ScrollArea className="h-96">
                  <div className="space-y-4">
                    {sessions?.map((session: UserSession) => (
                      <div key={session.id} className="border rounded-lg p-4 space-y-2">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <div className={`w-3 h-3 rounded-full ${
                              session.risk_score >= 0.7 ? 'bg-red-500' : 
                              session.risk_score >= 0.4 ? 'bg-orange-500' : 'bg-green-500'
                            }`} />
                            <span className="font-medium">{session.user_email}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <Badge className={getRiskColor(session.risk_score)}>
                              Risk: {Math.round(session.risk_score * 100)}%
                            </Badge>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => terminateSessionMutation.mutate(session.id)}
                              disabled={terminateSessionMutation.isLoading}
                            >
                              <XCircle className="h-4 w-4 mr-1" />
                              Terminate
                            </Button>
                          </div>
                        </div>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-muted-foreground">
                          <div>
                            <span className="font-medium">Device:</span>
                            <br />
                            {session.device_info?.deviceName || 'Unknown'}
                          </div>
                          <div>
                            <span className="font-medium">Location:</span>
                            <br />
                            {session.location_info ? 
                              `${session.location_info.city}, ${session.location_info.country}` : 
                              'Unknown'
                            }
                          </div>
                          <div>
                            <span className="font-medium">Last Activity:</span>
                            <br />
                            {formatTimeAgo(session.last_activity)}
                          </div>
                          <div>
                            <span className="font-medium">Expires:</span>
                            <br />
                            {formatTimeAgo(session.expires_at)}
                          </div>
                        </div>
                      </div>
                    )) || (
                      <p className="text-center text-muted-foreground py-8">
                        No active sessions found
                      </p>
                    )}
                  </div>
                </ScrollArea>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Security Incidents Tab */}
        <TabsContent value="incidents" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Security Incidents</CardTitle>
              <CardDescription>
                Track and manage security incidents and threats
              </CardDescription>
            </CardHeader>
            <CardContent>
              {incidentsLoading ? (
                <div className="flex items-center justify-center py-8">
                  <RefreshCw className="h-6 w-6 animate-spin" />
                </div>
              ) : (
                <ScrollArea className="h-96">
                  <div className="space-y-4">
                    {incidents?.map((incident: SecurityIncident) => (
                      <div key={incident.id} className="border rounded-lg p-4 space-y-2">
                        <div className="flex items-center justify-between">
                          <h4 className="font-medium">{incident.title}</h4>
                          <div className="flex items-center gap-2">
                            <Badge variant={
                              incident.severity === 'critical' ? 'destructive' :
                              incident.severity === 'high' ? 'destructive' :
                              incident.severity === 'medium' ? 'secondary' : 'outline'
                            }>
                              {incident.severity}
                            </Badge>
                            <Badge variant={
                              incident.status === 'open' ? 'destructive' :
                              incident.status === 'investigating' ? 'secondary' : 'outline'
                            }>
                              {incident.status}
                            </Badge>
                          </div>
                        </div>
                        <p className="text-sm text-muted-foreground">
                          {incident.description}
                        </p>
                        <div className="flex items-center justify-between text-xs text-muted-foreground">
                          <span>Created: {formatTimeAgo(incident.created_at)}</span>
                          <div className="flex gap-2">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => updateIncidentMutation.mutate({
                                incidentId: incident.id,
                                status: 'investigating'
                              })}
                              disabled={updateIncidentMutation.isLoading}
                            >
                              Investigate
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => updateIncidentMutation.mutate({
                                incidentId: incident.id,
                                status: 'resolved'
                              })}
                              disabled={updateIncidentMutation.isLoading}
                            >
                              Resolve
                            </Button>
                          </div>
                        </div>
                      </div>
                    )) || (
                      <p className="text-center text-muted-foreground py-8">
                        No security incidents found
                      </p>
                    )}
                  </div>
                </ScrollArea>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* MFA Devices Tab */}
        <TabsContent value="devices" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>MFA Devices</CardTitle>
              <CardDescription>
                Registered multi-factor authentication devices
              </CardDescription>
            </CardHeader>
            <CardContent>
              {mfaLoading ? (
                <div className="flex items-center justify-center py-8">
                  <RefreshCw className="h-6 w-6 animate-spin" />
                </div>
              ) : (
                <ScrollArea className="h-96">
                  <div className="space-y-4">
                    {mfaDevices?.map((device: MFADevice) => (
                      <div key={device.id} className="border rounded-lg p-4 space-y-2">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <Smartphone className="h-4 w-4" />
                            <span className="font-medium">{device.device_name}</span>
                          </div>
                          <Badge variant={device.is_active ? 'default' : 'secondary'}>
                            {device.is_active ? 'Active' : 'Inactive'}
                          </Badge>
                        </div>
                        <div className="grid grid-cols-3 gap-4 text-sm text-muted-foreground">
                          <div>
                            <span className="font-medium">Type:</span>
                            <br />
                            {device.device_type}
                          </div>
                          <div>
                            <span className="font-medium">Last Used:</span>
                            <br />
                            {device.last_used ? formatTimeAgo(device.last_used) : 'Never'}
                          </div>
                          <div>
                            <span className="font-medium">Registered:</span>
                            <br />
                            {formatTimeAgo(device.created_at)}
                          </div>
                        </div>
                      </div>
                    )) || (
                      <p className="text-center text-muted-foreground py-8">
                        No MFA devices found
                      </p>
                    )}
                  </div>
                </ScrollArea>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Audit Logs Tab */}
        <TabsContent value="audit" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                Audit Logs
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    securityAPI.exportAuditLogs('csv')
                      .then(() => toast.success('Audit logs exported'))
                      .catch(() => toast.error('Export failed'))
                  }}
                >
                  <Download className="h-4 w-4 mr-2" />
                  Export
                </Button>
              </CardTitle>
              <CardDescription>
                Complete audit trail of system activities
              </CardDescription>
            </CardHeader>
            <CardContent>
              {auditLoading ? (
                <div className="flex items-center justify-center py-8">
                  <RefreshCw className="h-6 w-6 animate-spin" />
                </div>
              ) : (
                <ScrollArea className="h-96">
                  <div className="space-y-2">
                    {auditLogs?.map((log: AuditLog) => (
                      <div key={log.id} className="border-b pb-2 last:border-b-0">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            {log.success ? (
                              <CheckCircle className="h-4 w-4 text-green-600" />
                            ) : (
                              <XCircle className="h-4 w-4 text-red-600" />
                            )}
                            <span className="font-medium">{log.action}</span>
                            <Badge variant="outline">{log.resource_type}</Badge>
                          </div>
                          <div className="flex items-center gap-2">
                            <Badge variant={getRiskBadgeVariant(log.risk_level)}>
                              {log.risk_level}
                            </Badge>
                            <span className="text-xs text-muted-foreground">
                              {formatTimeAgo(log.timestamp)}
                            </span>
                          </div>
                        </div>
                        <div className="mt-1 text-sm text-muted-foreground">
                          <span className="font-medium">{log.user_email}</span>
                          {log.ip_address && <span> • {log.ip_address}</span>}
                          {log.location_info && (
                            <span> • {log.location_info.city}, {log.location_info.country}</span>
                          )}
                        </div>
                      </div>
                    )) || (
                      <p className="text-center text-muted-foreground py-8">
                        No audit logs found
                      </p>
                    )}
                  </div>
                </ScrollArea>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
