import React, { useState, useEffect, useMemo } from 'react'
import { useLanguageStore } from '../../stores/languageStore'
import { useDynamicTranslations, useTranslationStore } from '../../lib/dynamicTranslations'
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
  AlertCircle,
  Loader2
} from 'lucide-react'

interface EditableTranslation {
  key: string
  en: string
  ar: string
  category: string
  isModified: boolean
}

const DynamicTranslationManagementPage: React.FC = () => {
  const { language } = useLanguageStore()
  const { t, isLoading: translationsLoading, refreshTranslations } = useDynamicTranslations(language)
  const { translations, loadTranslations, updateTranslation } = useTranslationStore()
  
  // State for all translations
  const [editableTranslations, setEditableTranslations] = useState<EditableTranslation[]>([])
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle')
  const [editingKey, setEditingKey] = useState<string | null>(null)
  const [isInitialized, setIsInitialized] = useState(false)

  // Initialize translations from the store
  useEffect(() => {
    if (!isInitialized && (Object.keys(translations.en).length > 0 || Object.keys(translations.ar).length > 0)) {
      const allKeys = new Set([
        ...Object.keys(translations.en || {}),
        ...Object.keys(translations.ar || {})
      ])

      const translationList: EditableTranslation[] = Array.from(allKeys).map(key => ({
        key,
        en: translations.en?.[key] || key,
        ar: translations.ar?.[key] || key,
        category: determineCategory(key),
        isModified: false
      }))

      setEditableTranslations(translationList)
      setIsInitialized(true)
    }
  }, [translations, isInitialized])

  // Auto-load translations on mount
  useEffect(() => {
    if (Object.keys(translations.en).length === 0 && Object.keys(translations.ar).length === 0 && !translationsLoading) {
      loadTranslations()
    }
  }, [translations, translationsLoading, loadTranslations])

  const determineCategory = (key: string): string => {
    if (key.includes('dashboard') || key.includes('Dashboard')) return 'Dashboard'
    if (key.includes('sales') || key.includes('Sales') || key.includes('customer') || key.includes('allies')) return 'Sales'
    if (key.includes('employee') || key.includes('Employee') || key.includes('travel') || key.includes('partner') || key.includes('retail')) return 'HR'
    if (key.includes('accounting') || key.includes('Accounting') || key.includes('account')) return 'Accounting'
    if (key.includes('setting') || key.includes('Setting') || key.includes('translation')) return 'Settings'
    if (key.includes('nav') || key.includes('Nav') || key.includes('menu')) return 'Navigation'
    return 'General'
  }

  const categories = useMemo(() => {
    const cats = ['all', ...new Set(editableTranslations.map(t => t.category))]
    return cats
  }, [editableTranslations])

  const filteredTranslations = useMemo(() => {
    let filtered = editableTranslations

    if (selectedCategory !== 'all') {
      filtered = filtered.filter(t => t.category === selectedCategory)
    }

    if (searchTerm.trim()) {
      const search = searchTerm.toLowerCase()
      filtered = filtered.filter(t => 
        t.key.toLowerCase().includes(search) ||
        t.en.toLowerCase().includes(search) ||
        t.ar.includes(search)
      )
    }

    return filtered.sort((a, b) => a.key.localeCompare(b.key))
  }, [editableTranslations, selectedCategory, searchTerm])

  const updateTranslationValue = (key: string, language: 'en' | 'ar', value: string) => {
    setEditableTranslations(prev => 
      prev.map(t => 
        t.key === key 
          ? { 
              ...t, 
              [language]: value, 
              isModified: true 
            }
          : t
      )
    )
  }

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
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const result = await response.json()
      
      if (result.status === 'success') {
        // Update the translation store
        modifiedTranslations.forEach(t => {
          updateTranslation('en', t.key, t.en)
          updateTranslation('ar', t.key, t.ar)
        })
        
        // Mark as saved
        setEditableTranslations(prev => 
          prev.map(t => ({ ...t, isModified: false }))
        )
        
        // Refresh the translations in the UI
        await refreshTranslations()
        
        setSaveStatus('saved')
        setTimeout(() => setSaveStatus('idle'), 3000)
      } else {
        throw new Error(result.message || 'Failed to save translations')
      }
    } catch (error) {
      console.error('Error saving translations:', error)
      setSaveStatus('error')
      setTimeout(() => setSaveStatus('idle'), 5000)
    }
  }

  const resetTranslations = async () => {
    try {
      const response = await fetch('/api/settings/translations/reset', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      // Reload translations from server
      await loadTranslations()
      setIsInitialized(false) // Force re-initialization
      
      setSaveStatus('saved')
      setTimeout(() => setSaveStatus('idle'), 3000)
    } catch (error) {
      console.error('Error resetting translations:', error)
      setSaveStatus('error')
      setTimeout(() => setSaveStatus('idle'), 5000)
    }
  }

  const modifiedCount = editableTranslations.filter(t => t.isModified).length

  if (translationsLoading && !isInitialized) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex items-center space-x-2">
          <Loader2 className="w-6 h-6 animate-spin" />
          <span className="text-lg">Loading translations...</span>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center">
              <Globe className="w-8 h-8 mr-3 text-blue-600" />
              {language === 'ar' ? 'إدارة الترجمات' : 'Translation Management'}
            </h1>
            <p className="text-gray-600 mt-2">
              {language === 'ar' 
                ? 'إدارة وتحرير نصوص الترجمة في النظام' 
                : 'Manage and edit translation strings across the system'
              }
            </p>
          </div>
          
          <div className="flex items-center space-x-3">
            {modifiedCount > 0 && (
              <span className="bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full text-sm font-medium">
                {modifiedCount} {language === 'ar' ? 'تغيير' : 'changes'}
              </span>
            )}
            
            <button
              onClick={resetTranslations}
              disabled={saveStatus === 'saving'}
              className="flex items-center px-4 py-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              {language === 'ar' ? 'إعادة تعيين' : 'Reset'}
            </button>
            
            <button
              onClick={saveAllTranslations}
              disabled={modifiedCount === 0 || saveStatus === 'saving'}
              className={`flex items-center px-6 py-2 rounded-lg font-medium transition-colors ${
                modifiedCount > 0 && saveStatus !== 'saving'
                  ? 'bg-blue-600 text-white hover:bg-blue-700'
                  : 'bg-gray-300 text-gray-500 cursor-not-allowed'
              }`}
            >
              {saveStatus === 'saving' ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : saveStatus === 'saved' ? (
                <Check className="w-4 h-4 mr-2" />
              ) : saveStatus === 'error' ? (
                <AlertCircle className="w-4 h-4 mr-2" />
              ) : (
                <Save className="w-4 h-4 mr-2" />
              )}
              {saveStatus === 'saving'
                ? (language === 'ar' ? 'جارٍ الحفظ...' : 'Saving...')
                : saveStatus === 'saved'
                ? (language === 'ar' ? 'تم الحفظ' : 'Saved!')
                : saveStatus === 'error'
                ? (language === 'ar' ? 'خطأ' : 'Error')
                : (language === 'ar' ? 'حفظ التغييرات' : 'Save Changes')
              }
            </button>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="mb-6 flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            placeholder={language === 'ar' ? 'البحث في الترجمات...' : 'Search translations...'}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
        
        <div className="relative">
          <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="pl-10 pr-8 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent appearance-none bg-white min-w-48"
          >
            <option value="all">{language === 'ar' ? 'جميع الفئات' : 'All Categories'}</option>
            {categories.filter(cat => cat !== 'all').map(category => (
              <option key={category} value={category}>{category}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Results Info */}
      <div className="mb-4 text-sm text-gray-600">
        {language === 'ar' 
          ? `عرض ${filteredTranslations.length} من ${editableTranslations.length} ترجمة`
          : `Showing ${filteredTranslations.length} of ${editableTranslations.length} translations`
        }
      </div>

      {/* Translation Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {language === 'ar' ? 'مفتاح الترجمة' : 'Translation Key'}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {language === 'ar' ? 'الإنجليزية' : 'English'}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {language === 'ar' ? 'العربية' : 'Arabic'}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {language === 'ar' ? 'الفئة' : 'Category'}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {language === 'ar' ? 'الحالة' : 'Status'}
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredTranslations.map((translation) => (
                <tr key={translation.key} className={`hover:bg-gray-50 ${translation.isModified ? 'bg-yellow-50' : ''}`}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">
                        {translation.key}
                      </code>
                    </div>
                  </td>
                  
                  <td className="px-6 py-4">
                    {editingKey === `${translation.key}-en` ? (
                      <input
                        type="text"
                        value={translation.en}
                        onChange={(e) => updateTranslationValue(translation.key, 'en', e.target.value)}
                        onBlur={() => setEditingKey(null)}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') setEditingKey(null)
                          if (e.key === 'Escape') setEditingKey(null)
                        }}
                        className="w-full px-3 py-2 border border-blue-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        autoFocus
                      />
                    ) : (
                      <div 
                        onClick={() => setEditingKey(`${translation.key}-en`)}
                        className="cursor-pointer hover:bg-gray-100 px-3 py-2 rounded min-h-[2.5rem] flex items-center"
                      >
                        {translation.en || <span className="text-gray-400 italic">Empty</span>}
                        <Edit3 className="w-4 h-4 ml-2 text-gray-400 opacity-0 group-hover:opacity-100" />
                      </div>
                    )}
                  </td>
                  
                  <td className="px-6 py-4">
                    {editingKey === `${translation.key}-ar` ? (
                      <input
                        type="text"
                        value={translation.ar}
                        onChange={(e) => updateTranslationValue(translation.key, 'ar', e.target.value)}
                        onBlur={() => setEditingKey(null)}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') setEditingKey(null)
                          if (e.key === 'Escape') setEditingKey(null)
                        }}
                        className="w-full px-3 py-2 border border-blue-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent text-right"
                        dir="rtl"
                        autoFocus
                      />
                    ) : (
                      <div 
                        onClick={() => setEditingKey(`${translation.key}-ar`)}
                        className="cursor-pointer hover:bg-gray-100 px-3 py-2 rounded min-h-[2.5rem] flex items-center text-right"
                        dir="rtl"
                      >
                        {translation.ar || <span className="text-gray-400 italic">Empty</span>}
                        <Edit3 className="w-4 h-4 mr-2 text-gray-400 opacity-0 group-hover:opacity-100" />
                      </div>
                    )}
                  </td>
                  
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      {translation.category}
                    </span>
                  </td>
                  
                  <td className="px-6 py-4 whitespace-nowrap">
                    {translation.isModified ? (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                        <AlertCircle className="w-3 h-3 mr-1" />
                        {language === 'ar' ? 'معدل' : 'Modified'}
                      </span>
                    ) : (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        <Check className="w-3 h-3 mr-1" />
                        {language === 'ar' ? 'محفوظ' : 'Saved'}
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {filteredTranslations.length === 0 && (
        <div className="text-center py-12">
          <Globe className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            {language === 'ar' ? 'لا توجد ترجمات' : 'No translations found'}
          </h3>
          <p className="text-gray-500">
            {language === 'ar' 
              ? 'لا توجد ترجمات تطابق معايير البحث المحددة'
              : 'No translations match the current search criteria'
            }
          </p>
        </div>
      )}
    </div>
  )
}

export default DynamicTranslationManagementPage 