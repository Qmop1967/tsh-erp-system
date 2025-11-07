import { useEffect } from 'react'
import { useLanguageStore } from '@/stores/languageStore'

export function LanguageInitializer({ children }: { children: React.ReactNode }) {
  const { language, isRTL } = useLanguageStore()

  useEffect(() => {
    // Apply language settings on mount and when language changes
    document.documentElement.dir = isRTL ? 'rtl' : 'ltr'
    document.documentElement.lang = language
    
    // Add/remove RTL class to body for CSS targeting
    if (isRTL) {
      document.body.classList.add('rtl')
      document.body.classList.remove('ltr')
    } else {
      document.body.classList.add('ltr')
      document.body.classList.remove('rtl')
    }
  }, [language, isRTL])

  return <>{children}</>
}
