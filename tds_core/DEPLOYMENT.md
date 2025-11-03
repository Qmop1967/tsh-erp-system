# TDS Core - Deployment Guide

## Overview

TDS Core (TSH DataSync Core) is a Python-based event synchronization system that processes Zoho Books webhooks and synchronizes data to the TSH ERP database.

**Production Server:** 167.71.39.50
**Services:** API (Port 8001) + Background Worker
**Framework:** FastAPI + SQLAlchemy 2.0 + PostgreSQL 14

---

## Architecture

```
Zoho Books Webhooks → TDS Core API → Inbox Storage
                                    ↓
                          Queue Management System
                                    ↓
                         Background Worker Pool
                                    ↓
                    Entity Handlers (Contacts, Products, etc.)
                                    ↓
                         TSH ERP Database
```

**Key Components:**
- **API Service** - Receives webhooks, stores in inbox, queues events
- **Worker Service** - Processes queue entries, handles retries, manages failures
- **Alert System** - Monitors health, tracks failures, sends notifications
- **Dashboard** - RESTful endpoints for monitoring and management

---

## Prerequisites

### System Requirements
- Ubuntu 20.04+ (VPS)
- Python 3.11+
- PostgreSQL 14+
- Nginx (reverse proxy)
- systemd (service management)
- 2GB+ RAM
- 20GB+ disk space

### Database Access
- PostgreSQL connection to TSH ERP database
- Database: `tsh_erp`
- Host: VPS PostgreSQL (localhost)
- Port: 5432

---

## Installation

### 1. Server Setup

```bash
# SSH into production server
ssh root@167.71.39.50

# Create application directory
mkdir -p /opt/tds_core
cd /opt/tds_core

# Install Python 3.11+
apt update
apt install -y python3.11 python3.11-venv python3-pip

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
# Install Python packages
pip install --upgrade pip
pip install -r requirements.txt

# Requirements.txt should include:
# fastapi==0.104.1
# uvicorn[standard]==0.24.0
# sqlalchemy[asyncio]==2.0.23
# asyncpg==0.29.0
# psycopg2-binary==2.9.9
# alembic==1.12.1
# pydantic==2.5.0
# pydantic-settings==2.1.0
# python-dotenv==1.0.0
# httpx==0.25.1
```

### 3. Configuration

Create `.env` file in `/opt/tds_core/`:

```bash
# Application
APP_NAME=TDS_Core
ENV=production
DEBUG=false

# API
API_HOST=0.0.0.0
API_PORT=8001
API_WORKERS=4

# Database (TSH ERP - Supabase)
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=postgres
DATABASE_USER=postgres.trjjglxhteqnzmyakxhe
DATABASE_PASSWORD=<your-password>

# Connection Pooling
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
DATABASE_POOL_TIMEOUT=30

# Worker Settings
WORKER_CONCURRENCY=5
WORKER_BATCH_SIZE=10
WORKER_POLL_INTERVAL=5

# Retry Configuration
RETRY_MAX_ATTEMPTS=3
RETRY_DELAYS=60,300,900

# Monitoring
MONITORING_INTERVAL=300
ALERT_EMAIL_ENABLED=false
ALERT_SLACK_ENABLED=false

# Security
SECRET_KEY=<generate-strong-random-key>
```

**Generate Secret Key:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4. Database Migration

```bash
# Initialize Alembic (if not already done)
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial TDS Core schema"

# Apply migration
alembic upgrade head
```

**Manual Table Creation (Alternative):**
```sql
-- Run SQL scripts from models/tds_models.py
-- Tables: tds_inbox_events, tds_sync_queue, tds_dead_letter_queue,
--         tds_sync_logs, tds_alerts
```

---

## Systemd Service Configuration

### API Service

Create `/etc/systemd/system/tds-core-api.service`:

```ini
[Unit]
Description=TDS Core API Service
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=notify
User=root
Group=root
WorkingDirectory=/opt/tds_core
Environment="PATH=/opt/tds_core/venv/bin"
ExecStart=/opt/tds_core/venv/bin/uvicorn main:app \
    --host 0.0.0.0 \
    --port 8001 \
    --workers 4 \
    --log-level info \
    --access-log \
    --use-colors

Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Resource limits
LimitNOFILE=65536
MemoryLimit=2G

[Install]
WantedBy=multi-user.target
```

### Worker Service

Create `/etc/systemd/system/tds-core-worker.service`:

```ini
[Unit]
Description=TDS Core Background Worker
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=/opt/tds_core
Environment="PATH=/opt/tds_core/venv/bin"
ExecStart=/opt/tds_core/venv/bin/python worker.py

Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Resource limits
LimitNOFILE=65536
MemoryLimit=2G

[Install]
WantedBy=multi-user.target
```

### Enable and Start Services

