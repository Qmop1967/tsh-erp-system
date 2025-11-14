# TSH NeuroLink - Unified Communication & Notification System

**Last Updated:** 2025-11-13
**Status:** Production | Active
**Purpose:** EXCLUSIVE notification and communication platform for TSH ERP Ecosystem

---

## 🎯 Overview

TSH NeuroLink is the **UNIFIED** notification and communication system for the entire TSH ERP Ecosystem. It handles ALL internal and external communications, replacing the need for third-party services like Twilio, Firebase, or other notification platforms.

**Core Principle**: One system for all communication needs - no fragmented services.

---

## 🏗️ Architecture

### System Components

```yaml
Core Services:
  - WebSocket Server: Real-time bidirectional communication
  - Event Bus: Redis-based message broker
  - Notification Engine: Rule-based notification delivery
  - Email Service: Resend API integration
  - Message Router: Intelligent message routing
  - Presence System: User online/offline status tracking

Data Layer:
  - PostgreSQL: Message persistence, user data, notification history
  - Redis: Event bus, real-time data, presence tracking
  - Shared with TSH ERP: User authentication, permissions, customer data

API Layer:
  - REST API: Message CRUD, notification settings, user management
  - WebSocket API: Real-time connections, live messaging
  - Event API: System-to-system event publishing
```

### Technology Stack

```yaml
Backend:
  - Language: Python 3.9+
  - Framework: FastAPI (WebSocket + REST)
  - Database: PostgreSQL (shared with TSH ERP)
  - Cache/Event Bus: Redis
  - Email: Resend API

Communication Protocols:
  - WebSocket: Real-time bidirectional messaging
  - REST: HTTP/JSON API for management operations
  - Event Bus: Redis Pub/Sub for system events

Authentication:
  - JWT tokens (shared with TSH ERP)
  - Role-based access control (RBAC)
  - Session management

Deployment:
  - Container: Docker (tsh_neurolink)
  - Port: 8002
  - Health Check: /health endpoint
  - Monitoring: Prometheus metrics
```

---

## 📡 Communication Channels

TSH NeuroLink provides **5 primary communication channels**:

### 1. Team Communication
**Purpose**: Internal collaboration between TSH employees

**Use Cases**:
- Office staff coordination
- Warehouse team communication
- Admin announcements
- Task assignments
- Shift handoffs

**Features**:
- Private 1-on-1 messaging
- Group channels by department
- File sharing
- Message history
- Read receipts
- Typing indicators

**Users**: All TSH employees (admin, warehouse, retail, HR, management)

---

### 2. Customer-Sales Communication
**Purpose**: Wholesale clients communicating with sales representatives

**Use Cases**:
- Order inquiries
- Product availability questions
- Price negotiations
- Order status updates
- Payment confirmations
- Credit limit discussions

**Features**:
- Customer assigned to specific sales rep
- Message threading by order
- Attachment support (invoices, receipts)
- Quick replies for common questions
- Notification when customer messages
- Sales rep availability status

**Users**:
- 500+ wholesale clients
- Sales representatives
- Sales managers (monitoring)

---

### 3. Consumer Support
**Purpose**: Retail consumers contacting technical support

**Use Cases**:
- Product support questions
- Order tracking
- Returns and exchanges
- Technical assistance
- Complaint handling
- General inquiries

**Features**:
- Support ticket creation
- Priority levels
- Assignment to support agents
- Canned responses
- Support history
- Customer satisfaction rating

**Users**:
- Retail consumers (via Consumer App)
- Technical support team
- Support managers

---

### 4. System Notifications
**Purpose**: Automated notifications from TSH ERP system

**Use Cases**:
- Order confirmations
- Payment received
- Stock alerts (low stock, out of stock)
- Sync status (TDS Core)
- System errors
- Scheduled reports
- Inventory movements
- Price changes

**Features**:
- Multi-channel delivery (in-app, email, push)
- User notification preferences
- Notification grouping
- Read/unread tracking
- Action buttons (approve, view, dismiss)
- Scheduled notifications

**Users**: All user roles based on relevance

---

### 5. Email Delivery
**Purpose**: Email notifications via Resend API

**Use Cases**:
- Order confirmations
- Invoice delivery
- Password reset
- Account notifications
- Promotional emails
- Weekly reports

**Features**:
- Template-based emails
- Arabic RTL support
- Attachment support
- Delivery tracking
- Bounce handling
- Unsubscribe management

**Integration**: Resend API

---

## 🔔 Notification Engine

