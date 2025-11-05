# TDS Core - Notifications Setup Guide

This guide explains how to configure email and Slack notifications for TDS Core alerts.

## Overview

TDS Core can send automated alerts via:
- **Email** (SMTP)
- **Slack** (Webhooks)
- **Generic Webhooks** (for custom integrations)

Alerts are automatically triggered for:
- Critical queue backlogs (>1000 pending events)
- High dead letter queue (>100 failed events)
- Elevated failure rates (>10%)
- Stuck events (processing >1 hour)

---

## Email Notifications Setup

### 1. Gmail Setup (Recommended for Testing)

**Step 1: Enable 2-Factor Authentication**
- Go to https://myaccount.google.com/security
- Enable 2-Step Verification

**Step 2: Create App Password**
- Go to https://myaccount.google.com/apppasswords
- Select "Mail" and "Other (Custom name)"
- Name it "TDS Core Alerts"
- Copy the 16-character password

**Step 3: Configure .env**

```bash
# Email Notifications
ALERT_EMAIL_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password
EMAIL_FROM=TDS Core Alerts <your-email@gmail.com>
EMAIL_TO=admin@tsh.sale,ops@tsh.sale
```

### 2. Custom SMTP Server

For production environments, use a dedicated SMTP service:

**SendGrid:**
```bash
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your-sendgrid-api-key
```

**AWS SES:**
```bash
SMTP_HOST=email-smtp.us-east-1.amazonaws.com
SMTP_PORT=587
SMTP_USER=your-ses-smtp-username
SMTP_PASSWORD=your-ses-smtp-password
```

**Mailgun:**
```bash
SMTP_HOST=smtp.mailgun.org
SMTP_PORT=587
SMTP_USER=your-mailgun-smtp-username
SMTP_PASSWORD=your-mailgun-smtp-password
```

### 3. Configure Settings

Add to `core/config.py`:

```python
# Alert email settings
alert_email_enabled: bool = Field(default=False, env='ALERT_EMAIL_ENABLED')
smtp_host: str = Field(default="smtp.gmail.com", env='SMTP_HOST')
smtp_port: int = Field(default=587, env='SMTP_PORT')
smtp_user: Optional[str] = Field(default=None, env='SMTP_USER')
smtp_password: Optional[str] = Field(default=None, env='SMTP_PASSWORD')
email_from: str = Field(default="noreply@tsh.sale", env='EMAIL_FROM')
email_to: List[str] = Field(default=[], env='EMAIL_TO')
```

### 4. Test Email Notifications

```python
# test_email.py
import asyncio
from services.notification_service import NotificationService

async def test_email():
    notif = NotificationService()

    success = await notif.send_email_alert(
        subject="Test Alert",
        body="This is a test alert from TDS Core",
        severity="info",
        metadata={"test": "value"}
    )

    print(f"Email sent: {success}")

asyncio.run(test_email())
```

Run test:
```bash
cd /opt/tds_core
source venv/bin/activate
python test_email.py
```

---

## Slack Notifications Setup

### 1. Create Slack Incoming Webhook

**Step 1: Create Slack App**
- Go to https://api.slack.com/apps
- Click "Create New App"
- Choose "From scratch"
- Name: "TDS Core Alerts"
- Select your workspace

