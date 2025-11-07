import { Button } from '@/components/ui/button'
import { useLanguageStore } from '@/stores/languageStore'
import { Languages } from 'lucide-react'

export function LanguageSwitcher() {
  const { language, setLanguage } = useLanguageStore()

  const toggleLanguage = () => {
    const newLanguage = language === 'en' ? 'ar' : 'en'
    setLanguage(newLanguage)
  }

  return (
    <Button
      variant="outline"
      size="sm"
      onClick={toggleLanguage}
      className="text-gray-700 dark:text-gray-200 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 border-gray-300 dark:border-gray-600 rounded-xl transition-all duration-200 relative group px-3 py-2 bg-white dark:bg-gray-800 shadow-sm"
      title={language === 'en' ? 'Switch to Arabic - تبديل إلى العربية' : 'Switch to English - تبديل إلى الإنجليزية'}
    >
      <div className="flex items-center space-x-2 group-hover:scale-105 transition-transform">
        <Languages className="h-4 w-4" />
        <div className="flex flex-col items-center">
          <span className="text-xs font-bold text-blue-600 dark:text-blue-400">
            {language === 'en' ? 'العربية' : 'English'}
          </span>
          <span className="text-[10px] text-gray-500 dark:text-gray-400">
            {language === 'en' ? 'ع' : 'EN'}
          </span>
        </div>
      </div>
    </Button>
  )
}