### Notification Types

```yaml
System Notifications:
  - order.created
  - order.confirmed
  - order.shipped
  - order.delivered
  - payment.received
  - invoice.generated
  - stock.low_alert
  - stock.out_of_stock
  - sync.success
  - sync.failure
  - price.changed

User Notifications:
  - message.received
  - mention.received
  - task.assigned
  - approval.requested
  - report.ready
```

### Notification Rules

```python
# Example notification rule structure
{
  "event_type": "order.created",
  "recipients": ["customer", "sales_rep", "warehouse_manager"],
  "channels": {
    "customer": ["email", "in_app", "push"],
    "sales_rep": ["in_app", "push"],
    "warehouse_manager": ["in_app"]
  },
  "template": "order_confirmation",
  "priority": "high",
  "delivery_time": "immediate"
}
```

### User Preferences

Users can control:
- ✅ Which notifications they receive
- ✅ Delivery channels (in-app, email, push)
- ✅ Quiet hours (no notifications during sleep)
- ✅ Notification grouping
- ✅ Sound/vibration preferences

---

## 🔌 Integration with TSH ERP

### Shared Resources

```yaml
Shared Database:
  - users table (authentication)
  - roles and permissions
  - customers table
  - orders table (for notification context)
  - products table (for notification content)

Shared Authentication:
  - JWT tokens
  - Same secret key
  - Same token expiration
  - Same RBAC system

Event Publishing:
  - TSH ERP publishes events to Redis
  - NeuroLink subscribes and processes
  - Bidirectional event flow
```

### Event Flow Example

```mermaid
TSH ERP → Redis Pub/Sub → NeuroLink → Process → Deliver
                              ↓
                         Database (persist)
                              ↓
                         WebSocket (real-time)
                              ↓
                         Resend API (email)
```

---

## 📝 API Reference

### REST API Endpoints

```yaml
Authentication:
  POST /api/auth/login          # JWT token
  POST /api/auth/refresh        # Refresh token
  GET  /api/auth/me             # Current user

Messages:
  GET    /api/messages          # List messages
  POST   /api/messages          # Send message
  GET    /api/messages/{id}     # Get message
  DELETE /api/messages/{id}     # Delete message
  PUT    /api/messages/{id}/read # Mark as read

Channels:
  GET  /api/channels            # List channels
  POST /api/channels            # Create channel
  GET  /api/channels/{id}       # Get channel
  POST /api/channels/{id}/members # Add member

Notifications:
  GET    /api/notifications     # List notifications
  PUT    /api/notifications/{id}/read # Mark as read
  DELETE /api/notifications/{id} # Delete notification
  GET    /api/notifications/settings # User preferences
  PUT    /api/notifications/settings # Update preferences

Health:
  GET /health                   # System health check
```

### WebSocket API

```yaml
Connection:
  ws://neurolink.tsh.sale/ws?token={jwt_token}

Client → Server Events:
  - message.send              # Send a message
  - typing.start              # User started typing
  - typing.stop               # User stopped typing
  - presence.update           # Update status

Server → Client Events:
  - message.received          # New message
  - message.delivered         # Message delivered
  - message.read              # Message read
  - typing.indicator          # Someone typing
  - presence.changed          # User status changed
  - notification.new          # New notification
```

---

## 🚀 Deployment

### Docker Configuration

```yaml
Container Name: tsh_neurolink
Image: tsh-neurolink:latest
Port: 8002
Environment:
  - DATABASE_URL (shared with TSH ERP)
  - REDIS_URL (event bus)
  - JWT_SECRET_KEY (shared with TSH ERP)
  - RESEND_API_KEY (email delivery)
  - TSH_ERP_API_URL (integration)

Dependencies:
  - tsh_postgres (healthy)
  - redis (started)

Health Check:
  - Endpoint: /health
  - Interval: 30s
  - Timeout: 10s
  - Retries: 3
```

### Environment Variables

```bash
# Database (shared with TSH ERP)
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/tsh_erp
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10

# Redis (event bus)
REDIS_URL=redis://tsh_redis:6379/2
REDIS_CHANNEL_PREFIX=neurolink:

# Authentication (shared with TSH ERP)
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=30

# Email (Resend API)
RESEND_API_KEY=re_xxxxxxxxxxxx
EMAIL_FROM_ADDRESS=notifications@tsh.sale
EMAIL_FROM_NAME=TSH ERP Notifications

# TSH ERP Integration
TSH_ERP_API_URL=http://app:8000
TSH_ERP_API_KEY=optional-api-key

# WebSocket
WS_HEARTBEAT_INTERVAL=30
WS_MAX_CONNECTIONS=1000

# Performance
WORKERS=4
EVENT_BATCH_SIZE=100
EVENT_POLL_INTERVAL_MS=1000

# Monitoring
LOG_LEVEL=INFO
ENABLE_METRICS=true
```

