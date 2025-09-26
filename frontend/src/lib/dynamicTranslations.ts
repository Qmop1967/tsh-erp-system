import { create } from 'zustand';

export interface DynamicTranslations {
  [key: string]: string;
}

export interface TranslationStore {
  translations: {
    en: DynamicTranslations;
    ar: DynamicTranslations;
  };
  isLoading: boolean;
  error: string | null;
  loadTranslations: () => Promise<void>;
  refreshTranslations: () => Promise<void>;
  updateTranslation: (language: string, key: string, value: string) => void;
}

// Translation store using Zustand
export const useTranslationStore = create<TranslationStore>((set, get) => ({
  translations: {
    en: {},
    ar: {}
  },
  isLoading: false,
  error: null,

  loadTranslations: async () => {
    set({ isLoading: true, error: null });
    
    try {
      const response = await fetch('/api/settings/translations');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      if (data.status === 'success' && data.translations) {
        set({ 
          translations: data.translations,
          isLoading: false,
          error: null 
        });
      } else {
        throw new Error('Invalid response format');
      }
    } catch (error) {
      console.error('Error loading translations:', error);
      set({ 
        isLoading: false, 
        error: error instanceof Error ? error.message : 'Unknown error'
      });
      
      // Fallback to default translations
      const fallbackTranslations = {
        en: {
          dashboard: "Dashboard",
          sales: "Sales",
          customers: "Customers",
          allies: "Allies",
          allEmployees: "All Employees",
          travelSalespersons: "Travel Salespersons",
          partnerSalesmen: "Partner Salesmen",
          retailermen: "Retailermen",
          settings: "Settings"
        },
        ar: {
          dashboard: "لوحة التحكم",
          sales: "المبيعات",
          customers: "العملاء",
          allies: "الحلفاء",
          allEmployees: "جميع الموظفين",
          travelSalespersons: "مندوبي السفر",
          partnerSalesmen: "مندوبي الشركاء",
          retailermen: "مندوبي التجزئة",
          settings: "الإعدادات"
        }
      };
      
      set({ translations: fallbackTranslations });
    }
  },

  refreshTranslations: async () => {
    const { loadTranslations } = get();
    await loadTranslations();
  },

  updateTranslation: (language: string, key: string, value: string) => {
    set((state) => ({
      translations: {
        ...state.translations,
        [language]: {
          ...state.translations[language as keyof typeof state.translations],
          [key]: value
        }
      }
    }));
  }
}));

// Hook for getting translations with language
export const useDynamicTranslations = (language: 'en' | 'ar') => {
  const { translations, isLoading, error, loadTranslations, refreshTranslations } = useTranslationStore();
  
  // Auto-load translations on first use
  React.useEffect(() => {
    if (Object.keys(translations.en).length === 0 && Object.keys(translations.ar).length === 0 && !isLoading) {
      loadTranslations();
    }
  }, [translations, isLoading, loadTranslations]);

  const t = React.useMemo(() => {
    const currentTranslations = translations[language] || {};
    
    // Create a proxy that returns the key itself if translation is missing
    return new Proxy(currentTranslations, {
      get: (target, prop: string) => {
        return target[prop] || prop;
      }
    });
  }, [translations, language]);

  return {
    t,
    isLoading,
    error,
    refreshTranslations
  };
};

// Utility function to get a single translation
export const getTranslation = (language: 'en' | 'ar', key: string): string => {
  const store = useTranslationStore.getState();
  return store.translations[language]?.[key] || key;
};

// Import React for useEffect and useMemo
import React from 'react'; 