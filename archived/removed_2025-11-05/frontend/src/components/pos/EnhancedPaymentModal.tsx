import React, { useState, useEffect } from 'react'
import { DollarSign, CreditCard, Smartphone, Building, CheckCircle, AlertCircle, Clock, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
// Using native select for now - can be replaced with UI library select later

interface PaymentMethod {
  type: 'CASH' | 'CARD' | 'ZAIN_CASH' | 'SUPER_QI' | 'ALTAIF_BANK'
  amount: number
  provider?: string
  reference_number?: string
  platform_fee?: number
  verification_status: 'pending' | 'verified' | 'failed'
}

interface EnhancedPaymentModalProps {
  isOpen: boolean
  onClose: () => void
  totalAmount: number
  amountPaid: number
  onAddPayment: (payment: PaymentMethod) => void
  language: 'ar' | 'en'
}

export default function EnhancedPaymentModal({
  isOpen,
  onClose,
  totalAmount,
  amountPaid,
  onAddPayment,
  language
}: EnhancedPaymentModalProps) {
  const [selectedMethod, setSelectedMethod] = useState<PaymentMethod['type']>('CASH')
  const [amount, setAmount] = useState<number>(totalAmount - amountPaid)
  const [provider, setProvider] = useState<string>('')
  const [referenceNumber, setReferenceNumber] = useState<string>('')
  const [platformFee, setPlatformFee] = useState<number>(0)
  const [isProcessing, setIsProcessing] = useState(false)
  const [verificationStatus, setVerificationStatus] = useState<PaymentMethod['verification_status']>('pending')

  const remainingAmount = totalAmount - amountPaid

  useEffect(() => {
    if (isOpen) {
      setAmount(remainingAmount)
      setProvider('')
      setReferenceNumber('')
      setPlatformFee(0)
      setVerificationStatus('pending')
    }
  }, [isOpen, remainingAmount])

  useEffect(() => {
    // Calculate platform fees based on payment method
    switch (selectedMethod) {
      case 'ZAIN_CASH':
        setPlatformFee(amount * 0.015) // 1.5% fee
        break
      case 'SUPER_QI':
        setPlatformFee(amount * 0.012) // 1.2% fee
        break
      case 'ALTAIF_BANK':
        setPlatformFee(amount * 0.008) // 0.8% fee
        break
      case 'CARD':
        setPlatformFee(amount * 0.025) // 2.5% fee
        break
      default:
        setPlatformFee(0)
    }
  }, [selectedMethod, amount])

  const paymentMethods = [
    {
      type: 'CASH' as const,
      name: language === 'ar' ? 'نقداً' : 'Cash',
      icon: DollarSign,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
      description: language === 'ar' ? 'الدفع نقداً' : 'Cash payment'
    },
    {
      type: 'CARD' as const,
      name: language === 'ar' ? 'بطاقة ائتمان' : 'Credit Card',
      icon: CreditCard,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      description: language === 'ar' ? 'دفع بالبطاقة' : 'Card payment'
    },
    {
      type: 'ZAIN_CASH' as const,
      name: 'ZAIN Cash',
      icon: Smartphone,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
      description: language === 'ar' ? 'زين كاش' : 'ZAIN Cash mobile payment'
    },
    {
      type: 'SUPER_QI' as const,
      name: 'SuperQi',
      icon: Smartphone,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
      description: language === 'ar' ? 'سوبر كيو' : 'SuperQi mobile payment'
    },
    {
      type: 'ALTAIF_BANK' as const,
      name: language === 'ar' ? 'مصرف الطيف' : 'ALTaif Bank',
      icon: Building,
      color: 'text-indigo-600',
      bgColor: 'bg-indigo-50',
      description: language === 'ar' ? 'مصرف الطيف للتحويل' : 'ALTaif Bank transfer'
    }
  ]

  const handlePaymentProcessing = async () => {
    setIsProcessing(true)
    
    try {
      // Simulate payment processing
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      // Set verification status based on payment method
      switch (selectedMethod) {
        case 'CASH':
          setVerificationStatus('verified')
          break
        case 'CARD':
          setVerificationStatus('verified')
          break
        case 'ZAIN_CASH':
        case 'SUPER_QI':
          setVerificationStatus('verified')
          break
        case 'ALTAIF_BANK':
          setVerificationStatus('pending') // Manual verification required
          break
      }
      
    } catch (error) {
      setVerificationStatus('failed')
    } finally {
      setIsProcessing(false)
    }
  }

  const handleAddPayment = () => {
    const payment: PaymentMethod = {
      type: selectedMethod,
      amount,
      provider: provider || undefined,
      reference_number: referenceNumber || undefined,
      platform_fee: platformFee,
      verification_status: verificationStatus
    }
    
    onAddPayment(payment)
    onClose()
  }

  if (!isOpen) return null

  const selectedPaymentMethod = paymentMethods.find(method => method.type === selectedMethod)

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <Card className="w-full max-w-2xl">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center space-x-2">
              {selectedPaymentMethod && (
                <div className={`p-2 rounded-lg ${selectedPaymentMethod.bgColor}`}>
                  <selectedPaymentMethod.icon className={`w-5 h-5 ${selectedPaymentMethod.color}`} />
                </div>
              )}
              <span>
                {language === 'ar' ? 'إضافة دفعة' : 'Add Payment'}
              </span>
            </CardTitle>
            <Button variant="ghost" size="icon" onClick={onClose}>
              <X className="w-5 h-5" />
            </Button>
          </div>
        </CardHeader>
        
        <CardContent className="space-y-6">
          {/* Payment Method Selection */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {paymentMethods.map((method) => (
              <Card 
                key={method.type}
                className={`cursor-pointer transition-all ${
                  selectedMethod === method.type
                    ? 'ring-2 ring-blue-500 bg-blue-50'
                    : 'hover:shadow-md'
                }`}
                onClick={() => setSelectedMethod(method.type)}
              >
                <CardContent className="p-4 text-center">
                  <div className={`p-3 rounded-lg ${method.bgColor} mx-auto mb-2 w-fit`}>
                    <method.icon className={`w-6 h-6 ${method.color}`} />
                  </div>
                  <h4 className="font-semibold text-sm">{method.name}</h4>
                  <p className="text-xs text-gray-500 mt-1">{method.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Payment Amount */}
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">
                  {language === 'ar' ? 'المبلغ' : 'Amount'}
                </label>
                <Input
                  type="number"
                  value={amount}
                  onChange={(e) => setAmount(Number(e.target.value))}
                  placeholder={language === 'ar' ? 'أدخل المبلغ' : 'Enter amount'}
                  min="0"
                  max={remainingAmount}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">
                  {language === 'ar' ? 'المبلغ المتبقي' : 'Remaining'}
                </label>
                <div className="p-2 bg-gray-50 rounded-lg text-lg font-bold text-blue-600">
                  {remainingAmount.toLocaleString()} IQD
                </div>
              </div>
            </div>

            {/* Platform Fee Display */}
            {platformFee > 0 && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">
                    {language === 'ar' ? 'رسوم المنصة' : 'Platform Fee'}
                  </span>
                  <span className="font-bold text-yellow-700">
                    {platformFee.toLocaleString()} IQD
                  </span>
                </div>
                <div className="flex justify-between items-center mt-1">
                  <span className="text-xs text-gray-600">
                    {language === 'ar' ? 'المبلغ الإجمالي' : 'Total Amount'}
                  </span>
                  <span className="text-sm font-bold">
                    {(amount + platformFee).toLocaleString()} IQD
                  </span>
                </div>
              </div>
            )}
          </div>

          {/* Payment Method Specific Fields */}
          {selectedMethod === 'ZAIN_CASH' && (
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium mb-2">
                  {language === 'ar' ? 'رقم الهاتف' : 'Phone Number'}
                </label>
                <Input
                  type="tel"
                  value={provider}
                  onChange={(e) => setProvider(e.target.value)}
                  placeholder={language === 'ar' ? 'رقم هاتف زين' : 'ZAIN phone number'}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">
                  {language === 'ar' ? 'رقم المرجع' : 'Reference Number'}
                </label>
                <Input
                  type="text"
                  value={referenceNumber}
                  onChange={(e) => setReferenceNumber(e.target.value)}
                  placeholder={language === 'ar' ? 'رقم تأكيد المعاملة' : 'Transaction reference'}
                />
              </div>
            </div>
          )}

          {selectedMethod === 'SUPER_QI' && (
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium mb-2">
                  {language === 'ar' ? 'رقم الهاتف' : 'Phone Number'}
                </label>
                <Input
                  type="tel"
                  value={provider}
                  onChange={(e) => setProvider(e.target.value)}
                  placeholder={language === 'ar' ? 'رقم هاتف سوبر كيو' : 'SuperQi phone number'}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">
                  {language === 'ar' ? 'رقم المرجع' : 'Reference Number'}
                </label>
                <Input
                  type="text"
                  value={referenceNumber}
                  onChange={(e) => setReferenceNumber(e.target.value)}
                  placeholder={language === 'ar' ? 'رقم تأكيد المعاملة' : 'Transaction reference'}
                />
              </div>
            </div>
          )}

          {selectedMethod === 'ALTAIF_BANK' && (
            <div className="space-y-3">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-center space-x-2 mb-2">
                  <Building className="w-5 h-5 text-blue-600" />
                  <span className="font-medium text-blue-800">
                    {language === 'ar' ? 'مصرف الطيف' : 'ALTaif Bank Transfer'}
                  </span>
                </div>
                <p className="text-sm text-blue-700">
                  {language === 'ar' 
                    ? 'يتطلب التحقق اليدوي من قبل المدير'
                    : 'Requires manual verification by manager'
                  }
                </p>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">
                  {language === 'ar' ? 'رقم الحساب' : 'Account Number'}
                </label>
                <Input
                  type="text"
                  value={provider}
                  onChange={(e) => setProvider(e.target.value)}
                  placeholder={language === 'ar' ? 'رقم الحساب' : 'Account number'}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">
                  {language === 'ar' ? 'رقم المرجع' : 'Reference Number'}
                </label>
                <Input
                  type="text"
                  value={referenceNumber}
                  onChange={(e) => setReferenceNumber(e.target.value)}
                  placeholder={language === 'ar' ? 'رقم تأكيد التحويل' : 'Transfer reference'}
                />
              </div>
            </div>
          )}

          {selectedMethod === 'CARD' && (
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium mb-2">
                  {language === 'ar' ? 'نوع البطاقة' : 'Card Type'}
                </label>
                <select 
                  value={provider} 
                  onChange={(e) => setProvider(e.target.value)}
                  className="w-full p-2 border rounded-lg bg-white"
                >
                  <option value="">
                    {language === 'ar' ? 'اختر نوع البطاقة' : 'Select card type'}
                  </option>
                  <option value="VISA">Visa</option>
                  <option value="MASTERCARD">Mastercard</option>
                  <option value="AMEX">American Express</option>
                  <option value="LOCAL">Local Bank Card</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">
                  {language === 'ar' ? 'رقم التأكيد' : 'Confirmation Number'}
                </label>
                <Input
                  type="text"
                  value={referenceNumber}
                  onChange={(e) => setReferenceNumber(e.target.value)}
                  placeholder={language === 'ar' ? 'رقم تأكيد البطاقة' : 'Card confirmation number'}
                />
              </div>
            </div>
          )}

          {/* Processing and Verification Status */}
          {isProcessing && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-center space-x-2">
                <Clock className="w-5 h-5 text-blue-600 animate-spin" />
                <span className="text-blue-800">
                  {language === 'ar' ? 'جاري معالجة الدفعة...' : 'Processing payment...'}
                </span>
              </div>
            </div>
          )}

          {verificationStatus === 'verified' && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <div className="flex items-center space-x-2">
                <CheckCircle className="w-5 h-5 text-green-600" />
                <span className="text-green-800">
                  {language === 'ar' ? 'تم التحقق من الدفعة' : 'Payment verified'}
                </span>
              </div>
            </div>
          )}

          {verificationStatus === 'failed' && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex items-center space-x-2">
                <AlertCircle className="w-5 h-5 text-red-600" />
                <span className="text-red-800">
                  {language === 'ar' ? 'فشل في التحقق من الدفعة' : 'Payment verification failed'}
                </span>
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex space-x-3">
            <Button 
              variant="outline" 
              onClick={onClose}
              className="flex-1"
            >
              {language === 'ar' ? 'إلغاء' : 'Cancel'}
            </Button>
            
            {!isProcessing && verificationStatus === 'pending' && (
              <Button 
                onClick={handlePaymentProcessing}
                className="flex-1"
                disabled={amount <= 0 || amount > remainingAmount}
              >
                {language === 'ar' ? 'معالجة الدفعة' : 'Process Payment'}
              </Button>
            )}
            
            {verificationStatus === 'verified' && (
              <Button 
                onClick={handleAddPayment}
                className="flex-1"
              >
                {language === 'ar' ? 'إضافة الدفعة' : 'Add Payment'}
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
} 