# Zoho Sync System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ZOHO SYNC SYSTEM                                   │
│                    (One-Direction: Zoho → TSH ERP)                          │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              DATA SOURCE                                     │
└─────────────────────────────────────────────────────────────────────────────┘

                                ┌──────────────┐
                                │  ZOHO CLOUD  │
                                │              │
                                │  ┌────────┐  │
                                │  │ Items  │  │
                                │  ├────────┤  │
                                │  │Customer│  │
                                │  ├────────┤  │
                                │  │Vendors │  │
                                │  └────────┘  │
                                └──────┬───────┘
                                       │
                            ┌──────────┴──────────┐
                            │   Zoho API          │
                            │   (OAuth 2.0)       │
                            └──────────┬──────────┘
                                       │
                        ┌──────────────┴──────────────┐
                        │  Real-Time Webhooks         │
                        │  (Optional)                 │
                        └──────────────┬──────────────┘
                                       │
                                       ▼

┌─────────────────────────────────────────────────────────────────────────────┐
│                        TSH ERP BACKEND (FastAPI)                            │
└─────────────────────────────────────────────────────────────────────────────┘

                        ┌──────────────────────┐
                        │  Webhook Receiver    │
                        │  (Real-Time Trigger) │
                        └──────────┬───────────┘
                                   │
                        ┌──────────▼───────────┐
                        │  Sync Orchestrator   │
                        │  - Batch Processing  │
                        │  - Error Handling    │
                        │  - Retry Logic       │
                        └──────────┬───────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
         ┌──────────▼─────┐  ┌────▼─────┐  ┌────▼─────┐
         │ Data Analyzer  │  │ Data     │  │ Data     │
         │                │  │Transformer│  │Validator │
         │ - Count Records│  │          │  │          │
         │ - Find New     │  │ - Field  │  │ - Type   │
         │ - Find Updated │  │   Mapping│  │   Check  │
         │ - Find Errors  │  │ - Rules  │  │ - Required│
         └────────────────┘  │   Apply  │  │   Fields │
                             │ - Image  │  │ - Format │
                             │   Download│  │   Valid  │
                             └──────┬───┘  └────┬─────┘
                                    │           │
                                    └─────┬─────┘
                                          │
                                   ┌──────▼──────┐
                                   │   Backup    │
                                   │  (Optional) │
                                   └──────┬──────┘
                                          │
                                   ┌──────▼──────┐
                                   │  Database   │
                                   │  Operations │
                                   │             │
                                   │ - INSERT    │
                                   │ - UPDATE    │
                                   │ - UPSERT    │
                                   └──────┬──────┘
                                          │
                                   ┌──────▼──────┐
                                   │   Logger    │
                                   │             │
                                   │ - Log Entry │
                                   │ - Statistics│
                                   │ - Update    │
                                   └─────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                         DATA STORAGE LAYER                                   │
└─────────────────────────────────────────────────────────────────────────────┘

        ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
        │ PostgreSQL   │  │ Config Files │  │  Log Files   │
        │   Database   │  │              │  │              │
        │              │  │ - mappings   │  │ - sync_logs  │
        │ ┌──────────┐ │  │ - control    │  │ - statistics │
        │ │  items   │ │  │ - credentials│  │              │
        │ ├──────────┤ │  └──────────────┘  └──────────────┘
        │ │customers │ │
        │ ├──────────┤ │
        │ │ vendors  │ │
        │ └──────────┘ │
        └──────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                          FRONTEND UI (React)                                │
