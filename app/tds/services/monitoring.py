"""
TDS Monitoring Service
======================

Real-time monitoring for all TDS integrations.
Consolidates zoho_monitoring.py functionality.

خدمة مراقبة TDS في الوقت الفعلي

Author: TSH ERP Team
Date: November 6, 2025
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import deque

logger = logging.getLogger(__name__)


@dataclass
class HealthMetrics:
    """Health metrics data"""
    timestamp: datetime
    sync_success_rate: float
    webhook_success_rate: float
    api_response_time_ms: float
    queue_depth: int
    error_rate: float
    is_healthy: bool


class TDSMonitoringService:
    """
    TDS Monitoring Service
    خدمة مراقبة TDS

    Provides real-time monitoring and health checks for all TDS operations.
    """

    def __init__(self, retention_hours: int = 24):
        """
        Initialize monitoring service

        Args:
            retention_hours: Hours to retain metrics
        """
        self.retention_hours = retention_hours
        self._metrics_history: deque = deque(maxlen=10000)

        # Current metrics
        self._current_metrics = {
            "sync_operations": {
                "total": 0,
                "successful": 0,
                "failed": 0,
                "in_progress": 0
            },
            "webhook_events": {
                "total": 0,
                "processed": 0,
                "failed": 0,
                "duplicates": 0
            },
            "api_requests": {
                "total": 0,
                "successful": 0,
                "failed": 0,
                "avg_response_time_ms": 0
            },
            "errors": [],
            "last_updated": None
        }

    def record_sync_operation(
        self,
        entity_type: str,
        success: bool,
        duration_ms: float,
        entities_processed: int
    ):
        """
        Record a sync operation

        Args:
            entity_type: Type of entity synced
            success: Whether sync was successful
            duration_ms: Duration in milliseconds
            entities_processed: Number of entities processed
        """
        self._current_metrics["sync_operations"]["total"] += 1

        if success:
            self._current_metrics["sync_operations"]["successful"] += 1
        else:
            self._current_metrics["sync_operations"]["failed"] += 1

        # Record metric
        self._metrics_history.append({
            "timestamp": datetime.utcnow(),
            "type": "sync",
            "entity_type": entity_type,
            "success": success,
            "duration_ms": duration_ms,
            "entities_processed": entities_processed
        })

        self._current_metrics["last_updated"] = datetime.utcnow().isoformat()

    def record_webhook_event(
        self,
        event_type: str,
        success: bool,
        processing_time_ms: float
    ):
        """Record a webhook event"""
        self._current_metrics["webhook_events"]["total"] += 1

        if success:
            self._current_metrics["webhook_events"]["processed"] += 1
        else:
            self._current_metrics["webhook_events"]["failed"] += 1

        self._metrics_history.append({
            "timestamp": datetime.utcnow(),
            "type": "webhook",
            "event_type": event_type,
            "success": success,
            "processing_time_ms": processing_time_ms
        })

        self._current_metrics["last_updated"] = datetime.utcnow().isoformat()

    def record_api_request(
        self,
        api_type: str,
        endpoint: str,
        success: bool,
        response_time_ms: float
    ):
        """Record an API request"""
        self._current_metrics["api_requests"]["total"] += 1

        if success:
            self._current_metrics["api_requests"]["successful"] += 1
        else:
            self._current_metrics["api_requests"]["failed"] += 1

        # Update average response time
        total = self._current_metrics["api_requests"]["total"]
        current_avg = self._current_metrics["api_requests"]["avg_response_time_ms"]
        new_avg = ((current_avg * (total - 1)) + response_time_ms) / total
        self._current_metrics["api_requests"]["avg_response_time_ms"] = new_avg

        self._current_metrics["last_updated"] = datetime.utcnow().isoformat()

    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current metrics snapshot"""
        return self._current_metrics.copy()

    def get_health_status(self) -> HealthMetrics:
        """Get current health status"""
        sync_ops = self._current_metrics["sync_operations"]
        webhook_events = self._current_metrics["webhook_events"]
        api_requests = self._current_metrics["api_requests"]

        # Calculate success rates
        sync_success_rate = (
            (sync_ops["successful"] / sync_ops["total"] * 100)
            if sync_ops["total"] > 0 else 100.0
        )

        webhook_success_rate = (
            (webhook_events["processed"] / webhook_events["total"] * 100)
            if webhook_events["total"] > 0 else 100.0
        )

        error_rate = (
            ((sync_ops["failed"] + webhook_events["failed"]) /
             (sync_ops["total"] + webhook_events["total"]) * 100)
            if (sync_ops["total"] + webhook_events["total"]) > 0 else 0.0
        )

        # Determine if healthy
        is_healthy = (
            sync_success_rate >= 95.0 and
            webhook_success_rate >= 95.0 and
            error_rate < 5.0
        )

        return HealthMetrics(
            timestamp=datetime.utcnow(),
            sync_success_rate=sync_success_rate,
            webhook_success_rate=webhook_success_rate,
            api_response_time_ms=api_requests["avg_response_time_ms"],
            queue_depth=sync_ops["in_progress"],
            error_rate=error_rate,
            is_healthy=is_healthy
        )

    def get_metrics_over_time(
        self,
        metric_type: Optional[str] = None,
        hours: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Get metrics over time period

        Args:
            metric_type: Type of metrics (sync, webhook, api) or None for all
            hours: Number of hours to look back

        Returns:
            list: Metrics data
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        filtered_metrics = [
            m for m in self._metrics_history
            if m["timestamp"] >= cutoff_time and
            (metric_type is None or m["type"] == metric_type)
        ]

        return filtered_metrics

    def clean_old_metrics(self):
        """Remove metrics older than retention period"""
        cutoff_time = datetime.utcnow() - timedelta(hours=self.retention_hours)

        while self._metrics_history and self._metrics_history[0]["timestamp"] < cutoff_time:
            self._metrics_history.popleft()
