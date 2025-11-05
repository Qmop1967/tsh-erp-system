import React, { useState, useRef, useCallback } from 'react'
import { Camera, Search, Upload, X, Target, AlertCircle, CheckCircle, Loader2, Package } from 'lucide-react'
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
  confidence?: number
}

interface ImageRecognitionProps {
  onProductSelect?: (product: Product) => void
  onClose?: () => void
  language?: 'ar' | 'en'
}

export default function ImageRecognition({ 
  onProductSelect, 
  onClose, 
  language = 'en' 
}: ImageRecognitionProps) {
  const [isCapturing, setIsCapturing] = useState(false)
  const [capturedImage, setCapturedImage] = useState<string | null>(null)
  const [searchResults, setSearchResults] = useState<Product[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [stream, setStream] = useState<MediaStream | null>(null)
  
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const startCamera = useCallback(async () => {
    try {
      setError(null)
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { 
          facingMode: 'environment', // Use rear camera
          width: { ideal: 1920 },
          height: { ideal: 1080 }
        }
      })
      
      setStream(mediaStream)
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream
        videoRef.current.play()
      }
      setIsCapturing(true)
    } catch (err) {
      setError('Unable to access camera. Please check permissions.')
      console.error('Camera access error:', err)
    }
  }, [])

  const stopCamera = useCallback(() => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop())
      setStream(null)
    }
    setIsCapturing(false)
  }, [stream])

  const captureImage = useCallback(() => {
    if (videoRef.current && canvasRef.current) {
      const canvas = canvasRef.current
      const video = videoRef.current
      
      canvas.width = video.videoWidth
      canvas.height = video.videoHeight
      
      const ctx = canvas.getContext('2d')
      if (ctx) {
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
        const imageData = canvas.toDataURL('image/jpeg', 0.8)
        setCapturedImage(imageData)
        stopCamera()
        searchByImage(imageData)
      }
    }
  }, [stopCamera])

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (e) => {
        const imageData = e.target?.result as string
        setCapturedImage(imageData)
        searchByImage(imageData)
      }
      reader.readAsDataURL(file)
    }
  }

  const searchByImage = async (imageData: string) => {
    try {
      setLoading(true)
      setError(null)
      
      // Convert base64 to blob
      const response = await fetch(imageData)
      const blob = await response.blob()
      
      // Create FormData for image upload
      const formData = new FormData()
      formData.append('image', blob, 'captured_image.jpg')
      
      // Send to backend for image recognition
      const searchResponse = await api.post('/api/products/search-by-image', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      
      setSearchResults(searchResponse.data.products || [])
      
      if (searchResponse.data.products.length === 0) {
        setError('No matching products found. Try taking another photo from a different angle.')
      }
      
    } catch (err) {
      console.error('Image search error:', err)
      setError('Failed to search for products. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const retakePhoto = () => {
    setCapturedImage(null)
    setSearchResults([])
    setError(null)
    startCamera()
  }

  const selectProduct = (product: Product) => {
    if (onProductSelect) {
      onProductSelect(product)
    }
    if (onClose) {
      onClose()
    }
  }

  React.useEffect(() => {
    return () => {
      stopCamera()
    }
  }, [stopCamera])

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-2">
              <Target className="w-6 h-6 text-blue-600" />
              <h2 className="text-xl font-bold">Product Image Recognition</h2>
            </div>
            <Button variant="ghost" size="icon" onClick={onClose}>
              <X className="w-5 h-5" />
            </Button>
          </div>

          {error && (
            <div className="mb-4 bg-red-50 border border-red-200 rounded-lg p-4 flex items-center space-x-2">
              <AlertCircle className="w-4 h-4 text-red-600" />
              <span className="text-red-800">{error}</span>
            </div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Camera/Image Section */}
            <div className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Camera className="w-5 h-5" />
                    <span>Capture Product Image</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {!isCapturing && !capturedImage && (
                      <div className="space-y-4">
                        <div className="bg-gray-100 rounded-lg p-8 text-center">
                          <Camera className="w-16 h-16 mx-auto mb-4 text-gray-400" />
                          <p className="text-gray-600 mb-4">
                            Take a photo of the product to search inventory
                          </p>
                          <div className="space-y-2">
                            <Button onClick={startCamera} className="w-full">
                              <Camera className="w-4 h-4 mr-2" />
                              Start Camera
                            </Button>
                            <Button 
                              variant="outline" 
                              onClick={() => fileInputRef.current?.click()}
                              className="w-full"
                            >
                              <Upload className="w-4 h-4 mr-2" />
                              Upload Image
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

                    {isCapturing && (
                      <div className="space-y-4">
                        <div className="relative bg-black rounded-lg overflow-hidden">
                          <video
                            ref={videoRef}
                            className="w-full h-64 object-cover"
                            autoPlay
                            playsInline
                            muted
                          />
                          <div className="absolute inset-0 flex items-center justify-center">
                            <div className="border-2 border-white border-dashed rounded-lg w-48 h-48 flex items-center justify-center">
                              <Target className="w-8 h-8 text-white" />
                            </div>
                          </div>
                        </div>
                        <div className="flex space-x-2">
                          <Button onClick={captureImage} className="flex-1">
                            <Camera className="w-4 h-4 mr-2" />
                            Capture
                          </Button>
                          <Button variant="outline" onClick={stopCamera} className="flex-1">
                            Cancel
                          </Button>
                        </div>
                      </div>
                    )}

                    {capturedImage && (
                      <div className="space-y-4">
                        <div className="relative">
                          <img
                            src={capturedImage}
                            alt="Captured product"
                            className="w-full h-64 object-cover rounded-lg"
                          />
                          {loading && (
                            <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center rounded-lg">
                              <div className="text-white text-center">
                                <Loader2 className="w-8 h-8 animate-spin mx-auto mb-2" />
                                <p>Searching products...</p>
                              </div>
                            </div>
                          )}
                        </div>
                        <div className="flex space-x-2">
                          <Button variant="outline" onClick={retakePhoto} className="flex-1">
                            <Camera className="w-4 h-4 mr-2" />
                            Retake
                          </Button>
                          <Button 
                            variant="outline" 
                            onClick={() => fileInputRef.current?.click()}
                            className="flex-1"
                          >
                            <Upload className="w-4 h-4 mr-2" />
                            Upload Different
                          </Button>
                        </div>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Results Section */}
            <div className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Search className="w-5 h-5" />
                    <span>Search Results</span>
                    {searchResults.length > 0 && (
                      <Badge variant="default">{searchResults.length} found</Badge>
                    )}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {loading && (
                    <div className="text-center py-8">
                      <Loader2 className="w-12 h-12 animate-spin mx-auto mb-4 text-blue-600" />
                      <p className="text-gray-600">Analyzing image...</p>
                    </div>
                  )}

                  {!loading && searchResults.length === 0 && !error && (
                    <div className="text-center py-8 text-gray-500">
                      <Package className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                      <p>Take a photo to search for products</p>
                    </div>
                  )}

                  {searchResults.length > 0 && (
                    <div className="space-y-3">
                      {searchResults.map((product) => (
                        <div
                          key={product.id}
                          className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors"
                          onClick={() => selectProduct(product)}
                        >
                          <div className="w-16 h-16 bg-white rounded-lg flex items-center justify-center">
                            {product.image_url ? (
                              <img
                                src={product.image_url}
                                alt={product.name_en}
                                className="w-full h-full object-cover rounded-lg"
                              />
                            ) : (
                              <Package className="w-6 h-6 text-gray-400" />
                            )}
                          </div>
                          <div className="flex-1">
                            <h4 className="font-semibold">
                              {language === 'ar' ? product.name_ar : product.name_en}
                            </h4>
                            <p className="text-sm text-gray-500">SKU: {product.sku}</p>
                            <div className="flex items-center space-x-2 mt-1">
                              <span className="font-bold text-blue-600">
                                {product.price.toLocaleString()} IQD
                              </span>
                              <Badge variant={product.stock_quantity > 0 ? "default" : "destructive"}>
                                Stock: {product.stock_quantity}
                              </Badge>
                              {product.confidence && (
                                <Badge variant="outline">
                                  {Math.round(product.confidence * 100)}% match
                                </Badge>
                              )}
                            </div>
                          </div>
                          <CheckCircle className="w-5 h-5 text-green-600" />
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>

          <canvas ref={canvasRef} className="hidden" />
        </div>
      </div>
    </div>
  )
} 