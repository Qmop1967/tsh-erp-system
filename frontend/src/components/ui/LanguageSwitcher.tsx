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
      variant="ghost"
      size="icon"
      onClick={toggleLanguage}
      className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-xl transition-all duration-200 relative group"
      title={language === 'en' ? 'Switch to Arabic' : 'تبديل إلى الإنجليزية'}
    >
      <div className="flex items-center space-x-1 group-hover:scale-105 transition-transform">
        <Languages className="h-5 w-5" />
        <span className="text-xs font-bold px-1 py-0.5 bg-gray-200 dark:bg-gray-600 rounded text-gray-700 dark:text-gray-200 min-w-[24px] text-center">
          {language === 'en' ? 'ع' : 'EN'}
        </span>
      </div>
    </Button>
  )
}