└─────────────────────────────────────────────────────────────────────────────┘

                        ┌──────────────────────┐
                        │   Settings Page      │
                        │   /settings          │
                        └──────────┬───────────┘
                                   │
                        ┌──────────▼───────────┐
                        │ Zoho Integration     │
                        │ Settings Page        │
                        └──────────┬───────────┘
                                   │
                        ┌──────────▼───────────┐
                        │ Sync Mappings UI     │
                        │                      │
                        │ ┌────────────────┐   │
                        │ │ Entity Tabs    │   │
                        │ │ - Items ✓      │   │
                        │ │ - Customers    │   │
                        │ │ - Vendors      │   │
                        │ └────────────────┘   │
                        │                      │
                        │ ┌────────────────┐   │
                        │ │ Statistics     │   │
                        │ │ Dashboard      │   │
                        │ └────────────────┘   │
                        │                      │
                        │ ┌────────────────┐   │
                        │ │ Field Mappings │   │
                        │ │ Table          │   │
                        │ └────────────────┘   │
                        │                      │
                        │ ┌────────────────┐   │
                        │ │ Control Panel  │   │
                        │ │ - Enable/Disable│  │
                        │ │ - Analyze      │   │
                        │ │ - Sync Now     │   │
                        │ │ - Reset        │   │
                        │ └────────────────┘   │
                        │                      │
                        │ ┌────────────────┐   │
                        │ │ Sync Logs      │   │
                        │ │ Viewer         │   │
                        │ └────────────────┘   │
                        └──────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                          API ENDPOINTS (18)                                  │
└─────────────────────────────────────────────────────────────────────────────┘

Configuration:
  GET    /api/settings/integrations/zoho/sync/mappings
  GET    /api/settings/integrations/zoho/sync/mappings/{entity_type}
  POST   /api/settings/integrations/zoho/sync/mappings/{entity_type}
  POST   /api/settings/integrations/zoho/sync/mappings/{entity_type}/reset

Control:
  GET    /api/settings/integrations/zoho/sync/control
  POST   /api/settings/integrations/zoho/sync/control

Operations:
  POST   /api/settings/integrations/zoho/sync/{entity_type}/analyze
  POST   /api/settings/integrations/zoho/sync/{entity_type}/execute
  GET    /api/settings/integrations/zoho/sync/{entity_type}/status
  POST   /api/settings/integrations/zoho/sync/{entity_type}/toggle
  GET    /api/settings/integrations/zoho/sync/statistics

Logs:
  GET    /api/settings/integrations/zoho/sync/logs
  DELETE /api/settings/integrations/zoho/sync/logs

┌─────────────────────────────────────────────────────────────────────────────┐
│                          SYNC FLOW DIAGRAM                                   │
└─────────────────────────────────────────────────────────────────────────────┘

 1. Trigger        2. Analyze         3. Transform       4. Validate
    (Webhook/       (Data              (Field             (Data
     Manual)         Analysis)          Mapping)           Integrity)
      │                │                   │                   │
      ▼                ▼                   ▼                   ▼
  ┌────────┐      ┌────────┐         ┌────────┐         ┌────────┐
  │ Event  │──────│ Count  │─────────│ Map    │─────────│ Check  │
  │ Detect │      │ & Diff │         │ Fields │         │ Rules  │
  └────────┘      └────────┘         └────────┘         └────────┘
                                                              │
                                                              ▼
 5. Backup         6. Execute         7. Log             8. Update
    (Optional)       (DB Insert/       (Record            (Statistics)
                     Update)            Operation)
      │                │                   │                   │
      ▼                ▼                   ▼                   ▼
  ┌────────┐      ┌────────┐         ┌────────┐         ┌────────┐
  │ Save   │──────│ Write  │─────────│ Create │─────────│ Update │
  │ Backup │      │ to DB  │         │ Log    │         │ Stats  │
  └────────┘      └────────┘         └────────┘         └────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                       FIELD MAPPING EXAMPLE                                  │
└─────────────────────────────────────────────────────────────────────────────┘

Zoho Item Record:
{
  "item_id": "ZI-001",
  "name": "Product A",
  "sku": "prd-a-001",
  "rate": 99.99,
  "stock_on_hand": 100,
  "image_name": "product-a.jpg"
}
              │
              │ Field Mapping + Transformation
              │
              ▼
TSH ERP Item Record:
{
  "zoho_item_id": "ZI-001",
  "name": "Product A",
  "sku": "PRD-A-001",           ← Uppercase transformation
  "unit_price": 99.99,
  "quantity_on_hand": 100,
  "image_url": "/images/..."    ← Downloaded and stored
}

