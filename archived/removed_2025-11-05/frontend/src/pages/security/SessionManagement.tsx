import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { useAuthStore } from '@/stores/authStore'
import axios from 'axios'
import { Laptop, Smartphone, Tablet, Globe, Clock, MapPin, AlertTriangle, CheckCircle } from 'lucide-react'

interface Session {
  id: number
  device_name: string
  device_type: string
  ip_address: string
  last_activity: string
  created_at: string
  is_current: boolean
}

export function SessionManagement() {
  const { token } = useAuthStore()
  const [sessions, setSessions] = useState<Session[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [terminatingId, setTerminatingId] = useState<number | null>(null)

  useEffect(() => {
    loadSessions()
  }, [])

  const loadSessions = async () => {
    try {
      setLoading(true)
      const response = await axios.get(
        'http://localhost:8000/api/auth/sessions',
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      )

      setSessions(response.data.sessions)
      setError('')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load sessions')
    } finally {
      setLoading(false)
    }
  }

  const terminateSession = async (sessionId: number) => {
    if (!confirm('Are you sure you want to terminate this session?')) return

    try {
      setTerminatingId(sessionId)
      await axios.delete(
        `http://localhost:8000/api/auth/sessions/${sessionId}`,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      )

      await loadSessions()
      alert('Session terminated successfully')
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to terminate session')
    } finally {
      setTerminatingId(null)
    }
  }

  const terminateAllOthers = async () => {
    if (!confirm('This will log you out of all other devices. Continue?')) return

    try {
      setLoading(true)
      await axios.post(
        'http://localhost:8000/api/auth/sessions/terminate-all',
        null,
        {
          params: { except_current: true },
          headers: { Authorization: `Bearer ${token}` }
        }
      )

      await loadSessions()
      alert('All other sessions terminated successfully')
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to terminate sessions')
    } finally {
      setLoading(false)
    }
  }

  const getDeviceIcon = (deviceType: string) => {
    switch (deviceType?.toLowerCase()) {
      case 'mobile':
        return <Smartphone className="w-5 h-5" />
      case 'tablet':
        return <Tablet className="w-5 h-5" />
      case 'web':
        return <Laptop className="w-5 h-5" />
      default:
        return <Globe className="w-5 h-5" />
    }
  }

  const formatDateTime = (dateString: string) => {
    if (!dateString) return 'Unknown'
    const date = new Date(dateString)
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getTimeAgo = (dateString: string) => {
    if (!dateString) return 'Unknown'
    const date = new Date(dateString)
    const now = new Date()
    const seconds = Math.floor((now.getTime() - date.getTime()) / 1000)

    if (seconds < 60) return 'Just now'
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`
    return `${Math.floor(seconds / 86400)}d ago`
  }

  return (
    <div className="container max-w-4xl mx-auto py-8 px-4">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span className="flex items-center gap-2">
              <Globe className="w-6 h-6" />
              Active Sessions
            </span>
            {sessions.length > 1 && (
              <Button
                onClick={terminateAllOthers}
                variant="destructive"
                size="sm"
                disabled={loading}
              >
                <AlertTriangle className="w-4 h-4 mr-2" />
                Logout All Others
              </Button>
            )}
          </CardTitle>
          <CardDescription>
            Manage devices that are signed into your account
          </CardDescription>
        </CardHeader>
        <CardContent>
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4 text-red-800">
              {error}
            </div>
          )}

          {loading && sessions.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto mb-4"></div>
              Loading sessions...
            </div>
          ) : (
            <div className="space-y-4">
              {sessions.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  No active sessions found
                </div>
              ) : (
                sessions.map((session) => (
                  <Card
                    key={session.id}
                    className={`${
                      session.is_current
                        ? 'border-2 border-green-500 bg-green-50'
                        : 'border-gray-200'
                    }`}
                  >
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between">
                        <div className="flex items-start gap-3">
                          <div
                            className={`p-2 rounded-lg ${
                              session.is_current ? 'bg-green-200' : 'bg-gray-200'
                            }`}
                          >
                            {getDeviceIcon(session.device_type)}
                          </div>

                          <div className="space-y-1">
                            <div className="flex items-center gap-2">
                              <h3 className="font-semibold">
                                {session.device_name || 'Unknown Device'}
                              </h3>
                              {session.is_current && (
                                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-green-600 text-white">
                                  <CheckCircle className="w-3 h-3" />
                                  Current
                                </span>
                              )}
                            </div>

                            <div className="text-sm text-gray-600 space-y-1">
                              <div className="flex items-center gap-2">
                                <MapPin className="w-4 h-4" />
                                <span>{session.ip_address}</span>
                              </div>

                              <div className="flex items-center gap-2">
                                <Clock className="w-4 h-4" />
                                <span>
                                  Last active: {getTimeAgo(session.last_activity)}
                                </span>
                              </div>

                              <div className="text-xs text-gray-500">
                                Signed in: {formatDateTime(session.created_at)}
                              </div>
                            </div>
                          </div>
                        </div>

                        {!session.is_current && (
                          <Button
                            onClick={() => terminateSession(session.id)}
                            variant="outline"
                            size="sm"
                            disabled={terminatingId === session.id}
                            className="text-red-600 hover:bg-red-50 hover:text-red-700"
                          >
                            {terminatingId === session.id ? 'Logging out...' : 'Logout'}
                          </Button>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}

              <div className="pt-4 border-t">
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h4 className="font-medium text-blue-900 mb-1">Security Tip</h4>
                  <p className="text-sm text-blue-800">
                    If you see a session you don't recognize, terminate it immediately and change your password.
                  </p>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

export default SessionManagement
