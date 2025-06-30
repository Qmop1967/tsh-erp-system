import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export type Language = 'en' | 'ar'

interface LanguageState {
  language: Language
  isRTL: boolean
  setLanguage: (language: Language) => void
}

export const useLanguageStore = create<LanguageState>()(
  persist(
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
    }),
    {
      name: 'language-store',
      onRehydrateStorage: () => (state) => {
        if (state) {
          // Apply language settings on page reload
          const isRTL = state.language === 'ar'
          document.documentElement.dir = isRTL ? 'rtl' : 'ltr'
          document.documentElement.lang = state.language
        }
      },
    }
  )
)
