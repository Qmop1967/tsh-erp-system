# Modern Settings System

## Overview
A comprehensive, modern settings interface designed for ERP systems with floating card-based UI, similar to major ERP platforms like SAP, Oracle NetSuite, and Odoo.

## Architecture

### Main Settings Dashboard
**Route:** `/settings`  
**Component:** `ModernSettingsPage.tsx`

The main settings dashboard features a beautiful floating card layout with 5 major modules:

---

## 1. **Integrations Module** 🔌
**Color:** Blue gradient  
**Icon:** Plug  
**Description:** Connect with external services and APIs

### Sub-modules:
- **WhatsApp Business API** (`/settings/integrations/whatsapp`)
  - Configure WhatsApp Business integration
  - Manage phone number ID, access tokens
  - Set up webhooks for incoming messages
  - Test connection functionality

- **Zoho Integration** (`/settings/integrations/zoho`)
  - Connect to Zoho CRM, Books, Inventory
  - OAuth configuration
  - Module-specific sync controls
  - Real-time data synchronization

- **API Configuration** (`/settings/integrations/api`)
  - Manage API keys
  - Configure webhook endpoints
  - API documentation access

---

## 2. **Authentication & Security Module** 🛡️
**Color:** Purple gradient  
**Icon:** Shield  
**Description:** Manage authentication methods and security settings

### Sub-modules:
- **Devices Management** (`/settings/auth/devices`)
  - View all authorized devices
  - Trust/Untrust devices
  - Monitor active sessions
  - Track device location and IP addresses
  - Remove unauthorized devices

- **Multi-Factor Authentication (MFA)** (`/settings/auth/mfa`)
  - Enable/disable 2FA
  - Choose authentication method:
    - Authenticator app (Google Authenticator, Authy)
    - SMS text messages
    - Email verification
  - QR code setup
  - Backup recovery codes management

- **Active Sessions** (`/settings/auth/sessions`)
  - View all active user sessions
  - Monitor login locations and times
  - Force logout from specific sessions

- **User Tracking** (`/settings/auth/tracking`)
  - Track user activities
  - Login history
  - Activity logs

- **Audit Logging** (`/settings/auth/audit`)
  - System audit logs
  - Security events
  - Compliance tracking

- **Governance** (`/settings/auth/governance`)
  - Define security policies
  - Compliance rules
  - Password policies
  - Session timeout settings

---

## 3. **RBAC & Record Security Module** ✅
**Color:** Emerald gradient  
**Icon:** ShieldCheck  
**Description:** Role-Based Access Control and Record-Level Security

### Sub-modules:
- **Users** (`/users`)
  - Manage system users
  - Create and edit user accounts
  - Assign roles and permissions

- **Roles** (`/roles`)
  - Create and configure user roles
  - Define role hierarchies
  - Role-based permissions

- **Permissions** (`/permissions`)
  - Granular permission management
  - Define access rights
  - Module-level permissions

- **Record Rules (RSL)** (`/settings/rbac/record-rules`)
  - Set up record-level security rules
  - Data access restrictions
  - Field-level security

- **Rule Groups** (`/settings/rbac/rule-groups`)
  - Organize security rules
  - Group management
  - Rule templates

---

## 4. **General Settings Module** ⚙️
**Color:** Orange gradient  
**Icon:** Settings  
**Description:** Company information and system preferences

### Sub-modules:
- **Organization Profile** (`/settings/general/organization`)
  - Company name and legal information
  - Tax ID and registration numbers
  - Contact information (email, phone, website)
  - Business address
  - Company logo upload
  - Establishment date
  - Regional settings (currency, timezone, language)

- **Translation Subsystem** (`/settings/translations`)
  - Multi-language management
  - Dynamic translation updates
  - Language-specific content
  - RTL support

- **System Preferences** (`/settings/general/preferences`)
  - Date and time formats
  - Number formats
  - Default values
  - UI preferences

---

## 5. **Accounting & Finance Module** 💰
**Color:** Indigo gradient  
**Icon:** Calculator  
**Description:** Financial configuration and accounting settings

### Sub-modules:
- **Journals** (`/accounting/journal-entries`)
  - Configure accounting journals
  - Posting rules
  - Journal templates

- **Chart of Accounts** (`/accounting/chart-of-accounts`)
  - Account structure management
  - Account categories
  - Account hierarchies

- **Fiscal Periods** (`/settings/accounting/periods`)
  - Define fiscal years
  - Accounting periods
  - Period lock/unlock

---

## Design Features

### Visual Design
- **Floating Cards:** Modern card-based UI with shadow and hover effects
- **Gradient Backgrounds:** Each module has its unique gradient color scheme
- **Smooth Animations:** Hover states and transitions for better UX
- **Icons:** Lucide React icons for consistency
- **Responsive:** Mobile-first design that adapts to all screen sizes

### User Experience
- **Quick Navigation:** Click any card to navigate to settings
- **Visual Hierarchy:** Clear separation between modules
- **Status Indicators:** Visual feedback for enabled/disabled features
- **Coming Soon Tags:** Features under development are clearly marked

### Accessibility
- **Keyboard Navigation:** Full keyboard support
- **Screen Reader Friendly:** Semantic HTML and ARIA labels
- **Color Contrast:** WCAG AA compliant color schemes
- **Focus Indicators:** Clear focus states for all interactive elements

---

## Implementation Status

### ✅ Completed
- Modern Settings Dashboard
- WhatsApp Business API Settings
- Zoho Integration Settings
- Devices Management
- MFA Settings
- Organization Profile
- Translation Management (existing)

### 🚧 In Progress
- API Configuration
- Active Sessions Management
- User Tracking
- Audit Logging
- Governance Settings

