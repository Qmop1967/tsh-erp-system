import React, { useState, useEffect } from 'react'
import { useAuthStore } from '@/stores/authStore'
import { useLanguageStore } from '@/stores/languageStore'
import { useDynamicTranslations } from '@/lib/dynamicTranslations'
import api from '@/lib/api'
import { Search, ShoppingCart, CreditCard, Smartphone, DollarSign, Receipt, Plus, Minus, Trash2, User, Package, Clock, AlertCircle, Check, X, Camera, Zap } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import ImageRecognition from '@/components/inventory/ImageRecognition'
import GoogleLensSearch from '@/components/pos/GoogleLensSearch'
import EnhancedPaymentModal from '@/components/pos/EnhancedPaymentModal'

interface Product {
  id: number
  name_ar: string
  name_en: string
  sku: string
  price: number
  stock_quantity: number
  category: string
  image_url?: string
}

interface CartItem {
  product: Product
  quantity: number
  subtotal: number
  discount?: number
}

interface PaymentMethod {
  type: 'CASH' | 'CARD' | 'ZAIN_CASH' | 'SUPER_QI' | 'ALTAIF_BANK'
  amount: number
  provider?: string
  reference_number?: string
  platform_fee?: number
  verification_status: 'pending' | 'verified' | 'failed'
}

interface POSSession {
  id: number
  session_number: string
  terminal_id: number
  start_time: string
  opening_cash_amount: number
  total_sales: number
  transaction_count: number
  status: 'OPEN' | 'CLOSED'
}

