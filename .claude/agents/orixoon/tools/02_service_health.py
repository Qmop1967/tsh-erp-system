#!/usr/bin/env python3
"""
Orixoon Phase 2: Service Health Checks
Verifies all services are running and healthy
"""

import json
import os
import sys
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import requests

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class ServiceHealthChecker:
    def __init__(self):
        self.results: List[Dict[str, Any]] = []
        self.start_time = time.time()
        self.critical_failures = 0
        self.timeout = 10

    def log_check(self, name: str, status: str, message: str, critical: bool = True, response_time: Optional[float] = None):
        """Log a check result"""
        result = {
            "name": name,
            "status": status,  # passed, failed, warning
            "message": message,
            "critical": critical,
            "timestamp": datetime.now().isoformat()
        }

        if response_time is not None:
            result["response_time_ms"] = round(response_time * 1000, 2)

        self.results.append(result)

        if status == "failed" and critical:
            self.critical_failures += 1
            print(f"❌ {name}: {message}", file=sys.stderr)
        elif status == "failed":
            print(f"⚠️  {name}: {message}", file=sys.stderr)
        else:
            print(f"✓ {name}: {message}")

    def check_docker_containers(self) -> bool:
        """Check Docker containers are running"""
        try:
            result = subprocess.run(
                ["docker", "ps", "--format", "{{.Names}}\t{{.Status}}"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                self.log_check(
                    "docker_containers",
                    "failed",
                    "Cannot list Docker containers",
                    critical=True
                )
                return False

            containers = {}
            for line in result.stdout.strip().split('\n'):
                if '\t' in line:
                    name, status = line.split('\t', 1)
                    containers[name] = status

            required_containers = [
                "tsh_postgres",
                "redis",
                "app",
                "neurolink"
            ]

            missing_containers = []
            unhealthy_containers = []

            for container in required_containers:
                if container not in containers:
                    missing_containers.append(container)
                elif "Up" not in containers[container]:
                    unhealthy_containers.append(f"{container} ({containers[container]})")

            if missing_containers:
                self.log_check(
                    "docker_containers",
                    "failed",
                    f"Missing containers: {', '.join(missing_containers)}",
                    critical=True
                )
                return False

            if unhealthy_containers:
                self.log_check(
                    "docker_containers",
                    "failed",
                    f"Unhealthy containers: {', '.join(unhealthy_containers)}",
                    critical=True
                )
                return False

            self.log_check(
                "docker_containers",
                "passed",
                f"All {len(required_containers)} required containers running"
            )
            return True

        except Exception as e:
            self.log_check(
                "docker_containers",
                "failed",
                f"Error checking containers: {str(e)}",
                critical=True
            )
            return False

    def check_http_endpoint(self, name: str, url: str, critical: bool = True, expected_status: int = 200) -> bool:
        """Check an HTTP endpoint"""
        try:
            start = time.time()
            response = requests.get(url, timeout=self.timeout, verify=False)
            response_time = time.time() - start

            if response.status_code == expected_status:
                self.log_check(
                    name,
                    "passed",
                    f"Endpoint healthy ({response.status_code}) - {url}",
                    critical=critical,
                    response_time=response_time
                )
                return True
            else:
                self.log_check(
                    name,
                    "failed",
                    f"Unexpected status {response.status_code} (expected {expected_status}) - {url}",
                    critical=critical,
                    response_time=response_time
                )
                return False

        except requests.exceptions.Timeout:
            self.log_check(
                name,
                "failed",
                f"Timeout after {self.timeout}s - {url}",
                critical=critical
            )
            return False
        except Exception as e:
            self.log_check(
                name,
                "failed",
                f"Error: {str(e)} - {url}",
                critical=critical
            )
            return False

    def check_postgres_health(self) -> bool:
        """Check PostgreSQL health"""
        try:
            result = subprocess.run(
                ["pg_isready", "-h", "localhost", "-p", "5432"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                self.log_check(
                    "postgresql_health",
                    "passed",
                    result.stdout.strip()
                )
                return True
            else:
                self.log_check(
                    "postgresql_health",
                    "failed",
                    result.stderr.strip() or "PostgreSQL not ready",
                    critical=True
                )
                return False

        except Exception as e:
            self.log_check(
                "postgresql_health",
                "failed",
                f"Cannot check PostgreSQL: {str(e)}",
                critical=True
            )
            return False

    def check_redis_health(self) -> bool:
        """Check Redis health"""
        try:
            result = subprocess.run(
                ["redis-cli", "-h", "localhost", "-p", "6379", "ping"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0 and "PONG" in result.stdout:
                self.log_check(
                    "redis_health",
                    "passed",
                    "Redis responding to PING"
                )
                return True
            else:
                self.log_check(
                    "redis_health",
                    "failed",
                    "Redis not responding",
                    critical=True
                )
                return False

        except Exception as e:
            self.log_check(
                "redis_health",
                "failed",
                f"Cannot check Redis: {str(e)}",
                critical=True
            )
            return False

    def check_background_workers(self) -> bool:
        """Check background workers are running"""
        try:
            # Check for Uvicorn workers
            result = subprocess.run(
                ["ps", "aux"],
                capture_output=True,
                text=True,
                timeout=10
            )

            uvicorn_count = result.stdout.count("uvicorn")
            tds_scheduler = "tds_auto_sync_scheduler" in result.stdout

            all_ok = True

            if uvicorn_count >= 1:
                self.log_check(
                    "uvicorn_workers",
                    "passed",
                    f"{uvicorn_count} Uvicorn worker(s) running"
                )
            else:
                self.log_check(
                    "uvicorn_workers",
                    "failed",
                    "No Uvicorn workers found",
                    critical=True
                )
                all_ok = False

            if tds_scheduler:
                self.log_check(
                    "tds_scheduler",
                    "passed",
                    "TDS auto-sync scheduler running"
                )
            else:
                self.log_check(
                    "tds_scheduler",
                    "failed",
                    "TDS auto-sync scheduler not found",
                    critical=True
                )
                all_ok = False

            return all_ok

        except Exception as e:
            self.log_check(
                "background_workers",
                "failed",
                f"Cannot check workers: {str(e)}",
                critical=False
            )
            return True  # Non-critical

    def check_recent_logs(self) -> bool:
        """Check for critical errors in recent logs"""
        try:
            # Check Docker logs for errors in last 5 minutes
            result = subprocess.run(
                ["docker", "logs", "--since", "5m", "app"],
                capture_output=True,
                text=True,
                timeout=10
            )

            logs = result.stdout + result.stderr
            error_count = logs.lower().count("error")
            critical_count = logs.lower().count("critical")
            exception_count = logs.lower().count("exception")

            total_issues = error_count + critical_count + exception_count

            if total_issues > 50:
                self.log_check(
                    "recent_logs",
                    "failed",
                    f"High error rate: {total_issues} errors/exceptions in last 5 minutes",
                    critical=True
                )
                return False
            elif total_issues > 10:
                self.log_check(
                    "recent_logs",
                    "warning",
                    f"Elevated error rate: {total_issues} errors/exceptions in last 5 minutes",
                    critical=False
                )
                return True
            else:
                self.log_check(
                    "recent_logs",
                    "passed",
                    f"Log health good: {total_issues} errors/exceptions in last 5 minutes"
                )
                return True

        except Exception as e:
            self.log_check(
                "recent_logs",
                "warning",
                f"Cannot check logs: {str(e)}",
                critical=False
            )
            return True  # Non-critical

    def check_authentication(self) -> bool:
        """Test authentication flow"""
        try:
            # Try to login with test credentials
            base_url = os.getenv("BASE_URL", "http://localhost:8000")

            # First, try health endpoint
            health_url = f"{base_url}/health"
            start = time.time()
            response = requests.get(health_url, timeout=10)
            response_time = time.time() - start

            if response.status_code != 200:
                self.log_check(
                    "authentication_endpoint",
                    "failed",
                    f"Health endpoint failed ({response.status_code})",
                    critical=True
                )
                return False

            # Try login endpoint (without credentials - just check it's accessible)
            login_url = f"{base_url}/api/auth/login"
            response = requests.post(
                login_url,
                json={"username": "test", "password": "test"},
                timeout=10
            )

            # We expect 401 or 422 (validation error) - endpoint is accessible
            if response.status_code in [401, 422]:
                self.log_check(
                    "authentication_endpoint",
                    "passed",
                    f"Auth endpoint accessible ({response.status_code})"
                )
                return True
            elif response.status_code == 200:
                # Somehow test user exists? That's OK too
                self.log_check(
                    "authentication_endpoint",
                    "passed",
                    "Auth endpoint accessible and responding"
                )
                return True
            else:
                self.log_check(
                    "authentication_endpoint",
                    "failed",
                    f"Unexpected auth response ({response.status_code})",
                    critical=True
                )
                return False

        except Exception as e:
            self.log_check(
                "authentication_endpoint",
                "failed",
                f"Auth endpoint error: {str(e)}",
                critical=True
            )
            return False

    def run_all_checks(self) -> Dict[str, Any]:
        """Run all service health checks"""
        print("🏥 Orixoon Phase 2: Service Health Checks\n")

        # Check Docker containers first
        self.check_docker_containers()

        # Check core services
        self.check_postgres_health()
        self.check_redis_health()

        # Check HTTP endpoints
        base_url = os.getenv("BASE_URL", "http://localhost:8000")
        public_url = os.getenv("PUBLIC_URL", "https://erp.tsh.sale")

        self.check_http_endpoint("main_api_health_local", f"{base_url}/health", critical=True)
        self.check_http_endpoint("main_api_health_public", f"{public_url}/health", critical=True)
        self.check_http_endpoint("neurolink_health", "http://localhost:8002/health", critical=True)
        self.check_http_endpoint("tds_dashboard", "http://localhost:3000", critical=False)

        # Check authentication
        self.check_authentication()

        # Check background workers
        self.check_background_workers()

        # Check recent logs
        self.check_recent_logs()

        duration = time.time() - self.start_time

        # Generate report
        passed = sum(1 for r in self.results if r["status"] == "passed")
        failed = sum(1 for r in self.results if r["status"] == "failed")
        warnings = sum(1 for r in self.results if r["status"] == "warning")

        report = {
            "phase": "02_service_health",
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
        print(f"Service Health: {report['status'].upper()}")
        print(f"Duration: {duration:.2f}s")
        print(f"Passed: {passed} | Failed: {failed} | Warnings: {warnings}")
        print(f"Critical Failures: {self.critical_failures}")
        print(f"{'='*60}\n")

        return report


def main():
    """Main entry point"""
    # Disable SSL warnings for self-signed certs
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    checker = ServiceHealthChecker()
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
