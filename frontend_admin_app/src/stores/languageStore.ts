import { create } from 'zustand'
// import { persist } from 'zustand/middleware' // Disabled for demo mode

export type Language = 'en' | 'ar'

interface LanguageState {
  language: Language
  isRTL: boolean
  setLanguage: (language: Language) => void
}

export const useLanguageStore = create<LanguageState>()(
  // Temporarily disable persist for demo mode
  (set) => ({
    language: 'en',
    isRTL: false,
    setLanguage: (language: Language) => {
      const isRTL = language === 'ar'
      
      // Update HTML direction
      document.documentElement.dir = isRTL ? 'rtl' : 'ltr'
      document.documentElement.lang = language
      
      set({ language, isRTL })
    },
  })
)
