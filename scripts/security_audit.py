#!/usr/bin/env python3
"""
Comprehensive Security Audit Script
Scans the entire TSH ERP codebase for security vulnerabilities
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict

class SecurityAuditor:
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.app_path = self.base_path / "app"
        self.routers_path = self.app_path / "routers"

        # Results storage
        self.results = {
            "authentication": {
                "total_endpoints": 0,
                "authenticated_endpoints": 0,
                "public_endpoints": [],
                "missing_auth": []
            },
            "authorization": {
                "rbac_coverage": {
                    "total_protected": 0,
                    "missing_rbac": []
                },
                "abac_patterns": [],
                "rls_coverage": {
                    "total_using_rls": 0,
                    "missing_rls": []
                }
            },
            "sql_injection": {
                "f_string_queries": [],
                "raw_sql": [],
                "vulnerable_files": []
            },
            "sensitive_data": {
                "hardcoded_secrets": [],
                "credentials_in_code": [],
                "api_keys": []
            },
            "files_scanned": 0,
            "severity_counts": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0
            }
        }

    def scan_endpoint_authentication(self):
        """Scan all router files for authentication dependencies"""
        print("🔍 Scanning endpoint authentication...")

        # Authentication patterns to look for
        auth_patterns = [
            r'Depends\(get_current_user\)',
            r'Depends\(get_current_user_async\)',
            r'Depends\(get_current_user_with_rls\)',
            r'current_user:\s*User\s*=\s*Depends'
        ]

        # Public endpoint patterns (should be minimal)
        public_patterns = [
            r'@router\.(get|post|put|delete|patch)\(["\']/(health|docs|openapi|login|register)',
        ]

        for router_file in self.routers_path.glob("*.py"):
            if router_file.name.startswith("_"):
                continue

            content = router_file.read_text()

            # Find all endpoint definitions
            endpoint_pattern = r'@router\.(get|post|put|delete|patch)\(["\']([^"\']+)'
            endpoints = re.findall(endpoint_pattern, content)

            for method, path in endpoints:
                self.results["authentication"]["total_endpoints"] += 1

                # Get the function definition after this decorator
                endpoint_regex = rf'@router\.{method}\(["\'][^"\']+["\'][^)]*\)(.*?)(?=@router\.|class |def \w+\(|$)'
                match = re.search(endpoint_regex, content, re.DOTALL)

                if match:
                    func_def = match.group(1)

                    # Check if any auth pattern is present
                    has_auth = any(re.search(pattern, func_def) for pattern in auth_patterns)
                    is_public = any(re.search(pattern, f"{method} {path}") for pattern in public_patterns)

                    if has_auth:
                        self.results["authentication"]["authenticated_endpoints"] += 1
                    elif is_public:
                        self.results["authentication"]["public_endpoints"].append({
                            "file": str(router_file.relative_to(self.base_path)),
                            "method": method.upper(),
                            "path": path
                        })
                    else:
                        self.results["authentication"]["missing_auth"].append({
                            "file": str(router_file.relative_to(self.base_path)),
                            "method": method.upper(),
                            "path": path,
                            "severity": "critical"
                        })
                        self.results["severity_counts"]["critical"] += 1

    def scan_rbac_coverage(self):
        """Scan for missing RBAC (Role-Based Access Control)"""
        print("🔍 Scanning RBAC coverage...")

        rbac_patterns = [
            r'Depends\(RoleChecker\(',
            r'Depends\(PermissionChecker\(',
            r'require_role\(',
            r'require_permissions\('
        ]

        for router_file in self.routers_path.glob("*.py"):
            if router_file.name.startswith("_"):
                continue

            content = router_file.read_text()

            # Find authenticated endpoints (has get_current_user)
            auth_pattern = r'@router\.(get|post|put|delete|patch)\(["\']([^"\']+)["\'][^)]*\)(.*?)(?=@router\.|class |$)'

            for match in re.finditer(auth_pattern, content, re.DOTALL):
                method, path, func_def = match.groups()

                # Skip public endpoints
                if any(pub in path for pub in ['/health', '/docs', '/login', '/register']):
                    continue

                # Check if has authentication
                has_auth = 'get_current_user' in func_def or 'Depends' in func_def

                if has_auth:
                    # Check if has RBAC
                    has_rbac = any(re.search(pattern, func_def) for pattern in rbac_patterns)

                    # Sensitive operations that MUST have RBAC
                    sensitive_ops = ['delete', 'create', 'update', 'admin', 'manage']
                    is_sensitive = any(op in path.lower() or method.lower() == 'delete' for op in sensitive_ops)

                    if has_rbac:
                        self.results["authorization"]["rbac_coverage"]["total_protected"] += 1
                    elif is_sensitive:
                        self.results["authorization"]["rbac_coverage"]["missing_rbac"].append({
                            "file": str(router_file.relative_to(self.base_path)),
                            "method": method.upper(),
                            "path": path,
                            "severity": "high"
                        })
                        self.results["severity_counts"]["high"] += 1

    def scan_sql_injection(self):
        """Scan for SQL injection vulnerabilities"""
        print("🔍 Scanning for SQL injection vulnerabilities...")

        # Patterns that indicate potential SQL injection
        dangerous_patterns = [
            (r'f["\'].*SELECT.*{.*}.*["\']', 'f-string with SELECT statement'),
            (r'f["\'].*INSERT.*{.*}.*["\']', 'f-string with INSERT statement'),
            (r'f["\'].*UPDATE.*{.*}.*["\']', 'f-string with UPDATE statement'),
            (r'f["\'].*DELETE.*{.*}.*["\']', 'f-string with DELETE statement'),
            (r'\.execute\(["\'].*\+.*["\']', 'String concatenation in execute()'),
            (r'\.execute\(f["\']', 'f-string in execute()'),
            (r'db\.execute\(.*%.*\)', 'String formatting in execute()'),
        ]

        # Search all Python files
        for py_file in self.app_path.rglob("*.py"):
            if 'venv' in str(py_file) or '__pycache__' in str(py_file):
                continue

            content = py_file.read_text()

            for pattern, description in dangerous_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    # Get line number
                    line_num = content[:match.start()].count('\n') + 1

                    self.results["sql_injection"]["vulnerable_files"].append({
                        "file": str(py_file.relative_to(self.base_path)),
                        "line": line_num,
                        "pattern": description,
                        "code": match.group(0)[:100],
                        "severity": "critical"
                    })
                    self.results["severity_counts"]["critical"] += 1

    def scan_sensitive_data(self):
        """Scan for hardcoded secrets and credentials"""
        print("🔍 Scanning for hardcoded secrets...")

        # Patterns for secrets (excluding test/example values)
        secret_patterns = [
            (r'password\s*=\s*["\'][^"\']{6,}["\']', 'Hardcoded password'),
            (r'api_key\s*=\s*["\'][^"\']{10,}["\']', 'Hardcoded API key'),
            (r'secret_key\s*=\s*["\'][^"\']{10,}["\']', 'Hardcoded secret key'),
            (r'token\s*=\s*["\'][A-Za-z0-9]{20,}["\']', 'Hardcoded token'),
            (r'Bearer [A-Za-z0-9]{20,}', 'Hardcoded Bearer token'),
            (r'aws_access_key_id\s*=\s*["\'][^"\']+["\']', 'AWS credentials'),
            (r'aws_secret_access_key\s*=\s*["\'][^"\']+["\']', 'AWS credentials'),
        ]

        # Files to exclude
        exclude_patterns = ['test', 'example', 'template', 'venv', '__pycache__']

        for py_file in self.app_path.rglob("*.py"):
            # Skip excluded files
            if any(pattern in str(py_file).lower() for pattern in exclude_patterns):
                continue

            content = py_file.read_text()

            for pattern, description in secret_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    # Skip if it's in a comment or contains placeholder text
                    matched_text = match.group(0)
                    if any(x in matched_text.lower() for x in ['example', 'test', 'xxx', 'change', 'your_']):
                        continue

                    line_num = content[:match.start()].count('\n') + 1

                    self.results["sensitive_data"]["hardcoded_secrets"].append({
                        "file": str(py_file.relative_to(self.base_path)),
                        "line": line_num,
                        "type": description,
                        "severity": "critical"
                    })
                    self.results["severity_counts"]["critical"] += 1

    def scan_rls_usage(self):
        """Scan for Row-Level Security usage"""
        print("🔍 Scanning RLS (Row-Level Security) usage...")

        rls_patterns = [
            r'Depends\(get_db_with_rls\)',
            r'get_current_user_with_rls',
            r'RLSContextManager'
        ]

        for router_file in self.routers_path.glob("*.py"):
            if router_file.name.startswith("_"):
                continue

            content = router_file.read_text()

            # Check if file uses RLS
            has_rls = any(re.search(pattern, content) for pattern in rls_patterns)

            if has_rls:
                self.results["authorization"]["rls_coverage"]["total_using_rls"] += 1
            else:
                # Check if file queries data (should probably use RLS)
                queries_data = bool(re.search(r'db\.query\(|\.filter\(|\.all\(\)|\.first\(\)', content))
                has_auth = 'get_current_user' in content

                if queries_data and has_auth:
                    self.results["authorization"]["rls_coverage"]["missing_rls"].append({
                        "file": str(router_file.relative_to(self.base_path)),
                        "severity": "medium"
                    })
                    self.results["severity_counts"]["medium"] += 1

    def generate_report(self) -> Dict:
        """Generate comprehensive audit report"""
        # Calculate scores
        auth_score = 0
        if self.results["authentication"]["total_endpoints"] > 0:
            auth_score = (self.results["authentication"]["authenticated_endpoints"] /
                         self.results["authentication"]["total_endpoints"]) * 100

        total_vulns = (self.results["severity_counts"]["critical"] +
                      self.results["severity_counts"]["high"] +
                      self.results["severity_counts"]["medium"] +
                      self.results["severity_counts"]["low"])

        return {
            "summary": {
                "total_files_scanned": self.results["files_scanned"],
                "authentication_coverage": f"{auth_score:.1f}%",
                "total_vulnerabilities": total_vulns,
                "severity_breakdown": self.results["severity_counts"]
            },
            "detailed_results": self.results
        }

    def run_full_audit(self):
        """Run complete security audit"""
        print("=" * 80)
        print("🛡️  TSH ERP SECURITY AUDIT")
        print("=" * 80)

        self.scan_endpoint_authentication()
        self.scan_rbac_coverage()
        self.scan_sql_injection()
        self.scan_sensitive_data()
        self.scan_rls_usage()

        # Count files scanned
        self.results["files_scanned"] = len(list(self.app_path.rglob("*.py")))

        report = self.generate_report()

        print("\n" + "=" * 80)
        print("📊 AUDIT COMPLETE")
        print("=" * 80)
        print(f"Files Scanned: {report['summary']['total_files_scanned']}")
        print(f"Authentication Coverage: {report['summary']['authentication_coverage']}")
        print(f"Total Vulnerabilities: {report['summary']['total_vulnerabilities']}")
        print("\nSeverity Breakdown:")
        print(f"  🔴 Critical: {report['summary']['severity_breakdown']['critical']}")
        print(f"  🟠 High: {report['summary']['severity_breakdown']['high']}")
        print(f"  🟡 Medium: {report['summary']['severity_breakdown']['medium']}")
        print(f"  🟢 Low: {report['summary']['severity_breakdown']['low']}")

        return report


if __name__ == "__main__":
    base_path = Path(__file__).parent.parent
    auditor = SecurityAuditor(str(base_path))
    report = auditor.run_full_audit()

    # Save report to file
    output_file = base_path / "SECURITY_AUDIT_REPORT.json"
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n📄 Full report saved to: {output_file}")