---

## 📊 Monitoring & Metrics

### Health Checks

```bash
# System health
curl http://localhost:8002/health

# WebSocket connections
curl http://localhost:8002/metrics | grep websocket_connections

# Message throughput
curl http://localhost:8002/metrics | grep messages_sent_total
```

### Key Metrics

```yaml
Performance:
  - websocket_connections (active connections)
  - messages_sent_total (total messages)
  - messages_sent_per_second (throughput)
  - notification_delivery_time (latency)
  - email_delivery_success_rate

System:
  - redis_connection_pool_size
  - database_query_latency
  - event_bus_lag
  - worker_utilization

Business:
  - active_users_count
  - messages_by_channel
  - notification_open_rate
  - support_response_time
```

---

## 🔧 Development Guidelines

### When to Use NeuroLink

**✅ USE for:**
- Any notification to users
- Real-time chat/messaging
- System alerts
- Email delivery
- Customer support communication
- Team collaboration

**❌ DO NOT USE for:**
- External SMS (Twilio removed - not supported)
- Push notifications to native apps (Firebase removed - not supported)
- Third-party integrations (WhatsApp Business has separate integration)

### Integration Pattern

```python
# Example: Sending notification from TSH ERP

from app.services.neurolink_service import NeuroLinkService

neurolink = NeuroLinkService()

# Method 1: Direct notification
await neurolink.send_notification(
    user_id=customer_id,
    type="order.created",
    title="Order Confirmed",
    message=f"Your order #{order_number} has been confirmed",
    data={"order_id": order_id},
    channels=["in_app", "email"]
)

# Method 2: Publish event (NeuroLink will handle)
await neurolink.publish_event(
    event_type="order.created",
    data={
        "order_id": order_id,
        "customer_id": customer_id,
        "total": order_total
    }
)
```

---

## 🚨 IMPORTANT RULES

### For AI Assistants (Claude Code)

**ALWAYS:**
- ✅ Direct ALL notification requirements to TSH NeuroLink
- ✅ Use NeuroLink for team communication
- ✅ Use NeuroLink for customer messaging
- ✅ Use NeuroLink for system alerts
- ✅ Check NeuroLink documentation before suggesting alternatives

**NEVER:**
- ❌ Suggest implementing Twilio
- ❌ Suggest implementing Firebase Cloud Messaging
- ❌ Suggest third-party notification services
- ❌ Implement direct SMS functionality
- ❌ Bypass NeuroLink for notifications

### For Developers

**Best Practices:**
- Use event-driven architecture (publish events, let NeuroLink handle delivery)
- Always provide notification context data (order_id, product_id, etc.)
- Respect user notification preferences
- Test notification delivery in staging first
- Monitor notification success rates

**Anti-Patterns:**
- Don't send notifications directly from controllers
- Don't hardcode notification templates in code
- Don't ignore user opt-out preferences
- Don't send notifications without rate limiting

---

## 📚 Related Documentation

- **ARCHITECTURE_RULES.md** - Notifications & Communication section
- **DECISIONS.md** - Twilio/Firebase removal decision
- **PROJECT_VISION.md** - TSH NeuroLink system overview
- **CODE_TEMPLATES.md** - Notification integration examples (to be added)
- **app/neurolink/app/config.py** - NeuroLink configuration
- **app/neurolink/README.md** - Technical implementation details

---

## 🔄 Migration from Legacy Systems

### Twilio → NeuroLink
**Status**: ✅ Completed - Twilio never implemented, removed configurations

### Firebase → NeuroLink
**Status**: ✅ Completed - Firebase never implemented, removed configurations

### Future Considerations
- WhatsApp Business API integration (planned, separate from NeuroLink)
- Telegram notifications (optional, through NeuroLink)
- SMS fallback (if needed, through alternative provider via NeuroLink)

---

**Questions or Issues?**
Contact: TSH ERP Development Team
Repository: [TSH_ERP_Ecosystem](https://github.com/tsh-erp/ecosystem)

---

**Remember**: TSH NeuroLink is the ONLY approved notification and communication system for TSH ERP Ecosystem. All notification needs should go through NeuroLink.
