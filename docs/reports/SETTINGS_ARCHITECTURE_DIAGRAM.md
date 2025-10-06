# Settings System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        MODERN SETTINGS DASHBOARD                             │
│                         /settings (Main Page)                                │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │
            ┌─────────────────────────┼─────────────────────────┐
            │                         │                         │
            ▼                         ▼                         ▼
┌────────────────────────┐ ┌────────────────────────┐ ┌────────────────────────┐
│   🔌 INTEGRATIONS     │ │ 🛡️ AUTHENTICATION      │ │ ✅ RBAC & RSL         │
│   (Blue Gradient)      │ │ (Purple Gradient)      │ │ (Green Gradient)      │
├────────────────────────┤ ├────────────────────────┤ ├────────────────────────┤
│                        │ │                        │ │                        │
│ ✅ WhatsApp Business  │ │ ✅ Devices Management │ │ ✅ Users              │
│    API Integration     │ │    - View Devices     │ │    /users             │
│    /settings/          │ │    - Trust/Untrust    │ │                        │
│    integrations/       │ │    - Remove Devices   │ │ ✅ Roles              │
│    whatsapp            │ │    /settings/auth/    │ │    /roles             │
│                        │ │    devices            │ │                        │
│ ✅ Zoho Integration   │ │                        │ │ ✅ Permissions        │
│    - CRM              │ │ ✅ Multi-Factor Auth  │ │    /permissions       │
│    - Books            │ │    - App/SMS/Email    │ │                        │
│    - Inventory        │ │    - QR Code Setup    │ │ 📋 Record Rules (RSL) │
│    - Invoice          │ │    - Backup Codes     │ │    /settings/rbac/    │
│    /settings/          │ │    /settings/auth/mfa │ │    record-rules       │
│    integrations/zoho   │ │                        │ │                        │
│                        │ │ 📋 Active Sessions    │ │ 📋 Rule Groups        │
│ 📋 API Configuration  │ │    /settings/auth/    │ │    /settings/rbac/    │
│    /settings/          │ │    sessions           │ │    rule-groups        │
│    integrations/api    │ │                        │ │                        │
│                        │ │ 📋 User Tracking      │ │                        │
│                        │ │    /settings/auth/    │ │                        │
│                        │ │    tracking           │ │                        │
│                        │ │                        │ │                        │
│                        │ │ 📋 Audit Logging      │ │                        │
│                        │ │    /settings/auth/    │ │                        │
│                        │ │    audit              │ │                        │
│                        │ │                        │ │                        │
│                        │ │ 📋 Governance         │ │                        │
│                        │ │    /settings/auth/    │ │                        │
│                        │ │    governance         │ │                        │
└────────────────────────┘ └────────────────────────┘ └────────────────────────┘

            ▼                         ▼
┌────────────────────────┐ ┌────────────────────────┐
│  ⚙️ GENERAL SETTINGS   │ │ 💰 ACCOUNTING &       │
│  (Orange Gradient)     │ │    FINANCE            │
├────────────────────────┤ │ (Indigo Gradient)     │
│                        │ ├────────────────────────┤
│ ✅ Organization       │ │                        │
│    Profile             │ │ ✅ Journals           │
│    - Company Info     │ │    /accounting/       │
│    - Logo Upload      │ │    journal-entries    │
│    - Contact Details  │ │                        │
│    - Business Address │ │ ✅ Chart of Accounts  │
│    - Regional Settings│ │    /accounting/       │
│    /settings/general/ │ │    chart-of-accounts  │
│    organization       │ │                        │
│                        │ │ 📋 Fiscal Periods     │
│ ✅ Translation        │ │    /settings/         │
│    Subsystem          │ │    accounting/periods │
│    - Multi-language   │ │                        │
│    - Dynamic Updates  │ │                        │
│    /settings/         │ │                        │
│    translations       │ │                        │
│                        │ │                        │
│ 📋 System Preferences │ │                        │
│    /settings/general/ │ │                        │
│    preferences        │ │                        │
└────────────────────────┘ └────────────────────────┘
```

## Legend
- ✅ = Implemented and Ready
- 📋 = Planned for Future
- 🔌 = External Integration
- 🛡️ = Security Feature
- ✅ = Access Control
- ⚙️ = Configuration
- 💰 = Financial

## Data Flow

```
┌──────────────┐
│   User       │
│   Browser    │
└──────┬───────┘
       │
       │ Navigate to /settings
       │
       ▼
┌──────────────────────┐
│  Modern Settings     │
│  Dashboard           │
│  (Card Selection)    │
└──────┬───────────────┘
       │
       │ Select Module/Sub-module
       │
       ▼
