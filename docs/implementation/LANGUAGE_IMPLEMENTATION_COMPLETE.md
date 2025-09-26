# TSH ERP System - Language Support Implementation

## Overview
The TSH ERP System now includes comprehensive bilingual support for English and Arabic languages with proper RTL (Right-to-Left) text handling.

## Features Implemented

### 1. Language Switching System
- **Language Switcher Component**: Located in the header of every page
- **Persistent Storage**: Language preference is saved in localStorage
- **Real-time Switching**: No page reload required when switching languages
- **RTL Support**: Automatic text direction switching for Arabic

### 2. Translation System
- **Comprehensive Translations**: All UI text is translated
- **Translation Keys**: Organized by modules (dashboard, financial, inventory, etc.)
- **Type Safety**: TypeScript support for translation keys
- **Fallback System**: Falls back to the key if translation is missing

### 3. Supported Languages
- **English (en)**: Default language, LTR text direction
- **Arabic (ar)**: Full Arabic support with RTL text direction

## Implementation Details

### Language Store (`/stores/languageStore.ts`)
Uses Zustand for state management:
```typescript
interface LanguageState {
  language: Language
  isRTL: boolean
  setLanguage: (language: Language) => void
}
```

### Translation Files (`/lib/translations.ts`)
Organized translation object with nested keys:
```typescript
export const translations = {
  en: {
    'dashboard.title': 'TSH ERP Dashboard',
    'financial.totalReceivables': 'Total Receivables',
    // ... more translations
  },
  ar: {
    'dashboard.title': 'لوحة تحكم نظام TSH ERP',
    'financial.totalReceivables': 'إجمالي المستحقات',
    // ... more translations
  }
}
```

### Usage in Components
```typescript
import { useLanguageStore } from '@/stores/languageStore'
import { useTranslations } from '@/lib/translations'

function MyComponent() {
  const { language } = useLanguageStore()
  const t = useTranslations(language)
  
  return <h1>{t.dashboard}</h1>
}
```

### Language Switcher Component (`/components/LanguageSwitcher.tsx`)
- Toggle button design
- Shows current selected language
- Smooth transitions

## Translated Modules

### 1. Dashboard
- ✅ Dashboard title and header
- ✅ Financial overview (receivables, payables, stock value)
- ✅ Inventory summary (positive items, total pieces)
- ✅ Staff summary (partner salesmen, travel salespersons)
- ✅ Money boxes (all 7 money boxes with descriptions)
- ✅ Quick actions buttons
- ✅ Loading states and error messages

### 2. Navigation & Layout
- ✅ Header welcome message
- ✅ Page titles
- ✅ Language switcher
- ✅ User information display

### 3. HR Module
- ✅ HR Management title
- ✅ Module description

### 4. Sales Module
- ✅ Sales Management title
- ✅ Module description

## RTL Support

### CSS Implementation (`/index.css`)
- Automatic direction switching
- RTL-specific margin and padding adjustments
- Proper text alignment for Arabic content

### Key RTL Features
- Right-to-left text flow
- Mirrored layout elements
- Proper spacing adjustments
- Arabic typography support

## Dashboard Data Integration

### API Endpoints
All dashboard data comes from backend APIs:
- `/api/accounting/summary` - Financial data
- `/api/inventory/summary` - Inventory metrics
- `/api/users/summary` - Staff counts (requires authentication)
- `/api/cashflow/summary` - Money box balances

### Real-time Data
- Auto-refresh every 30 seconds
- Manual refresh button
- Error handling with fallback data
- Loading states

## Business Metrics Displayed

### Financial Overview
1. **Total Receivables** (إجمالي المستحقات)
2. **Total Payables** (إجمالي المدفوعات)
3. **Stock Value (Cost)** (قيمة المخزون - التكلفة)

### Inventory Summary
1. **Positive Items in Warehouse** (الأصناف الموجبة في المستودع)
2. **Total Pieces Available** (إجمالي القطع المتاحة)

### Staff Summary
1. **Partner Salesmen** (مندوبي الشركاء) - TSH Partner Salesman app users
2. **Travel Salespersons** (مندوبي السفر) - TSH Salesperson app users

### Money Boxes (صناديق النقد)
1. **Main Money Box** (الصندوق الرئيسي)
2. **Frat Awsat Vector** (فرات أوسط فيكتور)
3. **First South Vector** (فيكتور الجنوب الأول)
4. **North Vector** (فيكتور الشمال)
5. **West Vector** (فيكتور الغرب)
6. **Dayla Money Box** (صندوق ديالى)
7. **Baghdad Money Box** (صندوق بغداد)
8. **Total Cash** (إجمالي النقد) - Sum of all money boxes

## Usage Instructions

### For End Users
1. **Switch Language**: Click the language switcher in the top-right header
2. **Arabic Mode**: Everything switches to Arabic with RTL layout
3. **English Mode**: Everything switches to English with LTR layout
4. **Persistent**: Your language choice is remembered across sessions

### For Developers
1. **Adding New Translations**: Add keys to both `en` and `ar` objects in `/lib/translations.ts`
2. **Using Translations**: Import `useLanguageStore` and `useTranslations`
3. **RTL Styling**: Use existing RTL CSS classes or add new ones to `/index.css`

## Current Status
- ✅ Language switching system implemented
- ✅ All dashboard content translated
- ✅ RTL support fully functional
- ✅ Backend API integration complete
- ✅ Persistent language storage
- ✅ Real-time data refresh
- ✅ Error handling and loading states

## Next Steps for Future Development
When adding new features, ensure:
1. Add translation keys for both English and Arabic
2. Use the `useTranslations` hook for all user-facing text
3. Test RTL layout for Arabic content
4. Consider cultural differences in UI design for Arabic users

The TSH ERP System now provides a fully localized experience for both English and Arabic users, with all requested business metrics displayed in a modern, responsive dashboard.
