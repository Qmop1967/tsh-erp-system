import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuthStore } from '../../stores/authStore'
import { Button } from '../../components/ui/button'
import { Input } from '../../components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card'
import { Lock, Mail, Wand2 } from 'lucide-react'
import axios from 'axios'

export function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [magicLinkMode, setMagicLinkMode] = useState(false)
  const [magicLinkSent, setMagicLinkSent] = useState(false)
  const [magicLinkUrl, setMagicLinkUrl] = useState('')

  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { login, setAuth } = useAuthStore()

  // Check for magic link token in URL on mount
  useEffect(() => {
    const token = searchParams.get('token')
    if (token) {
      verifyMagicLink(token)
    }
  }, [searchParams])

  const verifyMagicLink = async (token: string) => {
    setLoading(true)
    setError('')
    try {
      const response = await axios.get(`/api/auth/magic-link/verify?token=${token}`)
      if (response.data.success) {
        // Store the token and user data
        setAuth(response.data.access_token, response.data.user)
        navigate('/dashboard')
      }
    } catch (err: any) {
      console.error('Magic link verification error:', err)
      setError(err.response?.data?.detail || 'Invalid or expired magic link')
    } finally {
      setLoading(false)
    }
  }

  const handleMagicLinkRequest = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setMagicLinkSent(false)

    try {
      const response = await axios.post('/api/auth/magic-link/request', { email })
      if (response.data.success) {
        setMagicLinkSent(true)
        // Extract the magic link URL from the response message
        const linkMatch = response.data.message.match(/Link: (https?:\/\/[^\s]+)/)
        if (linkMatch) {
          setMagicLinkUrl(linkMatch[1])
        }
      }
    } catch (err: any) {
      console.error('Magic link request error:', err)
      setError(err.response?.data?.detail || 'Failed to send magic link')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      await login({ email, password })
      navigate('/dashboard')
    } catch (err: any) {
      console.error('Login error:', err)

      // Check if it's a 403 error (web access denied)
      if (err.response?.status === 403) {
        const detail = err.response?.data?.detail || ''
        if (detail.includes('mobile application')) {
          setError(`🚫 ${detail}\n\n📱 Mobile apps are available in: /mobile/flutter_apps/`)
        } else {
          setError(detail || 'Access denied. Please contact your administrator.')
        }
      } else {
        setError(err.response?.data?.detail || err.message || 'Login failed. Please try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-4">
      <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>
      
      {/* Mobile Users Notice */}
      <div className="absolute top-4 left-4 right-4 max-w-2xl mx-auto">
        <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded-lg shadow-md">
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd"/>
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-blue-700 font-semibold">
                📱 For Mobile Users (Salesperson, Cashier, Inventory, etc.)
              </p>
              <p className="mt-1 text-xs text-blue-600">
                Please use the mobile application. Web access is restricted to Admin users only.
              </p>
            </div>
          </div>
        </div>
      </div>
      
      <Card className="w-full max-w-md shadow-2xl border-0 bg-white/80 backdrop-blur-sm animate-slideIn mt-24">
        <CardHeader className="text-center pb-8">
          <div className="mx-auto w-16 h-16 bg-gradient-to-br from-blue-600 to-purple-600 rounded-2xl flex items-center justify-center mb-6 shadow-lg">
            <Lock className="h-8 w-8 text-white" />
          </div>
          <CardTitle className="text-3xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
            TSH ERP System
          </CardTitle>
          <CardDescription className="text-gray-600 text-lg mt-2">
            Welcome back! Sign in to continue
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {magicLinkMode ? (
            <form onSubmit={handleMagicLinkRequest} className="space-y-5">
              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl animate-fadeIn">
                  {error}
                </div>
              )}

              {magicLinkSent ? (
                <div className="space-y-4">
                  <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-xl">
                    Magic link sent! Check your email or use the link below.
                  </div>
                  {magicLinkUrl && (
                    <div className="bg-blue-50 border border-blue-200 px-4 py-3 rounded-xl">
                      <p className="text-sm font-semibold text-blue-700 mb-2">Development Mode - Direct Link:</p>
                      <a
                        href={magicLinkUrl}
                        className="text-xs text-blue-600 break-all hover:underline"
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        {magicLinkUrl}
                      </a>
                      <p className="text-xs text-blue-500 mt-2">
                        Click the link above to verify your magic link
                      </p>
                    </div>
                  )}
                </div>
              ) : (
                <>
                  <div className="space-y-3">
                    <label htmlFor="magic-email" className="text-sm font-semibold text-gray-700">
                      Email Address
                    </label>
                    <div className="relative group">
                      <Mail className="absolute left-3 top-3.5 h-5 w-5 text-gray-400 group-hover:text-purple-500 transition-colors" />
                      <Input
                        id="magic-email"
                        type="email"
                        placeholder="your@email.com"
                        className="pl-12 py-3 border-2 border-gray-200 rounded-xl focus:border-purple-500 focus:ring-0 transition-colors"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                      />
                    </div>
                  </div>

                  <Button
                    type="submit"
                    className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white py-3 rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all duration-200 transform hover:scale-105"
                    disabled={loading}
                  >
                    {loading ? (
                      <div className="flex items-center space-x-2">
                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                        <span>Sending Magic Link...</span>
                      </div>
                    ) : (
                      <div className="flex items-center space-x-2">
                        <Wand2 className="h-5 w-5" />
                        <span>Send Magic Link</span>
                      </div>
                    )}
                  </Button>
                </>
              )}

              <div className="text-center">
                <button
                  type="button"
                  onClick={() => {
                    setMagicLinkMode(false)
                    setMagicLinkSent(false)
                    setError('')
                  }}
                  className="text-sm text-gray-600 hover:text-blue-600 transition-colors"
                >
                  Back to password login
                </button>
              </div>
            </form>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-5">
              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl animate-fadeIn">
                  {error}
                </div>
              )}

              <div className="space-y-3">
                <label htmlFor="email" className="text-sm font-semibold text-gray-700">
                  Email Address
                </label>
                <div className="relative group">
                  <Mail className="absolute left-3 top-3.5 h-5 w-5 text-gray-400 group-hover:text-blue-500 transition-colors" />
                  <Input
                    id="email"
                    type="email"
                    placeholder="admin@tsh-erp.com"
                    className="pl-12 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:ring-0 transition-colors"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                  />
                </div>
              </div>

              <div className="space-y-3">
                <label htmlFor="password" className="text-sm font-semibold text-gray-700">
                  Password
                </label>
                <div className="relative group">
                  <Lock className="absolute left-3 top-3.5 h-5 w-5 text-gray-400 group-hover:text-blue-500 transition-colors" />
                  <Input
                    id="password"
                    type="password"
                    placeholder="Enter your password"
                    className="pl-12 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:ring-0 transition-colors"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                  />
                </div>
              </div>

              <Button
                type="submit"
                className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white py-3 rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all duration-200 transform hover:scale-105"
                disabled={loading}
              >
                {loading ? (
                  <div className="flex items-center space-x-2">
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    <span>Signing in...</span>
                  </div>
                ) : (
                  'Sign in to Dashboard'
                )}
              </Button>

              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-gray-200"></div>
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-2 bg-white text-gray-500">or</span>
                </div>
              </div>

              <button
                type="button"
                onClick={() => setMagicLinkMode(true)}
                className="w-full flex items-center justify-center space-x-2 py-3 border-2 border-purple-200 rounded-xl text-purple-600 font-semibold hover:bg-purple-50 transition-colors"
              >
                <Wand2 className="h-5 w-5" />
                <span>Sign in with Magic Link</span>
              </button>
            </form>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