**Step 2: Enable Incoming Webhooks**
- In app settings, go to "Incoming Webhooks"
- Toggle "Activate Incoming Webhooks" to ON
- Click "Add New Webhook to Workspace"
- Select channel (e.g., #tds-alerts)
- Click "Allow"
- Copy the Webhook URL

**Step 3: Configure .env**

```bash
# Slack Notifications
ALERT_SLACK_ENABLED=true
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX
SLACK_CHANNEL=#tds-alerts
```

### 2. Configure Settings

Add to `core/config.py`:

```python
# Slack alert settings
alert_slack_enabled: bool = Field(default=False, env='ALERT_SLACK_ENABLED')
slack_webhook_url: Optional[str] = Field(default=None, env='SLACK_WEBHOOK_URL')
slack_channel: str = Field(default="#alerts", env='SLACK_CHANNEL')
```

### 3. Test Slack Notifications

```python
# test_slack.py
import asyncio
from services.notification_service import NotificationService

async def test_slack():
    notif = NotificationService()

    success = await notif.send_slack_alert(
        title="Test Alert",
        message="This is a test alert from TDS Core",
        severity="info",
        metadata={"test": "value"}
    )

    print(f"Slack alert sent: {success}")

asyncio.run(test_slack())
```

Run test:
```bash
cd /opt/tds_core
source venv/bin/activate
python test_slack.py
```

---

## Alert Severity Levels

The notification system uses the following severity levels:

| Severity | Color | Email | Slack | Use Case |
|----------|-------|-------|-------|----------|
| **info** | Blue | No | No | Informational messages |
| **warning** | Yellow | No | No | Non-critical issues |
| **error** | Red | Optional | Optional | Errors that need attention |
| **critical** | Dark Red | Yes | Yes | Urgent issues requiring immediate action |

By default, only **critical** alerts trigger notifications.

---

## Customizing Alert Triggers

### Modify Alert Thresholds

Edit `services/alert_service.py`:

```python
# Current thresholds
if pending_count > 1000:  # Critical
if pending_count > 500:   # Warning

if dlq_count > 100:       # Critical
if dlq_count > 50:        # Warning

if failure_rate > 10:     # Critical
if failure_rate > 5:      # Warning
```

Change values as needed for your environment.

### Send Manual Notifications

```python
from services.notification_service import NotificationService

notif = NotificationService()

# Send to all enabled channels
await notif.send_alert(
    title="Custom Alert",
    message="Something important happened",
    severity="critical",
    metadata={"key": "value"},
    channels=['all']  # or ['email'], ['slack'], ['email', 'slack']
)
```

---

## Production Deployment

### 1. Update .env on Server

```bash
ssh root@167.71.39.50
nano /opt/tds_core/.env

# Add notification settings:
ALERT_EMAIL_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=alerts@tsh.sale
SMTP_PASSWORD=your-app-password
EMAIL_FROM=TDS Core <noreply@tsh.sale>
EMAIL_TO=admin@tsh.sale,ops@tsh.sale

ALERT_SLACK_ENABLED=true
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
SLACK_CHANNEL=#tds-alerts
```

### 2. Upload Notification Service

```bash
# From local machine
rsync -avz /Users/khaleelal-mulla/TSH_ERP_Ecosystem/tds_core/services/notification_service.py \
    root@167.71.39.50:/opt/tds_core/services/

rsync -avz /Users/khaleelal-mulla/TSH_ERP_Ecosystem/tds_core/services/alert_service.py \
    root@167.71.39.50:/opt/tds_core/services/

rsync -avz /Users/khaleelal-mulla/TSH_ERP_Ecosystem/tds_core/services/__init__.py \
    root@167.71.39.50:/opt/tds_core/services/
```

### 3. Install httpx (if not already installed)

```bash
ssh root@167.71.39.50
cd /opt/tds_core
source venv/bin/activate
pip install httpx
```

### 4. Restart Services

```bash
systemctl restart tds-core-api
systemctl restart tds-core-worker
```

### 5. Test Notifications

```bash
# Test email
python -c "
import asyncio
from services.notification_service import NotificationService

async def test():
    notif = NotificationService()
    await notif.send_email_alert('Test', 'Email works!', 'info')

asyncio.run(test())
"

# Test Slack
python -c "
import asyncio
from services.notification_service import NotificationService

async def test():
    notif = NotificationService()
    await notif.send_slack_alert('Test', 'Slack works!', 'info')

asyncio.run(test())
"
```

---

## Troubleshooting

### Email Not Sending

**Issue:** SMTP authentication failed
```
Solution: Check SMTP credentials, ensure app password is used (not regular password)
```

**Issue:** Connection timeout
```
Solution:
- Check SMTP host and port
- Ensure firewall allows outbound SMTP (port 587)
- Try alternate port (465 for SSL)
```

**Issue:** Emails go to spam
```
Solution:
- Use a verified domain email address
- Configure SPF and DKIM records
- Use a reputable SMTP service (SendGrid, AWS SES)
```

### Slack Not Sending

**Issue:** Webhook URL invalid
```
Solution: Verify webhook URL in Slack app settings, regenerate if needed
```

**Issue:** Message format error
```
Solution: Check Slack webhook payload format, ensure JSON is valid
```

### Check Logs

```bash
# View notification errors
journalctl -u tds-core-worker -f | grep "notification"

# View alert service logs
journalctl -u tds-core-worker -f | grep "alert"
```

---

## Best Practices

1. **Use Dedicated Email Account**
   - Create alerts@tsh.sale specifically for notifications
   - Don't use personal email accounts in production

2. **Dedicated Slack Channel**
   - Create #tds-alerts channel
   - Add only relevant team members
   - Set up proper notification preferences

3. **Test Regularly**
   - Test notifications monthly
   - Verify all recipients receive alerts
   - Check spam folders

4. **Monitor Notification Failures**
   - Check logs for failed sends
   - Set up fallback notifications
   - Have alternative contact methods

5. **Customize for Your Environment**
   - Adjust alert thresholds based on traffic
   - Configure quiet hours if needed
   - Set up different severity levels for different channels

6. **Secure Credentials**
   - Never commit credentials to git
   - Use environment variables
   - Rotate passwords/tokens quarterly
   - Use secret management (AWS Secrets Manager, HashiCorp Vault)

---

## Advanced Integrations

### PagerDuty

```python
async def send_pagerduty_alert(title, message, severity):
    """Send alert to PagerDuty"""
    payload = {
        "routing_key": "YOUR_PAGERDUTY_KEY",
        "event_action": "trigger",
        "payload": {
            "summary": title,
            "severity": severity,
            "source": "TDS Core",
            "custom_details": {"message": message}
        }
    }

    await notif_service.send_webhook_notification(
        webhook_url="https://events.pagerduty.com/v2/enqueue",
        payload=payload
    )
```

### Microsoft Teams

```python
async def send_teams_alert(title, message):
    """Send alert to Microsoft Teams"""
    payload = {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "summary": title,
        "themeColor": "FF0000",
        "title": title,
        "text": message
    }

    await notif_service.send_webhook_notification(
        webhook_url="YOUR_TEAMS_WEBHOOK_URL",
        payload=payload
    )
```

### Discord

```python
async def send_discord_alert(title, message, severity):
    """Send alert to Discord"""
    color_map = {"info": 0x3498db, "warning": 0xf39c12, "critical": 0xe74c3c}

    payload = {
        "embeds": [{
            "title": title,
            "description": message,
            "color": color_map.get(severity, 0x95a5a6)
        }]
    }

    await notif_service.send_webhook_notification(
        webhook_url="YOUR_DISCORD_WEBHOOK_URL",
        payload=payload
    )
```

---

## Support

For issues with notifications:
1. Check this guide
2. Review service logs
3. Test with simple examples
4. Contact system administrator

**Configuration Files:**
- `/opt/tds_core/.env` - Environment variables
- `/opt/tds_core/core/config.py` - Settings configuration
- `/opt/tds_core/services/notification_service.py` - Notification logic
