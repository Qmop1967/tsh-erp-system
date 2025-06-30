"""
TSH ERP Migration System
نظام الهجرة من Zoho إلى TSH ERP

This system handles migration from Zoho Books and Zoho Inventory to TSH ERP system.
Includes data mapping, currency conversion, and salesperson assignment logic.
"""

import os
import json
import pandas as pd
import logging
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('migration.log'),
        logging.StreamHandler()
    ]
)

class MigrationStatus(Enum):
    """حالات الهجرة"""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REQUIRES_REVIEW = "REQUIRES_REVIEW"


@dataclass
class MigrationResult:
    """نتيجة عملية الهجرة"""
    entity_type: str
    total_records: int
    successful_records: int
    failed_records: int
    errors: List[str]
    status: MigrationStatus
    start_time: datetime
    end_time: Optional[datetime] = None


class SalespersonMapping:
    """
    خريطة ربط مندوبي المبيعات بحسابات الودائع
    Maps salespeople to their deposit accounts for customer assignment
    """
    
    DEPOSIT_ACCOUNT_MAPPING = {
        'frati': 'ayad',      # Ayad Al-Baghdadi - Furat regions
        'southi': 'haider',   # Haider - South regions  
        'northi': 'hussien',  # Hussein - North regions
        'dyali': 'ahmed',     # Ahmed - Diyala region
        'westi': 'ayoob'      # Ayoob - West regions
    }
    
    SALESPERSON_REGIONS = {
        'ayad': ['KARBALA', 'NAJAF', 'BABEL'],
        'haider': ['BASRA', 'DHI_QAR', 'MAYSAN', 'MUTHANNA'],
        'hussien': ['MOSUL', 'ERBIL', 'DUHOK', 'SULAYMANIYAH', 'KIRKUK'],
        'ahmed': ['DIYALA', 'SALAHUDDIN'],
        'ayoob': ['ANBAR', 'BAGHDAD']
    }
    
    @classmethod
    def get_salesperson_by_deposit(cls, deposit_account_name: str) -> Optional[str]:
        """الحصول على مندوب المبيعات من خلال اسم حساب الودائع"""
        account_lower = deposit_account_name.lower()
        for deposit_key, salesperson in cls.DEPOSIT_ACCOUNT_MAPPING.items():
            if deposit_key in account_lower:
                return salesperson
        return None
    
    @classmethod
    def get_regions_by_salesperson(cls, salesperson: str) -> List[str]:
        """الحصول على المناطق المخصصة للمندوب"""
        return cls.SALESPERSON_REGIONS.get(salesperson.lower(), [])


class CurrencyConverter:
    """
    محول العملات
    Handles currency conversion from USD to IQD and other currencies
    """
    
    # Exchange rates (can be configurable)
    EXCHANGE_RATES = {
        'USD_TO_IQD': 1500.0,
        'USD_TO_RMB': 7.2,
        'IQD_TO_USD': 1.0 / 1500.0,
        'RMB_TO_USD': 1.0 / 7.2
    }
    
    @classmethod
    def convert_currency(cls, amount: float, from_currency: str, to_currency: str) -> Decimal:
        """تحويل العملة"""
        if from_currency == to_currency:
            return Decimal(str(amount))
        
        rate_key = f"{from_currency}_TO_{to_currency}"
        if rate_key in cls.EXCHANGE_RATES:
            converted = amount * cls.EXCHANGE_RATES[rate_key]
            return Decimal(str(round(converted, 3)))
        
        # Convert via USD if direct rate not available
        if from_currency != 'USD':
            usd_amount = cls.convert_currency(amount, from_currency, 'USD')
            return cls.convert_currency(float(usd_amount), 'USD', to_currency)
        
        raise ValueError(f"Conversion rate not found: {from_currency} to {to_currency}")


