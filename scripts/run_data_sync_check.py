#!/usr/bin/env python3
"""
Zoho ↔ TSH ERP Data Consistency Checker
Verifies synchronization between Zoho Books/Inventory and local PostgreSQL database

Usage:
    python run_data_sync_check.py --mode=staging
    python run_data_sync_check.py --mode=production --limit=50
"""

import sys
import os
import json
import argparse
from datetime import datetime
from typing import Dict, List, Any, Tuple
from decimal import Decimal

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import requests
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError as e:
    print(json.dumps({
        "status": "error",
        "message": f"Missing required dependency: {e}",
        "differences": 0,
        "checked": 0
    }))
    sys.exit(1)


class DataSyncChecker:
    """Compare Zoho data with local PostgreSQL database"""
    
    def __init__(self, mode: str = "staging", limit: int = 100):
        self.mode = mode
        self.limit = limit
        self.differences = []
        self.checked_count = 0
        
        # Load Zoho credentials
        self.zoho_org_id = os.getenv("ZOHO_ORGANIZATION_ID")
        self.zoho_access_token = os.getenv("ZOHO_ACCESS_TOKEN")
        self.zoho_refresh_token = os.getenv("ZOHO_REFRESH_TOKEN")
        
        # Database connection
        self.db_conn = None
        
    def connect_db(self):
        """Connect to PostgreSQL database"""
        try:
            db_config = {
                "host": os.getenv("DB_HOST", "localhost"),
                "port": int(os.getenv("DB_PORT", "5432")),
                "database": os.getenv("DB_NAME", "tsh_erp"),
                "user": os.getenv("DB_USER", "postgres"),
                "password": os.getenv("DB_PASSWORD", "")
            }
            
            self.db_conn = psycopg2.connect(**db_config, cursor_factory=RealDictCursor)
            return True
        except Exception as e:
            self.add_difference("database_connection", f"Failed to connect: {e}")
            return False
    
    def close_db(self):
        """Close database connection"""
        if self.db_conn:
            self.db_conn.close()
    
    def get_zoho_data(self, endpoint: str, params: Dict = None) -> List[Dict]:
        """Fetch data from Zoho API"""
        if not self.zoho_access_token or not self.zoho_org_id:
            return []
        
        headers = {
            "Authorization": f"Zoho-oauthtoken {self.zoho_access_token}"
        }
        
        base_url = "https://books.zoho.com/api/v3"
        url = f"{base_url}/{endpoint}"
        
        params = params or {}
        params["organization_id"] = self.zoho_org_id
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Handle different response structures
            if isinstance(data, dict):
                # Try common keys
                for key in ['invoices', 'customers', 'items', 'contacts']:
                    if key in data:
                        return data[key]
                # Return the whole dict if no known key
                return [data] if data else []
            elif isinstance(data, list):
                return data
            else:
                return []
                
        except requests.exceptions.RequestException as e:
            self.add_difference("zoho_api_error", f"{endpoint}: {str(e)}")
            return []
        except json.JSONDecodeError as e:
            self.add_difference("zoho_json_error", f"{endpoint}: Invalid JSON response")
            return []
    
    def get_db_data(self, query: str, params: Tuple = None) -> List[Dict]:
        """Fetch data from PostgreSQL"""
        if not self.db_conn:
            return []
        
        try:
            cursor = self.db_conn.cursor()
            cursor.execute(query, params)
            results = cursor.fetchall()
            cursor.close()
            return [dict(row) for row in results]
        except Exception as e:
            self.add_difference("database_query_error", f"Query failed: {e}")
            return []
    
    def add_difference(self, category: str, detail: str, zoho_value: Any = None, db_value: Any = None):
        """Add a difference to the list"""
        diff = {
            "category": category,
            "detail": detail,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if zoho_value is not None:
            diff["zoho_value"] = str(zoho_value)
        if db_value is not None:
            diff["db_value"] = str(db_value)
        
        self.differences.append(diff)
    
    def compare_invoices(self) -> bool:
        """Compare invoices between Zoho and database"""
        print("Checking invoices...")
        
        # Fetch from Zoho
        zoho_invoices = self.get_zoho_data("invoices", {
            "sort_column": "invoice_date",
            "sort_order": "D",
            "per_page": str(self.limit)
        })
        
        # Fetch from database
        db_invoices = self.get_db_data("""
            SELECT 
                zoho_invoice_id,
                invoice_number,
                customer_name,
                total,
                status,
                invoice_date
            FROM invoices
            WHERE zoho_invoice_id IS NOT NULL
            ORDER BY invoice_date DESC
            LIMIT %s
        """, (self.limit,))
        
        # Create lookup dictionaries
        zoho_by_id = {inv.get('invoice_id'): inv for inv in zoho_invoices if inv.get('invoice_id')}
        db_by_zoho_id = {inv['zoho_invoice_id']: inv for inv in db_invoices}
        
        self.checked_count += len(zoho_by_id)
        
        # Compare
        for zoho_id, zoho_inv in zoho_by_id.items():
            if zoho_id not in db_by_zoho_id:
                self.add_difference(
                    "missing_invoice_in_db",
                    f"Invoice {zoho_inv.get('invoice_number')} exists in Zoho but not in database",
                    zoho_value=zoho_id
                )
                continue
            
            db_inv = db_by_zoho_id[zoho_id]
            
            # Compare key fields
            if zoho_inv.get('invoice_number') != db_inv.get('invoice_number'):
                self.add_difference(
                    "invoice_number_mismatch",
                    f"Invoice {zoho_id} number mismatch",
                    zoho_value=zoho_inv.get('invoice_number'),
                    db_value=db_inv.get('invoice_number')
                )
            
            # Compare total (handle Decimal and float)
            zoho_total = float(zoho_inv.get('total', 0))
            db_total = float(db_inv.get('total', 0))
            if abs(zoho_total - db_total) > 0.01:  # Allow 1 cent difference
                self.add_difference(
                    "invoice_total_mismatch",
                    f"Invoice {zoho_inv.get('invoice_number')} total mismatch",
                    zoho_value=zoho_total,
                    db_value=db_total
                )
            
            # Compare status
            if zoho_inv.get('status') != db_inv.get('status'):
                self.add_difference(
                    "invoice_status_mismatch",
                    f"Invoice {zoho_inv.get('invoice_number')} status mismatch",
                    zoho_value=zoho_inv.get('status'),
                    db_value=db_inv.get('status')
                )
        
        return len(self.differences) == 0
    
    def compare_customers(self) -> bool:
        """Compare customers between Zoho and database"""
        print("Checking customers...")
        
        # Fetch from Zoho
        zoho_customers = self.get_zoho_data("contacts", {
            "sort_column": "created_time",
            "sort_order": "D",
            "per_page": str(self.limit)
        })
        
        # Fetch from database
        db_customers = self.get_db_data("""
            SELECT 
                zoho_contact_id,
                company_name,
                contact_name,
                email,
                phone,
                status
            FROM customers
            WHERE zoho_contact_id IS NOT NULL
            ORDER BY created_at DESC
            LIMIT %s
        """, (self.limit,))
        
        # Create lookup dictionaries
        zoho_by_id = {cust.get('contact_id'): cust for cust in zoho_customers if cust.get('contact_id')}
        db_by_zoho_id = {cust['zoho_contact_id']: cust for cust in db_customers}
        
        self.checked_count += len(zoho_by_id)
        
        # Compare
        for zoho_id, zoho_cust in zoho_by_id.items():
            if zoho_id not in db_by_zoho_id:
                self.add_difference(
                    "missing_customer_in_db",
                    f"Customer {zoho_cust.get('contact_name')} exists in Zoho but not in database",
                    zoho_value=zoho_id
                )
                continue
            
            db_cust = db_by_zoho_id[zoho_id]
            
            # Compare company name
            if zoho_cust.get('company_name') != db_cust.get('company_name'):
                self.add_difference(
                    "customer_company_mismatch",
                    f"Customer {zoho_id} company name mismatch",
                    zoho_value=zoho_cust.get('company_name'),
                    db_value=db_cust.get('company_name')
                )
            
            # Compare email
            if zoho_cust.get('email') and zoho_cust.get('email') != db_cust.get('email'):
                self.add_difference(
                    "customer_email_mismatch",
                    f"Customer {zoho_cust.get('contact_name')} email mismatch",
                    zoho_value=zoho_cust.get('email'),
                    db_value=db_cust.get('email')
                )
        
        return len(self.differences) == 0
    
    def compare_products(self) -> bool:
        """Compare products between Zoho and database"""
        print("Checking products...")
        
        # Fetch from Zoho Inventory
        zoho_products = self.get_zoho_data("items", {
            "sort_column": "created_time",
            "sort_order": "D",
            "per_page": str(self.limit)
        })
        
        # Fetch from database
        db_products = self.get_db_data("""
            SELECT 
                zoho_item_id,
                name,
                sku,
                rate,
                stock_quantity,
                is_active
            FROM products
            WHERE zoho_item_id IS NOT NULL
            ORDER BY created_at DESC
            LIMIT %s
        """, (self.limit,))
        
        # Create lookup dictionaries
        zoho_by_id = {prod.get('item_id'): prod for prod in zoho_products if prod.get('item_id')}
        db_by_zoho_id = {prod['zoho_item_id']: prod for prod in db_products}
        
        self.checked_count += len(zoho_by_id)
        
        # Compare
        for zoho_id, zoho_prod in zoho_by_id.items():
            if zoho_id not in db_by_zoho_id:
                self.add_difference(
                    "missing_product_in_db",
                    f"Product {zoho_prod.get('name')} exists in Zoho but not in database",
                    zoho_value=zoho_id
                )
                continue
            
            db_prod = db_by_zoho_id[zoho_id]
            
            # Compare name
            if zoho_prod.get('name') != db_prod.get('name'):
                self.add_difference(
                    "product_name_mismatch",
                    f"Product {zoho_id} name mismatch",
                    zoho_value=zoho_prod.get('name'),
                    db_value=db_prod.get('name')
                )
            
            # Compare SKU
            if zoho_prod.get('sku') and zoho_prod.get('sku') != db_prod.get('sku'):
                self.add_difference(
                    "product_sku_mismatch",
                    f"Product {zoho_prod.get('name')} SKU mismatch",
                    zoho_value=zoho_prod.get('sku'),
                    db_value=db_prod.get('sku')
                )
            
            # Compare rate/price (handle Decimal and float)
            if 'rate' in zoho_prod:
                zoho_rate = float(zoho_prod.get('rate', 0))
                db_rate = float(db_prod.get('rate', 0))
                if abs(zoho_rate - db_rate) > 0.01:
                    self.add_difference(
                        "product_rate_mismatch",
                        f"Product {zoho_prod.get('name')} rate mismatch",
                        zoho_value=zoho_rate,
                        db_value=db_rate
                    )
            
            # Compare stock quantity
            if 'stock_on_hand' in zoho_prod:
                zoho_stock = int(zoho_prod.get('stock_on_hand', 0))
                db_stock = int(db_prod.get('stock_quantity', 0))
                if zoho_stock != db_stock:
                    self.add_difference(
                        "product_stock_mismatch",
                        f"Product {zoho_prod.get('name')} stock mismatch",
                        zoho_value=zoho_stock,
                        db_value=db_stock
                    )
        
        return len(self.differences) == 0
    
    def run_check(self) -> Dict[str, Any]:
        """Run all data consistency checks"""
        print(f"\n{'='*60}")
        print(f"Zoho ↔ TSH ERP Data Consistency Check")
        print(f"Mode: {self.mode.upper()}")
        print(f"Limit: {self.limit} records per entity")
        print(f"{'='*60}\n")
        
        # Connect to database
        if not self.connect_db():
            return {
                "status": "failed",
                "differences": len(self.differences),
                "checked": 0,
                "details": self.differences,
                "error": "Failed to connect to database"
            }
        
        try:
            # Run comparisons
            self.compare_invoices()
            self.compare_customers()
            self.compare_products()
            
            # Generate result
            result = {
                "status": "ok" if len(self.differences) == 0 else "failed",
                "differences": len(self.differences),
                "checked": self.checked_count,
                "mode": self.mode,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            if self.differences:
                result["details"] = self.differences
            
            return result
            
        finally:
            self.close_db()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Zoho ↔ TSH ERP Data Consistency Checker"
    )
    parser.add_argument(
        "--mode",
        type=str,
        default="staging",
        choices=["staging", "production"],
        help="Environment mode (default: staging)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="Number of records to check per entity (default: 100)"
    )
    
    args = parser.parse_args()
    
    # Create checker and run
    checker = DataSyncChecker(mode=args.mode, limit=args.limit)
    result = checker.run_check()
    
    # Print result as JSON
    print("\n" + "="*60)
    print("RESULT:")
    print("="*60)
    print(json.dumps(result, indent=2))
    
    # Exit with appropriate code
    if result["status"] == "failed" or result["differences"] > 0:
        print(f"\n❌ Found {result['differences']} differences!")
        sys.exit(1)
    else:
        print(f"\n✅ All {result['checked']} records are synchronized!")
        sys.exit(0)


if __name__ == "__main__":
    main()
