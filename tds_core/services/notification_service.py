"""
TDS Core - Notification Service
Email and Slack notification system for alerts
"""
import logging
import smtplib
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any, List
from datetime import datetime

import httpx

from core.config import settings

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Multi-channel notification service

    Supports:
    - Email (SMTP)
    - Slack webhooks
    - Generic webhooks
    """

    def __init__(self):
        self.email_enabled = getattr(settings, 'alert_email_enabled', False)
        self.slack_enabled = getattr(settings, 'alert_slack_enabled', False)

        # Email configuration
        self.smtp_host = getattr(settings, 'smtp_host', 'smtp.gmail.com')
        self.smtp_port = getattr(settings, 'smtp_port', 587)
        self.smtp_user = getattr(settings, 'smtp_user', None)
        self.smtp_password = getattr(settings, 'smtp_password', None)
        self.email_from = getattr(settings, 'email_from', 'noreply@tsh.sale')
        self.email_to = getattr(settings, 'email_to', [])

        # Slack configuration
        self.slack_webhook_url = getattr(settings, 'slack_webhook_url', None)
        self.slack_channel = getattr(settings, 'slack_channel', '#alerts')

    # ========================================================================
    # EMAIL NOTIFICATIONS
    # ========================================================================

    async def send_email_alert(
        self,
        subject: str,
        body: str,
        severity: str = "info",
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Send email alert via SMTP

        Args:
            subject: Email subject
            body: Email body (HTML supported)
            severity: Alert severity (info, warning, error, critical)
            metadata: Additional context

        Returns:
            bool: Success status
        """
        if not self.email_enabled:
            logger.debug("Email notifications disabled")
            return False

        if not self.smtp_user or not self.smtp_password:
            logger.warning("SMTP credentials not configured")
            return False

        if not self.email_to:
            logger.warning("No email recipients configured")
            return False

        try:
            # Run in thread pool to avoid blocking
            await asyncio.to_thread(
                self._send_email_sync,
                subject,
                body,
                severity,
                metadata
            )
            return True

        except Exception as e:
            logger.error(f"Failed to send email alert: {e}", exc_info=True)
            return False

    def _send_email_sync(
        self,
        subject: str,
        body: str,
        severity: str,
        metadata: Optional[Dict[str, Any]]
    ):
        """Synchronous email sending (called in thread pool)"""
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"[TDS Core - {severity.upper()}] {subject}"
        msg['From'] = self.email_from
        msg['To'] = ', '.join(self.email_to) if isinstance(self.email_to, list) else self.email_to

        # Create HTML version
        html_body = self._format_email_html(subject, body, severity, metadata)
        msg.attach(MIMEText(html_body, 'html'))

        # Send via SMTP
        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            server.send_message(msg)

        logger.info(f"Email alert sent: {subject}")

    def _format_email_html(
        self,
        subject: str,
        body: str,
        severity: str,
        metadata: Optional[Dict[str, Any]]
    ) -> str:
        """Format email as HTML"""
        severity_colors = {
            'info': '#17a2b8',
            'warning': '#ffc107',
            'error': '#dc3545',
            'critical': '#721c24'
        }

        color = severity_colors.get(severity, '#6c757d')

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: {color}; color: white; padding: 20px; border-radius: 5px 5px 0 0; }}
                .content {{ background-color: #f8f9fa; padding: 20px; border: 1px solid #dee2e6; }}
                .metadata {{ background-color: #e9ecef; padding: 15px; margin-top: 15px; border-radius: 5px; }}
                .footer {{ text-align: center; padding: 15px; color: #6c757d; font-size: 12px; }}
                .badge {{ display: inline-block; padding: 5px 10px; border-radius: 3px; background-color: {color}; color: white; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>TDS Core Alert</h2>
                    <span class="badge">{severity.upper()}</span>
                </div>
                <div class="content">
                    <h3>{subject}</h3>
                    <p>{body.replace(chr(10), '<br>')}</p>

                    {self._format_metadata_html(metadata) if metadata else ''}

                    <p style="margin-top: 20px; color: #6c757d;">
                        <strong>Time:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
                    </p>
                </div>
                <div class="footer">
                    TDS Core - TSH DataSync | <a href="https://api.tsh.sale/tds/dashboard">View Dashboard</a>
                </div>
            </div>
        </body>
        </html>
        """
        return html

    def _format_metadata_html(self, metadata: Dict[str, Any]) -> str:
        """Format metadata as HTML"""
        items = []
        for key, value in metadata.items():
            items.append(f"<strong>{key}:</strong> {value}")

        return f"""
        <div class="metadata">
            <h4>Details:</h4>
            {'<br>'.join(items)}
        </div>
        """

    # ========================================================================
    # SLACK NOTIFICATIONS
    # ========================================================================

    async def send_slack_alert(
        self,
        title: str,
        message: str,
        severity: str = "info",
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Send alert to Slack via webhook

        Args:
            title: Alert title
            message: Alert message
            severity: Alert severity
            metadata: Additional context

        Returns:
            bool: Success status
        """
        if not self.slack_enabled:
            logger.debug("Slack notifications disabled")
            return False

        if not self.slack_webhook_url:
            logger.warning("Slack webhook URL not configured")
            return False

        try:
            payload = self._format_slack_payload(title, message, severity, metadata)

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.slack_webhook_url,
                    json=payload,
                    timeout=10.0
                )
                response.raise_for_status()

            logger.info(f"Slack alert sent: {title}")
            return True

        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}", exc_info=True)
            return False

    def _format_slack_payload(
        self,
        title: str,
        message: str,
        severity: str,
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Format Slack message payload"""
        severity_colors = {
            'info': '#17a2b8',
            'warning': '#ffc107',
            'error': '#dc3545',
            'critical': '#721c24'
        }

        severity_emojis = {
            'info': ':information_source:',
            'warning': ':warning:',
            'error': ':x:',
            'critical': ':rotating_light:'
        }

        color = severity_colors.get(severity, '#6c757d')
        emoji = severity_emojis.get(severity, ':bell:')

        # Build fields for metadata
        fields = []
        if metadata:
            for key, value in metadata.items():
                fields.append({
                    "title": key.replace('_', ' ').title(),
                    "value": str(value),
                    "short": True
                })

        payload = {
            "channel": self.slack_channel,
            "username": "TDS Core",
            "icon_emoji": ":robot_face:",
            "attachments": [
                {
                    "color": color,
                    "title": f"{emoji} {title}",
                    "text": message,
                    "fields": fields,
                    "footer": "TDS Core - TSH DataSync",
                    "footer_icon": "https://api.tsh.sale/favicon.ico",
                    "ts": int(datetime.utcnow().timestamp())
                }
            ]
        }

        return payload

    # ========================================================================
    # GENERIC WEBHOOK
    # ========================================================================

    async def send_webhook_notification(
        self,
        webhook_url: str,
        payload: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Send generic webhook notification

        Args:
            webhook_url: Target webhook URL
            payload: JSON payload
            headers: Optional HTTP headers

        Returns:
            bool: Success status
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    webhook_url,
                    json=payload,
                    headers=headers or {},
                    timeout=10.0
                )
                response.raise_for_status()

            logger.info(f"Webhook notification sent to {webhook_url}")
            return True

        except Exception as e:
            logger.error(f"Failed to send webhook notification: {e}", exc_info=True)
            return False

    # ========================================================================
    # UNIFIED ALERT SENDING
    # ========================================================================

    async def send_alert(
        self,
        title: str,
        message: str,
        severity: str = "info",
        metadata: Optional[Dict[str, Any]] = None,
        channels: Optional[List[str]] = None
    ) -> Dict[str, bool]:
        """
        Send alert to multiple channels

        Args:
            title: Alert title
            message: Alert message
            severity: Alert severity (info, warning, error, critical)
            metadata: Additional context
            channels: List of channels to send to (email, slack, all)
                     If None, sends to all enabled channels

        Returns:
            dict: Status for each channel
        """
        if channels is None:
            channels = ['all']

        results = {}

        # Determine which channels to use
        send_email = 'all' in channels or 'email' in channels
        send_slack = 'all' in channels or 'slack' in channels

        # Send to email
        if send_email and self.email_enabled:
            results['email'] = await self.send_email_alert(
                subject=title,
                body=message,
                severity=severity,
                metadata=metadata
            )

        # Send to Slack
        if send_slack and self.slack_enabled:
            results['slack'] = await self.send_slack_alert(
                title=title,
                message=message,
                severity=severity,
                metadata=metadata
            )

        return results


# ============================================================================
# CONFIGURATION EXAMPLES
# ============================================================================

"""
Add to .env file:

# Email Notifications
ALERT_EMAIL_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=alerts@tsh.sale
SMTP_PASSWORD=your-app-password
EMAIL_FROM=TDS Core <noreply@tsh.sale>
EMAIL_TO=admin@tsh.sale,ops@tsh.sale

# Slack Notifications
ALERT_SLACK_ENABLED=true
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
SLACK_CHANNEL=#tds-alerts

Add to core/config.py:

# Alert settings
alert_email_enabled: bool = False
smtp_host: str = "smtp.gmail.com"
smtp_port: int = 587
smtp_user: Optional[str] = None
smtp_password: Optional[str] = None
email_from: str = "noreply@tsh.sale"
email_to: list = []

alert_slack_enabled: bool = False
slack_webhook_url: Optional[str] = None
slack_channel: str = "#alerts"
"""