class ZohoDataExtractor:
    """
    مستخرج البيانات من Zoho
    Handles data extraction from Zoho Books and Zoho Inventory
    """
    
    def __init__(self, zoho_books_file: str, zoho_inventory_file: str):
        self.zoho_books_file = zoho_books_file
        self.zoho_inventory_file = zoho_inventory_file
    
    def extract_items(self) -> pd.DataFrame:
        """استخراج الأصناف من Zoho Inventory"""
        try:
            # Placeholder for actual Zoho API extraction
            # This would be replaced with actual Zoho API calls
            logging.info("Extracting items from Zoho Inventory...")
            
            # Sample structure - replace with actual Zoho data extraction
            return pd.DataFrame([
                {
                    'item_id': '1',
                    'item_name': 'Sample Item',
                    'sku': 'SKU001',
                    'category': 'Electronics',
                    'unit_price_usd': 100.0,
                    'stock_on_hand': 50,
                    'reorder_level': 10,
                    'is_active': True
                }
            ])
        except Exception as e:
            logging.error(f"Error extracting items: {str(e)}")
            raise
    
    def extract_customers(self) -> pd.DataFrame:
        """استخراج العملاء من Zoho Books"""
        try:
            logging.info("Extracting customers from Zoho Books...")
            
            # Sample structure - replace with actual Zoho data extraction
            return pd.DataFrame([
                {
                    'customer_id': '1',
                    'customer_name': 'Sample Customer',
                    'email': 'customer@example.com',
                    'phone': '+964770123456',
                    'currency': 'IQD',
                    'outstanding_receivable': 1500000.0,
                    'deposit_account': 'frati_deposit',
                    'price_list_id': 'PL001',
                    'is_active': True
                }
            ])
        except Exception as e:
            logging.error(f"Error extracting customers: {str(e)}")
            raise
    
    def extract_vendors(self) -> pd.DataFrame:
        """استخراج الموردين من Zoho Books"""
        try:
            logging.info("Extracting vendors from Zoho Books...")
            
            return pd.DataFrame([
                {
                    'vendor_id': '1',
                    'vendor_name': 'Sample Vendor',
                    'email': 'vendor@example.com',
                    'phone': '+1234567890',
                    'currency': 'USD',
                    'outstanding_payable': 5000.0,
                    'is_active': True
                }
            ])
        except Exception as e:
            logging.error(f"Error extracting vendors: {str(e)}")
            raise
    
    def extract_price_lists(self) -> pd.DataFrame:
        """استخراج قوائم الأسعار من Zoho Inventory"""
        try:
            logging.info("Extracting price lists from Zoho Inventory...")
            
            return pd.DataFrame([
                {
                    'price_list_id': 'PL001',
                    'name': 'Retail Price List',
                    'currency': 'IQD',
                    'is_active': True
                }
            ])
        except Exception as e:
            logging.error(f"Error extracting price lists: {str(e)}")
            raise