export default function POSInterface() {
  const { user } = useAuthStore()
  const { language } = useLanguageStore()
  const { t } = useDynamicTranslations(language)
  
  // POS State
  const [activeSession, setActiveSession] = useState<POSSession | null>(null)
  const [products, setProducts] = useState<Product[]>([])
  const [searchTerm, setSearchTerm] = useState('')
  const [cart, setCart] = useState<CartItem[]>([])
  const [customer, setCustomer] = useState<any>(null)
  const [paymentMethods, setPaymentMethods] = useState<PaymentMethod[]>([])
  const [currentPayment, setCurrentPayment] = useState<PaymentMethod>({ type: 'CASH', amount: 0, verification_status: 'pending' })
  const [showPaymentModal, setShowPaymentModal] = useState(false)
  const [showCustomerModal, setShowCustomerModal] = useState(false)
  const [receipt, setReceipt] = useState<any>(null)
  const [showReceiptModal, setShowReceiptModal] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showGoogleLens, setShowGoogleLens] = useState(false)
  const [showEnhancedPayment, setShowEnhancedPayment] = useState(false)

  // Calculations
  const subtotal = cart.reduce((sum, item) => sum + item.subtotal, 0)
  const totalDiscount = cart.reduce((sum, item) => sum + (item.discount || 0), 0)
  const total = subtotal - totalDiscount
  const amountPaid = paymentMethods.reduce((sum, payment) => sum + payment.amount, 0)
  const change = amountPaid - total

  useEffect(() => {
    loadInitialData()
  }, [])

  const loadInitialData = async () => {
    try {
      setLoading(true)
      setError(null)

      // Try to load active session (optional)
      try {
        const sessionResponse = await api.get('/pos/sessions/active/1')
        setActiveSession(sessionResponse.data)
      } catch (sessionError) {
        console.log('No active POS session, continuing without it')
        // Create a mock session for now
        setActiveSession({
          id: 1,
          session_number: 'SESSION-' + Date.now(),
          terminal_id: 1,
          start_time: new Date().toISOString(),
          opening_cash_amount: 0,
          total_sales: 0,
          transaction_count: 0,
          status: 'OPEN'
        })
      }

      // Load products/items from inventory
      const productsResponse = await api.get('/inventory/items')
      const items = productsResponse.data

      // Transform items to match Product interface
      // Note: /items endpoint returns inventory items with nested product
      const transformedProducts = items.map((item: any) => {
        const product = item.product || item; // Handle both nested and flat structure
        return {
          id: product.id || item.product_id,
          name_ar: product.name_ar || product.name || '',
          name_en: product.name_en || product.name || '',
          sku: product.sku || product.code || '',
          price: parseFloat(product.unit_price || product.selling_price || product.price || 0),
          stock_quantity: item.available_quantity || item.quantity_on_hand || product.quantity || product.stock_quantity || 0,
          category: product.category_name || product.category?.name || product.category || 'General',
          image_url: product.image_url || product.image
        };
      })

      setProducts(transformedProducts)
      console.log('Loaded', transformedProducts.length, 'products')
    } catch (error) {
      console.error('Error loading POS data:', error)
      setError('Failed to load products. Please refresh.')
    } finally {
      setLoading(false)
    }
  }

  const searchProducts = (term: string) => {
    return products.filter(product =>
      product.name_ar.toLowerCase().includes(term.toLowerCase()) ||
      product.name_en.toLowerCase().includes(term.toLowerCase()) ||
      product.sku.toLowerCase().includes(term.toLowerCase())
    )
  }

  const addToCart = (product: Product, quantity: number = 1) => {
    const existingItem = cart.find(item => item.product.id === product.id)
    
    if (existingItem) {
      updateCartQuantity(product.id, existingItem.quantity + quantity)
    } else {
      const newItem: CartItem = {
        product,
        quantity,
        subtotal: product.price * quantity
      }
      setCart([...cart, newItem])
    }
  }

  const updateCartQuantity = (productId: number, newQuantity: number) => {
    if (newQuantity <= 0) {
      removeFromCart(productId)
      return
    }
    
    setCart(cart.map(item => 
      item.product.id === productId 
        ? { ...item, quantity: newQuantity, subtotal: item.product.price * newQuantity }
        : item
    ))
  }

  const removeFromCart = (productId: number) => {
    setCart(cart.filter(item => item.product.id !== productId))
  }

  const applyDiscount = (productId: number, discount: number) => {
    setCart(cart.map(item => 
      item.product.id === productId 
        ? { ...item, discount }
        : item
    ))
  }

  const clearCart = () => {
    setCart([])
    setCustomer(null)
    setPaymentMethods([])
  }

  const addPayment = (payment: PaymentMethod) => {
    setPaymentMethods([...paymentMethods, payment])
    setCurrentPayment({ type: 'CASH', amount: 0, verification_status: 'pending' })
    setShowPaymentModal(false)
  }

  const processTransaction = async () => {
    if (!activeSession) {
      setError('No active session found')
      return
    }

    if (cart.length === 0) {
      setError('Cart is empty')
      return
    }

    if (amountPaid < total) {
      setError('Insufficient payment amount')
      return
    }

    try {
      setLoading(true)
      
      // Create transaction
      const transaction = {
        session_id: activeSession.id,
        customer_id: customer?.id || null,
        items: cart.map(item => ({
          product_id: item.product.id,
          quantity: item.quantity,
          unit_price: item.product.price,
          discount_amount: item.discount || 0,
          line_total: item.subtotal - (item.discount || 0)
        })),
        payments: paymentMethods,
        subtotal,
        discount_amount: totalDiscount,
        total_amount: total,
        amount_paid: amountPaid,
        change_amount: change
      }

      const response = await api.post('/api/pos/transactions', transaction)
      const createdTransaction = response.data

      // Generate receipt
      setReceipt(createdTransaction)
      setShowReceiptModal(true)
      
      // Clear cart after successful transaction
      clearCart()
      
      // Update session stats
      setActiveSession(prev => prev ? {
        ...prev,
        total_sales: prev.total_sales + total,
        transaction_count: prev.transaction_count + 1
      } : null)
      
    } catch (error) {
      console.error('Transaction error:', error)
      setError('Failed to process transaction')
    } finally {
      setLoading(false)
    }
  }

  const filteredProducts = searchTerm ? searchProducts(searchTerm) : products.slice(0, 20)

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Package className="w-8 h-8 text-blue-600" />
                <h1 className="text-2xl font-bold text-gray-900">TSH POS System</h1>
              </div>
              {activeSession && (
                <Badge variant="outline" className="bg-green-50 text-green-700">
                  <Clock className="w-4 h-4 mr-1" />
                  Session: {activeSession.session_number}
                </Badge>
              )}
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-600">
                Cashier: {user?.name || 'Unknown'}
              </div>
              <Badge variant="outline">
                {language === 'ar' ? 'العربية' : 'English'}
              </Badge>
            </div>
          </div>
        </div>
      </div>

      {error && (
        <div className="max-w-7xl mx-auto mt-4 mx-4 bg-red-50 border-red-200 p-4 rounded-lg border flex items-center">
          <AlertCircle className="w-4 h-4 text-red-600 mr-2" />
          <span className="text-red-800 flex-1">{error}</span>
          <Button 
            variant="ghost" 
            size="sm" 
            onClick={() => setError(null)}
            className="ml-auto"
          >
            <X className="w-4 h-4" />
          </Button>
        </div>
      )}

      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Product Search & Selection */}
          <div className="lg:col-span-2 space-y-4">
            {/* Search Bar */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Search className="w-5 h-5" />
                  <span>Product Search</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex space-x-2">
                  <Input
                    placeholder="Search by name, SKU, or scan barcode..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="flex-1"
                  />
                  <Button variant="outline" size="icon">
                    <Search className="w-4 h-4" />
                  </Button>
                  <Button 
                    variant="outline" 
                    size="icon"
                    onClick={() => setShowGoogleLens(true)}
                    className="bg-blue-50 hover:bg-blue-100"
                  >
                    <Camera className="w-4 h-4 text-blue-600" />
                  </Button>
                </div>
                <div className="mt-2 text-center">
                  <Button 
                    variant="ghost" 
                    size="sm"
                    onClick={() => setShowGoogleLens(true)}
                    className="text-blue-600 hover:text-blue-700"
                  >
                    <Camera className="w-4 h-4 mr-1" />
                    {language === 'ar' ? 'البحث بالصورة' : 'Search by Image'}
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Product Grid */}
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {filteredProducts.map((product) => (
                <Card key={product.id} className="hover:shadow-md transition-shadow cursor-pointer">
                  <CardContent className="p-4">
                    <div className="space-y-2">
                      <div className="aspect-square bg-gray-100 rounded-lg flex items-center justify-center">
                        {product.image_url ? (
                          <img
                            src={product.image_url}
                            alt={product.name_en}
                            className="w-full h-full object-cover rounded-lg"
                          />
                        ) : (
                          <Package className="w-8 h-8 text-gray-400" />
                        )}
                      </div>
                      <div>
                        <h3 className="font-semibold text-sm truncate">
                          {language === 'ar' ? product.name_ar : product.name_en}
                        </h3>
                        <p className="text-xs text-gray-500">{product.sku}</p>
                        <div className="flex items-center justify-between mt-2">
                          <span className="font-bold text-lg text-blue-600">
                            {product.price.toLocaleString()} IQD
                          </span>
                          <Badge variant={product.stock_quantity > 0 ? "default" : "destructive"}>
                            {product.stock_quantity}
                          </Badge>
                        </div>
                      </div>
                      <Button
                        className="w-full"
                        onClick={() => addToCart(product)}
                        disabled={product.stock_quantity === 0}
                      >
                        <Plus className="w-4 h-4 mr-2" />
                        Add to Cart
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* Cart & Checkout */}
          <div className="space-y-4">
            {/* Cart */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <ShoppingCart className="w-5 h-5" />
                    <span>Shopping Cart</span>
                  </div>
                  <Badge variant="outline">{cart.length} items</Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                {cart.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    <ShoppingCart className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                    <p>Cart is empty</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {cart.map((item) => (
                      <div key={item.product.id} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                        <div className="flex-1">
                          <h4 className="font-semibold text-sm">
                            {language === 'ar' ? item.product.name_ar : item.product.name_en}
                          </h4>
                          <p className="text-xs text-gray-500">{item.product.sku}</p>
                          <p className="text-sm font-bold text-blue-600">
                            {item.product.price.toLocaleString()} IQD each
                          </p>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Button
                            variant="outline"
                            size="icon"
                            className="h-8 w-8"
                            onClick={() => updateCartQuantity(item.product.id, item.quantity - 1)}
                          >
                            <Minus className="w-3 h-3" />
                          </Button>
                          <span className="w-8 text-center font-semibold">{item.quantity}</span>
                          <Button
                            variant="outline"
                            size="icon"
                            className="h-8 w-8"
                            onClick={() => updateCartQuantity(item.product.id, item.quantity + 1)}
                          >
                            <Plus className="w-3 h-3" />
                          </Button>
                          <Button
                            variant="destructive"
                            size="icon"
                            className="h-8 w-8"
                            onClick={() => removeFromCart(item.product.id)}
                          >
                            <Trash2 className="w-3 h-3" />
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Customer Selection */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <User className="w-5 h-5" />
                  <span>Customer</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                {customer ? (
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-semibold">{customer.name}</p>
                      <p className="text-sm text-gray-500">{customer.phone}</p>
                    </div>
                    <Button variant="outline" size="sm" onClick={() => setCustomer(null)}>
                      Remove
                    </Button>
                  </div>
                ) : (
                  <Button 
                    variant="outline" 
                    className="w-full"
                    onClick={() => setShowCustomerModal(true)}
                  >
                    Select Customer (Optional)
                  </Button>
                )}
              </CardContent>
            </Card>

            {/* Order Summary */}
            <Card>
              <CardHeader>
                <CardTitle>Order Summary</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>Subtotal:</span>
                    <span>{subtotal.toLocaleString()} IQD</span>
                  </div>
                  {totalDiscount > 0 && (
                    <div className="flex justify-between text-red-600">
                      <span>Discount:</span>
                      <span>-{totalDiscount.toLocaleString()} IQD</span>
                    </div>
                  )}
                  <hr className="my-2" />
                  <div className="flex justify-between font-bold text-lg">
                    <span>Total:</span>
                    <span>{total.toLocaleString()} IQD</span>
                  </div>
                  {amountPaid > 0 && (
                    <>
                      <div className="flex justify-between text-green-600">
                        <span>Amount Paid:</span>
                        <span>{amountPaid.toLocaleString()} IQD</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Change:</span>
                        <span>{change.toLocaleString()} IQD</span>
                      </div>
                    </>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Payment Methods */}
            <Card>
              <CardHeader>
                <CardTitle>Payment Methods</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {paymentMethods.map((payment, index) => (
                    <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                      <div className="flex items-center space-x-2">
                        {payment.type === 'CASH' && <DollarSign className="w-4 h-4" />}
                        {payment.type === 'CARD' && <CreditCard className="w-4 h-4" />}
                        {(payment.type === 'ZAIN_CASH' || payment.type === 'SUPER_QI' || payment.type === 'ALTAIF_BANK') && <Smartphone className="w-4 h-4" />}
                        <span className="font-semibold">{payment.type}</span>
                      </div>
                      <span>{payment.amount.toLocaleString()} IQD</span>
                    </div>
                  ))}
                  <div className="space-y-2">
                    <div className="grid grid-cols-3 gap-2">
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => {
                          setCurrentPayment({ type: 'CASH', amount: total - amountPaid, verification_status: 'pending' })
                          setShowPaymentModal(true)
                        }}
                      >
                        <DollarSign className="w-4 h-4 mr-1" />
                        Cash
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => {
                          setCurrentPayment({ type: 'CARD', amount: total - amountPaid, verification_status: 'pending' })
                          setShowPaymentModal(true)
                        }}
                      >
                        <CreditCard className="w-4 h-4 mr-1" />
                        Card
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => {
                          setCurrentPayment({ type: 'ZAIN_CASH', amount: total - amountPaid, verification_status: 'pending' })
                          setShowPaymentModal(true)
                        }}
                      >
                        <Smartphone className="w-4 h-4 mr-1" />
                        Mobile
                      </Button>
                    </div>
                    <Button 
                      variant="default" 
                      size="sm"
                      onClick={() => setShowEnhancedPayment(true)}
                      className="w-full bg-blue-600 hover:bg-blue-700"
                    >
                      <Zap className="w-4 h-4 mr-1" />
                      {language === 'ar' ? 'دفع متقدم' : 'Enhanced Payment'}
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Action Buttons */}
            <div className="space-y-2">
              <Button 
                className="w-full h-12 text-lg font-bold"
                onClick={processTransaction}
                disabled={cart.length === 0 || amountPaid < total || loading}
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Processing...
                  </>
                ) : (
                  <>
                    <Receipt className="w-5 h-5 mr-2" />
                    Complete Sale
                  </>
                )}
              </Button>
              <Button 
                variant="outline" 
                className="w-full"
                onClick={clearCart}
                disabled={cart.length === 0}
              >
                Clear Cart
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Payment Modal */}
      {showPaymentModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-4">Add Payment - {currentPayment.type}</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Amount</label>
                <Input
                  type="number"
                  value={currentPayment.amount}
                  onChange={(e) => setCurrentPayment({
                    ...currentPayment,
                    amount: Number(e.target.value)
                  })}
                  placeholder="Enter amount"
                />
              </div>
              {(currentPayment.type === 'ZAIN_CASH' || currentPayment.type === 'SUPER_QI' || currentPayment.type === 'ALTAIF_BANK') && (
                <div>
                  <label className="block text-sm font-medium mb-2">Provider Details</label>
                  <select 
                    className="w-full p-2 border rounded"
                    onChange={(e) => setCurrentPayment({
                      ...currentPayment,
                      provider: e.target.value
                    })}
                  >
                    <option value="">Select Provider</option>
                    <option value="ZAIN">ZAIN Cash</option>
                    <option value="ASIA_CELL">Asia Cell</option>
                    <option value="SUPER_QI">SuperQi</option>
                    <option value="ALTAIF_BANK">ALTaif Bank</option>
                  </select>
                </div>
              )}
              <div className="flex space-x-2">
                <Button 
                  variant="outline" 
                  onClick={() => setShowPaymentModal(false)}
                  className="flex-1"
                >
                  Cancel
                </Button>
                <Button 
                  onClick={() => addPayment(currentPayment)}
                  className="flex-1"
                  disabled={currentPayment.amount <= 0}
                >
                  Add Payment
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Receipt Modal */}
      {showReceiptModal && receipt && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <div className="text-center mb-4">
              <h3 className="text-lg font-semibold">Transaction Complete</h3>
              <Badge variant="default" className="mt-2">
                <Check className="w-4 h-4 mr-1" />
                Receipt #{receipt.transaction_number}
              </Badge>
            </div>
            
            {/* Receipt Content */}
            <div className="border-2 border-dashed border-gray-300 p-4 bg-gray-50 rounded-lg">
              <div className="text-center mb-4">
                <h4 className="font-bold">TSH ERP SYSTEM</h4>
                <p className="text-sm text-gray-600">Retail Receipt</p>
                <p className="text-xs text-gray-500">{new Date().toLocaleString()}</p>
              </div>
              
              <div className="space-y-2 text-sm">
                {receipt.items?.map((item: any, index: number) => (
                  <div key={index} className="flex justify-between">
                    <span>{item.product_name} x{item.quantity}</span>
                    <span>{item.line_total.toLocaleString()} IQD</span>
                  </div>
                ))}
                <div className="border-t pt-2">
                  <div className="flex justify-between font-bold">
                    <span>Total:</span>
                    <span>{receipt.total_amount.toLocaleString()} IQD</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Paid:</span>
                    <span>{receipt.amount_paid.toLocaleString()} IQD</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Change:</span>
                    <span>{receipt.change_amount.toLocaleString()} IQD</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="flex space-x-2 mt-4">
              <Button 
                variant="outline" 
                onClick={() => setShowReceiptModal(false)}
                className="flex-1"
              >
                Close
              </Button>
              <Button 
                onClick={() => window.print()}
                className="flex-1"
              >
                <Receipt className="w-4 h-4 mr-2" />
                Print Receipt
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Google Lens Search Modal */}
      {showGoogleLens && (
        <GoogleLensSearch
          onProductSelect={addToCart}
          onClose={() => setShowGoogleLens(false)}
          language={language}
        />
      )}

      {/* Enhanced Payment Modal */}
      {showEnhancedPayment && (
        <EnhancedPaymentModal
          isOpen={showEnhancedPayment}
          onClose={() => setShowEnhancedPayment(false)}
          totalAmount={total}
          amountPaid={amountPaid}
          onAddPayment={addPayment}
          language={language}
        />
      )}
    </div>
  )
} 