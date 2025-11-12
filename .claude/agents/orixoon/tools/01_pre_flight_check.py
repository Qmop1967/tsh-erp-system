#!/usr/bin/env python3
"""
Orixoon Phase 1: Pre-Flight Checks
Validates environment readiness before deployment
"""

import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Any
import socket
import subprocess
import psycopg2
import redis
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class PreFlightChecker:
    def __init__(self):
        self.results: List[Dict[str, Any]] = []
        self.start_time = time.time()
        self.critical_failures = 0

    def log_check(self, name: str, status: str, message: str, critical: bool = True):
        """Log a check result"""
        result = {
            "name": name,
            "status": status,  # passed, failed, warning
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

    def check_environment_variables(self) -> bool:
        """Check all required environment variables exist"""
        required_vars = [
            "DATABASE_URL",
            "REDIS_URL",
            "SECRET_KEY",
            "ZOHO_CLIENT_ID",
            "ZOHO_CLIENT_SECRET",
            "ZOHO_ORGANIZATION_ID",
        ]

        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)

        if missing_vars:
            self.log_check(
                "environment_variables",
                "failed",
                f"Missing required variables: {', '.join(missing_vars)}",
                critical=True
            )
            return False

        self.log_check(
            "environment_variables",
            "passed",
            f"All {len(required_vars)} required environment variables present"
        )
        return True

    def check_database_connectivity(self) -> bool:
        """Check PostgreSQL database connectivity"""
        try:
            database_url = os.getenv("DATABASE_URL", "postgresql://tsh_admin:TSH@2025Secure!Production@localhost:5432/tsh_erp")
            conn = psycopg2.connect(database_url, connect_timeout=10)
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            cursor.close()
            conn.close()

            self.log_check(
                "database_connectivity",
                "passed",
                f"PostgreSQL connected: {version[:50]}..."
            )
            return True

        except Exception as e:
            self.log_check(
                "database_connectivity",
                "failed",
                f"Cannot connect to database: {str(e)}",
                critical=True
            )
            return False

    def check_redis_connectivity(self) -> bool:
        """Check Redis connectivity"""
        try:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
            r = redis.from_url(redis_url, socket_connect_timeout=10)
            r.ping()
            info = r.info()

            self.log_check(
                "redis_connectivity",
                "passed",
                f"Redis connected: version {info.get('redis_version', 'unknown')}"
            )
            return True

        except Exception as e:
            self.log_check(
                "redis_connectivity",
                "failed",
                f"Cannot connect to Redis: {str(e)}",
                critical=True
            )
            return False

    def check_disk_space(self) -> bool:
        """Check available disk space"""
        try:
            result = subprocess.run(
                ["df", "-h", "/"],
                capture_output=True,
                text=True,
                timeout=10
            )

            lines = result.stdout.strip().split('\n')
            if len(lines) < 2:
                raise Exception("Cannot parse df output")

            # Parse: Filesystem Size Used Avail Use% Mounted on
            parts = lines[1].split()
            available = parts[3]  # e.g., "45G"
            use_percent = parts[4]  # e.g., "34%"

            # Convert to GB
            available_gb = 0
            if 'G' in available:
                available_gb = float(available.replace('G', ''))
            elif 'T' in available:
                available_gb = float(available.replace('T', '')) * 1024
            elif 'M' in available:
                available_gb = float(available.replace('M', '')) / 1024

            if available_gb < 5:
                self.log_check(
                    "disk_space",
                    "failed",
                    f"Insufficient disk space: {available} available (need >5GB)",
                    critical=True
                )
                return False
            elif available_gb < 10:
                self.log_check(
                    "disk_space",
                    "warning",
                    f"Low disk space: {available} available (recommended >10GB)",
                    critical=False
                )
                return True
            else:
                self.log_check(
                    "disk_space",
                    "passed",
                    f"Disk space OK: {available} available ({use_percent} used)"
                )
                return True

        except Exception as e:
            self.log_check(
                "disk_space",
                "failed",
                f"Cannot check disk space: {str(e)}",
                critical=False
            )
            return True  # Non-critical

    def check_memory_available(self) -> bool:
        """Check available memory"""
        try:
            result = subprocess.run(
                ["free", "-m"],
                capture_output=True,
                text=True,
                timeout=10
            )

            lines = result.stdout.strip().split('\n')
            # Parse: Mem: total used free shared buff/cache available
            mem_line = lines[1].split()
            total = int(mem_line[1])
            available = int(mem_line[6])

            available_percent = (available / total) * 100

            if available_percent < 10:
                self.log_check(
                    "memory_available",
                    "failed",
                    f"Critical: Only {available_percent:.1f}% memory available",
                    critical=True
                )
                return False
            elif available_percent < 20:
                self.log_check(
                    "memory_available",
                    "warning",
                    f"Low memory: {available_percent:.1f}% available ({available}MB)",
                    critical=False
                )
                return True
            else:
                self.log_check(
                    "memory_available",
                    "passed",
                    f"Memory OK: {available_percent:.1f}% available ({available}MB)"
                )
                return True

        except Exception as e:
            self.log_check(
                "memory_available",
                "failed",
                f"Cannot check memory: {str(e)}",
                critical=False
            )
            return True  # Non-critical

    def check_ports_available(self) -> bool:
        """Check required ports are available or in use by our services"""
        required_ports = [
            (5432, "PostgreSQL"),
            (6379, "Redis"),
            (8000, "Main API"),
            (8002, "Neurolink"),
            (3000, "TDS Dashboard")
        ]

        all_ok = True
        for port, service in required_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                sock.close()

                if result == 0:
                    # Port is in use - check if it's our service
                    self.log_check(
                        f"port_{port}",
                        "passed",
                        f"Port {port} ({service}) is in use (service running)"
                    )
                else:
                    # Port not in use - might be OK if service not started yet
                    self.log_check(
                        f"port_{port}",
                        "warning",
                        f"Port {port} ({service}) not in use (service not started yet?)",
                        critical=False
                    )

            except Exception as e:
                self.log_check(
                    f"port_{port}",
                    "failed",
                    f"Cannot check port {port}: {str(e)}",
                    critical=False
                )

        return all_ok

    def check_docker_running(self) -> bool:
        """Check if Docker daemon is running"""
        try:
            result = subprocess.run(
                ["docker", "ps"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                container_count = len(lines) - 1  # Minus header

                self.log_check(
                    "docker_daemon",
                    "passed",
                    f"Docker daemon running ({container_count} containers)"
                )
                return True
            else:
                self.log_check(
                    "docker_daemon",
                    "failed",
                    "Docker daemon not running or not accessible",
                    critical=True
                )
                return False

        except Exception as e:
            self.log_check(
                "docker_daemon",
                "failed",
                f"Cannot access Docker: {str(e)}",
                critical=True
            )
            return False

    def check_backup_directory(self) -> bool:
        """Check backup directory is writable"""
        try:
            backup_dir = PROJECT_ROOT / "backups"
            backup_dir.mkdir(exist_ok=True)

            # Test write
            test_file = backup_dir / ".orixoon_test"
            test_file.write_text("test")
            test_file.unlink()

            self.log_check(
                "backup_directory",
                "passed",
                f"Backup directory writable: {backup_dir}"
            )
            return True

        except Exception as e:
            self.log_check(
                "backup_directory",
                "failed",
                f"Backup directory not writable: {str(e)}",
                critical=False
            )
            return True  # Non-critical

    def check_zoho_credentials(self) -> bool:
        """Check Zoho credentials are configured"""
        client_id = os.getenv("ZOHO_CLIENT_ID")
        client_secret = os.getenv("ZOHO_CLIENT_SECRET")
        org_id = os.getenv("ZOHO_ORGANIZATION_ID")

        if not client_id or not client_secret or not org_id:
            self.log_check(
                "zoho_credentials",
                "failed",
                "Zoho credentials not configured",
                critical=True
            )
            return False

        # Check if credentials look valid (not placeholder values)
        if "your_" in client_id.lower() or "your_" in client_secret.lower():
            self.log_check(
                "zoho_credentials",
                "failed",
                "Zoho credentials appear to be placeholders",
                critical=True
            )
            return False

        self.log_check(
            "zoho_credentials",
            "passed",
            f"Zoho credentials configured (org: {org_id})"
        )
        return True

    def run_all_checks(self) -> Dict[str, Any]:
        """Run all pre-flight checks"""
        print("🚀 Orixoon Phase 1: Pre-Flight Checks\n")

        # Load environment variables from .env.production if exists
        env_file = PROJECT_ROOT / ".env.production"
        if env_file.exists():
            print(f"Loading environment from: {env_file}\n")
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ.setdefault(key, value)

        # Run all checks
        self.check_environment_variables()
        self.check_database_connectivity()
        self.check_redis_connectivity()
        self.check_disk_space()
        self.check_memory_available()
        self.check_ports_available()
        self.check_docker_running()
        self.check_backup_directory()
        self.check_zoho_credentials()

        duration = time.time() - self.start_time

        # Generate report
        passed = sum(1 for r in self.results if r["status"] == "passed")
        failed = sum(1 for r in self.results if r["status"] == "failed")
        warnings = sum(1 for r in self.results if r["status"] == "warning")

        report = {
            "phase": "01_pre_flight_check",
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
        print(f"Pre-Flight Checks: {report['status'].upper()}")
        print(f"Duration: {duration:.2f}s")
        print(f"Passed: {passed} | Failed: {failed} | Warnings: {warnings}")
        print(f"Critical Failures: {self.critical_failures}")
        print(f"{'='*60}\n")

        return report


def main():
    """Main entry point"""
    checker = PreFlightChecker()
    report = checker.run_all_checks()

    # Output JSON report
    print(json.dumps(report, indent=2))

    # Exit with appropriate code
    if report["status"] == "failed":
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
