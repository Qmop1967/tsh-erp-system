#!/usr/bin/env python3
"""
Orixoon Auto-Healing Engine
Automatically fixes common service issues during pre-deployment testing
"""

import json
import os
import sys
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import psycopg2
import redis

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class AutoHealingEngine:
    """
    Auto-healing engine that attempts to fix common service issues
    """

    def __init__(self, dry_run: bool = False, max_attempts: int = 3):
        self.dry_run = dry_run
        self.max_attempts = max_attempts
        self.healing_log: List[Dict[str, Any]] = []
        self.healed_count = 0
        self.failed_healing_count = 0

    def log_healing_action(self, issue: str, action: str, success: bool, details: str = ""):
        """Log a healing action"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "issue": issue,
            "action": action,
            "success": success,
            "details": details,
            "dry_run": self.dry_run
        }
        self.healing_log.append(entry)

        if success:
            self.healed_count += 1
            print(f"✅ HEALED: {issue} - {action}")
        else:
            self.failed_healing_count += 1
            print(f"❌ HEALING FAILED: {issue} - {action}")

        if details:
            print(f"   Details: {details}")

    # ========================================
    # DOCKER CONTAINER HEALING
    # ========================================

    def heal_container_not_running(self, container_name: str) -> bool:
        """Restart a stopped Docker container"""
        try:
            if self.dry_run:
                self.log_healing_action(
                    f"Container {container_name} not running",
                    "Would restart container",
                    True,
                    "DRY RUN - no action taken"
                )
                return True

            # Try to start the container
            result = subprocess.run(
                ["docker", "start", container_name],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                # Wait for container to be healthy
                time.sleep(5)

                # Check if container is running
                check = subprocess.run(
                    ["docker", "ps", "--filter", f"name={container_name}", "--format", "{{.Status}}"],
                    capture_output=True,
                    text=True
                )

                if "Up" in check.stdout:
                    self.log_healing_action(
                        f"Container {container_name} not running",
                        "Restarted container",
                        True,
                        f"Container now running: {check.stdout.strip()}"
                    )
                    return True

            self.log_healing_action(
                f"Container {container_name} not running",
                "Attempted restart",
                False,
                f"Failed: {result.stderr}"
            )
            return False

        except Exception as e:
            self.log_healing_action(
                f"Container {container_name} not running",
                "Attempted restart",
                False,
                f"Error: {str(e)}"
            )
            return False

    def heal_container_unhealthy(self, container_name: str) -> bool:
        """Restart an unhealthy Docker container"""
        try:
            if self.dry_run:
                self.log_healing_action(
                    f"Container {container_name} unhealthy",
                    "Would restart container",
                    True,
                    "DRY RUN - no action taken"
                )
                return True

            # Restart the container
            result = subprocess.run(
                ["docker", "restart", container_name],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                # Wait for container to stabilize
                time.sleep(10)

                # Check container status
                check = subprocess.run(
                    ["docker", "ps", "--filter", f"name={container_name}", "--format", "{{.Status}}"],
                    capture_output=True,
                    text=True
                )

                if "Up" in check.stdout and "unhealthy" not in check.stdout.lower():
                    self.log_healing_action(
                        f"Container {container_name} unhealthy",
                        "Restarted container",
                        True,
                        f"Container now healthy: {check.stdout.strip()}"
                    )
                    return True

            self.log_healing_action(
                f"Container {container_name} unhealthy",
                "Attempted restart",
                False,
                f"Failed: {result.stderr}"
            )
            return False

        except Exception as e:
            self.log_healing_action(
                f"Container {container_name} unhealthy",
                "Attempted restart",
                False,
                f"Error: {str(e)}"
            )
            return False

    # ========================================
    # DATABASE HEALING
    # ========================================

    def heal_database_connection_pool_exhausted(self) -> bool:
        """Kill idle database connections to free up pool"""
        try:
            if self.dry_run:
                self.log_healing_action(
                    "Database connection pool exhausted",
                    "Would kill idle connections",
                    True,
                    "DRY RUN - no action taken"
                )
                return True

            database_url = os.getenv("DATABASE_URL", "postgresql://tsh_admin:TSH@2025Secure!Production@localhost:5432/tsh_erp")
            conn = psycopg2.connect(database_url)
            cursor = conn.cursor()

            # Kill idle connections older than 5 minutes
            cursor.execute("""
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE datname = current_database()
                AND state = 'idle'
                AND state_change < NOW() - INTERVAL '5 minutes'
                AND pid <> pg_backend_pid()
            """)

            killed_count = cursor.rowcount
            conn.commit()
            cursor.close()
            conn.close()

            self.log_healing_action(
                "Database connection pool exhausted",
                "Killed idle connections",
                True,
                f"Terminated {killed_count} idle connections"
            )
            return True

        except Exception as e:
            self.log_healing_action(
                "Database connection pool exhausted",
                "Attempted to kill idle connections",
                False,
                f"Error: {str(e)}"
            )
            return False

    def heal_database_table_locks(self) -> bool:
        """Clear blocking database locks"""
        try:
            if self.dry_run:
                self.log_healing_action(
                    "Database table locks detected",
                    "Would clear blocking locks",
                    True,
                    "DRY RUN - no action taken"
                )
                return True

            database_url = os.getenv("DATABASE_URL", "postgresql://tsh_admin:TSH@2025Secure!Production@localhost:5432/tsh_erp")
            conn = psycopg2.connect(database_url)
            cursor = conn.cursor()

            # Find and kill blocking queries
            cursor.execute("""
                SELECT pg_terminate_backend(blocked_locks.pid)
                FROM pg_catalog.pg_locks blocked_locks
                JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
                WHERE NOT blocked_locks.granted
                AND blocked_activity.state = 'idle in transaction'
            """)

            killed_count = cursor.rowcount
            conn.commit()
            cursor.close()
            conn.close()

            self.log_healing_action(
                "Database table locks detected",
                "Cleared blocking locks",
                True,
                f"Terminated {killed_count} blocking queries"
            )
            return True

        except Exception as e:
            self.log_healing_action(
                "Database table locks detected",
                "Attempted to clear locks",
                False,
                f"Error: {str(e)}"
            )
            return False

    # ========================================
    # REDIS HEALING
    # ========================================

    def heal_redis_memory_full(self) -> bool:
        """Clear Redis cache to free memory"""
        try:
            if self.dry_run:
                self.log_healing_action(
                    "Redis memory full",
                    "Would flush expired keys",
                    True,
                    "DRY RUN - no action taken"
                )
                return True

            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
            r = redis.from_url(redis_url)

            # Get memory info before
            info_before = r.info('memory')
            used_before = info_before.get('used_memory_human', 'unknown')

            # Delete keys with TTL that are about to expire (within 1 hour)
            # This is safer than FLUSHALL
            cursor = 0
            deleted = 0
            while True:
                cursor, keys = r.scan(cursor, count=100)
                for key in keys:
                    ttl = r.ttl(key)
                    if 0 < ttl < 3600:  # Expires in less than 1 hour
                        r.delete(key)
                        deleted += 1
                if cursor == 0:
                    break

            # Get memory info after
            info_after = r.info('memory')
            used_after = info_after.get('used_memory_human', 'unknown')

            self.log_healing_action(
                "Redis memory full",
                "Flushed expiring keys",
                True,
                f"Deleted {deleted} keys. Memory: {used_before} -> {used_after}"
            )
            return True

        except Exception as e:
            self.log_healing_action(
                "Redis memory full",
                "Attempted to flush cache",
                False,
                f"Error: {str(e)}"
            )
            return False

    def heal_redis_not_responding(self) -> bool:
        """Restart Redis container"""
        return self.heal_container_unhealthy("redis")

    # ========================================
    # SERVICE HEALING
    # ========================================

    def heal_background_worker_not_running(self, worker_name: str) -> bool:
        """Restart a background worker service"""
        try:
            if self.dry_run:
                self.log_healing_action(
                    f"Background worker {worker_name} not running",
                    "Would restart worker",
                    True,
                    "DRY RUN - no action taken"
                )
                return True

            # Map worker names to restart commands
            restart_commands = {
                "tds_scheduler": ["systemctl", "restart", "tds-scheduler"],
                "uvicorn": ["systemctl", "restart", "tsh-erp"],
            }

            if worker_name not in restart_commands:
                self.log_healing_action(
                    f"Background worker {worker_name} not running",
                    "No restart command defined",
                    False,
                    f"Unknown worker: {worker_name}"
                )
                return False

            # Restart the worker
            result = subprocess.run(
                restart_commands[worker_name],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                time.sleep(5)

                self.log_healing_action(
                    f"Background worker {worker_name} not running",
                    "Restarted worker service",
                    True,
                    "Worker restarted successfully"
                )
                return True
            else:
                self.log_healing_action(
                    f"Background worker {worker_name} not running",
                    "Attempted restart",
                    False,
                    f"Failed: {result.stderr}"
                )
                return False

        except Exception as e:
            self.log_healing_action(
                f"Background worker {worker_name} not running",
                "Attempted restart",
                False,
                f"Error: {str(e)}"
            )
            return False

    def heal_high_error_rate(self) -> bool:
        """Restart main application to clear error state"""
        try:
            if self.dry_run:
                self.log_healing_action(
                    "High error rate in logs",
                    "Would restart main application",
                    True,
                    "DRY RUN - no action taken"
                )
                return True

            # Restart main app container
            result = subprocess.run(
                ["docker", "restart", "app"],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                time.sleep(10)

                self.log_healing_action(
                    "High error rate in logs",
                    "Restarted main application",
                    True,
                    "Application restarted to clear error state"
                )
                return True
            else:
                self.log_healing_action(
                    "High error rate in logs",
                    "Attempted application restart",
                    False,
                    f"Failed: {result.stderr}"
                )
                return False

        except Exception as e:
            self.log_healing_action(
                "High error rate in logs",
                "Attempted application restart",
                False,
                f"Error: {str(e)}"
            )
            return False

    # ========================================
    # ZOHO SYNC HEALING
    # ========================================

    def heal_zoho_sync_queue_stuck(self) -> bool:
        """Clear stuck items in Zoho sync queue"""
        try:
            if self.dry_run:
                self.log_healing_action(
                    "Zoho sync queue stuck",
                    "Would requeue failed items",
                    True,
                    "DRY RUN - no action taken"
                )
                return True

            database_url = os.getenv("DATABASE_URL", "postgresql://tsh_admin:TSH@2025Secure!Production@localhost:5432/tsh_erp")
            conn = psycopg2.connect(database_url)
            cursor = conn.cursor()

            # Reset stuck items (processing for > 1 hour)
            cursor.execute("""
                UPDATE tds_sync_queue
                SET status = 'pending',
                    retry_count = retry_count + 1,
                    updated_at = NOW()
                WHERE status = 'processing'
                AND updated_at < NOW() - INTERVAL '1 hour'
                AND retry_count < 5
            """)

            reset_count = cursor.rowcount

            # Move failed items to dead letter queue
            cursor.execute("""
                INSERT INTO tds_dead_letter_queue (
                    original_id, event_type, payload, error_message, failed_at
                )
                SELECT id, event_type, payload, 'Max retries exceeded', NOW()
                FROM tds_sync_queue
                WHERE status = 'failed'
                AND retry_count >= 5
                RETURNING id
            """)

            moved_count = cursor.rowcount

            # Delete moved items from sync queue
            if moved_count > 0:
                cursor.execute("""
                    DELETE FROM tds_sync_queue
                    WHERE status = 'failed'
                    AND retry_count >= 5
                """)

            conn.commit()
            cursor.close()
            conn.close()

            self.log_healing_action(
                "Zoho sync queue stuck",
                "Cleared stuck items",
                True,
                f"Reset {reset_count} stuck items, moved {moved_count} to DLQ"
            )
            return True

        except Exception as e:
            self.log_healing_action(
                "Zoho sync queue stuck",
                "Attempted to clear queue",
                False,
                f"Error: {str(e)}"
            )
            return False

    # ========================================
    # COMPREHENSIVE HEALING
    # ========================================

    def heal_all_issues(self, issues: List[Dict[str, Any]]) -> Tuple[int, int]:
        """
        Attempt to heal all detected issues
        Returns: (healed_count, failed_count)
        """
        print(f"\n{'='*60}")
        print(f"🔧 AUTO-HEALING ENGINE ACTIVATED")
        print(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE'}")
        print(f"Issues to heal: {len(issues)}")
        print(f"{'='*60}\n")

        for issue in issues:
            issue_type = issue.get("type")
            issue_data = issue.get("data", {})

            # Route to appropriate healing function
            if issue_type == "container_not_running":
                self.heal_container_not_running(issue_data.get("container_name"))

            elif issue_type == "container_unhealthy":
                self.heal_container_unhealthy(issue_data.get("container_name"))

            elif issue_type == "database_pool_exhausted":
                self.heal_database_connection_pool_exhausted()

            elif issue_type == "database_locks":
                self.heal_database_table_locks()

            elif issue_type == "redis_memory_full":
                self.heal_redis_memory_full()

            elif issue_type == "redis_not_responding":
                self.heal_redis_not_responding()

            elif issue_type == "background_worker_not_running":
                self.heal_background_worker_not_running(issue_data.get("worker_name"))

            elif issue_type == "high_error_rate":
                self.heal_high_error_rate()

            elif issue_type == "zoho_sync_stuck":
                self.heal_zoho_sync_queue_stuck()

            else:
                self.log_healing_action(
                    issue_type,
                    "Unknown issue type",
                    False,
                    f"No healing action defined for: {issue_type}"
                )

        print(f"\n{'='*60}")
        print(f"🔧 AUTO-HEALING SUMMARY")
        print(f"Successfully healed: {self.healed_count}")
        print(f"Failed to heal: {self.failed_healing_count}")
        print(f"{'='*60}\n")

        return self.healed_count, self.failed_healing_count

    def get_healing_report(self) -> Dict[str, Any]:
        """Generate healing report"""
        return {
            "timestamp": datetime.now().isoformat(),
            "dry_run": self.dry_run,
            "summary": {
                "total_actions": len(self.healing_log),
                "successful": self.healed_count,
                "failed": self.failed_healing_count,
                "success_rate": f"{(self.healed_count / len(self.healing_log) * 100) if self.healing_log else 0:.1f}%"
            },
            "actions": self.healing_log
        }


def main():
    """Main entry point for standalone testing"""
    import argparse

    parser = argparse.ArgumentParser(description="Orixoon Auto-Healing Engine")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode (no actual changes)")
    parser.add_argument("--issue-file", type=str, help="JSON file with issues to heal")
    args = parser.parse_args()

    engine = AutoHealingEngine(dry_run=args.dry_run)

    if args.issue_file:
        with open(args.issue_file) as f:
            issues = json.load(f)
        engine.heal_all_issues(issues)
    else:
        # Example issues for testing
        test_issues = [
            {"type": "container_unhealthy", "data": {"container_name": "app"}},
            {"type": "zoho_sync_stuck", "data": {}}
        ]
        engine.heal_all_issues(test_issues)

    # Print report
    report = engine.get_healing_report()
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
