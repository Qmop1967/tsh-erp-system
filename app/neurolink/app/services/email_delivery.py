"""
TSH NeuroLink - Email Delivery Service
Uses Resend API for reliable email delivery with tracking
"""

import os
from typing import List, Dict, Optional
from datetime import datetime
import logging
import resend
from jinja2 import Template
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert

from app.models import NeurolinkNotification, NeurolinkDeliveryLog
from app.config import settings

logger = logging.getLogger(__name__)

# Initialize Resend with API key
resend.api_key = settings.RESEND_API_KEY


class EmailDeliveryService:
    """
    Handles email delivery for NeuroLink notifications using Resend API
    """

    def __init__(self):
        self.from_email = settings.EMAIL_FROM_ADDRESS
        self.from_name = settings.EMAIL_FROM_NAME

    async def send_notification_email(
        self,
        notification: NeurolinkNotification,
        recipient_email: str,
        recipient_name: str,
        db: AsyncSession
    ) -> Dict:
        """
        Send a notification as an email

        Args:
            notification: The notification object
            recipient_email: Email address to send to
            recipient_name: Name of recipient
            db: Database session for logging

        Returns:
            Dict with status and provider message ID
        """
        try:
            # Generate email HTML from notification
            email_html = self._generate_email_html(
                notification=notification,
                recipient_name=recipient_name
            )

            # Send via Resend
            response = resend.Emails.send({
                "from": f"{self.from_name} <{self.from_email}>",
                "to": recipient_email,
                "subject": notification.title,
                "html": email_html
            })

            # Log successful delivery
            await self._log_delivery(
                db=db,
                notification_id=notification.id,
                recipient=recipient_email,
                status="sent",
                provider="resend",
                provider_message_id=response.get('id')
            )

            logger.info(
                f"Email sent successfully to {recipient_email} "
                f"for notification {notification.id}"
            )

            return {
                "success": True,
                "provider_message_id": response.get('id'),
                "status": "sent"
            }

        except Exception as e:
            logger.error(
                f"Failed to send email to {recipient_email}: {str(e)}"
            )

            # Log failed delivery
            await self._log_delivery(
                db=db,
                notification_id=notification.id,
                recipient=recipient_email,
                status="failed",
                provider="resend",
                error_message=str(e)
            )

            return {
                "success": False,
                "error": str(e),
                "status": "failed"
            }

    async def send_announcement_email(
        self,
        announcement: Dict,
        recipient_email: str,
        recipient_name: str,
        db: AsyncSession
    ) -> Dict:
        """
        Send an announcement as an email

        Args:
            announcement: Announcement data
            recipient_email: Email address
            recipient_name: Name of recipient
            db: Database session

        Returns:
            Dict with status
        """
        try:
            email_html = self._generate_announcement_email_html(
                announcement=announcement,
                recipient_name=recipient_name
            )

            response = resend.Emails.send({
                "from": f"{self.from_name} <{self.from_email}>",
                "to": recipient_email,
                "subject": f"[Announcement] {announcement['title']}",
                "html": email_html
            })

            logger.info(
                f"Announcement email sent to {recipient_email}"
            )

            return {
                "success": True,
                "provider_message_id": response.get('id'),
                "status": "sent"
            }

        except Exception as e:
            logger.error(
                f"Failed to send announcement email to {recipient_email}: {str(e)}"
            )
            return {
                "success": False,
                "error": str(e),
                "status": "failed"
            }

    async def send_emergency_broadcast_email(
        self,
        broadcast: Dict,
        recipient_email: str,
        recipient_name: str,
        db: AsyncSession
    ) -> Dict:
        """
        Send emergency broadcast as email

        Args:
            broadcast: Emergency broadcast data
            recipient_email: Email address
            recipient_name: Name of recipient
            db: Database session

        Returns:
            Dict with status
        """
        try:
            email_html = self._generate_emergency_email_html(
                broadcast=broadcast,
                recipient_name=recipient_name
            )

            response = resend.Emails.send({
                "from": f"TSH ERP URGENT <{self.from_email}>",
                "to": recipient_email,
                "subject": f"🚨 URGENT: {broadcast['title']}",
                "html": email_html
            })

            logger.info(
                f"Emergency broadcast email sent to {recipient_email}"
            )

            return {
                "success": True,
                "provider_message_id": response.get('id'),
                "status": "sent"
            }

        except Exception as e:
            logger.error(
                f"Failed to send emergency email to {recipient_email}: {str(e)}"
            )
            return {
                "success": False,
                "error": str(e),
                "status": "failed"
            }

    def _generate_email_html(
        self,
        notification: NeurolinkNotification,
        recipient_name: str
    ) -> str:
        """Generate HTML email from notification"""

        severity_colors = {
            "info": "#3b82f6",
            "warning": "#f59e0b",
            "error": "#ef4444",
            "critical": "#dc2626"
        }

        severity_icons = {
            "info": "ℹ️",
            "warning": "⚠️",
            "error": "❌",
            "critical": "🚨"
        }

        color = severity_colors.get(notification.severity, "#3b82f6")
        icon = severity_icons.get(notification.severity, "📢")

        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: {{ color }}; color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
                .content {{ background-color: #f9fafb; padding: 30px; border-radius: 0 0 8px 8px; }}
                .title {{ margin: 0; font-size: 24px; }}
                .body {{ margin: 20px 0; }}
                .button {{
                    display: inline-block;
                    background-color: {{ color }};
                    color: white;
                    padding: 12px 24px;
                    text-decoration: none;
                    border-radius: 6px;
                    margin-top: 20px;
                }}
                .footer {{ text-align: center; margin-top: 30px; font-size: 12px; color: #6b7280; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 class="title">{{ icon }} {{ title }}</h1>
                </div>
                <div class="content">
                    <p>Hi {{ recipient_name }},</p>
                    <div class="body">
                        {{ body }}
                    </div>
                    {% if action_url and action_label %}
                    <a href="{{ base_url }}{{ action_url }}" class="button">{{ action_label }}</a>
                    {% endif %}
                </div>
                <div class="footer">
                    <p>This is an automated notification from TSH ERP NeuroLink</p>
                    <p>&copy; 2025 TSH ERP. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        template = Template(html_template)
        return template.render(
            title=notification.title,
            body=notification.body.replace('\n', '<br>'),
            icon=icon,
            color=color,
            recipient_name=recipient_name,
            action_url=notification.action_url,
            action_label=notification.action_label,
            base_url=settings.APP_BASE_URL
        )

    def _generate_announcement_email_html(
        self,
        announcement: Dict,
        recipient_name: str
    ) -> str:
        """Generate HTML email for announcements"""

        severity_colors = {
            "info": "#3b82f6",
            "warning": "#f59e0b",
            "urgent": "#ef4444",
            "critical": "#dc2626"
        }

        color = severity_colors.get(announcement.get('severity', 'info'), "#3b82f6")

        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 700px; margin: 0 auto; padding: 20px; }}
                .announcement {{
                    background: white;
                    border-left: 5px solid {{ color }};
                    padding: 30px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .title {{ color: {{ color }}; font-size: 28px; margin-bottom: 10px; }}
                .content {{ margin-top: 20px; white-space: pre-wrap; }}
                .footer {{ text-align: center; margin-top: 40px; font-size: 12px; color: #999; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="announcement">
                    <h1 class="title">{{ title }}</h1>
                    {% if summary %}
                    <p><strong>{{ summary }}</strong></p>
                    {% endif %}
                    <div class="content">{{ content }}</div>
                </div>
                <div class="footer">
                    <p>TSH ERP System Announcement</p>
                </div>
            </div>
        </body>
        </html>
        """

        template = Template(html_template)
        return template.render(
            title=announcement['title'],
            summary=announcement.get('summary', ''),
            content=announcement['content'],
            color=color,
            recipient_name=recipient_name
        )

    def _generate_emergency_email_html(
        self,
        broadcast: Dict,
        recipient_name: str
    ) -> str:
        """Generate HTML email for emergency broadcasts"""

        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #fef2f2; }}
                .container {{ max-width: 600px; margin: 30px auto; }}
                .emergency {{
                    background: white;
                    border: 3px solid #dc2626;
                    padding: 30px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.2);
                }}
                .title {{
                    color: #dc2626;
                    font-size: 32px;
                    text-align: center;
                    margin-bottom: 20px;
                }}
                .icon {{ font-size: 48px; text-align: center; margin-bottom: 20px; }}
                .message {{ font-size: 18px; line-height: 1.8; text-align: center; }}
                .footer {{
                    background: #dc2626;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="emergency">
                    <div class="icon">🚨</div>
                    <h1 class="title">URGENT: {{ title }}</h1>
                    <div class="message">{{ message }}</div>
                    <div class="footer">
                        <strong>IMMEDIATE ACTION REQUIRED</strong><br>
                        Please acknowledge this message immediately
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

        template = Template(html_template)
        return template.render(
            title=broadcast['title'],
            message=broadcast['message'],
            recipient_name=recipient_name
        )

    async def _log_delivery(
        self,
        db: AsyncSession,
        notification_id: str,
        recipient: str,
        status: str,
        provider: str,
        provider_message_id: Optional[str] = None,
        error_message: Optional[str] = None
    ):
        """Log delivery attempt to database"""
        try:
            log_data = {
                "notification_id": notification_id,
                "channel": "email",
                "recipient": recipient,
                "status": status,
                "provider": provider,
                "provider_message_id": provider_message_id,
                "error_message": error_message,
                "sent_at": datetime.utcnow() if status == "sent" else None,
                "failed_at": datetime.utcnow() if status == "failed" else None
            }

            stmt = insert(NeurolinkDeliveryLog).values(**log_data)
            await db.execute(stmt)
            await db.commit()

        except Exception as e:
            logger.error(f"Failed to log delivery: {str(e)}")
            await db.rollback()
