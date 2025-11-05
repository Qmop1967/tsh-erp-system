import React, { useState, useEffect, useMemo } from 'react'
import { translations, TranslationKey } from '../../lib/translations'
import { useLanguageStore } from '../../stores/languageStore'
import { useTranslations } from '../../lib/translations'
import { 
  Search, 
  Save, 
  RefreshCw, 
  Filter, 
  Edit3, 
  Globe, 
  Eye, 
  X,
  Check,
  AlertCircle
} from 'lucide-react'

interface EditableTranslation {
  key: TranslationKey
  en: string
  ar: string
  category: string
  isModified: boolean
}

const TranslationManagementPage: React.FC = () => {
  const { language } = useLanguageStore()
  const t = useTranslations(language)
  
  // State for all translations
  const [editableTranslations, setEditableTranslations] = useState<EditableTranslation[]>([])
  const [originalTranslations, setOriginalTranslations] = useState<{en: Record<string, string>, ar: Record<string, string>}>({en: {}, ar: {}})
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle')
  const [isLoading, setIsLoading] = useState(true)
  
  // Load translations from backend on component mount
  useEffect(() => {
    loadTranslationsFromBackend()
  }, [])

  const loadTranslationsFromBackend = async () => {
    try {
      setIsLoading(true)
      const response = await fetch('/api/settings/translations')
      
      if (response.ok) {
        const result = await response.json()
        console.log('Loaded translations from backend:', result)
        
        if (result.data) {
          setOriginalTranslations(result.data)
          initializeEditableTranslations(result.data)
        } else {
          // Fallback to local translations if backend doesn't have data
          console.log('Backend has no data, using local translations')
          setOriginalTranslations(translations)
          initializeEditableTranslations(translations)
        }
      } else {
        console.warn('Failed to load from backend, using local translations')
        setOriginalTranslations(translations)
        initializeEditableTranslations(translations)
      }
    } catch (error) {
      console.error('Error loading translations:', error)
      // Fallback to local translations
      setOriginalTranslations(translations)
      initializeEditableTranslations(translations)
    } finally {
      setIsLoading(false)
    }
  }

  const initializeEditableTranslations = (translationData: {en: Record<string, string>, ar: Record<string, string>}) => {
    const allKeys = new Set([
      ...Object.keys(translationData.en || {}),
      ...Object.keys(translationData.ar || {})
    ])

    const editableList: EditableTranslation[] = Array.from(allKeys).map(key => ({
      key: key as TranslationKey,
      en: translationData.en[key] || '',
      ar: translationData.ar[key] || '',
      category: categorizeTranslation(key),
      isModified: false
    }))

    setEditableTranslations(editableList)
  }
  
  // Categorize translations based on key patterns
  const categorizeTranslation = (key: string): string => {
    if (key.includes('dashboard') || key.includes('Dashboard')) return 'Dashboard'
    if (key.includes('nav') || key.includes('Nav') || key.includes('menu')) return 'Navigation'
    if (key.includes('header') || key.includes('Header') || key.includes('title')) return 'Header'
    if (key.includes('sales') || key.includes('Sales')) return 'Sales'
    if (key.includes('purchase') || key.includes('Purchase')) return 'Purchases'
    if (key.includes('account') || key.includes('Account')) return 'Accounting'
    if (key.includes('inventory') || key.includes('Inventory')) return 'Inventory'
    if (key.includes('employee') || key.includes('Employee') || key.includes('hr') || key.includes('HR')) return 'HR'
    if (key.includes('customer') || key.includes('Customer') || key.includes('client') || key.includes('Client')) return 'Customers'
    if (key.includes('expense') || key.includes('Expense')) return 'Expenses'
    if (key.includes('pos') || key.includes('POS')) return 'POS'
    if (key.includes('cashflow') || key.includes('CashFlow')) return 'Cash Flow'
    if (key.includes('button') || key.includes('Button') || key.includes('btn')) return 'Buttons'
    if (key.includes('form') || key.includes('Form') || key.includes('input')) return 'Forms'
    return 'General'
  }
  
  // Get unique categories
  const categories = useMemo(() => {
    const uniqueCategories = new Set(editableTranslations.map(t => t.category))
    return ['all', ...Array.from(uniqueCategories).sort()]
  }, [editableTranslations])
  
  // Filter translations based on search and category
  const filteredTranslations = useMemo(() => {
    return editableTranslations.filter(translation => {
      const matchesSearch = searchTerm === '' || 
        translation.key.toLowerCase().includes(searchTerm.toLowerCase()) ||
        translation.en.toLowerCase().includes(searchTerm.toLowerCase()) ||
        translation.ar.includes(searchTerm)
      
      const matchesCategory = selectedCategory === 'all' || translation.category === selectedCategory
      
      return matchesSearch && matchesCategory
    })
  }, [editableTranslations, searchTerm, selectedCategory])
  
  // Update a translation
  const updateTranslation = (key: TranslationKey, language: 'en' | 'ar', value: string) => {
    setEditableTranslations(prev => 
      prev.map(t => 
        t.key === key 
          ? { 
              ...t, 
              [language]: value, 
              isModified: value !== originalTranslations[language][key]
            }
          : t
      )
    )
  }
  
  // Save all translations (with real API calls)
  const saveAllTranslations = async () => {
    setSaveStatus('saving')
    
    try {
      const modifiedTranslations = editableTranslations.filter(t => t.isModified)
      
      if (modifiedTranslations.length === 0) {
        setSaveStatus('saved')
        setTimeout(() => setSaveStatus('idle'), 3000)
        return
      }
      
      // Prepare translation updates for API
      const translationUpdates = {
        en: {} as Record<string, string>,
        ar: {} as Record<string, string>
      }
      
      modifiedTranslations.forEach(t => {
        translationUpdates.en[t.key] = t.en
        translationUpdates.ar[t.key] = t.ar
      })
      
      // Make API call to save translations
      const response = await fetch('/api/settings/translations', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          translations: translationUpdates
        })
      })
      
      if (!response.ok) {
        throw new Error(`Failed to save: ${response.statusText}`)
      }
      
      const result = await response.json()
      console.log('Save result:', result)
      
      // Mark translations as saved (no longer modified)
      setEditableTranslations(prev => 
        prev.map(t => ({ ...t, isModified: false }))
      )
      
      // Update original translations to reflect the new saved state
      const newOriginalTranslations = {
        en: {} as Record<string, string>,
        ar: {} as Record<string, string>
      }
      
      editableTranslations.forEach(t => {
        newOriginalTranslations.en[t.key] = t.en
        newOriginalTranslations.ar[t.key] = t.ar
      })
      
      setOriginalTranslations(newOriginalTranslations)
      
      setSaveStatus('saved')
      
      // Force refresh of the page to reload translations
      setTimeout(() => {
        window.location.reload()
      }, 1500)
      
    } catch (error) {
      console.error('Error saving translations:', error)
      setSaveStatus('error')
    }
    
    // Reset status after 3 seconds
    setTimeout(() => setSaveStatus('idle'), 3000)
  }
  
  // Reset all translations to default (with API call)
  const resetTranslations = async () => {
    try {
      // Call backend API to reset translations
      const response = await fetch('/api/settings/translations/reset', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      })
      
      if (!response.ok) {
        console.warn('Failed to reset translations on backend, proceeding with local reset')
      } else {
        const result = await response.json()
        console.log('Translation reset result:', result)
      }
      
      // Reload translations from backend
      await loadTranslationsFromBackend()
      
    } catch (error) {
      console.error('Error resetting translations:', error)
      // Reset local state as fallback
      setEditableTranslations(prev => 
        prev.map(t => ({
          ...t,
          en: originalTranslations.en[t.key] || '',
          ar: originalTranslations.ar[t.key] || '',
          isModified: false
        }))
      )
    }
  }
  
  // Get count of modified translations
  const modifiedCount = editableTranslations.filter(t => t.isModified).length
  
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="bg-white rounded-lg shadow-sm p-8">
            <div className="flex items-center justify-center">
              <RefreshCw className="animate-spin w-6 h-6 mr-2" />
              <span>Loading translations...</span>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <Globe className="w-8 h-8 text-blue-600 mr-3" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">{t.translationManagement}</h1>
                <p className="text-gray-600 mt-1">{t.manageTranslations}</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              {/* Save Status Indicator */}
              {saveStatus === 'saving' && (
                <div className="flex items-center text-blue-600">
                  <RefreshCw className="animate-spin w-4 h-4 mr-2" />
                  <span className="text-sm">Saving...</span>
                </div>
              )}
              {saveStatus === 'saved' && (
                <div className="flex items-center text-green-600">
                  <Check className="w-4 h-4 mr-2" />
                  <span className="text-sm">{t.translationsSaved}</span>
                </div>
              )}
              {saveStatus === 'error' && (
                <div className="flex items-center text-red-600">
                  <AlertCircle className="w-4 h-4 mr-2" />
                  <span className="text-sm">Save failed</span>
                </div>
              )}
              
              {/* Action Buttons */}
              <button
                onClick={loadTranslationsFromBackend}
                className="flex items-center px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Reload
              </button>
              
              <button
                onClick={resetTranslations}
                className="flex items-center px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
              >
                <X className="w-4 h-4 mr-2" />
                {t.resetTranslations}
              </button>
              
              <button
                onClick={saveAllTranslations}
                disabled={modifiedCount === 0 || saveStatus === 'saving'}
                className="flex items-center px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <Save className="w-4 h-4 mr-2" />
                {t.saveTranslations} {modifiedCount > 0 && `(${modifiedCount})`}
              </button>
            </div>
          </div>
        </div>

        {/* Controls */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
            <div className="flex-1 max-w-md">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <input
                  type="text"
                  placeholder={t.searchTranslations}
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="flex items-center">
                <Filter className="w-4 h-4 text-gray-500 mr-2" />
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="all">{t.allCategories}</option>
                  {categories.slice(1).map(category => (
                    <option key={category} value={category}>{category}</option>
                  ))}
                </select>
              </div>
              
                             <div className="text-sm text-gray-500">
                 {filteredTranslations.length} {t.translationCount}
               </div>
            </div>
          </div>
        </div>

        {/* Preview Section */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex items-center mb-4">
            <Eye className="w-5 h-5 text-gray-600 mr-2" />
            <h3 className="text-lg font-medium text-gray-900">{t.translationPreview}</h3>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="border rounded-lg p-4">
              <h4 className="font-medium text-blue-600 mb-2">{t.previewInEnglish}</h4>
              <div className="text-sm text-gray-600">
                Sample preview with current translations...
              </div>
            </div>
            
            <div className="border rounded-lg p-4">
              <h4 className="font-medium text-green-600 mb-2">{t.previewInArabic}</h4>
              <div className="text-sm text-gray-600" dir="rtl">
                معاينة نموذجية مع الترجمات الحالية...
              </div>
            </div>
          </div>
        </div>

        {/* Translations Table */}
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
                     <div className="px-6 py-4 border-b border-gray-200">
             <h3 className="text-lg font-medium text-gray-900">
               {filteredTranslations.length} {t.translationCount}
             </h3>
           </div>
          
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    ACTIONS
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    CATEGORY
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {t.arabicValue}
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {t.englishValue}
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {t.translationKey}
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredTranslations.map((translation) => (
                  <tr 
                    key={translation.key} 
                    className={`hover:bg-gray-50 ${translation.isModified ? 'bg-yellow-50' : ''}`}
                  >
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex items-center space-x-2">
                        <Edit3 className="w-4 h-4 text-gray-400" />
                        {translation.isModified && (
                          <span className="inline-block w-2 h-2 bg-yellow-400 rounded-full" title="Modified"></span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                        {translation.category}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      <input
                        type="text"
                        value={translation.ar}
                        onChange={(e) => updateTranslation(translation.key, 'ar', e.target.value)}
                        className="w-full border border-gray-300 rounded px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        dir="rtl"
                      />
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      <input
                        type="text"
                        value={translation.en}
                        onChange={(e) => updateTranslation(translation.key, 'en', e.target.value)}
                        className="w-full border border-gray-300 rounded px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-500">
                      {translation.key}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}

export default TranslationManagementPage 