class TSHERPMigrator:
    """
    مهاجر بيانات TSH ERP
    Main migration controller for TSH ERP system
    """
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.migration_results: List[MigrationResult] = []
        self.converter = CurrencyConverter()
        self.salesperson_mapper = SalespersonMapping()
    
    def start_migration(self, zoho_books_file: str, zoho_inventory_file: str) -> Dict[str, Any]:
        """بدء عملية الهجرة الكاملة"""
        logging.info("🚀 Starting TSH ERP Migration Process")
        
        extractor = ZohoDataExtractor(zoho_books_file, zoho_inventory_file)
        
        migration_plan = {
            'start_time': datetime.now(),
            'status': MigrationStatus.IN_PROGRESS,
            'steps': [
                {'name': 'Items Migration', 'status': 'pending'},
                {'name': 'Price Lists Migration', 'status': 'pending'},
                {'name': 'Customers Migration', 'status': 'pending'},
                {'name': 'Vendors Migration', 'status': 'pending'},
                {'name': 'Stock Migration', 'status': 'pending'},
                {'name': 'Outstanding Balances', 'status': 'pending'},
                {'name': 'Salesperson Assignment', 'status': 'pending'}
            ]
        }
        
        try:
            # Step 1: Migrate Items
            logging.info("Step 1: Migrating Items...")
            items_df = extractor.extract_items()
            items_result = self.migrate_items(items_df)
            self.migration_results.append(items_result)
            
            # Step 2: Migrate Price Lists
            logging.info("Step 2: Migrating Price Lists...")
            price_lists_df = extractor.extract_price_lists()
            price_lists_result = self.migrate_price_lists(price_lists_df)
            self.migration_results.append(price_lists_result)
            
            # Step 3: Migrate Customers
            logging.info("Step 3: Migrating Customers...")
            customers_df = extractor.extract_customers()
            customers_result = self.migrate_customers(customers_df)
            self.migration_results.append(customers_result)
            
            # Step 4: Migrate Vendors
            logging.info("Step 4: Migrating Vendors...")
            vendors_df = extractor.extract_vendors()
            vendors_result = self.migrate_vendors(vendors_df)
            self.migration_results.append(vendors_result)
            
            # Step 5: Assign Salespeople to Customers
            logging.info("Step 5: Assigning Salespeople...")
            salesperson_result = self.assign_salespeople_to_customers(customers_df)
            self.migration_results.append(salesperson_result)
            
            migration_plan['status'] = MigrationStatus.COMPLETED
            migration_plan['end_time'] = datetime.now()
            
            logging.info("✅ Migration completed successfully!")
            
        except Exception as e:
            migration_plan['status'] = MigrationStatus.FAILED
            migration_plan['error'] = str(e)
            logging.error(f"❌ Migration failed: {str(e)}")
        
        return migration_plan
    
    def migrate_items(self, items_df: pd.DataFrame) -> MigrationResult:
        """هجرة الأصناف"""
        result = MigrationResult(
            entity_type="Items",
            total_records=len(items_df),
            successful_records=0,
            failed_records=0,
            errors=[],
            status=MigrationStatus.IN_PROGRESS,
            start_time=datetime.now()
        )
        
        try:
            for _, item in items_df.iterrows():
                try:
                    # Convert USD prices to IQD
                    price_iqd = self.converter.convert_currency(
                        item['unit_price_usd'], 'USD', 'IQD'
                    )
                    
                    # TODO: Insert into TSH ERP database
                    # This would be actual database insertion
                    logging.info(f"Migrating item: {item['item_name']} - Price: {price_iqd} IQD")
                    
                    result.successful_records += 1
                    
                except Exception as e:
                    result.failed_records += 1
                    result.errors.append(f"Item {item.get('item_name', 'Unknown')}: {str(e)}")
            
            result.status = MigrationStatus.COMPLETED if result.failed_records == 0 else MigrationStatus.REQUIRES_REVIEW
            result.end_time = datetime.now()
            
        except Exception as e:
            result.status = MigrationStatus.FAILED
            result.errors.append(str(e))
        
        return result
    
    def migrate_customers(self, customers_df: pd.DataFrame) -> MigrationResult:
        """هجرة العملاء"""
        result = MigrationResult(
            entity_type="Customers",
            total_records=len(customers_df),
            successful_records=0,
            failed_records=0,
            errors=[],
            status=MigrationStatus.IN_PROGRESS,
            start_time=datetime.now()
        )
        
        try:
            for _, customer in customers_df.iterrows():
                try:
                    # Determine salesperson from deposit account
                    salesperson = self.salesperson_mapper.get_salesperson_by_deposit(
                        customer.get('deposit_account', '')
                    )
                    
                    if not salesperson:
                        result.errors.append(
                            f"Customer {customer['customer_name']}: Could not determine salesperson from deposit account"
                        )
                    
                    # TODO: Insert into TSH ERP database
                    logging.info(f"Migrating customer: {customer['customer_name']} -> Salesperson: {salesperson}")
                    
                    result.successful_records += 1
                    
                except Exception as e:
                    result.failed_records += 1
                    result.errors.append(f"Customer {customer.get('customer_name', 'Unknown')}: {str(e)}")
            
            result.status = MigrationStatus.COMPLETED if result.failed_records == 0 else MigrationStatus.REQUIRES_REVIEW
            result.end_time = datetime.now()
            
        except Exception as e:
            result.status = MigrationStatus.FAILED
            result.errors.append(str(e))
        
        return result
    
    def migrate_vendors(self, vendors_df: pd.DataFrame) -> MigrationResult:
        """هجرة الموردين"""
        result = MigrationResult(
            entity_type="Vendors",
            total_records=len(vendors_df),
            successful_records=0,
            failed_records=0,
            errors=[],
            status=MigrationStatus.IN_PROGRESS,
            start_time=datetime.now()
        )
        
        try:
            for _, vendor in vendors_df.iterrows():
                try:
                    # TODO: Insert into TSH ERP database
                    logging.info(f"Migrating vendor: {vendor['vendor_name']} - Currency: {vendor['currency']}")
                    
                    result.successful_records += 1
                    
                except Exception as e:
                    result.failed_records += 1
                    result.errors.append(f"Vendor {vendor.get('vendor_name', 'Unknown')}: {str(e)}")
            
            result.status = MigrationStatus.COMPLETED if result.failed_records == 0 else MigrationStatus.REQUIRES_REVIEW
            result.end_time = datetime.now()
            
        except Exception as e:
            result.status = MigrationStatus.FAILED
            result.errors.append(str(e))
        
        return result
    
    def migrate_price_lists(self, price_lists_df: pd.DataFrame) -> MigrationResult:
        """هجرة قوائم الأسعار"""
        result = MigrationResult(
            entity_type="Price Lists",
            total_records=len(price_lists_df),
            successful_records=0,
            failed_records=0,
            errors=[],
            status=MigrationStatus.IN_PROGRESS,
            start_time=datetime.now()
        )
        
        try:
            for _, price_list in price_lists_df.iterrows():
                try:
                    # TODO: Insert into TSH ERP database
                    logging.info(f"Migrating price list: {price_list['name']}")
                    
                    result.successful_records += 1
                    
                except Exception as e:
                    result.failed_records += 1
                    result.errors.append(f"Price List {price_list.get('name', 'Unknown')}: {str(e)}")
            
            result.status = MigrationStatus.COMPLETED if result.failed_records == 0 else MigrationStatus.REQUIRES_REVIEW
            result.end_time = datetime.now()
            
        except Exception as e:
            result.status = MigrationStatus.FAILED
            result.errors.append(str(e))
        
        return result
    
    def assign_salespeople_to_customers(self, customers_df: pd.DataFrame) -> MigrationResult:
        """تعيين مندوبي المبيعات للعملاء"""
        result = MigrationResult(
            entity_type="Salesperson Assignment",
            total_records=len(customers_df),
            successful_records=0,
            failed_records=0,
            errors=[],
            status=MigrationStatus.IN_PROGRESS,
            start_time=datetime.now()
        )
        
        assignment_summary = {}
        
        try:
            for _, customer in customers_df.iterrows():
                try:
                    deposit_account = customer.get('deposit_account', '')
                    salesperson = self.salesperson_mapper.get_salesperson_by_deposit(deposit_account)
                    
                    if salesperson:
                        if salesperson not in assignment_summary:
                            assignment_summary[salesperson] = []
                        assignment_summary[salesperson].append(customer['customer_name'])
                        result.successful_records += 1
                    else:
                        result.failed_records += 1
                        result.errors.append(
                            f"Could not assign salesperson for customer {customer['customer_name']} "
                            f"with deposit account: {deposit_account}"
                        )
                    
                except Exception as e:
                    result.failed_records += 1
                    result.errors.append(f"Customer {customer.get('customer_name', 'Unknown')}: {str(e)}")
            
            # Log assignment summary
            logging.info("Salesperson Assignment Summary:")
            for salesperson, customers in assignment_summary.items():
                logging.info(f"  {salesperson}: {len(customers)} customers")
            
            result.status = MigrationStatus.COMPLETED if result.failed_records == 0 else MigrationStatus.REQUIRES_REVIEW
            result.end_time = datetime.now()
            
        except Exception as e:
            result.status = MigrationStatus.FAILED
            result.errors.append(str(e))
        
        return result
    
    def generate_migration_report(self) -> Dict[str, Any]:
        """إنشاء تقرير الهجرة"""
        total_records = sum(r.total_records for r in self.migration_results)
        successful_records = sum(r.successful_records for r in self.migration_results)
        failed_records = sum(r.failed_records for r in self.migration_results)
        
        return {
            'migration_summary': {
                'total_entities': len(self.migration_results),
                'total_records': total_records,
                'successful_records': successful_records,
                'failed_records': failed_records,
                'success_rate': f"{(successful_records/total_records*100):.2f}%" if total_records > 0 else "0%"
            },
            'entity_results': [
                {
                    'entity_type': r.entity_type,
                    'total': r.total_records,
                    'successful': r.successful_records,
                    'failed': r.failed_records,
                    'status': r.status.value,
                    'errors': r.errors[:5]  # First 5 errors only
                }
                for r in self.migration_results
            ],
            'salesperson_mapping': {
                'deposit_accounts': self.salesperson_mapper.DEPOSIT_ACCOUNT_MAPPING,
                'regions': self.salesperson_mapper.SALESPERSON_REGIONS
            }
        }


if __name__ == "__main__":
    # Example usage
    print("🚀 TSH ERP Migration System")
    print("=" * 50)
    
    # Initialize migrator
    migrator = TSHERPMigrator("sqlite:///./test.db")
    
    # Start migration (with sample files)
    migration_plan = migrator.start_migration(
        zoho_books_file="zoho_books_export.csv",
        zoho_inventory_file="zoho_inventory_export.csv"
    )
    
    # Generate report
    report = migrator.generate_migration_report()
    
    print("\n📊 Migration Report:")
    print(json.dumps(report, indent=2, default=str))