```bash
# Reload systemd
systemctl daemon-reload

# Enable services to start on boot
systemctl enable tds-core-api
systemctl enable tds-core-worker

# Start services
systemctl start tds-core-api
systemctl start tds-core-worker

# Check status
systemctl status tds-core-api
systemctl status tds-core-worker

# View logs
journalctl -u tds-core-api -f
journalctl -u tds-core-worker -f
```

---

## Nginx Configuration

### Reverse Proxy Setup

Add to `/etc/nginx/sites-available/tds-core`:

```nginx
upstream tds_core_backend {
    server 127.0.0.1:8001;
    keepalive 32;
}

server {
    listen 80;
    server_name api.tsh.sale;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.tsh.sale;

    # SSL certificates (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/api.tsh.sale/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.tsh.sale/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Logging
    access_log /var/log/nginx/tds-core-access.log;
    error_log /var/log/nginx/tds-core-error.log;

    # TDS Core API
    location /tds/ {
        proxy_pass http://tds_core_backend/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;

        # Timeouts for long-running requests
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health check endpoint
    location /tds/health {
        proxy_pass http://tds_core_backend/health;
        access_log off;
    }
}
```

**Enable Site:**
```bash
ln -s /etc/nginx/sites-available/tds-core /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

---

## SSL Certificate Setup

```bash
# Install Certbot
apt install -y certbot python3-certbot-nginx

# Obtain certificate
certbot --nginx -d api.tsh.sale

# Auto-renewal is configured automatically
# Test renewal:
certbot renew --dry-run
```

---

## Deployment Process

### Initial Deployment

```bash
# 1. Upload code from local machine
rsync -avz --exclude='__pycache__' --exclude='*.pyc' --exclude='.env' --exclude='venv' \
    /Users/khaleelal-mulla/TSH_ERP_Ecosystem/tds_core/ \
    root@167.71.39.50:/opt/tds_core/

# 2. SSH into server
ssh root@167.71.39.50

# 3. Activate virtual environment
cd /opt/tds_core
source venv/bin/activate

# 4. Install/update dependencies
pip install -r requirements.txt

# 5. Run database migrations
alembic upgrade head

# 6. Restart services
systemctl restart tds-core-api
systemctl restart tds-core-worker

# 7. Verify deployment
systemctl status tds-core-api
systemctl status tds-core-worker
curl https://api.tsh.sale/tds/health
```

### Updates and Hotfixes

```bash
# 1. Upload changes
rsync -avz --exclude='__pycache__' --exclude='*.pyc' --exclude='.env' --exclude='venv' \
    /Users/khaleelal-mulla/TSH_ERP_Ecosystem/tds_core/ \
    root@167.71.39.50:/opt/tds_core/

# 2. Restart services (zero-downtime for API with multiple workers)
ssh root@167.71.39.50 "systemctl restart tds-core-api && systemctl restart tds-core-worker"

# 3. Monitor logs
ssh root@167.71.39.50 "journalctl -u tds-core-api -f"
```

---

## Monitoring Setup

### Health Checks

The system includes built-in health monitoring:

**Endpoints:**
- `GET /health` - Basic health check
- `GET /dashboard/metrics` - Comprehensive system metrics
- `GET /dashboard/queue-stats` - Queue statistics

**Monitoring Service:**
- Runs every 5 minutes
- Checks queue health, failure rates, stuck events
- Creates alerts automatically

**Alert Thresholds:**
- **Critical:** Pending queue >1000, DLQ >100, failure rate >10%
- **Warning:** Pending queue >500, DLQ >50, failure rate >5%

### Log Management

```bash
# View API logs
journalctl -u tds-core-api -f

# View Worker logs
journalctl -u tds-core-worker -f

# View errors only
journalctl -u tds-core-api -p err -f

# View last 100 lines
journalctl -u tds-core-api -n 100

# Export logs to file
journalctl -u tds-core-api --since "1 hour ago" > /tmp/api-logs.txt
```

### Database Monitoring

```bash
# Check active connections
SELECT count(*) FROM pg_stat_activity WHERE datname = 'tsh_erp';

# Check table sizes
SELECT
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public' AND tablename LIKE 'tds_%'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

# Check queue status
SELECT status, COUNT(*) FROM tds_sync_queue GROUP BY status;
```

---

## Backup and Recovery

### Database Backup

```bash
# Automated daily backups (add to cron)
0 2 * * * /opt/tds_core/scripts/backup.sh

# backup.sh:
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=/opt/backups/tds_core
mkdir -p $BACKUP_DIR

# Backup TDS tables only
pg_dump -h localhost \
    -U postgres.trjjglxhteqnzmyakxhe \
    -d postgres \
    -t 'tds_*' \
    -F c \
    -f $BACKUP_DIR/tds_core_$DATE.backup

