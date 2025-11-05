# TSH ERP System - Language Switching System

## Overview
The TSH ERP System now includes a comprehensive Arabic and English language switching system with proper RTL (Right-to-Left) support for Arabic text.

## Features
- ✅ **Language Switcher Component**: Toggle between Arabic (العربية) and English
- ✅ **Persistent Language Selection**: Language preference is saved in localStorage
- ✅ **RTL Layout Support**: Proper right-to-left layout for Arabic
- ✅ **Comprehensive Translations**: All UI elements are translated
- ✅ **Automatic Font Selection**: Optimized fonts for Arabic text
- ✅ **Icon Direction Adjustment**: Icons flip appropriately for RTL layout

## How to Use

### Language Switcher
The language switcher is located in the top-right corner of the header. It shows:
- **"EN"** when Arabic is active (click to switch to English)
- **"ع"** when English is active (click to switch to Arabic)

### Adding New Translations

1. **Add to Translation File**: Edit `src/lib/translations.ts`
```typescript
export const translations = {
  en: {
    // Add your English text here
    newFeature: 'New Feature',
  },
  ar: {
    // Add your Arabic translation here
    newFeature: 'ميزة جديدة',
  },
}
```

2. **Use in Components**:
```typescript
import { useLanguageStore } from '@/stores/languageStore'
import { useTranslations } from '@/lib/translations'

function MyComponent() {
  const { language } = useLanguageStore()
  const t = useTranslations(language)
  
  return <h1>{t.newFeature}</h1>
}
```

## Implementation Details

### Language Store (`src/stores/languageStore.ts`)
- Uses Zustand for state management
- Persists language selection in localStorage
- Automatically applies HTML direction and language attributes
- Manages RTL/LTR state

### Translation System (`src/lib/translations.ts`)
- Centralized translation object for both languages
- Type-safe translation keys
- Hook-based translation access

### RTL CSS Support (`src/index.css`)
- Comprehensive RTL styling overrides
- Margin, padding, and spacing adjustments
- Flexbox and positioning fixes
- Icon direction handling
- Arabic font optimization

### Language Initializer (`src/components/LanguageInitializer.tsx`)
- Ensures language settings are applied on app startup
- Manages body classes for CSS targeting
- Handles browser reload scenarios

## Supported Languages
- **English (en)**: Left-to-right layout
- **Arabic (ar)**: Right-to-left layout with proper Arabic font rendering

## Current Translations
The system includes translations for:
- Navigation menus and labels
- Dashboard components and metrics
- Financial data labels
- Inventory and staff sections
- Quick actions and buttons
- Status messages and notifications
- Form labels and placeholders
- Common UI elements (save, cancel, edit, etc.)

## Best Practices

### When Adding New Features:
1. **Always use translation keys** instead of hardcoded strings
2. **Add both English and Arabic translations** simultaneously
3. **Test RTL layout** to ensure proper alignment
4. **Consider text length differences** between languages
5. **Use semantic translation keys** (e.g., `userProfile` not `text1`)

### RTL Considerations:
- Use `space-x-reverse` class for RTL spacing
- Check icon directions in Arabic mode
- Test dropdown and modal positioning
- Verify text alignment in complex layouts

## Testing
1. Start the development server: `npm run dev`
2. Open the application in your browser
3. Click the language switcher in the header
4. Verify:
   - Text changes to Arabic/English
   - Layout switches to RTL/LTR
   - Icons flip appropriately
   - Spacing and alignment look correct

## File Structure
```
frontend/src/
├── stores/
│   └── languageStore.ts          # Language state management
├── lib/
│   └── translations.ts           # Translation definitions
├── components/
│   ├── LanguageInitializer.tsx   # Language initialization
│   └── ui/
│       └── LanguageSwitcher.tsx  # Language switcher button
├── index.css                     # RTL CSS support
└── main.tsx                      # App wrapper with LanguageInitializer
```

## Extending the System

### Adding a New Language
1. Update the `Language` type in `languageStore.ts`
2. Add the new language to the `translations` object
3. Update the `LanguageSwitcher` component logic
4. Add any language-specific CSS if needed

### Adding Context-Specific Translations
Create namespaced translation keys:
```typescript
const translations = {
  en: {
    dashboard: {
      welcome: 'Welcome to Dashboard',
      stats: 'Statistics'
    },
    inventory: {
      items: 'Items',
      stock: 'Stock Level'
    }
  }
}
```

## Notes
- The system automatically detects and applies the user's language preference
- RTL mode affects the entire application layout
- All form inputs and interactive elements are properly adjusted for RTL
- The language selection persists across browser sessions 