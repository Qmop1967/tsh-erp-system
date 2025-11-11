#!/usr/bin/env python3
"""
Orixoon Phase 3: Database Validation
Ensures database integrity and migrations are current
"""

import json
import os
import sys
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import psycopg2

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class DatabaseValidator:
    def __init__(self):
        self.results: List[Dict[str, Any]] = []
        self.start_time = time.time()
        self.critical_failures = 0
        self.conn = None

    def log_check(self, name: str, status: str, message: str, critical: bool = True):
        """Log a check result"""
        result = {
            "name": name,
            "status": status,
            "message": message,
            "critical": critical,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)

        if status == "failed" and critical:
            self.critical_failures += 1
            print(f"❌ {name}: {message}", file=sys.stderr)
        elif status == "failed":
            print(f"⚠️  {name}: {message}", file=sys.stderr)
        else:
            print(f"✓ {name}: {message}")

    def connect_database(self) -> bool:
        """Establish database connection"""
        try:
            database_url = os.getenv("DATABASE_URL", "postgresql://tsh_admin:TSH@2025Secure!Production@localhost:5432/tsh_erp")
            self.conn = psycopg2.connect(database_url)
            return True
        except Exception as e:
            self.log_check(
                "database_connection",
                "failed",
                f"Cannot connect: {str(e)}",
                critical=True
            )
            return False

    def check_alembic_migrations(self) -> bool:
        """Check Alembic migrations are up to date"""
        try:
            os.chdir(PROJECT_ROOT)
            result = subprocess.run(
                ["alembic", "current"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                current = result.stdout.strip()
                self.log_check(
                    "alembic_migrations",
                    "passed",
                    f"Migrations current: {current[:50]}"
                )
                return True
            else:
                self.log_check(
                    "alembic_migrations",
                    "failed",
                    "Migration check failed",
                    critical=True
                )
                return False

        except Exception as e:
            self.log_check(
                "alembic_migrations",
                "failed",
                f"Cannot check migrations: {str(e)}",
                critical=True
            )
            return False

    def check_critical_tables(self) -> bool:
        """Check critical tables exist"""
        critical_tables = [
            "users", "roles", "permissions",
            "products", "categories",
            "inventory_items",
            "sales_orders", "sales_invoices",
            "branches", "customers"
        ]

        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
            """)
            existing_tables = {row[0] for row in cursor.fetchall()}

            missing_tables = [t for t in critical_tables if t not in existing_tables]

            if missing_tables:
                self.log_check(
                    "critical_tables",
                    "failed",
                    f"Missing tables: {', '.join(missing_tables)}",
                    critical=True
                )
                return False

            self.log_check(
                "critical_tables",
                "passed",
                f"All {len(critical_tables)} critical tables exist"
            )
            return True

        except Exception as e:
            self.log_check(
                "critical_tables",
                "failed",
                f"Cannot check tables: {str(e)}",
                critical=True
            )
            return False

    def check_data_counts(self) -> bool:
        """Check critical data exists"""
        try:
            cursor = self.conn.cursor()

            # Check users
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]

            # Check products
            cursor.execute("SELECT COUNT(*) FROM products")
            product_count = cursor.fetchone()[0]

            # Check admin users
            cursor.execute("""
                SELECT COUNT(*) FROM users u
                JOIN user_roles ur ON u.id = ur.user_id
                JOIN roles r ON ur.role_id = r.id
                WHERE r.name = 'Admin'
            """)
            admin_count = cursor.fetchone()[0]

            all_ok = True

            if user_count == 0:
                self.log_check(
                    "users_count",
                    "failed",
                    "No users found in database",
                    critical=True
                )
                all_ok = False
            else:
                self.log_check(
                    "users_count",
                    "passed",
                    f"{user_count} users in database"
                )

            if product_count == 0:
                self.log_check(
                    "products_count",
                    "warning",
                    "No products found in database",
                    critical=False
                )
            else:
                self.log_check(
                    "products_count",
                    "passed",
                    f"{product_count} products in database"
                )

            if admin_count == 0:
                self.log_check(
                    "admin_users",
                    "failed",
                    "No admin users found",
                    critical=True
                )
                all_ok = False
            else:
                self.log_check(
                    "admin_users",
                    "passed",
                    f"{admin_count} admin user(s) configured"
                )

            return all_ok

        except Exception as e:
            self.log_check(
                "data_counts",
                "failed",
                f"Cannot check data: {str(e)}",
                critical=False
            )
            return True

    def check_connection_pool(self) -> bool:
        """Check database connection pool health"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT count(*)
                FROM pg_stat_activity
                WHERE datname = current_database()
            """)
            active_connections = cursor.fetchone()[0]

            cursor.execute("SHOW max_connections")
            max_connections = int(cursor.fetchone()[0])

            usage_percent = (active_connections / max_connections) * 100

            if usage_percent > 90:
                self.log_check(
                    "connection_pool",
                    "failed",
                    f"Connection pool near exhaustion: {active_connections}/{max_connections} ({usage_percent:.1f}%)",
                    critical=True
                )
                return False
            elif usage_percent > 70:
                self.log_check(
                    "connection_pool",
                    "warning",
                    f"High connection usage: {active_connections}/{max_connections} ({usage_percent:.1f}%)",
                    critical=False
                )
                return True
            else:
                self.log_check(
                    "connection_pool",
                    "passed",
                    f"Connection pool healthy: {active_connections}/{max_connections} ({usage_percent:.1f}%)"
                )
                return True

        except Exception as e:
            self.log_check(
                "connection_pool",
                "warning",
                f"Cannot check pool: {str(e)}",
                critical=False
            )
            return True

    def run_all_checks(self) -> Dict[str, Any]:
        """Run all database validation checks"""
        print("🗄️  Orixoon Phase 3: Database Validation\n")

        if not self.connect_database():
            duration = time.time() - self.start_time
            return {
                "phase": "03_database_validator",
                "status": "failed",
                "timestamp": datetime.now().isoformat(),
                "duration": round(duration, 2),
                "summary": {
                    "total_checks": len(self.results),
                    "passed": 0,
                    "failed": len(self.results),
                    "warnings": 0,
                    "critical_failures": self.critical_failures
                },
                "checks": self.results
            }

        # Run all checks
        self.check_alembic_migrations()
        self.check_critical_tables()
        self.check_data_counts()
        self.check_connection_pool()

        if self.conn:
            self.conn.close()

        duration = time.time() - self.start_time

        # Generate report
        passed = sum(1 for r in self.results if r["status"] == "passed")
        failed = sum(1 for r in self.results if r["status"] == "failed")
        warnings = sum(1 for r in self.results if r["status"] == "warning")

        report = {
            "phase": "03_database_validator",
            "status": "passed" if self.critical_failures == 0 else "failed",
            "timestamp": datetime.now().isoformat(),
            "duration": round(duration, 2),
            "summary": {
                "total_checks": len(self.results),
                "passed": passed,
                "failed": failed,
                "warnings": warnings,
                "critical_failures": self.critical_failures
            },
            "checks": self.results
        }

        print(f"\n{'='*60}")
        print(f"Database Validation: {report['status'].upper()}")
        print(f"Duration: {duration:.2f}s")
        print(f"Passed: {passed} | Failed: {failed} | Warnings: {warnings}")
        print(f"Critical Failures: {self.critical_failures}")
        print(f"{'='*60}\n")

        return report


def main():
    """Main entry point"""
    validator = DatabaseValidator()
    report = validator.run_all_checks()

    # Output JSON report
    print(json.dumps(report, indent=2))

    # Exit with appropriate code
    if report["status"] == "failed":
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
