import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Link } from 'react-router-dom'
import { Shield, Key, Globe, AlertTriangle, CheckCircle, Clock, Activity } from 'lucide-react'
import { useAuthStore } from '@/stores/authStore'
import axios from 'axios'

interface SecurityStats {
  mfa_enabled: boolean
  active_sessions: number
  last_login: string
  failed_login_attempts: number
  account_locked: boolean
}

export function SecurityDashboard() {
  const { user, token } = useAuthStore()
  const [stats, setStats] = useState<SecurityStats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadSecurityStats()
  }, [])

  const loadSecurityStats = async () => {
    try {
      // In production, create an API endpoint for security stats
      // For now, we'll simulate it with existing data
      const sessionsResponse = await axios.get(
        'http://localhost:8000/api/auth/sessions',
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      )

      setStats({
        mfa_enabled: user?.mfa_enabled || false,
        active_sessions: sessionsResponse.data.total || 0,
        last_login: new Date().toISOString(),
        failed_login_attempts: 0,
        account_locked: false
      })
    } catch (err) {
      console.error('Failed to load security stats:', err)
    } finally {
      setLoading(false)
    }
  }

  const securityScore = () => {
    let score = 50 // Base score

    if (stats?.mfa_enabled) score += 30
    if (stats && stats.active_sessions <= 2) score += 10
    if (stats && stats.failed_login_attempts === 0) score += 10

    return score
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600 bg-green-50 border-green-200'
    if (score >= 60) return 'text-yellow-600 bg-yellow-50 border-yellow-200'
    return 'text-red-600 bg-red-50 border-red-200'
  }

  const getScoreLabel = (score: number) => {
    if (score >= 80) return 'Excellent'
    if (score >= 60) return 'Good'
    return 'Needs Improvement'
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900"></div>
      </div>
    )
  }

  const score = securityScore()

  return (
    <div className="container max-w-6xl mx-auto py-8 px-4">
      <div className="mb-8">
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <Shield className="w-8 h-8" />
          Security Center
        </h1>
        <p className="text-gray-600 mt-2">
          Manage your account security settings and monitor activity
        </p>
      </div>

      {/* Security Score */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle>Security Score</CardTitle>
          <CardDescription>Your current account security rating</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-4 mb-4">
                <div className={`text-6xl font-bold ${getScoreColor(score).split(' ')[0]}`}>
                  {score}
                </div>
                <div>
                  <p className={`text-xl font-semibold ${getScoreColor(score).split(' ')[0]}`}>
                    {getScoreLabel(score)}
                  </p>
                  <p className="text-sm text-gray-600">out of 100</p>
                </div>
              </div>

              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className={`h-3 rounded-full transition-all ${
                    score >= 80 ? 'bg-green-600' : score >= 60 ? 'bg-yellow-600' : 'bg-red-600'
                  }`}
                  style={{ width: `${score}%` }}
                ></div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-6 md:grid-cols-2 mb-8">
        {/* MFA Status */}
        <Link to="/security/mfa-setup">
          <Card className="hover:shadow-lg transition-shadow cursor-pointer">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <Key className="w-5 h-5" />
                  Multi-Factor Authentication
                </CardTitle>
                {stats?.mfa_enabled ? (
                  <CheckCircle className="w-5 h-5 text-green-600" />
                ) : (
                  <AlertTriangle className="w-5 h-5 text-yellow-600" />
                )}
              </div>
            </CardHeader>
            <CardContent>
              {stats?.mfa_enabled ? (
                <div className="text-sm">
                  <p className="text-green-600 font-medium mb-2">✓ Enabled</p>
                  <p className="text-gray-600">Your account is protected with 2FA</p>
                </div>
              ) : (
                <div className="text-sm">
                  <p className="text-yellow-600 font-medium mb-2">⚠ Not Enabled</p>
                  <p className="text-gray-600">Add an extra layer of security</p>
                </div>
              )}
            </CardContent>
          </Card>
        </Link>

        {/* Active Sessions */}
        <Link to="/security/sessions">
          <Card className="hover:shadow-lg transition-shadow cursor-pointer">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <Globe className="w-5 h-5" />
                  Active Sessions
                </CardTitle>
                <span className="text-2xl font-bold">{stats?.active_sessions || 0}</span>
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-sm">
                <p className="text-gray-600 mb-2">
                  {stats?.active_sessions === 1 ? 'Current device only' : `${stats?.active_sessions} devices active`}
                </p>
                <p className="text-gray-500">Click to manage sessions</p>
              </div>
            </CardContent>
          </Card>
        </Link>

        {/* Last Login */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Clock className="w-5 h-5" />
              Last Login
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-sm">
              <p className="font-medium mb-1">
                {stats?.last_login ? new Date(stats.last_login).toLocaleString() : 'Unknown'}
              </p>
              <p className="text-gray-600">From your current device</p>
            </div>
          </CardContent>
        </Card>

        {/* Security Alerts */}
        <Link to="/security/audit-log">
          <Card className="hover:shadow-lg transition-shadow cursor-pointer">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="w-5 h-5" />
                Recent Activity
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-sm">
                <p className="text-gray-600 mb-2">
                  {stats?.failed_login_attempts || 0} failed login attempts
                </p>
                <p className="text-gray-500">View full audit log</p>
              </div>
            </CardContent>
          </Card>
        </Link>
      </div>

      {/* Recommendations */}
      <Card>
        <CardHeader>
          <CardTitle>Security Recommendations</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {!stats?.mfa_enabled && (
              <div className="flex items-start gap-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                <AlertTriangle className="w-5 h-5 text-yellow-600 mt-0.5" />
                <div>
                  <p className="font-medium text-yellow-900">Enable Multi-Factor Authentication</p>
                  <p className="text-sm text-yellow-800">
                    Protect your account with an additional security layer.
                  </p>
                </div>
              </div>
            )}

            {stats && stats.active_sessions > 3 && (
              <div className="flex items-start gap-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <Activity className="w-5 h-5 text-blue-600 mt-0.5" />
                <div>
                  <p className="font-medium text-blue-900">Review Active Sessions</p>
                  <p className="text-sm text-blue-800">
                    You have {stats.active_sessions} active sessions. Review and remove any unfamiliar devices.
                  </p>
                </div>
              </div>
            )}

            {stats && stats.failed_login_attempts > 0 && (
              <div className="flex items-start gap-3 p-3 bg-red-50 border border-red-200 rounded-lg">
                <AlertTriangle className="w-5 h-5 text-red-600 mt-0.5" />
                <div>
                  <p className="font-medium text-red-900">Failed Login Attempts Detected</p>
                  <p className="text-sm text-red-800">
                    There were {stats.failed_login_attempts} failed login attempts. Consider changing your password.
                  </p>
                </div>
              </div>
            )}

            {stats?.mfa_enabled && stats.active_sessions <= 2 && stats.failed_login_attempts === 0 && (
              <div className="flex items-start gap-3 p-3 bg-green-50 border border-green-200 rounded-lg">
                <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
                <div>
                  <p className="font-medium text-green-900">Great! Your account is well protected</p>
                  <p className="text-sm text-green-800">
                    You're following security best practices. Keep it up!
                  </p>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default SecurityDashboard
