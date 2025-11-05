import React, { useState, useRef, useCallback } from 'react'
import { Camera, Upload, Search, X, Loader, CheckCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import api from '@/lib/api'

interface Product {
  id: number
  name_ar: string
  name_en: string
  sku: string
  price: number
  stock_quantity: number
  category: string
  image_url?: string
  confidence: number
}

interface GoogleLensSearchProps {
  onProductSelect: (product: Product) => void
  onClose: () => void
  language: 'ar' | 'en'
}

export default function GoogleLensSearch({ onProductSelect, onClose, language }: GoogleLensSearchProps) {
  const [isSearching, setIsSearching] = useState(false)
  const [searchResults, setSearchResults] = useState<Product[]>([])
  const [capturedImage, setCapturedImage] = useState<string | null>(null)
  const [isCamera, setIsCamera] = useState(false)
  const [searchTime, setSearchTime] = useState<number | null>(null)
  const [error, setError] = useState<string | null>(null)
  
  const fileInputRef = useRef<HTMLInputElement>(null)
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)

  const startCamera = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { facingMode: 'environment' } // Use back camera on mobile
      })
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream
        videoRef.current.play()
        setIsCamera(true)
      }
    } catch (err) {
      setError('Unable to access camera. Please use file upload instead.')
    }
  }, [])

  const stopCamera = useCallback(() => {
    if (videoRef.current?.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream
      stream.getTracks().forEach(track => track.stop())
      setIsCamera(false)
    }
  }, [])

  const capturePhoto = useCallback(() => {
    if (videoRef.current && canvasRef.current) {
      const canvas = canvasRef.current
      const video = videoRef.current
      const context = canvas.getContext('2d')
      
      if (context) {
        canvas.width = video.videoWidth
        canvas.height = video.videoHeight
        context.drawImage(video, 0, 0)
        
        const imageData = canvas.toDataURL('image/jpeg', 0.8)
        setCapturedImage(imageData)
        stopCamera()
        
        // Automatically search after capture
        searchProductsByImage(imageData)
      }
    }
  }, [stopCamera])

  const handleFileUpload = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (e) => {
        const imageData = e.target?.result as string
        setCapturedImage(imageData)
        searchProductsByImage(imageData)
      }
      reader.readAsDataURL(file)
    }
  }, [])

  const searchProductsByImage = async (imageData: string) => {
    try {
      setIsSearching(true)
      setError(null)
      
      // Remove data:image prefix for API
      const base64Data = imageData.split(',')[1]
      
      const response = await api.post('/api/pos/enhanced/google-lens/search', {
        image_data: base64Data,
        confidence_threshold: 0.6
      })
      
      setSearchResults(response.data.products)
      setSearchTime(response.data.search_time)
      
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Search failed. Please try again.')
    } finally {
      setIsSearching(false)
    }
  }

  const handleProductSelect = (product: Product) => {
    onProductSelect(product)
    onClose()
  }

  const resetSearch = () => {
    setCapturedImage(null)
    setSearchResults([])
    setSearchTime(null)
    setError(null)
    stopCamera()
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <Card className="w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center space-x-2">
              <Search className="w-6 h-6 text-blue-600" />
              <span>
                {language === 'ar' ? 'البحث بالصورة - جوجل لينس' : 'Google Lens Image Search'}
              </span>
            </CardTitle>
            <Button variant="ghost" size="icon" onClick={onClose}>
              <X className="w-5 h-5" />
            </Button>
          </div>
        </CardHeader>
        
        <CardContent className="space-y-6">
          {/* Camera Controls */}
          {!capturedImage && !isSearching && (
            <div className="space-y-4">
              <div className="text-center">
                <p className="text-gray-600 mb-4">
                  {language === 'ar' 
                    ? 'التقط صورة للمنتج أو ارفع صورة من الجهاز'
                    : 'Take a photo of the product or upload an image'
                  }
                </p>
                
                <div className="flex justify-center space-x-4">
                  <Button
                    onClick={startCamera}
                    disabled={isCamera}
                    className="flex items-center space-x-2"
                  >
                    <Camera className="w-4 h-4" />
                    <span>
                      {language === 'ar' ? 'فتح الكاميرا' : 'Open Camera'}
                    </span>
                  </Button>
                  
                  <Button
                    onClick={() => fileInputRef.current?.click()}
                    variant="outline"
                    className="flex items-center space-x-2"
                  >
                    <Upload className="w-4 h-4" />
                    <span>
                      {language === 'ar' ? 'رفع صورة' : 'Upload Image'}
                    </span>
                  </Button>
                </div>
              </div>
              
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleFileUpload}
                className="hidden"
              />
            </div>
          )}

          {/* Camera View */}
          {isCamera && (
            <div className="text-center space-y-4">
              <div className="relative inline-block">
                <video
                  ref={videoRef}
                  className="rounded-lg max-w-full max-h-64"
                  playsInline
                  muted
                />
                <div className="absolute inset-0 border-2 border-blue-500 rounded-lg pointer-events-none">
                  <div className="absolute top-2 left-2 w-6 h-6 border-t-2 border-l-2 border-blue-500"></div>
                  <div className="absolute top-2 right-2 w-6 h-6 border-t-2 border-r-2 border-blue-500"></div>
                  <div className="absolute bottom-2 left-2 w-6 h-6 border-b-2 border-l-2 border-blue-500"></div>
                  <div className="absolute bottom-2 right-2 w-6 h-6 border-b-2 border-r-2 border-blue-500"></div>
                </div>
              </div>
              
              <div className="space-x-2">
                <Button onClick={capturePhoto} className="bg-blue-600 hover:bg-blue-700">
                  <Camera className="w-4 h-4 mr-2" />
                  {language === 'ar' ? 'التقاط الصورة' : 'Capture Photo'}
                </Button>
                <Button onClick={stopCamera} variant="outline">
                  {language === 'ar' ? 'إلغاء' : 'Cancel'}
                </Button>
              </div>
            </div>
          )}

          {/* Captured Image */}
          {capturedImage && (
            <div className="text-center">
              <img
                src={capturedImage}
                alt="Captured product"
                className="max-w-full max-h-64 rounded-lg mx-auto mb-4"
              />
              <Button onClick={resetSearch} variant="outline" size="sm">
                {language === 'ar' ? 'أخذ صورة جديدة' : 'Take New Photo'}
              </Button>
            </div>
          )}

          {/* Loading State */}
          {isSearching && (
            <div className="text-center py-8">
              <Loader className="w-12 h-12 animate-spin text-blue-600 mx-auto mb-4" />
              <p className="text-gray-600">
                {language === 'ar' 
                  ? 'جاري البحث عن المنتجات...' 
                  : 'Searching for products...'
                }
              </p>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="text-center py-4">
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-red-800">{error}</p>
                <Button onClick={resetSearch} variant="outline" size="sm" className="mt-2">
                  {language === 'ar' ? 'إعادة المحاولة' : 'Try Again'}
                </Button>
              </div>
            </div>
          )}

          {/* Search Results */}
          {searchResults.length > 0 && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold">
                  {language === 'ar' ? 'نتائج البحث' : 'Search Results'}
                </h3>
                {searchTime && (
                  <Badge variant="outline" className="text-green-600">
                    <CheckCircle className="w-3 h-3 mr-1" />
                    {searchTime.toFixed(2)}s
                  </Badge>
                )}
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {searchResults.map((product) => (
                  <Card 
                    key={product.id} 
                    className="cursor-pointer hover:shadow-md transition-shadow"
                    onClick={() => handleProductSelect(product)}
                  >
                    <CardContent className="p-4">
                      <div className="space-y-3">
                        <div className="aspect-square bg-gray-100 rounded-lg flex items-center justify-center">
                          {product.image_url ? (
                            <img
                              src={product.image_url}
                              alt={product.name_en}
                              className="w-full h-full object-cover rounded-lg"
                            />
                          ) : (
                            <div className="w-12 h-12 bg-gray-300 rounded-lg flex items-center justify-center">
                              <Search className="w-6 h-6 text-gray-500" />
                            </div>
                          )}
                        </div>
                        
                        <div>
                          <h4 className="font-semibold text-sm truncate">
                            {language === 'ar' ? product.name_ar : product.name_en}
                          </h4>
                          <p className="text-xs text-gray-500">{product.sku}</p>
                          <p className="text-xs text-gray-500">{product.category}</p>
                        </div>
                        
                        <div className="space-y-2">
                          <div className="flex justify-between items-center">
                            <span className="font-bold text-blue-600">
                              {product.price.toLocaleString()} IQD
                            </span>
                            <Badge variant={product.stock_quantity > 0 ? "default" : "destructive"}>
                              {product.stock_quantity}
                            </Badge>
                          </div>
                          
                          <div className="flex justify-between items-center">
                            <span className="text-xs text-gray-500">
                              {language === 'ar' ? 'الثقة' : 'Confidence'}
                            </span>
                            <Badge 
                              variant="outline" 
                              className={
                                product.confidence >= 0.9 ? "text-green-600" :
                                product.confidence >= 0.7 ? "text-yellow-600" :
                                "text-red-600"
                              }
                            >
                              {(product.confidence * 100).toFixed(0)}%
                            </Badge>
                          </div>
                        </div>
                        
                        <Button
                          className="w-full"
                          disabled={product.stock_quantity === 0}
                          onClick={(e) => {
                            e.stopPropagation()
                            handleProductSelect(product)
                          }}
                        >
                          {language === 'ar' ? 'اختيار المنتج' : 'Select Product'}
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )}

          {/* No Results */}
          {!isSearching && searchResults.length === 0 && capturedImage && (
            <div className="text-center py-8">
              <Search className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">
                {language === 'ar' 
                  ? 'لم يتم العثور على منتجات مطابقة. جرب صورة أخرى.' 
                  : 'No matching products found. Try another image.'
                }
              </p>
              <Button onClick={resetSearch} variant="outline" className="mt-4">
                {language === 'ar' ? 'جرب صورة أخرى' : 'Try Another Image'}
              </Button>
            </div>
          )}
        </CardContent>
        
        <canvas ref={canvasRef} className="hidden" />
      </Card>
    </div>
  )
} 