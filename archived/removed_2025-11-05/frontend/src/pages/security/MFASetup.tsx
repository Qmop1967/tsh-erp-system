import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useAuthStore } from '@/stores/authStore'
import axios from 'axios'
import { Shield, Key, CheckCircle, AlertCircle } from 'lucide-react'

export function MFASetup() {
  const { token } = useAuthStore()
  const [step, setStep] = useState<'initial' | 'scan' | 'verify' | 'complete'>('initial')
  const [qrCodeUri, setQrCodeUri] = useState('')
  const [secret, setSecret] = useState('')
  const [verificationCode, setVerificationCode] = useState('')
  const [backupCodes, setBackupCodes] = useState<string[]>([])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const initiateMFASetup = async () => {
    try {
      setLoading(true)
      setError('')
      const response = await axios.post(
        'http://localhost:8000/api/auth/mfa/setup',
        {},
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      )

      setQrCodeUri(response.data.qr_uri)
      setSecret(response.data.secret)
      setStep('scan')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to setup MFA')
    } finally {
      setLoading(false)
    }
  }

  const verifyMFACode = async () => {
    try {
      setLoading(true)
      setError('')
      await axios.post(
        'http://localhost:8000/api/auth/mfa/verify-setup',
        null,
        {
          params: { code: verificationCode },
          headers: { Authorization: `Bearer ${token}` }
        }
      )

      setStep('verify')
      await generateBackupCodes()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Invalid code')
    } finally {
      setLoading(false)
    }
  }

  const generateBackupCodes = async () => {
    try {
      const response = await axios.get(
        'http://localhost:8000/api/auth/mfa/backup-codes',
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      )

      setBackupCodes(response.data.codes)
      setStep('complete')
    } catch (err: any) {
      console.error('Failed to generate backup codes:', err)
    }
  }

  const downloadBackupCodes = () => {
    const text = `TSH ERP MFA Backup Codes\n\n${backupCodes.join('\n')}\n\nSave these codes securely. Each can only be used once.`
    const blob = new Blob([text], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'tsh-erp-backup-codes.txt'
    a.click()
  }

  return (
    <div className="container max-w-2xl mx-auto py-8 px-4">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="w-6 h-6" />
            Multi-Factor Authentication Setup
          </CardTitle>
          <CardDescription>
            Add an extra layer of security to your account
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center gap-2 text-red-800">
              <AlertCircle className="w-5 h-5" />
              {error}
            </div>
          )}

          {step === 'initial' && (
            <div className="space-y-4">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h3 className="font-semibold mb-2">What is MFA?</h3>
                <p className="text-sm text-gray-700">
                  Multi-Factor Authentication adds an extra security layer by requiring a code from your phone
                  in addition to your password.
                </p>
              </div>

              <div className="space-y-2">
                <h4 className="font-medium">You'll need:</h4>
                <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
                  <li>A smartphone</li>
                  <li>Google Authenticator, Authy, or similar app</li>
                  <li>5 minutes to complete setup</li>
                </ul>
              </div>

              <Button onClick={initiateMFASetup} disabled={loading} className="w-full">
                <Key className="w-4 h-4 mr-2" />
                {loading ? 'Setting up...' : 'Begin MFA Setup'}
              </Button>
            </div>
          )}

          {step === 'scan' && (
            <div className="space-y-4">
              <div>
                <h3 className="font-semibold mb-2">Step 1: Scan QR Code</h3>
                <p className="text-sm text-gray-600 mb-4">
                  Open your authenticator app and scan this QR code:
                </p>

                <div className="bg-white p-4 rounded-lg border-2 border-gray-200 flex justify-center">
                  {qrCodeUri && (
                    <img
                      src={`https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(qrCodeUri)}`}
                      alt="MFA QR Code"
                      className="w-48 h-48"
                    />
                  )}
                </div>

                <details className="mt-4">
                  <summary className="text-sm text-blue-600 cursor-pointer">Can't scan? Enter manually</summary>
                  <div className="mt-2 p-3 bg-gray-50 rounded border">
                    <p className="text-xs text-gray-500 mb-1">Secret Key:</p>
                    <code className="text-sm font-mono break-all">{secret}</code>
                  </div>
                </details>
              </div>

              <div>
                <h3 className="font-semibold mb-2">Step 2: Enter Verification Code</h3>
                <p className="text-sm text-gray-600 mb-3">
                  Enter the 6-digit code from your authenticator app:
                </p>

                <Input
                  type="text"
                  maxLength={6}
                  placeholder="000000"
                  value={verificationCode}
                  onChange={(e) => setVerificationCode(e.target.value.replace(/\D/g, ''))}
                  className="text-center text-2xl tracking-widest"
                />
              </div>

              <Button
                onClick={verifyMFACode}
                disabled={verificationCode.length !== 6 || loading}
                className="w-full"
              >
                {loading ? 'Verifying...' : 'Verify & Enable MFA'}
              </Button>
            </div>
          )}

          {step === 'complete' && (
            <div className="space-y-4">
              <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-center gap-2 text-green-800">
                <CheckCircle className="w-5 h-5" />
                <div>
                  <p className="font-semibold">MFA Enabled Successfully!</p>
                  <p className="text-sm">Your account is now more secure.</p>
                </div>
              </div>

              <div>
                <h3 className="font-semibold mb-2">Backup Recovery Codes</h3>
                <p className="text-sm text-gray-600 mb-3">
                  Save these codes in a secure place. Use them if you lose access to your authenticator app.
                </p>

                <div className="bg-gray-50 rounded-lg p-4 border-2 border-dashed border-gray-300">
                  <div className="grid grid-cols-2 gap-2">
                    {backupCodes.map((code, index) => (
                      <code key={index} className="text-sm font-mono bg-white px-3 py-2 rounded border">
                        {code}
                      </code>
                    ))}
                  </div>
                </div>
              </div>

              <div className="flex gap-3">
                <Button onClick={downloadBackupCodes} variant="outline" className="flex-1">
                  Download Codes
                </Button>
                <Button onClick={() => window.location.href = '/dashboard'} className="flex-1">
                  Done
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

export default MFASetup