┌──────────────────────┐
│  Settings Page       │
│  (Form/Config)       │
└──────┬───────────────┘
       │
       │ Save Configuration
       │
       ▼
┌──────────────────────┐
│  API Endpoint        │
│  /api/settings/*     │
└──────┬───────────────┘
       │
       │ Store in Database
       │
       ▼
┌──────────────────────┐
│  PostgreSQL          │
│  Settings Tables     │
└──────────────────────┘
```

## Component Hierarchy

```
App.tsx
├── Routes
│   ├── /settings
│   │   └── ModernSettingsPage
│   │       ├── Integration Cards (Blue)
│   │       ├── Authentication Cards (Purple)
│   │       ├── RBAC Cards (Green)
│   │       ├── General Cards (Orange)
│   │       └── Accounting Cards (Indigo)
│   │
│   ├── /settings/integrations/whatsapp
│   │   └── WhatsAppBusinessSettings
│   │
│   ├── /settings/integrations/zoho
│   │   └── ZohoIntegrationSettings
│   │
│   ├── /settings/auth/devices
│   │   └── DevicesManagement
│   │
│   ├── /settings/auth/mfa
│   │   └── MFASettings
│   │
│   └── /settings/general/organization
│       └── OrganizationProfile
```

## Permission Structure

```
┌─────────────────────────────────────┐
│         Admin Role                  │
├─────────────────────────────────────┤
│  Has Access To:                     │
│  ✅ All Settings                    │
│  ✅ All Integrations                │
│  ✅ All Security Features           │
│  ✅ All Configurations              │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│    Settings Manager Role            │
├─────────────────────────────────────┤
│  Has Access To:                     │
│  ✅ General Settings                │
│  ✅ Organization Profile            │
│  ✅ Translations                    │
│  ❌ Security Settings               │
│  ❌ Authentication                  │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│      Regular User                   │
├─────────────────────────────────────┤
│  Has Access To:                     │
│  ✅ Own Device Management           │
│  ✅ Own MFA Settings                │
│  ❌ Organization Settings           │
│  ❌ System Configuration            │
└─────────────────────────────────────┘
```

## Technology Stack

```
┌────────────────────────────────────────────┐
│          Frontend Layer                     │
├────────────────────────────────────────────┤
│  React 18 + TypeScript                     │
│  React Router v6                           │
│  Tailwind CSS                              │
│  Lucide React Icons                        │
│  Zustand (State Management)                │
└────────────────┬───────────────────────────┘
                 │
                 │ HTTP/REST API
                 │
┌────────────────▼───────────────────────────┐
│          Backend Layer                      │
├────────────────────────────────────────────┤
│  FastAPI (Python)                          │
│  Pydantic (Validation)                     │
│  SQLAlchemy (ORM)                          │
│  Alembic (Migrations)                      │
└────────────────┬───────────────────────────┘
                 │
                 │ SQL
                 │
┌────────────────▼───────────────────────────┐
│          Database Layer                     │
├────────────────────────────────────────────┤
│  PostgreSQL                                │
│  - settings_general                        │
│  - settings_integrations                   │
│  - settings_authentication                 │
│  - settings_organization                   │
└────────────────────────────────────────────┘
```

## Database Schema (Proposed)

```sql
-- Settings Tables

CREATE TABLE settings_organization (
    id SERIAL PRIMARY KEY,
    company_name VARCHAR(255),
    legal_name VARCHAR(255),
    tax_id VARCHAR(100),
    email VARCHAR(255),
    phone VARCHAR(50),
    address TEXT,
    logo_url VARCHAR(500),
    currency VARCHAR(3),
    timezone VARCHAR(100),
    language VARCHAR(10),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE settings_integrations (
    id SERIAL PRIMARY KEY,
    integration_type VARCHAR(50), -- 'whatsapp', 'zoho', 'api'
    enabled BOOLEAN DEFAULT FALSE,
    config JSONB, -- Store integration-specific config
    last_sync TIMESTAMP,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE settings_devices (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    device_name VARCHAR(255),
    device_type VARCHAR(50), -- 'mobile', 'desktop', 'tablet'
    os VARCHAR(100),
    browser VARCHAR(100),
    ip_address VARCHAR(50),
    location VARCHAR(255),
    trusted BOOLEAN DEFAULT FALSE,
    last_active TIMESTAMP,
    created_at TIMESTAMP
);

CREATE TABLE settings_mfa (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    enabled BOOLEAN DEFAULT FALSE,
    method VARCHAR(50), -- 'app', 'sms', 'email'
    secret_key VARCHAR(500),
    backup_codes TEXT[],
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

---

*This diagram shows the complete architecture of the Modern Settings System*
