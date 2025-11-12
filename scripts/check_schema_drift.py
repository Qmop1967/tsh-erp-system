#!/usr/bin/env python3
"""
Database Schema Drift Checker
==============================

Checks for schema drift between SQLAlchemy models and actual database.

Usage:
    # Check production database
    python scripts/check_schema_drift.py --env production

    # Check staging database
    python scripts/check_schema_drift.py --env staging

    # Generate migration script
    python scripts/check_schema_drift.py --env production --generate-migration

    # Export report
    python scripts/check_schema_drift.py --env production --export drift-report.json
"""

import os
import sys
import json
import argparse
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass, field
from enum import Enum


class DriftSeverity(Enum):
    """Drift severity levels"""
    NONE = "none"
    MINOR = "minor"
    MAJOR = "major"
    CRITICAL = "critical"


@dataclass
class DriftReport:
    """Schema drift report"""
    severity: DriftSeverity
    drift_detected: bool
    total_changes: int = 0
    critical_changes: int = 0
    major_changes: int = 0
    minor_changes: int = 0
    sql_diff: str = ""
    recommendations: List[str] = field(default_factory=list)


class SchemaDriftChecker:
    """Check for schema drift between models and database"""

    # Patterns for classifying drift severity
    CRITICAL_PATTERNS = [
        r'DROP TABLE',
        r'DROP COLUMN',
        r'ALTER COLUMN .* DROP NOT NULL',
        r'DROP CONSTRAINT .* FOREIGN KEY',
    ]

    MAJOR_PATTERNS = [
        r'ALTER TABLE .* ADD COLUMN .* NOT NULL',
        r'ALTER COLUMN .* TYPE',
        r'ADD CONSTRAINT .* FOREIGN KEY',
        r'DROP INDEX',
        r'ALTER TABLE .* ALTER COLUMN .* SET NOT NULL',
    ]

    MINOR_PATTERNS = [
        r'ALTER TABLE .* ADD COLUMN',
        r'CREATE TABLE',
        r'CREATE INDEX',
        r'ALTER TABLE .* DROP CONSTRAINT .* CHECK',
        r'COMMENT ON',
    ]

    def __init__(self, environment: str = "production"):
        self.environment = environment
        self.remote_db_url = self._get_remote_db_url()
        self.local_db_url = None

    def _get_remote_db_url(self) -> str:
        """Get remote database URL based on environment"""
        if self.environment == "production":
            host = os.getenv("PROD_DB_HOST", "167.71.39.50")
            port = os.getenv("PROD_DB_PORT", "5432")
            db = os.getenv("PROD_DB_NAME", "tsh_erp_production")
            user = os.getenv("PROD_DB_USER", "tsh_app_user")
            password = os.getenv("PROD_DB_PASSWORD")
        elif self.environment == "staging":
            host = os.getenv("STAGING_DB_HOST", "167.71.58.65")
            port = os.getenv("STAGING_DB_PORT", "5432")
            db = os.getenv("STAGING_DB_NAME", "tsh_erp_staging")
            user = os.getenv("STAGING_DB_USER", "tsh_app_user")
            password = os.getenv("STAGING_DB_PASSWORD")
        else:
            raise ValueError(f"Unknown environment: {self.environment}")

        if not password:
            print(f"❌ Database password not set for {self.environment}")
            print(f"   Set {self.environment.upper()}_DB_PASSWORD environment variable")
            sys.exit(1)

        return f"postgresql://{user}:{password}@{host}:{port}/{db}"

    def _create_local_schema(self) -> str:
        """Create temporary database with local schema"""
        print("📦 Creating local schema from SQLAlchemy models...")

        # Create temporary database
        with tempfile.NamedTemporaryFile(mode='w', suffix='.db', delete=False) as f:
            temp_db = f.name

        local_db_url = f"sqlite:///{temp_db}"

        try:
            # Import and create schema
            from app.db.database import Base, engine

            # Create all tables
            Base.metadata.create_all(bind=engine)

            print("✅ Local schema created successfully")
            return local_db_url

        except Exception as e:
            print(f"❌ Failed to create local schema: {e}")
            sys.exit(1)

    def _test_remote_connection(self) -> bool:
        """Test connection to remote database"""
        print(f"🔌 Testing connection to {self.environment} database...")

        try:
            # Parse URL to get connection details
            import re
            match = re.match(r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', self.remote_db_url)
            if not match:
                print("❌ Invalid database URL format")
                return False

            user, password, host, port, db = match.groups()

            # Test connection with psql
            result = subprocess.run(
                ['psql', '-h', host, '-p', port, '-U', user, '-d', db, '-c', 'SELECT version();'],
                env={**os.environ, 'PGPASSWORD': password},
                capture_output=True,
                timeout=10
            )

            if result.returncode == 0:
                print(f"✅ Connected to {self.environment} database successfully")
                return True
            else:
                print(f"❌ Failed to connect to {self.environment} database")
                print(f"   Error: {result.stderr.decode()}")
                return False

        except FileNotFoundError:
            print("❌ psql command not found. Install PostgreSQL client tools.")
            return False
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return False

    def _run_migra(self) -> Tuple[bool, str]:
        """Run migra to compare schemas"""
        print("🔍 Comparing schemas with migra...")

        try:
            result = subprocess.run(
                ['migra', '--unsafe', self.remote_db_url, self.local_db_url],
                capture_output=True,
                text=True,
                timeout=30
            )

            sql_diff = result.stdout.strip()

            if sql_diff:
                print("⚠️  Schema drift detected!")
                return True, sql_diff
            else:
                print("✅ No schema drift detected")
                return False, ""

        except FileNotFoundError:
            print("❌ migra command not found. Install with: pip install migra")
            sys.exit(1)
        except subprocess.TimeoutExpired:
            print("❌ migra command timed out")
            sys.exit(1)
        except Exception as e:
            print(f"❌ migra failed: {e}")
            sys.exit(1)

    def _analyze_drift(self, sql_diff: str) -> DriftReport:
        """Analyze drift severity and generate report"""
        import re

        report = DriftReport(
            severity=DriftSeverity.NONE,
            drift_detected=bool(sql_diff),
            sql_diff=sql_diff
        )

        if not sql_diff:
            report.recommendations.append("No action needed - schemas are synchronized")
            return report

        # Count critical changes
        for pattern in self.CRITICAL_PATTERNS:
            matches = re.findall(pattern, sql_diff, re.IGNORECASE)
            report.critical_changes += len(matches)

        # Count major changes
        for pattern in self.MAJOR_PATTERNS:
            matches = re.findall(pattern, sql_diff, re.IGNORECASE)
            report.major_changes += len(matches)

        # Count minor changes
        for pattern in self.MINOR_PATTERNS:
            matches = re.findall(pattern, sql_diff, re.IGNORECASE)
            report.minor_changes += len(matches)

        report.total_changes = (
            report.critical_changes + report.major_changes + report.minor_changes
        )

        # Determine severity
        if report.critical_changes > 0:
            report.severity = DriftSeverity.CRITICAL
            report.recommendations.extend([
                "🔴 CRITICAL: Review all DROP operations carefully",
                "Create database backup before applying changes",
                "Generate and review Alembic migration",
                "Test migration on staging environment first",
                "Schedule maintenance window for production",
            ])
        elif report.major_changes > 0:
            report.severity = DriftSeverity.MAJOR
            report.recommendations.extend([
                "🟠 MAJOR: Review schema changes",
                "Generate Alembic migration",
                "Test on staging environment",
                "Deploy during low-traffic period",
            ])
        elif report.minor_changes > 0:
            report.severity = DriftSeverity.MINOR
            report.recommendations.extend([
                "🟡 MINOR: Review changes at convenience",
                "Generate migration when ready",
                "Can be deployed with next regular release",
            ])

        return report

    def _print_report(self, report: DriftReport):
        """Print drift report to console"""
        print("\n" + "=" * 70)
        print("📊 SCHEMA DRIFT REPORT")
        print("=" * 70)
        print(f"\nEnvironment: {self.environment}")
        print(f"Drift Detected: {'Yes' if report.drift_detected else 'No'}")
        print(f"Severity: {report.severity.value.upper()}")

        if report.drift_detected:
            print("\nChange Breakdown:")
            print(f"  🔴 Critical: {report.critical_changes}")
            print(f"  🟠 Major:    {report.major_changes}")
            print(f"  🟡 Minor:    {report.minor_changes}")
            print(f"  📊 Total:    {report.total_changes}")

            print("\n" + "─" * 70)
            print("SQL Differences:")
            print("─" * 70)
            print(report.sql_diff)

            print("\n" + "─" * 70)
            print("Recommendations:")
            print("─" * 70)
            for rec in report.recommendations:
                print(f"  • {rec}")

        print("\n" + "=" * 70)

    def _export_report(self, report: DriftReport, output_file: str):
        """Export report to JSON file"""
        report_data = {
            "environment": self.environment,
            "drift_detected": report.drift_detected,
            "severity": report.severity.value,
            "changes": {
                "critical": report.critical_changes,
                "major": report.major_changes,
                "minor": report.minor_changes,
                "total": report.total_changes,
            },
            "sql_diff": report.sql_diff,
            "recommendations": report.recommendations,
        }

        with open(output_file, 'w') as f:
            json.dump(report_data, f, indent=2)

        print(f"📄 Report exported to: {output_file}")

    def _generate_migration(self, report: DriftReport):
        """Generate Alembic migration from drift"""
        if not report.drift_detected:
            print("ℹ️  No drift detected - no migration needed")
            return

        print("\n📝 Generating Alembic migration...")

        try:
            # Generate migration
            result = subprocess.run(
                ['alembic', 'revision', '--autogenerate', '-m', f'Fix schema drift on {self.environment}'],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                print("✅ Migration generated successfully")
                print(result.stdout)
            else:
                print("❌ Failed to generate migration")
                print(result.stderr)

        except FileNotFoundError:
            print("❌ alembic command not found. Install with: pip install alembic")
        except Exception as e:
            print(f"❌ Migration generation failed: {e}")

    def check(
        self,
        generate_migration: bool = False,
        export_file: str = None
    ) -> DriftReport:
        """
        Check for schema drift

        Args:
            generate_migration: Generate Alembic migration if drift detected
            export_file: Export report to JSON file

        Returns:
            DriftReport object
        """
        # Test remote connection
        if not self._test_remote_connection():
            sys.exit(1)

        # Create local schema
        self.local_db_url = self._create_local_schema()

        # Run migra
        drift_detected, sql_diff = self._run_migra()

        # Analyze drift
        report = self._analyze_drift(sql_diff)

        # Print report
        self._print_report(report)

        # Export if requested
        if export_file:
            self._export_report(report, export_file)

        # Generate migration if requested
        if generate_migration and drift_detected:
            self._generate_migration(report)

        return report


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Check for database schema drift"
    )
    parser.add_argument(
        "--env",
        choices=["staging", "production"],
        default="production",
        help="Environment to check"
    )
    parser.add_argument(
        "--generate-migration",
        action="store_true",
        help="Generate Alembic migration if drift detected"
    )
    parser.add_argument(
        "--export",
        help="Export report to JSON file"
    )

    args = parser.parse_args()

    # Create checker
    checker = SchemaDriftChecker(environment=args.env)

    # Run check
    report = checker.check(
        generate_migration=args.generate_migration,
        export_file=args.export
    )

    # Exit with appropriate code
    if report.severity == DriftSeverity.CRITICAL:
        sys.exit(2)  # Critical drift
    elif report.severity == DriftSeverity.MAJOR:
        sys.exit(1)  # Major drift
    else:
        sys.exit(0)  # No drift or minor drift


if __name__ == "__main__":
    main()
