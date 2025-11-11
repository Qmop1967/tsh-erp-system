#!/usr/bin/env python3
"""
Service Dependency Graph Validator
===================================

Validates that all TSH ERP services are properly configured and connected.

Usage:
    python tests/infrastructure/validate_dependencies.py
    python tests/infrastructure/validate_dependencies.py --env production
    python tests/infrastructure/validate_dependencies.py --service app
"""

import json
import os
import sys
import time
import socket
import requests
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass, field
from enum import Enum


class ValidationStatus(Enum):
    """Validation status"""
    PASS = "✅ PASS"
    FAIL = "❌ FAIL"
    WARN = "⚠️  WARN"
    SKIP = "⏭️  SKIP"


@dataclass
class ValidationResult:
    """Result of a validation check"""
    service: str
    check: str
    status: ValidationStatus
    message: str
    details: Dict = field(default_factory=dict)


class ServiceDependencyValidator:
    """Validates service dependencies"""

    def __init__(self, manifest_path: str = None, environment: str = "development"):
        self.environment = environment
        self.manifest_path = manifest_path or self._get_default_manifest_path()
        self.manifest = self._load_manifest()
        self.results: List[ValidationResult] = []

    def _get_default_manifest_path(self) -> str:
        """Get default manifest path"""
        return os.path.join(
            Path(__file__).parent,
            "dependency_graph.json"
        )

    def _load_manifest(self) -> Dict:
        """Load dependency graph manifest"""
        try:
            with open(self.manifest_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Manifest file not found: {self.manifest_path}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in manifest: {e}")
            sys.exit(1)

    def validate_all(self, service_name: str = None) -> bool:
        """
        Validate all services or a specific service

        Args:
            service_name: Optional service name to validate only that service

        Returns:
            True if all validations pass, False otherwise
        """
        print("\n" + "=" * 70)
        print(f"🔍 TSH ERP SERVICE DEPENDENCY VALIDATION")
        print(f"Environment: {self.environment}")
        print(f"Manifest Version: {self.manifest.get('version', 'unknown')}")
        print("=" * 70 + "\n")

        services = self.manifest.get("services", [])

        if service_name:
            services = [s for s in services if s["name"] == service_name]
            if not services:
                print(f"❌ Service not found: {service_name}")
                return False

        # Validate each service
        for service in services:
            self._validate_service(service)

        # Print summary
        self._print_summary()

        # Return overall success
        failed = [r for r in self.results if r.status == ValidationStatus.FAIL]
        return len(failed) == 0

    def _validate_service(self, service: Dict):
        """Validate a single service"""
        service_name = service["name"]
        print(f"\n{'─' * 70}")
        print(f"📦 Service: {service_name} ({service.get('description', 'No description')})")
        print(f"{'─' * 70}")

        # 1. Check environment variables
        self._check_env_vars(service)

        # 2. Check dependencies
        self._check_dependencies(service)

        # 3. Check network connectivity
        self._check_network(service)

        # 4. Check health endpoint
        self._check_health(service)

        # 5. Check API endpoints
        self._check_api_endpoints(service)

    def _check_env_vars(self, service: Dict):
        """Check if required environment variables are set"""
        service_name = service["name"]
        required_vars = service.get("required_env_vars", [])
        optional_vars = service.get("optional_env_vars", [])

        # Check required vars
        for var in required_vars:
            if os.getenv(var):
                self.results.append(ValidationResult(
                    service=service_name,
                    check="env_var",
                    status=ValidationStatus.PASS,
                    message=f"✓ {var} is set"
                ))
            else:
                self.results.append(ValidationResult(
                    service=service_name,
                    check="env_var",
                    status=ValidationStatus.FAIL,
                    message=f"✗ {var} is NOT set (required)"
                ))

        # Check optional vars (warnings only)
        for var in optional_vars:
            if not os.getenv(var):
                self.results.append(ValidationResult(
                    service=service_name,
                    check="env_var",
                    status=ValidationStatus.WARN,
                    message=f"⚠ {var} is NOT set (optional)"
                ))

    def _check_dependencies(self, service: Dict):
        """Check if service dependencies are available"""
        service_name = service["name"]
        depends_on = service.get("depends_on", [])

        for dep_name in depends_on:
            # Find dependency in manifest
            dep_service = next(
                (s for s in self.manifest["services"] if s["name"] == dep_name),
                None
            )

            if not dep_service:
                self.results.append(ValidationResult(
                    service=service_name,
                    check="dependency",
                    status=ValidationStatus.FAIL,
                    message=f"✗ Dependency '{dep_name}' not found in manifest"
                ))
                continue

            # Check if dependency is reachable
            port = dep_service.get("port")
            if isinstance(port, list):
                port = port[0]

            host = os.getenv(f"{dep_name.upper()}_HOST", "localhost")

            if self._check_port(host, port):
                self.results.append(ValidationResult(
                    service=service_name,
                    check="dependency",
                    status=ValidationStatus.PASS,
                    message=f"✓ Dependency '{dep_name}' is reachable at {host}:{port}"
                ))
            else:
                self.results.append(ValidationResult(
                    service=service_name,
                    check="dependency",
                    status=ValidationStatus.FAIL,
                    message=f"✗ Dependency '{dep_name}' is NOT reachable at {host}:{port}"
                ))

    def _check_network(self, service: Dict):
        """Check network connectivity to service"""
        service_name = service["name"]
        port = service.get("port")

        # Skip if no port defined
        if not port:
            return

        if isinstance(port, list):
            ports = port
        else:
            ports = [port]

        host = os.getenv(f"{service_name.upper()}_HOST", "localhost")

        for p in ports:
            if self._check_port(host, p):
                self.results.append(ValidationResult(
                    service=service_name,
                    check="network",
                    status=ValidationStatus.PASS,
                    message=f"✓ Port {p} is open on {host}"
                ))
            else:
                # Only fail for critical services
                status = ValidationStatus.FAIL if service.get("critical", True) else ValidationStatus.WARN
                self.results.append(ValidationResult(
                    service=service_name,
                    check="network",
                    status=status,
                    message=f"✗ Port {p} is NOT open on {host}"
                ))

    def _check_health(self, service: Dict):
        """Check service health endpoint"""
        service_name = service["name"]
        health_endpoint = service.get("health_endpoint")

        if not health_endpoint:
            # Check if there's a command instead
            health_command = service.get("health_check_command")
            if health_command:
                self._check_health_command(service, health_command)
            return

        port = service.get("port")
        if isinstance(port, list):
            port = port[0]

        protocol = service.get("protocol", "http")
        host = os.getenv(f"{service_name.upper()}_HOST", "localhost")
        url = f"{protocol}://{host}:{port}{health_endpoint}"

        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                self.results.append(ValidationResult(
                    service=service_name,
                    check="health",
                    status=ValidationStatus.PASS,
                    message=f"✓ Health check passed: {url}"
                ))
            else:
                self.results.append(ValidationResult(
                    service=service_name,
                    check="health",
                    status=ValidationStatus.FAIL,
                    message=f"✗ Health check failed: {url} (status: {response.status_code})"
                ))
        except requests.exceptions.RequestException as e:
            status = ValidationStatus.FAIL if service.get("critical", True) else ValidationStatus.WARN
            self.results.append(ValidationResult(
                service=service_name,
                check="health",
                status=status,
                message=f"✗ Health check failed: {url} ({str(e)})"
            ))

    def _check_health_command(self, service: Dict, command: str):
        """Check health using a command"""
        service_name = service["name"]

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                self.results.append(ValidationResult(
                    service=service_name,
                    check="health",
                    status=ValidationStatus.PASS,
                    message=f"✓ Health check command passed: {command}"
                ))
            else:
                self.results.append(ValidationResult(
                    service=service_name,
                    check="health",
                    status=ValidationStatus.FAIL,
                    message=f"✗ Health check command failed: {command}"
                ))
        except Exception as e:
            self.results.append(ValidationResult(
                service=service_name,
                check="health",
                status=ValidationStatus.FAIL,
                message=f"✗ Health check command error: {str(e)}"
            ))

    def _check_api_endpoints(self, service: Dict):
        """Check API endpoints"""
        service_name = service["name"]

        # Find endpoints in manifest
        api_endpoints = next(
            (item["endpoints"] for item in self.manifest.get("api_endpoints", [])
             if item["service"] == service_name),
            []
        )

        if not api_endpoints:
            return

        port = service.get("port")
        if isinstance(port, list):
            port = port[0]

        protocol = service.get("protocol", "http")
        host = os.getenv(f"{service_name.upper()}_HOST", "localhost")

        for endpoint in api_endpoints:
            path = endpoint["path"]
            method = endpoint["method"]
            expected_status = endpoint.get("expected_status", 200)
            timeout = endpoint.get("timeout", 5)

            if isinstance(expected_status, list):
                expected_statuses = expected_status
            else:
                expected_statuses = [expected_status]

            url = f"{protocol}://{host}:{port}{path}"

            try:
                if method == "GET":
                    response = requests.get(url, timeout=timeout)
                elif method == "POST":
                    response = requests.post(url, json={}, timeout=timeout)
                else:
                    continue

                if response.status_code in expected_statuses:
                    self.results.append(ValidationResult(
                        service=service_name,
                        check="api_endpoint",
                        status=ValidationStatus.PASS,
                        message=f"✓ {method} {path} returned {response.status_code}"
                    ))
                else:
                    self.results.append(ValidationResult(
                        service=service_name,
                        check="api_endpoint",
                        status=ValidationStatus.WARN,
                        message=f"⚠ {method} {path} returned {response.status_code} (expected {expected_statuses})"
                    ))
            except requests.exceptions.RequestException as e:
                self.results.append(ValidationResult(
                    service=service_name,
                    check="api_endpoint",
                    status=ValidationStatus.WARN,
                    message=f"⚠ {method} {path} failed: {str(e)}"
                ))

    def _check_port(self, host: str, port: int, timeout: int = 3) -> bool:
        """Check if a port is open"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception:
            return False

    def _print_summary(self):
        """Print validation summary"""
        print("\n" + "=" * 70)
        print("📊 VALIDATION SUMMARY")
        print("=" * 70)

        # Count by status
        passed = sum(1 for r in self.results if r.status == ValidationStatus.PASS)
        failed = sum(1 for r in self.results if r.status == ValidationStatus.FAIL)
        warnings = sum(1 for r in self.results if r.status == ValidationStatus.WARN)
        skipped = sum(1 for r in self.results if r.status == ValidationStatus.SKIP)

        total = len(self.results)

        print(f"\nTotal Checks: {total}")
        print(f"  ✅ Passed:   {passed}")
        print(f"  ❌ Failed:   {failed}")
        print(f"  ⚠️  Warnings: {warnings}")
        print(f"  ⏭️  Skipped:  {skipped}")

        # Print failed checks
        if failed > 0:
            print(f"\n{'─' * 70}")
            print("❌ FAILED CHECKS:")
            print(f"{'─' * 70}")
            for result in self.results:
                if result.status == ValidationStatus.FAIL:
                    print(f"  [{result.service}] {result.message}")

        # Print warnings
        if warnings > 0:
            print(f"\n{'─' * 70}")
            print("⚠️  WARNINGS:")
            print(f"{'─' * 70}")
            for result in self.results:
                if result.status == ValidationStatus.WARN:
                    print(f"  [{result.service}] {result.message}")

        print("\n" + "=" * 70)

        if failed > 0:
            print("❌ VALIDATION FAILED")
        else:
            print("✅ ALL VALIDATIONS PASSED")

        print("=" * 70 + "\n")

    def export_results(self, output_file: str):
        """Export results to JSON file"""
        results_data = [
            {
                "service": r.service,
                "check": r.check,
                "status": r.status.name,
                "message": r.message,
                "details": r.details
            }
            for r in self.results
        ]

        with open(output_file, 'w') as f:
            json.dump(results_data, f, indent=2)

        print(f"📄 Results exported to: {output_file}")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate TSH ERP service dependencies"
    )
    parser.add_argument(
        "--env",
        choices=["development", "staging", "production"],
        default="development",
        help="Environment to validate"
    )
    parser.add_argument(
        "--service",
        help="Validate only a specific service"
    )
    parser.add_argument(
        "--manifest",
        help="Path to dependency graph manifest JSON file"
    )
    parser.add_argument(
        "--export",
        help="Export results to JSON file"
    )

    args = parser.parse_args()

    # Create validator
    validator = ServiceDependencyValidator(
        manifest_path=args.manifest,
        environment=args.env
    )

    # Run validation
    success = validator.validate_all(service_name=args.service)

    # Export results if requested
    if args.export:
        validator.export_results(args.export)

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