┌─────────────────────────────────────────────────────────────────────────────┐
│                         ERROR HANDLING FLOW                                  │
└─────────────────────────────────────────────────────────────────────────────┘

                        ┌──────────────────┐
                        │  Sync Attempt    │
                        └────────┬─────────┘
                                 │
                        ┌────────▼─────────┐
                        │   Success?       │
                        └────────┬─────────┘
                                 │
                    ┌────────────┼────────────┐
                    │ YES                     │ NO
                    │                         │
         ┌──────────▼────────┐      ┌────────▼─────────┐
         │  Log Success      │      │  Attempt < Max?  │
         │  Update Stats     │      └────────┬─────────┘
         │  Continue         │               │
         └───────────────────┘    ┌──────────┼──────────┐
                                  │ YES               │ NO
                                  │                   │
                       ┌──────────▼────────┐   ┌──────▼──────┐
                       │  Wait Retry Delay │   │ Log Error   │
                       │  Retry Sync       │   │ Notify User │
                       └───────────────────┘   │ Stop Sync   │
                                               └─────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                      CONFIGURATION HIERARCHY                                 │
└─────────────────────────────────────────────────────────────────────────────┘

Global Configuration
    │
    ├── Zoho Credentials
    │   ├── Organization ID
    │   ├── Client ID
    │   ├── Client Secret
    │   └── Refresh Token
    │
    ├── Sync Control
    │   ├── Webhook Settings
    │   ├── Batch Size
    │   ├── Retry Settings
    │   ├── Error Threshold
    │   └── Validation Rules
    │
    └── Entity Mappings
        │
        ├── Items
        │   ├── Enabled: Yes/No
        │   ├── Sync Mode: Real-time/Scheduled
        │   ├── Field Mappings (17 fields)
        │   ├── Image Sync: Enabled
        │   └── Auto Create/Update: Enabled
        │
        ├── Customers
        │   ├── Enabled: Yes/No
        │   ├── Sync Mode: Real-time/Scheduled
        │   ├── Field Mappings (18 fields)
        │   └── Auto Create/Update: Enabled
        │
        └── Vendors
            ├── Enabled: Yes/No
            ├── Sync Mode: Real-time/Scheduled
            ├── Field Mappings (16 fields)
            └── Auto Create/Update: Enabled

┌─────────────────────────────────────────────────────────────────────────────┐
│                        MONITORING DASHBOARD                                  │
└─────────────────────────────────────────────────────────────────────────────┘

╔═══════════════════════════════════════════════════════════════════════════╗
║                     SYNC STATISTICS DASHBOARD                              ║
╠═══════════════════════════════════════════════════════════════════════════╣
║                                                                            ║
║  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    ║
║  │ Total Synced│  │Total Errors │  │Active Syncs │  │ Total Logs  │    ║
║  │             │  │             │  │             │  │             │    ║
║  │    1,500    │  │      12     │  │      3      │  │     524     │    ║
║  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘    ║
║                                                                            ║
║  Entity Performance:                                                       ║
║  ┌────────────────────────────────────────────────────────────────┐      ║
║  │ Items:      500 synced | 5 errors  | Success Rate: 99.0% | ✓   │      ║
║  │ Customers:  600 synced | 4 errors  | Success Rate: 99.3% | ✓   │      ║
║  │ Vendors:    400 synced | 3 errors  | Success Rate: 99.2% | ✓   │      ║
║  └────────────────────────────────────────────────────────────────┘      ║
║                                                                            ║
║  Recent Activity:                                                          ║
║  ┌────────────────────────────────────────────────────────────────┐      ║
║  │ ● sync_item_20251004_143022    | Success | 2 mins ago          │      ║
║  │ ● sync_customer_20251004_142500| Success | 7 mins ago          │      ║
║  │ ● sync_vendor_20251004_142100  | Success | 11 mins ago         │      ║
║  │ ● sync_item_20251004_141800    | Error   | 14 mins ago         │      ║
║  └────────────────────────────────────────────────────────────────┘      ║
╚═══════════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────────────┐
│                             LEGEND                                           │
└─────────────────────────────────────────────────────────────────────────────┘

Symbols:
  ✓   = Enabled/Active
  ✗   = Disabled/Inactive
  ●   = Activity Indicator
  ▶   = Action Button
  ⚠   = Warning
  ✓   = Success
  ✗   = Error

Colors (in actual UI):
  Green  = Success/Active
  Red    = Error/Inactive
  Yellow = Warning/In Progress
  Blue   = Information
  Purple = Analysis/Statistics
  Gray   = Disabled/Neutral
```