### 📋 Planned
- Record Rules (RSL)
- Rule Groups
- System Preferences
- Fiscal Periods
- Additional authentication methods

---

## Technical Stack

- **Frontend Framework:** React 18 + TypeScript
- **Routing:** React Router v6
- **Icons:** Lucide React
- **Styling:** Tailwind CSS
- **State Management:** Zustand (auth store)
- **Forms:** React Hook Form (planned)
- **Validation:** Zod (planned)

---

## File Structure

```
frontend/src/pages/settings/
├── ModernSettingsPage.tsx          # Main settings dashboard
├── integrations/
│   ├── WhatsAppBusinessSettings.tsx
│   ├── ZohoIntegrationSettings.tsx
│   └── APIConfiguration.tsx        # Coming soon
├── auth/
│   ├── DevicesManagement.tsx
│   ├── MFASettings.tsx
│   ├── SessionsManagement.tsx      # Coming soon
│   ├── UserTracking.tsx            # Coming soon
│   ├── AuditLogging.tsx            # Coming soon
│   └── Governance.tsx              # Coming soon
├── rbac/
│   ├── RecordRules.tsx             # Coming soon
│   └── RuleGroups.tsx              # Coming soon
├── general/
│   ├── OrganizationProfile.tsx
│   └── SystemPreferences.tsx       # Coming soon
├── accounting/
│   └── FiscalPeriods.tsx           # Coming soon
└── DynamicTranslationManagementPage.tsx  # Existing
```

---

## Routes Configuration

All routes are protected and require authentication. Add to `App.tsx`:

```typescript
// Settings Routes
<Route path="/settings" element={<ProtectedRoute><ModernSettingsPage /></ProtectedRoute>} />
<Route path="/settings/integrations/whatsapp" element={<ProtectedRoute><WhatsAppBusinessSettings /></ProtectedRoute>} />
<Route path="/settings/integrations/zoho" element={<ProtectedRoute><ZohoIntegrationSettings /></ProtectedRoute>} />
<Route path="/settings/auth/devices" element={<ProtectedRoute><DevicesManagement /></ProtectedRoute>} />
<Route path="/settings/auth/mfa" element={<ProtectedRoute><MFASettings /></ProtectedRoute>} />
<Route path="/settings/general/organization" element={<ProtectedRoute><OrganizationProfile /></ProtectedRoute>} />
<Route path="/settings/translations" element={<ProtectedRoute><DynamicTranslationManagementPage /></ProtectedRoute>} />
```

---

## Usage Example

### Navigate to Settings
```typescript
import { useNavigate } from 'react-router-dom';

const navigate = useNavigate();
navigate('/settings');
```

### Navigate to Specific Setting
```typescript
// Go to WhatsApp settings
navigate('/settings/integrations/whatsapp');

// Go to MFA settings
navigate('/settings/auth/mfa');

// Go to Organization Profile
navigate('/settings/general/organization');
```

---

## Backend Integration

### Required API Endpoints

#### WhatsApp Integration
- `POST /api/settings/integrations/whatsapp` - Save configuration
- `GET /api/settings/integrations/whatsapp` - Get configuration
- `POST /api/settings/integrations/whatsapp/test` - Test connection

#### Zoho Integration
- `POST /api/settings/integrations/zoho` - Save configuration
- `GET /api/settings/integrations/zoho` - Get configuration
- `POST /api/settings/integrations/zoho/sync` - Trigger sync
- `GET /api/settings/integrations/zoho/modules` - Get module status

#### Devices Management
- `GET /api/settings/auth/devices` - List all devices
- `DELETE /api/settings/auth/devices/:id` - Remove device
- `PUT /api/settings/auth/devices/:id/trust` - Trust/untrust device

#### MFA Settings
- `POST /api/settings/auth/mfa/enable` - Enable MFA
- `POST /api/settings/auth/mfa/disable` - Disable MFA
- `GET /api/settings/auth/mfa/qr` - Get QR code
- `GET /api/settings/auth/mfa/backup-codes` - Generate backup codes

#### Organization Profile
- `GET /api/settings/organization` - Get organization profile
- `PUT /api/settings/organization` - Update organization profile
- `POST /api/settings/organization/logo` - Upload logo

---

## Security Considerations

1. **Authentication Required:** All settings routes are protected
2. **Role-Based Access:** Admin or specific permissions required
3. **Audit Logging:** All changes should be logged
4. **Sensitive Data:** Encrypt API keys and tokens in database
5. **CSRF Protection:** Implement CSRF tokens for state-changing operations
6. **Rate Limiting:** Protect settings API endpoints from abuse

---

## Future Enhancements

1. **Export/Import Settings:** Backup and restore configurations
2. **Settings History:** Track changes over time
3. **Multi-tenancy:** Support for multiple organizations
4. **Advanced Search:** Quick search across all settings
5. **Settings Templates:** Pre-configured templates for common setups
6. **Webhooks Manager:** Visual webhook configuration
7. **API Key Rotation:** Automated key rotation policies
8. **SSO Integration:** SAML, OAuth2, OpenID Connect
9. **Compliance Reports:** Generate compliance documentation
10. **Settings Versioning:** Version control for configurations

---

## Contributing

When adding new settings:

1. Create a new component in the appropriate directory
2. Add the route to `App.tsx`
3. Update the `settingsModules` array in `ModernSettingsPage.tsx`
4. Add necessary API endpoints
5. Update this documentation
6. Add translations for new features
7. Write tests for new functionality

---

## Support

For questions or issues:
- Email: support@tsh-travel.com
- Documentation: /docs/settings
- GitHub Issues: [Create an issue]

---

*Last Updated: October 4, 2025*