# Keep last 7 days
find $BACKUP_DIR -type f -mtime +7 -delete
```

### Application Backup

```bash
# Backup entire application directory
tar -czf /opt/backups/tds_core_app_$(date +%Y%m%d).tar.gz \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    /opt/tds_core/
```

### Recovery

```bash
# Restore database
pg_restore -h localhost \
    -U postgres.trjjglxhteqnzmyakxhe \
    -d postgres \
    -c \
    /opt/backups/tds_core/tds_core_20241031.backup

# Restore application
tar -xzf /opt/backups/tds_core_app_20241031.tar.gz -C /
systemctl restart tds-core-api tds-core-worker
```

---

## Security Considerations

### Firewall Configuration

```bash
# UFW firewall
ufw allow 22/tcp      # SSH
ufw allow 80/tcp      # HTTP
ufw allow 443/tcp     # HTTPS
ufw enable

# Block direct access to API port
ufw deny 8001/tcp
```

### Environment Variables

- **Never commit `.env` file to git**
- Use strong random secrets
- Rotate credentials regularly
- Use environment-specific configurations

### Database Security

- Use connection pooling to prevent exhaustion
- Enable SSL for database connections (production)
- Use strong passwords
- Limit database user permissions to only required tables

### API Security

- Rate limiting (implement in Nginx or FastAPI)
- Webhook signature verification (implement in handlers)
- Input validation (Pydantic models)
- SQL injection prevention (SQLAlchemy ORM)

---

## Troubleshooting

### API Service Won't Start

```bash
# Check logs
journalctl -u tds-core-api -n 50

# Common issues:
# - Port 8001 already in use: lsof -i :8001
# - Database connection failed: Check .env credentials
# - Python import errors: pip install -r requirements.txt
```

### Worker Service Issues

```bash
# Check worker status
systemctl status tds-core-worker

# Check if processing events
SELECT * FROM tds_sync_queue WHERE status = 'processing';

# Restart worker
systemctl restart tds-core-worker
```

### High Queue Backlog

```bash
# Check queue size
SELECT status, COUNT(*) FROM tds_sync_queue GROUP BY status;

# Increase worker concurrency in .env
WORKER_CONCURRENCY=10

# Restart worker
systemctl restart tds-core-worker
```

### Database Connection Pool Exhausted

```bash
# Check active connections
SELECT count(*) FROM pg_stat_activity WHERE datname = 'tsh_erp';

# Increase pool size in .env
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=40

# Restart services
systemctl restart tds-core-api tds-core-worker
```

---

## Performance Tuning

### API Performance

```ini
# Increase Uvicorn workers (in systemd service)
--workers 8

# Enable HTTP/2 in Nginx
listen 443 ssl http2;

# Enable Nginx caching for static endpoints
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m;
```

### Worker Performance

```bash
# Increase concurrency
WORKER_CONCURRENCY=10

# Increase batch size
WORKER_BATCH_SIZE=20

# Decrease poll interval (more aggressive)
WORKER_POLL_INTERVAL=2
```

### Database Performance

```sql
-- Add indexes for common queries
CREATE INDEX idx_queue_status ON tds_sync_queue(status);
CREATE INDEX idx_queue_created ON tds_sync_queue(created_at);
CREATE INDEX idx_inbox_processed ON tds_inbox_events(processed);

-- Vacuum regularly (automated)
VACUUM ANALYZE tds_sync_queue;
VACUUM ANALYZE tds_inbox_events;
```

---

## Scaling Considerations

### Horizontal Scaling

**API Service:**
- Multiple API instances behind load balancer
- Stateless design allows easy horizontal scaling
- Use Redis for distributed rate limiting

**Worker Service:**
- Multiple worker instances on different servers
- PostgreSQL queue provides distributed coordination
- Use advisory locks to prevent duplicate processing

**Database:**
- Read replicas for reporting/dashboard queries
- Connection pooling (PgBouncer) for high concurrency
- Partitioning for large tables (queue, logs)

---

## Maintenance Tasks

### Weekly

- Review alert dashboard for anomalies
- Check dead letter queue for failed events
- Monitor disk space usage
- Review error logs

### Monthly

- Update dependencies (security patches)
- Review and optimize slow queries
- Clean up old logs (>30 days)
- Database maintenance (VACUUM, REINDEX)

### Quarterly

- Review and update monitoring thresholds
- Performance testing and optimization
- Security audit
- Disaster recovery drill

---

## Contact and Support

**Deployment Issues:** Check logs first, then contact system administrator
**Feature Requests:** Submit to development team
**Emergency:** Restart services and check monitoring dashboard

**Key Files:**
- Configuration: `/opt/tds_core/.env`
- Logs: `journalctl -u tds-core-api` or `journalctl -u tds-core-worker`
- Service Files: `/etc/systemd/system/tds-core-*.service`
- Nginx Config: `/etc/nginx/sites-available/tds-core`
