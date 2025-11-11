#!/usr/bin/env python3
"""
Orixoon Phase 7: Flutter Consumer API Tests
Tests API contracts that Flutter consumer app depends on
"""

import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import requests

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class FlutterAPITester:
    def __init__(self):
        self.results: List[Dict[str, Any]] = []
        self.start_time = time.time()
        self.critical_failures = 0
        self.base_url = os.getenv("BASE_URL", "http://localhost:8000")
        self.timeout = 10

    def log_check(self, name: str, status: str, message: str, critical: bool = True, response_time: float = None):
        """Log a check result"""
        result = {
            "name": name,
            "status": status,
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

    def test_price_list_api(self) -> bool:
        """Test price list API - CRITICAL for consumer app"""
        try:
            url = f"{self.base_url}/api/bff/mobile/tds/pricelists"
            start = time.time()
            response = requests.get(url, timeout=self.timeout)
            response_time = time.time() - start

            if response.status_code != 200:
                self.log_check(
                    "price_list_api",
                    "failed",
                    f"API returned {response.status_code}",
                    critical=True,
                    response_time=response_time
                )
                return False

            data = response.json()

            if not isinstance(data, list) or len(data) == 0:
                self.log_check(
                    "price_list_api",
                    "failed",
                    "No price lists returned",
                    critical=True,
                    response_time=response_time
                )
                return False

            # Check consumer price list exists
            consumer_price_list = None
            for pl in data:
                if "consumer" in pl.get("name", "").lower():
                    consumer_price_list = pl
                    break

            if not consumer_price_list:
                self.log_check(
                    "price_list_api",
                    "warning",
                    f"No consumer price list found (have {len(data)} price lists)",
                    critical=False,
                    response_time=response_time
                )
            else:
                self.log_check(
                    "price_list_api",
                    "passed",
                    f"Consumer price list found with {len(data)} total price lists",
                    critical=True,
                    response_time=response_time
                )

            return True

        except Exception as e:
            self.log_check(
                "price_list_api",
                "failed",
                f"Error: {str(e)}",
                critical=True
            )
            return False

    def test_products_api(self) -> bool:
        """Test products listing API"""
        try:
            url = f"{self.base_url}/api/bff/mobile/tds/products"
            start = time.time()
            response = requests.get(url, params={"limit": 10}, timeout=self.timeout)
            response_time = time.time() - start

            if response.status_code != 200:
                self.log_check(
                    "products_list_api",
                    "failed",
                    f"API returned {response.status_code}",
                    critical=True,
                    response_time=response_time
                )
                return False

            data = response.json()

            if not isinstance(data, (list, dict)):
                self.log_check(
                    "products_list_api",
                    "failed",
                    "Invalid response format",
                    critical=True,
                    response_time=response_time
                )
                return False

            # Extract products from response
            products = data if isinstance(data, list) else data.get("items", data.get("products", []))

            if len(products) == 0:
                self.log_check(
                    "products_list_api",
                    "warning",
                    "No products returned",
                    critical=False,
                    response_time=response_time
                )
            else:
                # Validate first product structure
                product = products[0]
                required_fields = ["id", "name"]
                missing_fields = [f for f in required_fields if f not in product]

                if missing_fields:
                    self.log_check(
                        "products_list_api",
                        "failed",
                        f"Missing fields: {', '.join(missing_fields)}",
                        critical=True,
                        response_time=response_time
                    )
                    return False

                self.log_check(
                    "products_list_api",
                    "passed",
                    f"{len(products)} products returned with valid structure",
                    critical=True,
                    response_time=response_time
                )

            return True

        except Exception as e:
            self.log_check(
                "products_list_api",
                "failed",
                f"Error: {str(e)}",
                critical=True
            )
            return False

    def test_categories_api(self) -> bool:
        """Test categories API"""
        try:
            url = f"{self.base_url}/api/bff/mobile/tds/categories"
            start = time.time()
            response = requests.get(url, timeout=self.timeout)
            response_time = time.time() - start

            if response.status_code != 200:
                self.log_check(
                    "categories_api",
                    "warning",
                    f"API returned {response.status_code}",
                    critical=False,
                    response_time=response_time
                )
                return True  # Non-critical

            data = response.json()

            if isinstance(data, list):
                self.log_check(
                    "categories_api",
                    "passed",
                    f"{len(data)} categories available",
                    critical=False,
                    response_time=response_time
                )
            else:
                self.log_check(
                    "categories_api",
                    "passed",
                    "Categories API responding",
                    critical=False,
                    response_time=response_time
                )

            return True

        except Exception as e:
            self.log_check(
                "categories_api",
                "warning",
                f"Error: {str(e)}",
                critical=False
            )
            return True  # Non-critical

    def test_cart_api(self) -> bool:
        """Test cart API endpoints"""
        try:
            url = f"{self.base_url}/api/bff/mobile/tds/cart"
            start = time.time()
            response = requests.get(url, timeout=self.timeout)
            response_time = time.time() - start

            # Cart might require auth (401) or return empty cart (200)
            if response.status_code in [200, 401]:
                self.log_check(
                    "cart_api",
                    "passed",
                    f"Cart API accessible ({response.status_code})",
                    critical=True,
                    response_time=response_time
                )
                return True
            else:
                self.log_check(
                    "cart_api",
                    "failed",
                    f"Unexpected status {response.status_code}",
                    critical=True,
                    response_time=response_time
                )
                return False

        except Exception as e:
            self.log_check(
                "cart_api",
                "failed",
                f"Error: {str(e)}",
                critical=True
            )
            return False

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all Flutter API tests"""
        print("📱 Orixoon Phase 7: Flutter Consumer API Tests\n")

        # Test critical APIs
        self.test_price_list_api()
        self.test_products_api()
        self.test_categories_api()
        self.test_cart_api()

        duration = time.time() - self.start_time

        # Generate report
        passed = sum(1 for r in self.results if r["status"] == "passed")
        failed = sum(1 for r in self.results if r["status"] == "failed")
        warnings = sum(1 for r in self.results if r["status"] == "warning")

        report = {
            "phase": "06_flutter_api_tester",
            "status": "passed" if self.critical_failures == 0 else "failed",
            "timestamp": datetime.now().isoformat(),
            "duration": round(duration, 2),
            "summary": {
                "total_tests": len(self.results),
                "passed": passed,
                "failed": failed,
                "warnings": warnings,
                "critical_failures": self.critical_failures
            },
            "tests": self.results
        }

        print(f"\n{'='*60}")
        print(f"Flutter API Tests: {report['status'].upper()}")
        print(f"Duration: {duration:.2f}s")
        print(f"Passed: {passed} | Failed: {failed} | Warnings: {warnings}")
        print(f"Critical Failures: {self.critical_failures}")
        print(f"{'='*60}\n")

        return report


def main():
    """Main entry point"""
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    tester = FlutterAPITester()
    report = tester.run_all_tests()

    # Output JSON report
    print(json.dumps(report, indent=2))

    # Exit with appropriate code
    if report["status"] == "failed":
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
