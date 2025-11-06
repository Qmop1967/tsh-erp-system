"""
TDS Alert Service
=================

Alert management for TDS sync issues.
Consolidates zoho_alert.py functionality.

خدمة التنبيهات لمشاكل المزامنة

Author: TSH ERP Team
Date: November 6, 2025
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class AlertSeverity(str, Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertChannel(str, Enum):
    """Alert notification channels"""
    LOG = "log"
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"


@dataclass
class Alert:
    """Alert data"""
    alert_id: str
    title: str
    message: str
    severity: AlertSeverity
    timestamp: datetime
    metadata: Dict[str, Any]
    acknowledged: bool = False


class TDSAlertService:
    """
    TDS Alert Service
    خدمة تنبيهات TDS

    Manages alerts for sync issues and errors.
    """

    def __init__(self):
        """Initialize alert service"""
        # Alert handlers by channel
        self._handlers: Dict[AlertChannel, List[Callable]] = {
            AlertChannel.LOG: [self._log_handler],
        }

        # Alert history
        self._alerts: List[Alert] = []

        # Alert rules
        self._rules = {
            "sync_failure_rate": {
                "threshold": 10.0,  # %
                "severity": AlertSeverity.WARNING
            },
            "webhook_failure_rate": {
                "threshold": 15.0,  # %
                "severity": AlertSeverity.ERROR
            },
            "api_response_time": {
                "threshold": 5000,  # ms
                "severity": AlertSeverity.WARNING
            }
        }

    async def create_alert(
        self,
        title: str,
        message: str,
        severity: AlertSeverity,
        metadata: Optional[Dict[str, Any]] = None,
        channels: Optional[List[AlertChannel]] = None
    ) -> Alert:
        """
        Create and send alert

        Args:
            title: Alert title
            message: Alert message
            severity: Alert severity
            metadata: Additional metadata
            channels: Channels to send alert to

        Returns:
            Alert: Created alert
        """
        # Create alert
        alert = Alert(
            alert_id=f"alert_{datetime.utcnow().timestamp()}",
            title=title,
            message=message,
            severity=severity,
            timestamp=datetime.utcnow(),
            metadata=metadata or {}
        )

        # Store alert
        self._alerts.append(alert)

        # Send to channels
        channels = channels or [AlertChannel.LOG]
        for channel in channels:
            await self._send_alert(alert, channel)

        logger.info(f"Alert created: {alert.title} ({alert.severity})")

        return alert

    async def _send_alert(self, alert: Alert, channel: AlertChannel):
        """Send alert to specific channel"""
        if channel in self._handlers:
            for handler in self._handlers[channel]:
                try:
                    await handler(alert)
                except Exception as e:
                    logger.error(f"Alert handler error: {str(e)}")

    async def _log_handler(self, alert: Alert):
        """Log alert handler"""
        log_level = {
            AlertSeverity.INFO: logging.INFO,
            AlertSeverity.WARNING: logging.WARNING,
            AlertSeverity.ERROR: logging.ERROR,
            AlertSeverity.CRITICAL: logging.CRITICAL
        }.get(alert.severity, logging.INFO)

        logger.log(
            log_level,
            f"[ALERT] {alert.title}: {alert.message}",
            extra={"alert_metadata": alert.metadata}
        )

    def register_handler(
        self,
        channel: AlertChannel,
        handler: Callable[[Alert], None]
    ):
        """Register custom alert handler"""
        if channel not in self._handlers:
            self._handlers[channel] = []

        self._handlers[channel].append(handler)

    def get_alerts(
        self,
        severity: Optional[AlertSeverity] = None,
        limit: int = 100
    ) -> List[Alert]:
        """Get recent alerts"""
        alerts = self._alerts

        if severity:
            alerts = [a for a in alerts if a.severity == severity]

        return list(reversed(alerts))[-limit:]
