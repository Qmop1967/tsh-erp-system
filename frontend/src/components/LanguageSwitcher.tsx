import React from 'react'
import { useLanguageStore } from '../stores/languageStore'
import { useTranslation } from '../hooks/useTranslation'

export const LanguageSwitcher: React.FC = () => {
  const { language, setLanguage } = useLanguageStore()
  const { t } = useTranslation()

  return (
    <div className="flex items-center gap-2">
      <span className="text-sm text-gray-600">{t('language.switch')}:</span>
      <div className="flex bg-gray-100 rounded-lg p-1">
        <button
          onClick={() => setLanguage('en')}
          className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
            language === 'en'
              ? 'bg-white text-blue-600 shadow-sm'
              : 'text-gray-600 hover:text-gray-800'
          }`}
        >
          {t('language.english')}
        </button>
        <button
          onClick={() => setLanguage('ar')}
          className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
            language === 'ar'
              ? 'bg-white text-blue-600 shadow-sm'
              : 'text-gray-600 hover:text-gray-800'
          }`}
        >
          {t('language.arabic')}
        </button>
      </div>
    </div>
  )
}
