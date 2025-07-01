# TSH ERP System - Language Support Documentation

## Overview
The TSH ERP System now includes comprehensive bilingual support for English and Arabic languages, including full RTL (Right-to-Left) support for Arabic text.

## Features
- ✅ **Language Switcher**: Toggle between English and Arabic
- ✅ **RTL Support**: Proper right-to-left layout for Arabic
- ✅ **Persistent Storage**: Language preference is saved in localStorage
- ✅ **Complete Translation**: All dashboard elements are translated
- ✅ **Dynamic Updates**: Language changes apply immediately without page reload

## Implementation Details

### Language Store (Zustand)
Located: `frontend/src/stores/languageStore.ts`
- Manages current language state
- Handles RTL/LTR direction switching
- Persists language preference in localStorage
- Automatically applies HTML direction attributes

### Translation System
Located: `frontend/src/lib/translations.ts`
- Contains complete English and Arabic translations
- Organized by sections (dashboard, financial, inventory, etc.)
- Type-safe translation keys
- `useTranslations(language)` hook for easy access

### Language Switcher Component
Located: `frontend/src/components/LanguageSwitcher.tsx`
- Clean toggle button design
- Visual feedback for active language
- Integrated into the main header layout

### RTL Styling
Located: `frontend/src/index.css`
- Comprehensive RTL CSS adjustments
- Margin and padding corrections for Arabic layout
- Text alignment and direction overrides
- Seamless integration with Tailwind CSS

## Usage Examples

### In Components
```tsx
import { useLanguageStore } from '@/stores/languageStore'
import { useTranslations } from '@/lib/translations'

function MyComponent() {
  const { language } = useLanguageStore()
  const t = useTranslations(language)
  
  return <h1>{t.dashboard}</h1>
}
```

### Adding New Translations
1. Add keys to both `en` and `ar` objects in `translations.ts`
2. Use the translation in components with `t.yourNewKey`

## Dashboard Translations Coverage

### ✅ Completed Sections
- **Header & Navigation**: Dashboard title, welcome message, refresh button
- **Financial Overview**: Receivables, payables, stock value with descriptions
- **Inventory Summary**: Positive items count, total pieces available
- **Staff Summary**: Partner salesmen and travel salespersons counts
- **Money Boxes**: All 7 money boxes with regional descriptions
- **Quick Actions**: All action buttons (Reports, Transactions, Inventory, Staff)
- **Loading States**: Loading messages and error states

### Language Switcher Location
The language switcher is prominently displayed in the main header, allowing users to easily toggle between English (English) and Arabic (العربية).

## Current Metrics Displayed

### Financial Data
- **Total Receivables**: Amount owed to the company
- **Total Payables**: Amount the company owes
- **Stock Value**: Current inventory cost value

### Inventory Data  
- **Positive Items**: Number of items with positive stock
- **Total Pieces**: Sum of all pieces in stock

### Staff Data
- **Partner Salesmen**: Count of partner salesman users
- **Travel Salespersons**: Count of travel salesperson users

### Money Boxes (7 Regional Boxes)
1. **Main Money Box**: Primary cash flow operations
2. **Frat Awsat Vector**: Central region operations
3. **First South Vector**: Southern region operations  
4. **North Vector**: Northern region operations
5. **West Vector**: Western region operations
6. **Dayla Money Box**: Dayla region operations
7. **Baghdad Money Box**: Baghdad region operations
8. **Total Cash**: Sum of all money boxes

## Technical Integration

### Backend API Endpoints
All dashboard data is fetched from these endpoints:
- `GET /api/accounting/summary` - Financial data (receivables, payables, stock value)
- `GET /api/inventory/summary` - Inventory metrics (positive items, total pieces)
- `GET /api/users/summary` - Staff counts (partner salesmen, travel salespersons) 
- `GET /api/cashflow/summary` - Money box balances (all 7 regional boxes)

### Frontend Data Flow
1. `useDashboardData.ts` hook fetches data from all endpoints
2. Components use `useTranslations()` for text rendering
3. Language switcher updates global language state
4. All components re-render with new language automatically

## Future Enhancements
- [ ] Add more languages (French, German, etc.)
- [ ] Currency formatting based on locale
- [ ] Date/time formatting per language
- [ ] Number formatting per language conventions
- [ ] Translation management interface for administrators

## Development Notes
- All new components should use the translation system
- RTL styles are automatically applied when Arabic is selected
- Language preference persists across browser sessions
- Backend returns consistent data structure regardless of frontend language

This completes the comprehensive bilingual support for the TSH ERP System dashboard.
