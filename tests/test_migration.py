#!/usr/bin/env python3
"""
Migration System Test Script
نص اختبار نظام الهجرة

Test script to validate the complete migration workflow from Zoho to TSH ERP.
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any


class MigrationTester:
    """اختبار نظام الهجرة"""
    
    def __init__(self, api_base_url: str = "http://localhost:8000/migration"):
        self.api_base_url = api_base_url
        self.test_results = []
    
    def log_test(self, test_name: str, success: bool, message: str = "", data: Any = None):
        """تسجيل نتائج الاختبار"""
        result = {
            "test_name": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        
        if data and not success:
            print(f"   Data: {json.dumps(data, indent=2)}")
    
    def make_request(self, endpoint: str, method: str = "GET", data: dict = None) -> Dict[str, Any]:
        """تقديم طلب API"""
        try:
            url = f"{self.api_base_url}/{endpoint}"
            headers = {"Content-Type": "application/json"}
            
            if method.upper() == "GET":
                response = requests.get(url, headers=headers)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=headers)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            if response.status_code in [200, 201]:
                return {"success": True, "data": response.json()}
            else:
                return {
                    "success": False, 
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def test_api_connectivity(self):
        """اختبار الاتصال بالـ API"""
        result = self.make_request("batches")
        
        if result["success"]:
            self.log_test(
                "API Connectivity", 
                True, 
                f"Successfully connected to API, found {len(result['data'])} batches"
            )
        else:
            self.log_test(
                "API Connectivity", 
                False, 
                f"Failed to connect to API: {result['error']}"
            )
        
        return result["success"]
    
    def test_create_migration_batch(self) -> int:
        """اختبار إنشاء دفعة هجرة"""
        batch_data = {
            "batch_name": f"Test Migration Batch {datetime.now().strftime('%Y%m%d%H%M%S')}",
            "description": "Test batch created by migration tester",
            "source_system": "Zoho Books/Inventory"
        }
        
        result = self.make_request("batches", "POST", batch_data)
        
        if result["success"]:
            batch_id = result["data"]["id"]
            self.log_test(
                "Create Migration Batch", 
                True, 
                f"Created batch with ID: {batch_id}"
            )
            return batch_id
        else:
            self.log_test(
                "Create Migration Batch", 
                False, 
                f"Failed to create batch: {result['error']}"
            )
            return None
    
    def test_items_migration(self, batch_id: int):
        """اختبار هجرة الأصناف"""
        sample_items = [
            {
                "item_id": "TEST001",
                "name": "Test Laptop",
                "sku": "TEST-LAPTOP-001",
                "category": "Electronics",
                "unit": "PCS",
                "rate": 1000.0,
                "currency_code": "USD",
                "status": "active",
                "description": "Test laptop for migration"
            },
            {
                "item_id": "TEST002",
                "name": "Test Phone",
                "sku": "TEST-PHONE-001", 
                "category": "Mobile",
                "unit": "PCS",
                "rate": 800.0,
                "currency_code": "USD",
                "status": "active",
                "description": "Test phone for migration"
            }
        ]
        
        result = self.make_request(f"batches/{batch_id}/migrate-items-from-data", "POST", sample_items)
        
        if result["success"]:
            data = result["data"]
            total = data.get("total_records", 0)
            success = data.get("successful_records", 0)
            failed = data.get("failed_records", 0)
            
            self.log_test(
                "Items Migration", 
                success == total,
                f"Migrated {success}/{total} items, {failed} failed"
            )
        else:
            self.log_test(
                "Items Migration", 
                False, 
                f"Failed to migrate items: {result['error']}"
            )
    
    def test_customers_migration(self, batch_id: int):
        """اختبار هجرة العملاء"""
        sample_customers = [
            {
                "contact_id": "CUST001",
                "display_name": "Test Customer 1",
                "company_name": "Test Company Ltd",
                "email": "test1@example.com",
                "phone": "+964-771-123-4567",
                "currency_code": "USD",
                "outstanding_receivable_amount": 1500.0,
                "status": "active",
                "billing_address": {
                    "address": "123 Test Street",
                    "city": "Baghdad",
                    "country": "Iraq"
                }
            },
            {
                "contact_id": "CUST002",
                "display_name": "Test Customer 2",
                "company_name": "Another Test Co",
                "email": "test2@example.com",
                "phone": "+964-771-987-6543",
                "currency_code": "USD",
                "outstanding_receivable_amount": 2000.0,
                "status": "active",
                "billing_address": {
                    "address": "456 Another St",
                    "city": "Basra",
                    "country": "Iraq"
                }
            }
        ]
        
        result = self.make_request(f"batches/{batch_id}/migrate-customers-from-data", "POST", sample_customers)
        
        if result["success"]:
            data = result["data"]
            total = data.get("total_records", 0)
            success = data.get("successful_records", 0)
            failed = data.get("failed_records", 0)
            
            self.log_test(
                "Customers Migration", 
                success == total,
                f"Migrated {success}/{total} customers, {failed} failed"
            )
        else:
            self.log_test(
                "Customers Migration", 
                False, 
                f"Failed to migrate customers: {result['error']}"
            )
    
    def test_vendors_migration(self, batch_id: int):
        """اختبار هجرة الموردين"""
        sample_vendors = [
            {
                "contact_id": "VEND001",
                "display_name": "Test Vendor 1",
                "company_name": "Test Supplier Ltd",
                "email": "vendor1@example.com",
                "phone": "+1-555-123-4567",
                "currency_code": "USD",
                "outstanding_payable_amount": 5000.0,
                "status": "active",
                "address": {
                    "address": "789 Supplier Ave",
                    "city": "New York",
                    "country": "USA"
                }
            }
        ]
        
        result = self.make_request(f"batches/{batch_id}/migrate-vendors-from-data", "POST", sample_vendors)
        
        if result["success"]:
            data = result["data"]
            total = data.get("total_records", 0)
            success = data.get("successful_records", 0)
            failed = data.get("failed_records", 0)
            
            self.log_test(
                "Vendors Migration", 
                success == total,
                f"Migrated {success}/{total} vendors, {failed} failed"
            )
        else:
            self.log_test(
                "Vendors Migration", 
                False, 
                f"Failed to migrate vendors: {result['error']}"
            )
    
    def test_batch_completion(self, batch_id: int):
        """اختبار إكمال الدفعة"""
        # Start the batch
        result = self.make_request(f"batches/{batch_id}/start", "PUT")
        if not result["success"]:
            self.log_test(
                "Start Batch", 
                False, 
                f"Failed to start batch: {result['error']}"
            )
            return
        
        # Wait a moment
        time.sleep(1)
        
        # Complete the batch
        result = self.make_request(f"batches/{batch_id}/complete", "PUT")
        if result["success"]:
            self.log_test(
                "Complete Batch", 
                True, 
                "Successfully completed migration batch"
            )
        else:
            self.log_test(
                "Complete Batch", 
                False, 
                f"Failed to complete batch: {result['error']}"
            )
    
    def test_reports_generation(self, batch_id: int):
        """اختبار تقارير الهجرة"""
        # Test batch report
        result = self.make_request(f"reports/batch/{batch_id}")
        if result["success"]:
            self.log_test(
                "Batch Report", 
                True, 
                "Successfully generated batch report"
            )
        else:
            self.log_test(
                "Batch Report", 
                False, 
                f"Failed to generate batch report: {result['error']}"
            )
        
        # Test summary report
        result = self.make_request("reports/summary")
        if result["success"]:
            self.log_test(
                "Summary Report", 
                True, 
                "Successfully generated summary report"
            )
        else:
            self.log_test(
                "Summary Report", 
                False, 
                f"Failed to generate summary report: {result['error']}"
            )
    
    def run_complete_test(self):
        """تشغيل اختبار شامل"""
        print("🚀 Starting Migration System Test")
        print("=" * 50)
        
        # Test 1: API Connectivity
        if not self.test_api_connectivity():
            print("❌ API connectivity failed, stopping tests")
            return
        
        # Test 2: Create Migration Batch
        batch_id = self.test_create_migration_batch()
        if batch_id is None:
            print("❌ Failed to create migration batch, stopping tests")
            return
        
        # Test 3: Items Migration
        self.test_items_migration(batch_id)
        
        # Test 4: Customers Migration
        self.test_customers_migration(batch_id)
        
        # Test 5: Vendors Migration
        self.test_vendors_migration(batch_id)
        
        # Test 6: Batch Completion
        self.test_batch_completion(batch_id)
        
        # Test 7: Reports Generation
        self.test_reports_generation(batch_id)
        
        # Print Summary
        print("\n" + "=" * 50)
        print("🎯 TEST SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test_name']}: {result['message']}")
        
        print("\n🎉 Migration system test completed!")
        
        # Save results to file
        with open(f"migration_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
        
        return passed_tests == total_tests


def main():
    """تشغيل الاختبارات"""
    tester = MigrationTester()
    success = tester.run_complete_test()
    
    if success:
        print("\n✅ All tests passed! Migration system is ready.")
    else:
        print("\n❌ Some tests failed. Check the results above.")
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
