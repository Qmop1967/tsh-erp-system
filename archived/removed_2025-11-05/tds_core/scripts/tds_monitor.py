#!/usr/bin/env python3
"""
TDS Core Monitoring Script
Monitors TDS Core for errors and automatically corrects data flow issues

Part of TSH ERP Unified Skills
Command: tds_monitor
"""

import sys
import json
import requests
import logging
from datetime import datetime
from typing import Dict, Any, List
import psycopg2
from psycopg2.extras import RealDictCursor

# Configuration
TDS_API_URL = "http://localhost:8001"
HEALTH_THRESHOLD = 70
DUPLICATE_THRESHOLD = 10.0
SUCCESS_RATE_THRESHOLD = 90.0

# Database connection
DB_CONFIG = {
    "host": "localhost",
    "database": "tsh_erp",
    "user": "tsh_erp",
    "password": "TSH@2025Secure!Production"
}

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/tds-core/tds_monitor.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class TDSMonitor:
    """Monitor and auto-correct TDS Core issues"""

    def __init__(self):
        self.api_url = TDS_API_URL
        self.issues_found = []
        self.corrections_applied = []

    def check_health(self) -> Dict[str, Any]:
        """Check TDS Core health metrics"""
        try:
            response = requests.get(f"{self.api_url}/webhooks/health?hours=1", timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to fetch health metrics: {e}")
            return {"success": False, "error": str(e)}

    def check_duplicate_webhooks(self) -> Dict[str, Any]:
        """Check for excessive duplicate webhooks"""
        try:
            response = requests.get(f"{self.api_url}/webhooks/duplicates?hours=1", timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to fetch duplicate analysis: {e}")
            return {"success": False, "error": str(e)}

    def check_queue_stats(self) -> Dict[str, Any]:
        """Check processing queue statistics"""
        try:
            response = requests.get(f"{self.api_url}/queue/stats", timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to fetch queue stats: {e}")
            return {"success": False, "error": str(e)}

    def analyze_issues(self, health_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze health data and identify issues"""
        issues = []

        if not health_data.get("success"):
            issues.append({
                "severity": "critical",
                "type": "api_unavailable",
                "message": "TDS Core API is not responding",
                "auto_fix": False
            })
            return issues

        metrics = health_data.get("metrics", {})
        health_score = metrics.get("health_score", 0)

        # Low health score
        if health_score < HEALTH_THRESHOLD:
            issues.append({
                "severity": "warning",
                "type": "low_health_score",
                "message": f"Health score is {health_score}/100",
                "auto_fix": False
            })

        # High duplicate rate
        inbox_stats = metrics.get("inbox_stats", {})
        duplicate_rate = inbox_stats.get("duplicate_rate", 0)
        if duplicate_rate > DUPLICATE_THRESHOLD:
            issues.append({
                "severity": "warning",
                "type": "high_duplicate_rate",
                "message": f"Duplicate webhook rate is {duplicate_rate}%",
                "auto_fix": True,
                "fix_action": "clear_old_duplicates"
            })

        # Low success rate
        processing_stats = metrics.get("processing_stats", {})
        success_rate = processing_stats.get("success_rate", 0)
        if success_rate < SUCCESS_RATE_THRESHOLD:
            issues.append({
                "severity": "error",
                "type": "low_success_rate",
                "message": f"Processing success rate is {success_rate}%",
                "auto_fix": False
            })

        # Dead letter queue accumulation
        failure_analysis = metrics.get("failure_analysis", {})
        dead_letter_count = failure_analysis.get("dead_letter_events", 0)
        if dead_letter_count > 5:
            issues.append({
                "severity": "error",
                "type": "dead_letter_accumulation",
                "message": f"{dead_letter_count} events in dead letter queue",
                "auto_fix": True,
                "fix_action": "retry_dead_letter"
            })

        return issues

    def auto_fix_issues(self, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Automatically fix issues where possible"""
        corrections = []

        for issue in issues:
            if not issue.get("auto_fix"):
                continue

            fix_action = issue.get("fix_action")

            try:
                if fix_action == "clear_old_duplicates":
                    result = self._clear_old_duplicates()
                    corrections.append({
                        "issue": issue["type"],
                        "action": "clear_old_duplicates",
                        "result": result,
                        "success": result.get("success", False)
                    })

                elif fix_action == "retry_dead_letter":
                    result = self._retry_dead_letter_events()
                    corrections.append({
                        "issue": issue["type"],
                        "action": "retry_dead_letter",
                        "result": result,
                        "success": result.get("success", False)
                    })

            except Exception as e:
                logger.error(f"Failed to auto-fix {issue['type']}: {e}")
                corrections.append({
                    "issue": issue["type"],
                    "action": fix_action,
                    "success": False,
                    "error": str(e)
                })

        return corrections

    def _clear_old_duplicates(self) -> Dict[str, Any]:
        """Clear old duplicate inbox events (keep only first occurrence)"""
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor()

            # Keep only the first occurrence of each idempotency key
            query = """
                WITH ranked_events AS (
                    SELECT id,
                           ROW_NUMBER() OVER (
                               PARTITION BY idempotency_key
                               ORDER BY received_at ASC
                           ) as rn
                    FROM tds_inbox_events
                    WHERE received_at < NOW() - INTERVAL '24 hours'
                )
                DELETE FROM tds_inbox_events
                WHERE id IN (
                    SELECT id FROM ranked_events WHERE rn > 1
                )
            """
            cursor.execute(query)
            deleted_count = cursor.rowcount
            conn.commit()

            logger.info(f"Cleared {deleted_count} old duplicate events")

            cursor.close()
            conn.close()

            return {
                "success": True,
                "deleted_count": deleted_count,
                "message": f"Cleared {deleted_count} old duplicate events"
            }

        except Exception as e:
            logger.error(f"Failed to clear duplicates: {e}")
            return {"success": False, "error": str(e)}

    def _retry_dead_letter_events(self) -> Dict[str, Any]:
        """Retry all events in dead letter queue"""
        try:
            # Get dead letter events
            response = requests.get(
                f"{self.api_url}/dashboard/dead-letter?limit=100",
                timeout=30
            )
            response.raise_for_status()
            data = response.json()

            events = data.get("events", [])
            retried = 0
            failed = 0

            for event in events:
                event_id = event.get("id")
                try:
                    retry_response = requests.post(
                        f"{self.api_url}/dashboard/dead-letter/{event_id}/retry",
                        timeout=10
                    )
                    if retry_response.status_code == 200:
                        retried += 1
                    else:
                        failed += 1
                except Exception as e:
                    logger.warning(f"Failed to retry event {event_id}: {e}")
                    failed += 1

            return {
                "success": True,
                "retried": retried,
                "failed": failed,
                "message": f"Retried {retried} events, {failed} failed"
            }

        except Exception as e:
            logger.error(f"Failed to retry dead letter events: {e}")
            return {"success": False, "error": str(e)}

    def generate_report(
        self,
        health_data: Dict[str, Any],
        issues: List[Dict[str, Any]],
        corrections: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate monitoring report"""
        metrics = health_data.get("metrics", {})

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "healthy" if len(issues) == 0 else "issues_found",
            "health_score": metrics.get("health_score", 0),
            "issues_found": len(issues),
            "corrections_applied": len([c for c in corrections if c.get("success")]),
            "issues": issues,
            "corrections": corrections,
            "metrics_summary": {
                "duplicate_rate": metrics.get("inbox_stats", {}).get("duplicate_rate", 0),
                "success_rate": metrics.get("processing_stats", {}).get("success_rate", 0),
                "dead_letter_count": metrics.get("failure_analysis", {}).get("dead_letter_events", 0)
            }
        }

    def run(self) -> Dict[str, Any]:
        """Run complete monitoring cycle"""
        logger.info("Starting TDS Core monitoring cycle")

        # 1. Check health
        health_data = self.check_health()

        # 2. Analyze issues
        issues = self.analyze_issues(health_data)

        # 3. Auto-fix issues
        corrections = []
        if issues:
            logger.info(f"Found {len(issues)} issues, attempting auto-fix...")
            corrections = self.auto_fix_issues(issues)

        # 4. Generate report
        report = self.generate_report(health_data, issues, corrections)

        # 5. Log report
        logger.info(f"Monitoring cycle complete: {report['status']}")
        if issues:
            logger.warning(f"Issues found: {len(issues)}")
            for issue in issues:
                logger.warning(f"  - [{issue['severity']}] {issue['message']}")

        if corrections:
            logger.info(f"Corrections applied: {len(corrections)}")
            for correction in corrections:
                if correction.get("success"):
                    logger.info(f"  - ✓ {correction['action']}: {correction.get('result', {}).get('message')}")
                else:
                    logger.error(f"  - ✗ {correction['action']}: {correction.get('error')}")

        return report


def main():
    """Main entry point"""
    try:
        monitor = TDSMonitor()
        report = monitor.run()

        # Print report as JSON
        print(json.dumps(report, indent=2))

        # Exit with appropriate code
        if report["status"] == "healthy":
            sys.exit(0)
        elif report["corrections_applied"] > 0:
            sys.exit(0)  # Issues found but fixed
        else:
            sys.exit(1)  # Issues found but not fixed

    except Exception as e:
        logger.error(f"Monitor failed: {e}", exc_info=True)
        print(json.dumps({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }))
        sys.exit(2)


if __name__ == "__main__":
    main()
