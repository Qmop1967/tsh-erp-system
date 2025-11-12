# TSH NeuroLink

**Event-Driven Notification & Messaging System for TSH ERP**

Version 1.0.0 | Phase 0-1 Implementation

---

## Overview

TSH NeuroLink is an intelligent notification and messaging system that transforms business events from TSH ERP into actionable notifications delivered across multiple channels. It provides real-time, context-aware communication to keep your team informed and productive.

### Key Features

- ✅ **Event Ingestion API** - Receive business events with idempotency protection
- ✅ **Smart Notifications** - Rule-based notification generation
- ✅ **Multi-User Support** - Branch and role-based access control
- ✅ **JWT Authentication** - Seamless integration with TSH ERP auth
- ✅ **RESTful API** - Full CRUD operations for events and notifications
- 🚧 **WebSocket Real-time** - Coming in Phase 2
- 🚧 **Multi-Channel Delivery** - Email, SMS, Telegram (Phase 3-4)
- 🚧 **NeuroChat** - Contextual discussions (Phase 3)
- 🚧 **Rule Engine UI** - Visual rule builder (Phase 2)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         TSH ERP Modules                          │
│   (Sales, Inventory, Invoicing, Purchases, Payments, etc.)      │
└────────────────────────┬────────────────────────────────────────┘
                         │ Business Events
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      TSH NeuroLink API                           │
│  ┌──────────────┐  ┌───────────────┐  ┌──────────────────┐    │
│  │Event Ingestion│─▶│ Rule Engine   │─▶│Notification Gen  │    │
│  │ + Idempotency │  │ (Template-    │  │ (User-specific)  │    │
│  └──────────────┘  │  based)        │  └──────────────────┘    │
│                     └───────────────┘                            │
└────────────────────────┬────────────────────────────────────────┘
                         │ Redis Event Bus
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Notification Delivery                        │
│  ┌──────────┐  ┌────────┐  ┌──────┐  ┌──────────┐  ┌────────┐ │
│  │ In-App   │  │ Email  │  │ SMS  │  │ Telegram │  │ Slack  │ │
│  │(WebSocket│  │        │  │      │  │          │  │        │ │
│  └──────────┘  └────────┘  └──────┘  └──────────┘  └────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## Database Schema

NeuroLink uses the existing `tsh_erp` PostgreSQL database with tables prefixed `neurolink_*`:

### Core Tables

1. **neurolink_events** - Business events from TSH ERP
2. **neurolink_notification_rules** - Rules for generating notifications
3. **neurolink_notifications** - User-specific notifications
4. **neurolink_messages** - NeuroChat contextual discussions
5. **neurolink_delivery_log** - Multi-channel delivery tracking
6. **neurolink_user_preferences** - Per-user notification settings
7. **neurolink_metrics** - System performance metrics

---

## Quick Start

### Prerequisites

- Python 3.9+
- PostgreSQL 14+ (TSH ERP database)
- Redis 6+
- TSH ERP running with JWT authentication

### Installation

```bash
# 1. Clone and navigate
cd /Users/khaleelal-mulla/TSH_ERP_Ecosystem/tsh_neurolink

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
nano .env  # Edit configuration

# 5. Run database migration
psql -U khaleel -d tsh_erp -f migrations/001_initial_schema.sql

# 6. Start the server
python app/main.py
```

### Development Server

```bash
# Start with auto-reload
uvicorn app.main:app --reload --port 8002
```

Access:
- **API**: http://localhost:8002
- **Docs**: http://localhost:8002/docs
- **Health**: http://localhost:8002/health

---

## API Documentation

### Authentication

All endpoints (except `/health`) require JWT authentication:

```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  http://localhost:8002/v1/notifications
```

### Event Ingestion

**POST /v1/events**

Ingest a new business event:

```json
{
  "source_module": "invoicing",
  "event_type": "invoice.overdue",
  "severity": "warning",
  "occurred_at": "2024-10-31T10:00:00Z",
  "payload": {
    "invoice_id": 12345,
    "invoice_number": "INV-2024-001",
    "customer_name": "Acme Corp",
    "amount": 50000,
    "currency": "IQD",
    "days_overdue": 7
  },
  "producer_idempotency_key": "invoice_12345_overdue_20241031",
  "correlation_id": "order_flow_98765"
}
```

### Notifications

**GET /v1/notifications** - Get user notifications
**GET /v1/notifications/{id}** - Get specific notification
**PATCH /v1/notifications/{id}/read** - Mark as read
**POST /v1/notifications/mark-all-read** - Mark all as read
**DELETE /v1/notifications/{id}** - Delete notification

---

## Configuration

Key environment variables:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/tsh_erp

# Redis (Event Bus)
REDIS_URL=redis://localhost:6379/2

# Authentication (must match TSH ERP)
JWT_SECRET_KEY=your-secret-key-must-match-tsh-erp

# Email Notifications
SMTP_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_USER=alerts@tsh.sale
SMTP_PASSWORD=your-app-password
```

---

## Deployment

### Production Setup (Ubuntu 20.04/22.04)

```bash
# 1. Create deployment directory
sudo mkdir -p /opt/tsh_neurolink
sudo chown $USER:$USER /opt/tsh_neurolink

# 2. Copy files to server
rsync -avz --exclude='venv' --exclude='.git' \
  /Users/khaleelal-mulla/TSH_ERP_Ecosystem/tsh_neurolink/ \
  root@167.71.39.50:/opt/tsh_neurolink/

# 3. Install on server
ssh root@167.71.39.50
cd /opt/tsh_neurolink
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Run database migration
sudo -u postgres psql -d tsh_erp -f migrations/001_initial_schema.sql

# 5. Configure environment
cp .env.example .env
nano .env  # Configure for production

# 6. Install SystemD service
sudo cp scripts/tsh-neurolink-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable tsh-neurolink-api
sudo systemctl start tsh-neurolink-api

# 7. Check status
sudo systemctl status tsh-neurolink-api
sudo journalctl -u tsh-neurolink-api -f
```

### Nginx Configuration

Add to your Nginx config:

```nginx
# TSH NeuroLink API
location /neurolink/ {
    proxy_pass http://localhost:8002/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    # WebSocket support
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

---

## Event Types

### Standard TSH ERP Event Types

**Invoicing:**
- `invoice.created` - New invoice generated
- `invoice.overdue` - Invoice payment overdue
- `invoice.paid` - Invoice marked as paid
- `invoice.partially_paid` - Partial payment received

**Inventory:**
- `stock.low` - Stock below minimum threshold
- `stock.out` - Product out of stock
- `stock.adjusted` - Stock manually adjusted
- `stock.transferred` - Stock transferred between warehouses

**Sales:**
- `order.created` - New sales order
- `order.approved` - Order approved
- `order.shipped` - Order shipped
- `order.delivered` - Order delivered
- `order.cancelled` - Order cancelled

**Purchases:**
- `po.created` - Purchase order created
- `po.approved` - Purchase order approved
- `po.received` - Goods received
- `po.rejected` - Purchase order rejected

---

## Notification Rules

Rules are defined in the database using templates:

```sql
INSERT INTO neurolink_notification_rules (
    name,
    source_module,
    event_type_pattern,
    notification_template,
    priority
) VALUES (
    'invoice_overdue',
    'invoicing',
    'invoice.overdue',
    '{
        "title": "Invoice {{invoice_number}} is overdue",
        "body": "Invoice #{{invoice_number}} for {{customer_name}} is {{days_overdue}} days overdue. Amount: {{amount}} {{currency}}",
        "severity": "warning",
        "action_url": "/invoices/{{invoice_id}}",
        "action_label": "View Invoice",
        "channels": ["in_app", "email"],
        "recipient_roles": ["accountant", "finance_manager"]
    }'::jsonb,
    100
);
```

---

## Monitoring

### Health Check

```bash
curl http://localhost:8002/health
```

### Logs

```bash
# View real-time logs
sudo journalctl -u tsh-neurolink-api -f

# View recent errors
sudo journalctl -u tsh-neurolink-api --since "1 hour ago" -p err
```

### Metrics

Access system metrics:

```bash
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8002/v1/events/stats/summary
```

---

## Development

### Project Structure

```
tsh_neurolink/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Settings management
│   ├── database.py          # Database connections
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── api/
│   │   └── v1/
│   │       ├── events.py    # Event endpoints
│   │       └── notifications.py
│   └── middleware/
│       └── auth.py          # JWT authentication
├── migrations/
│   └── 001_initial_schema.sql
├── scripts/
│   └── tsh-neurolink-api.service
├── docs/
├── tests/
├── requirements.txt
├── .env.example
└── README.md
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/ -v
```

---

## Roadmap

### Phase 0-1: Foundation ✅ (Completed)
- ✅ Event ingestion API with idempotency
- ✅ Notification CRUD endpoints
- ✅ JWT authentication
- ✅ Database schema
- ✅ SystemD service files

### Phase 2: Rule Engine (Week 3)
- ⏳ Rule evaluation worker
- ⏳ Template rendering (Jinja2)
- ⏳ Admin UI for rule management
- ⏳ Rule testing interface

### Phase 3: Real-time & Chat (Week 4-5)
- ⏳ WebSocket server for real-time updates
- ⏳ NeuroChat messaging system
- ⏳ Message threading and mentions
- ⏳ File attachments

### Phase 4: Multi-Channel (Week 6)
- ⏳ Email delivery (SMTP)
- ⏳ SMS integration (Twilio)
- ⏳ Telegram bot
- ⏳ Delivery tracking and retry logic

### Phase 5: Production Hardening (Week 7)
- ⏳ Performance optimization
- ⏳ Monitoring dashboards
- ⏳ Backup automation
- ⏳ Security audit

---

## Support

**Issues:** Report bugs or request features via GitHub Issues
**Documentation:** See `/docs` directory for detailed guides
**Contact:** TSH Development Team

---

## License

Proprietary - TSH (Trading Services House)

---

**Built with ❤️ for TSH ERP by the Development Team**
