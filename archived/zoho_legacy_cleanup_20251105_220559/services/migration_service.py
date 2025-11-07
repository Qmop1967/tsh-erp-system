"""
Migration Services for TSH ERP System
خدمات الهجرة لنظام TSH ERP

Service layer for handling data migration from Zoho to TSH ERP.
"""

import json
import logging
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.models.migration import (
    MigrationBatch as MigrationBatchModel, 
    MigrationRecord as MigrationRecordModel, 
    MigrationStatusEnum, 
    MigrationItem as ItemModel, 
    ItemCategory as ItemCategoryModel, 
    PriceList as PriceListModel, 
    PriceListItem as PriceListItemModel, 
    MigrationCustomer as CustomerModel, 
    MigrationVendor as VendorModel, 
    MigrationStock as MigrationStockModel
)
# Add aliases for backwards compatibility
from app.models.migration import (
    MigrationItem as Item,
    MigrationCustomer as Customer, 
    MigrationVendor as Vendor,
    ItemCategory,
    MigrationStock
)
from app.models.user import User
from app.models.branch import Branch
from app.models.warehouse import Warehouse
from app.models.cashflow import SalespersonRegion, RegionEnum
from app.schemas.migration import (
    MigrationBatch, MigrationBatchCreate, MigrationBatchUpdate, MigrationRecord,
    Item, CustomerCreate, VendorCreate, StockCreate, PriceList,
    MigrationStatusEnum as SchemaStatusEnum, ItemCreate, ItemUpdate, 
    ItemCategoryCreate, PriceListCreate, ZohoConfigCreate
)
from app.services.zoho_service import (
    ZohoAPIService, ZohoDataExtractor, ZohoFileParser, ZohoConfig,
    ZohoAsyncService, ZohoAPIError
)


class MigrationService:
    """خدمة الهجرة الرئيسية"""
    
    # Exchange rates configuration
    EXCHANGE_RATES = {
        'USD_TO_IQD': 1500.0,
        'USD_TO_RMB': 7.2,
        'IQD_TO_USD': 1.0 / 1500.0,
        'RMB_TO_USD': 1.0 / 7.2
    }
    
    # Salesperson to deposit account mapping
    SALESPERSON_DEPOSIT_MAPPING = {
        'frati': 'ayad',      # Ayad Al-Baghdadi - Furat regions
        'southi': 'haider',   # Haider - South regions  
        'northi': 'hussien',  # Hussein - North regions
        'dyali': 'ahmed',     # Ahmed - Diyala region
        'westi': 'ayoob'      # Ayoob - West regions
    }
    
    def __init__(self, db: Session, zoho_config: Optional[ZohoConfig] = None):
        self.db = db
        self.logger = logging.getLogger(__name__)
        
        # Initialize Zoho services if config provided
        self.zoho_service = None
        self.zoho_extractor = None
        self.file_parser = ZohoFileParser()
        
        if zoho_config:
            self.zoho_service = ZohoAPIService(zoho_config)
            self.zoho_extractor = ZohoDataExtractor(self.zoho_service)
    
    def set_zoho_config(self, zoho_config: ZohoConfig):
        """Set Zoho API configuration"""
        self.zoho_service = ZohoAPIService(zoho_config)
        self.zoho_extractor = ZohoDataExtractor(self.zoho_service)
    
    def extract_zoho_data(self, data_type: str) -> List[Dict[str, Any]]:
        """Extract data from Zoho API"""
        if not self.zoho_extractor:
            raise ValueError("Zoho configuration not set. Call set_zoho_config() first.")
        
        try:
            if data_type == 'items':
                return self.zoho_extractor.extract_all_items()
            elif data_type == 'customers':
                return self.zoho_extractor.extract_all_customers()
            elif data_type == 'vendors':
                return self.zoho_extractor.extract_all_vendors()
            elif data_type == 'price_lists':
                return self.zoho_extractor.extract_price_lists()
            else:
                raise ValueError(f"Unsupported data type: {data_type}")
                
        except Exception as e:
            self.logger.error(f"Failed to extract {data_type} from Zoho: {e}")
            raise
    
    def parse_uploaded_file(self, file_content: bytes, file_type: str, filename: str) -> List[Dict[str, Any]]:
        """Parse uploaded file content"""
        try:
            if filename.endswith('.csv'):
                return self.file_parser.parse_csv_file(file_content, file_type)
            elif filename.endswith(('.xlsx', '.xls')):
                return self.file_parser.parse_excel_file(file_content, file_type)
            else:
                raise ValueError(f"Unsupported file format: {filename}")
                
        except Exception as e:
            self.logger.error(f"Failed to parse uploaded file {filename}: {e}")
            raise
    
    def migrate_from_zoho_api(self, batch_id: int, data_type: str) -> Dict[str, Any]:
        """Migrate data directly from Zoho API"""
        if not self.zoho_extractor:
            raise ValueError("Zoho configuration not set")
        
        try:
            # Extract data from Zoho
            data = self.extract_zoho_data(data_type)
            
            # Migrate based on data type
            if data_type == 'items':
                results = self.migrate_items_from_data(batch_id, data)
            elif data_type == 'customers':
                results = self.migrate_customers_from_data(batch_id, data)
            elif data_type == 'vendors':
                results = self.migrate_vendors_from_data(batch_id, data)
            elif data_type == 'price_lists':
                results = self.migrate_price_lists_from_data(batch_id, data)
            else:
                raise ValueError(f"Unsupported data type: {data_type}")
            
            return {
                'total_records': len(data),
                'successful_records': len([r for r in results if r.status == MigrationStatusEnum.COMPLETED]),
                'failed_records': len([r for r in results if r.status == MigrationStatusEnum.FAILED]),
                'results': results
            }
            
        except Exception as e:
            self.logger.error(f"Failed to migrate {data_type} from Zoho API: {e}")
            raise
    
    def migrate_from_uploaded_file(self, batch_id: int, file_content: bytes, 
                                  file_type: str, filename: str) -> Dict[str, Any]:
        """Migrate data from uploaded file"""
        try:
            # Parse file content
            data = self.parse_uploaded_file(file_content, file_type, filename)
            
            # Migrate based on file type
            if file_type == 'items':
                results = self.migrate_items_from_data(batch_id, data)
            elif file_type == 'customers':
                results = self.migrate_customers_from_data(batch_id, data)
            elif file_type == 'vendors':
                results = self.migrate_vendors_from_data(batch_id, data)
            elif file_type == 'stock':
                results = self.migrate_stock_from_data(batch_id, data)
            elif file_type == 'price_lists':
                results = self.migrate_price_lists_from_data(batch_id, data)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
            
            return {
                'total_records': len(data),
                'successful_records': len([r for r in results if r.status == MigrationStatusEnum.COMPLETED]),
                'failed_records': len([r for r in results if r.status == MigrationStatusEnum.FAILED]),
                'results': results
            }
            
        except Exception as e:
            self.logger.error(f"Failed to migrate from uploaded file {filename}: {e}")
            raise
    
    def convert_currency(self, amount: float, from_currency: str, to_currency: str) -> Decimal:
        """تحويل العملة"""
        if from_currency == to_currency:
            return Decimal(str(amount))
        
        rate_key = f"{from_currency}_TO_{to_currency}"
        if rate_key in self.EXCHANGE_RATES:
            converted = amount * self.EXCHANGE_RATES[rate_key]
            return Decimal(str(round(converted, 3)))
        
        # Convert via USD if direct rate not available
        if from_currency != 'USD':
            usd_amount = self.convert_currency(amount, from_currency, 'USD')
            return self.convert_currency(float(usd_amount), 'USD', to_currency)
        
        raise ValueError(f"Conversion rate not found: {from_currency} to {to_currency}")
    
    def create_migration_batch(self, batch_name: str, description: str, 
                              source_system: str, created_by: int) -> MigrationBatch:
        """إنشاء دفعة هجرة جديدة"""
        batch_number = f"MIG-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        batch = MigrationBatchModel(
            batch_number=batch_number,
            batch_name=batch_name,
            description=description,
            source_system=source_system,
            created_by=created_by,
            status=MigrationStatusEnum.PENDING
        )
        
        self.db.add(batch)
        self.db.commit()
        self.db.refresh(batch)
        
        self.logger.info(f"Created migration batch: {batch_number}")
        
        # Convert to Pydantic schema
        from app.schemas.migration import MigrationBatch as MigrationBatchSchema
        return MigrationBatchSchema.model_validate(batch)
    
    def start_migration_batch(self, batch_id: int) -> MigrationBatch:
        """بدء تنفيذ دفعة الهجرة"""
        batch = self.db.query(MigrationBatch).filter(MigrationBatch.id == batch_id).first()
        if not batch:
            raise ValueError(f"Migration batch {batch_id} not found")
        
        batch.status = MigrationStatusEnum.IN_PROGRESS
        batch.start_time = datetime.utcnow()
        self.db.commit()
        
        self.logger.info(f"Started migration batch: {batch.batch_number}")
        return batch
    
    def complete_migration_batch(self, batch_id: int, success: bool = True) -> MigrationBatch:
        """إكمال دفعة الهجرة"""
        batch = self.db.query(MigrationBatch).filter(MigrationBatch.id == batch_id).first()
        if not batch:
            raise ValueError(f"Migration batch {batch_id} not found")
        
        # Calculate statistics
        records = self.db.query(MigrationRecord).filter(MigrationRecord.batch_id == batch_id).all()
        batch.total_records = len(records)
        batch.successful_records = sum(1 for r in records if r.status == MigrationStatusEnum.COMPLETED)
        batch.failed_records = sum(1 for r in records if r.status == MigrationStatusEnum.FAILED)
        
        batch.status = MigrationStatusEnum.COMPLETED if success else MigrationStatusEnum.FAILED
        batch.end_time = datetime.utcnow()
        self.db.commit()
        
        self.logger.info(f"Completed migration batch: {batch.batch_number}")
        return batch


class ItemMigrationService(MigrationService):
    """خدمة هجرة الأصناف"""
    
    def migrate_item_categories(self, batch_id: int, categories_data: List[Dict]) -> List[MigrationRecord]:
        """هجرة فئات الأصناف"""
        results = []
        
        for category_data in categories_data:
            record = MigrationRecord(
                batch_id=batch_id,
                entity_type="ITEM_CATEGORY",
                source_id=category_data.get('id', ''),
                source_data=json.dumps(category_data),
                status=MigrationStatusEnum.PENDING
            )
            self.db.add(record)
            self.db.flush()
            
            try:
                # Check if category already exists
                existing = self.db.query(ItemCategory).filter(
                    ItemCategory.code == category_data.get('code', '')
                ).first()
                
                if existing:
                    # Update existing category
                    existing.name_ar = category_data.get('name_ar', existing.name_ar)
                    existing.name_en = category_data.get('name_en', existing.name_en)
                    existing.description_ar = category_data.get('description_ar')
                    existing.description_en = category_data.get('description_en')
                    existing.updated_at = datetime.utcnow()
                    category = existing
                else:
                    # Create new category
                    category = ItemCategory(
                        code=category_data.get('code', f"CAT-{category_data.get('id', '')}"),
                        name_ar=category_data.get('name_ar', category_data.get('name', '')),
                        name_en=category_data.get('name_en', category_data.get('name', '')),
                        description_ar=category_data.get('description_ar'),
                        description_en=category_data.get('description_en'),
                        is_active=category_data.get('is_active', True)
                    )
                    self.db.add(category)
                
                self.db.flush()
                
                record.target_id = category.id
                record.status = MigrationStatusEnum.COMPLETED
                record.processed_at = datetime.utcnow()
                
                self.logger.info(f"Migrated category: {category.name_en}")
                
            except Exception as e:
                record.status = MigrationStatusEnum.FAILED
                record.error_message = str(e)
                record.processed_at = datetime.utcnow()
                self.logger.error(f"Failed to migrate category {category_data.get('name', '')}: {str(e)}")
            
            results.append(record)
        
        self.db.commit()
        return results
    
    def migrate_items(self, batch_id: int, items_data: List[Dict]) -> List[MigrationRecord]:
        """هجرة الأصناف"""
        results = []
        
        for item_data in items_data:
            record = MigrationRecord(
                batch_id=batch_id,
                entity_type="ITEM",
                source_id=item_data.get('item_id', ''),
                source_data=json.dumps(item_data),
                status=MigrationStatusEnum.PENDING
            )
            self.db.add(record)
            self.db.flush()
            
            try:
                # Check if item already exists
                existing = self.db.query(Item).filter(
                    or_(
                        Item.code == item_data.get('sku', ''),
                        Item.zoho_item_id == item_data.get('item_id', '')
                    )
                ).first()
                
                # Convert USD prices to IQD
                cost_price_usd = Decimal(str(item_data.get('cost_price', 0)))
                selling_price_usd = Decimal(str(item_data.get('selling_price', item_data.get('rate', 0))))
                
                cost_price_iqd = self.convert_currency(float(cost_price_usd), 'USD', 'IQD')
                selling_price_iqd = self.convert_currency(float(selling_price_usd), 'USD', 'IQD')
                
                # Find or create category
                category = self._find_or_create_category(item_data.get('category_name', 'OTHER'))
                
                if existing:
                    # Update existing item
                    existing.name_ar = item_data.get('name_ar', existing.name_ar)
                    existing.name_en = item_data.get('name', existing.name_en)
                    existing.description_ar = item_data.get('description_ar')
                    existing.description_en = item_data.get('description', existing.description_en)
                    existing.category_id = category.id if category else existing.category_id
                    existing.cost_price_usd = cost_price_usd
                    existing.cost_price_iqd = cost_price_iqd
                    existing.selling_price_usd = selling_price_usd
                    existing.selling_price_iqd = selling_price_iqd
                    existing.reorder_level = Decimal(str(item_data.get('reorder_level', 0)))
                    existing.updated_at = datetime.utcnow()
                    existing.zoho_last_sync = datetime.utcnow()
                    item = existing
                else:
                    # Create new item
                    item = Item(
                        code=item_data.get('sku', f"ITEM-{item_data.get('item_id', '')}"),
                        name_ar=item_data.get('name_ar', item_data.get('name', '')),
                        name_en=item_data.get('name', ''),
                        description_ar=item_data.get('description_ar'),
                        description_en=item_data.get('description', ''),
                        category_id=category.id if category else None,
                        brand=item_data.get('brand'),
                        model=item_data.get('model'),
                        unit_of_measure=item_data.get('unit', 'PCS'),
                        cost_price_usd=cost_price_usd,
                        cost_price_iqd=cost_price_iqd,
                        selling_price_usd=selling_price_usd,
                        selling_price_iqd=selling_price_iqd,
                        track_inventory=item_data.get('track_inventory', True),
                        reorder_level=Decimal(str(item_data.get('reorder_level', 0))),
                        reorder_quantity=Decimal(str(item_data.get('reorder_quantity', 0))),
                        is_active=item_data.get('status', 'active').lower() == 'active',
                        zoho_item_id=item_data.get('item_id'),
                        zoho_last_sync=datetime.utcnow()
                    )
                    self.db.add(item)
                
                self.db.flush()
                
                record.target_id = item.id
                record.status = MigrationStatusEnum.COMPLETED
                record.processed_at = datetime.utcnow()
                
                self.logger.info(f"Migrated item: {item.name_en} - IQD: {selling_price_iqd}")
                
            except Exception as e:
                record.status = MigrationStatusEnum.FAILED
                record.error_message = str(e)
                record.processed_at = datetime.utcnow()
                self.logger.error(f"Failed to migrate item {item_data.get('name', '')}: {str(e)}")
            
            results.append(record)
        
        self.db.commit()
        return results
    
    def migrate_items_from_data(self, batch_id: int, items_data: List[Dict[str, Any]]) -> List[MigrationRecord]:
        """Migrate items from extracted Zoho data"""
        results = []
        
        for item_data in items_data:
            record = MigrationRecord(
                batch_id=batch_id,
                entity_type="ITEM",
                source_id=item_data.get('item_id', ''),
                source_data=json.dumps(item_data),
                status=MigrationStatusEnum.PENDING
            )
            self.db.add(record)
            self.db.flush()
            
            try:
                # Check if item already exists
                existing = self.db.query(Item).filter(
                    or_(
                        Item.zoho_item_id == item_data.get('item_id'),
                        Item.code == item_data.get('sku', '')
                    )
                ).first()
                
                # Get or create category
                category = None
                if item_data.get('category'):
                    category = self.db.query(ItemCategory).filter(
                        ItemCategory.name_en == item_data.get('category')
                    ).first()
                    
                    if not category:
                        category = ItemCategory(
                            code=f"CAT-{item_data.get('category').replace(' ', '_').upper()}",
                            name_en=item_data.get('category'),
                            name_ar=item_data.get('category'),
                            is_active=True
                        )
                        self.db.add(category)
                        self.db.flush()
                
                # Convert currency
                original_rate = Decimal(str(item_data.get('rate', 0)))
                currency_code = item_data.get('currency_code', 'USD')
                
                if currency_code == 'USD':
                    selling_price_usd = original_rate
                    selling_price_iqd = self.convert_currency(float(original_rate), 'USD', 'IQD')
                else:
                    # Convert to USD first, then to IQD
                    selling_price_usd = self.convert_currency(float(original_rate), currency_code, 'USD')
                    selling_price_iqd = self.convert_currency(float(selling_price_usd), 'USD', 'IQD')
                
                # Assume cost price is 80% of selling price if not provided
                cost_price_usd = selling_price_usd * Decimal('0.8')
                cost_price_iqd = selling_price_iqd * Decimal('0.8')
                
                if existing:
                    # Update existing item
                    existing.name_en = item_data.get('name', existing.name_en)
                    existing.name_ar = item_data.get('name', existing.name_ar)
                    existing.description_en = item_data.get('description', existing.description_en)
                    existing.unit_of_measure = item_data.get('unit', existing.unit_of_measure)
                    existing.cost_price_usd = cost_price_usd
                    existing.cost_price_iqd = cost_price_iqd
                    existing.selling_price_usd = selling_price_usd
                    existing.selling_price_iqd = selling_price_iqd
                    existing.is_active = item_data.get('status', 'active').lower() == 'active'
                    existing.zoho_last_sync = datetime.utcnow()
                    existing.updated_at = datetime.utcnow()
                    item = existing
                else:
                    # Create new item
                    item = Item(
                        code=item_data.get('sku', f"ITEM-{item_data.get('item_id', '')}"),
                        name_ar=item_data.get('name', ''),
                        name_en=item_data.get('name', ''),
                        description_en=item_data.get('description', ''),
                        category_id=category.id if category else None,
                        unit_of_measure=item_data.get('unit', 'PCS'),
                        cost_price_usd=cost_price_usd,
                        cost_price_iqd=cost_price_iqd,
                        selling_price_usd=selling_price_usd,
                        selling_price_iqd=selling_price_iqd,
                        track_inventory=True,
                        is_active=item_data.get('status', 'active').lower() == 'active',
                        zoho_item_id=item_data.get('item_id'),
                        zoho_last_sync=datetime.utcnow()
                    )
                    self.db.add(item)
                
                self.db.flush()
                
                # Handle stock data if available
                if item_data.get('stock_data'):
                    stock_info = item_data['stock_data']
                    if isinstance(stock_info, dict) and stock_info.get('stock_on_hand'):
                        self._create_stock_record(item.id, stock_info)
                
                record.target_id = item.id
                record.status = MigrationStatusEnum.COMPLETED
                record.processed_at = datetime.utcnow()
                
                self.logger.info(f"Migrated item: {item.name_en} - USD: {selling_price_usd}, IQD: {selling_price_iqd}")
                
            except Exception as e:
                record.status = MigrationStatusEnum.FAILED
                record.error_message = str(e)
                record.processed_at = datetime.utcnow()
                self.logger.error(f"Failed to migrate item {item_data.get('name', '')}: {str(e)}")
            
            results.append(record)
        
        self.db.commit()
        return results
    
    def migrate_customers(self, batch_id: int, customers_data: List[Dict]) -> List[MigrationRecord]:
        """هجرة العملاء"""
        results = []
        
        for customer_data in customers_data:
            record = MigrationRecord(
                batch_id=batch_id,
                entity_type="CUSTOMER",
                source_id=customer_data.get('customer_id', ''),
                source_data=json.dumps(customer_data),
                status=MigrationStatusEnum.PENDING
            )
            self.db.add(record)
            self.db.flush()
            
            try:
                # Check if customer already exists
                existing = self.db.query(Customer).filter(
                    or_(
                        Customer.zoho_customer_id == customer_data.get('customer_id'),
                        Customer.code == customer_data.get('customer_name', '')
                    )
                ).first()
                
                # Determine salesperson from deposit account
                deposit_account = customer_data.get('deposit_account', '').lower()
                salesperson_username = None
                
                for deposit_key, username in self.SALESPERSON_DEPOSIT_MAPPING.items():
                    if deposit_key in deposit_account:
                        salesperson_username = username
                        break
                
                salesperson = None
                if salesperson_username:
                    salesperson = self.db.query(User).filter(
                        User.name.ilike(f"%{salesperson_username}%")
                    ).first()
                
                # Find price list
                price_list = None
                if customer_data.get('price_list_name'):
                    price_list = self.db.query(PriceList).filter(
                        PriceList.name_en.ilike(f"%{customer_data.get('price_list_name')}%")
                    ).first()
                
                if existing:
                    # Update existing customer
                    existing.name_ar = customer_data.get('name_ar', existing.name_ar)
                    existing.name_en = customer_data.get('customer_name', existing.name_en)
                    existing.email = customer_data.get('email')
                    existing.phone = customer_data.get('phone')
                    existing.currency = customer_data.get('currency', 'IQD')
                    existing.outstanding_receivable = Decimal(str(customer_data.get('outstanding_receivable', 0)))
                    existing.salesperson_id = salesperson.id if salesperson else existing.salesperson_id
                    existing.price_list_id = price_list.id if price_list else existing.price_list_id
                    existing.zoho_deposit_account = customer_data.get('deposit_account')
                    existing.updated_at = datetime.utcnow()
                    existing.zoho_last_sync = datetime.utcnow()
                    customer = existing
                else:
                    # Create new customer
                    customer = Customer(
                        code=customer_data.get('customer_name', f"CUST-{customer_data.get('customer_id', '')}"),
                        name_ar=customer_data.get('name_ar', customer_data.get('customer_name', '')),
                        name_en=customer_data.get('customer_name', ''),
                        email=customer_data.get('email'),
                        phone=customer_data.get('phone'),
                        address_ar=customer_data.get('address_ar'),
                        address_en=customer_data.get('billing_address', {}).get('address'),
                        city=customer_data.get('billing_address', {}).get('city'),
                        currency=customer_data.get('currency', 'IQD'),
                        outstanding_receivable=Decimal(str(customer_data.get('outstanding_receivable', 0))),
                        salesperson_id=salesperson.id if salesperson else None,
                        price_list_id=price_list.id if price_list else None,
                        is_active=customer_data.get('status', 'active').lower() == 'active',
                        zoho_customer_id=customer_data.get('customer_id'),
                        zoho_deposit_account=customer_data.get('deposit_account'),
                        zoho_last_sync=datetime.utcnow()
                    )
                    self.db.add(customer)
                
                self.db.flush()
                
                record.target_id = customer.id
                record.status = MigrationStatusEnum.COMPLETED
                record.processed_at = datetime.utcnow()
                
                salesperson_info = f" -> {salesperson.name}" if salesperson else " (No salesperson assigned)"
                self.logger.info(f"Migrated customer: {customer.name_en}{salesperson_info}")
                
            except Exception as e:
                record.status = MigrationStatusEnum.FAILED
                record.error_message = str(e)
                record.processed_at = datetime.utcnow()
                self.logger.error(f"Failed to migrate customer {customer_data.get('customer_name', '')}: {str(e)}")
            
            results.append(record)
        
        self.db.commit()
        return results
    
    def migrate_customers_from_data(self, batch_id: int, customers_data: List[Dict[str, Any]]) -> List[MigrationRecord]:
        """Migrate customers from extracted Zoho data"""
        results = []
        
        for customer_data in customers_data:
            record = MigrationRecord(
                batch_id=batch_id,
                entity_type="CUSTOMER",
                source_id=customer_data.get('contact_id', ''),
                source_data=json.dumps(customer_data),
                status=MigrationStatusEnum.PENDING
            )
            self.db.add(record)
            self.db.flush()
            
            try:
                # Check if customer already exists
                existing = self.db.query(Customer).filter(
                    or_(
                        Customer.zoho_contact_id == customer_data.get('contact_id'),
                        Customer.email == customer_data.get('email')
                    )
                ).first()
                
                # Determine salesperson based on deposit account or other criteria
                salesperson_id = self._determine_salesperson(customer_data)
                
                # Handle currency and price list
                currency_code = customer_data.get('currency_code', 'USD')
                price_list_id = None
                
                if customer_data.get('price_list_id'):
                    # Try to find matching price list
                    price_list = self.db.query(PriceList).filter(
                        PriceList.zoho_price_list_id == customer_data.get('price_list_id')
                    ).first()
                    if price_list:
                        price_list_id = price_list.id
                
                # Extract address information
                billing_address = customer_data.get('billing_address', {})
                shipping_address = customer_data.get('shipping_address', {})
                
                if existing:
                    # Update existing customer
                    existing.display_name = customer_data.get('display_name', existing.display_name)
                    existing.company_name = customer_data.get('company_name', existing.company_name)
                    existing.email = customer_data.get('email', existing.email)
                    existing.phone = customer_data.get('phone', existing.phone)
                    existing.currency_code = currency_code
                    existing.salesperson_id = salesperson_id
                    existing.price_list_id = price_list_id
                    existing.outstanding_receivable_amount = Decimal(str(customer_data.get('outstanding_receivable_amount', 0)))
                    existing.zoho_last_sync = datetime.utcnow()
                    existing.updated_at = datetime.utcnow()
                    customer = existing
                else:
                    # Create new customer
                    customer = Customer(
                        display_name=customer_data.get('display_name', customer_data.get('company_name', '')),
                        company_name=customer_data.get('company_name'),
                        email=customer_data.get('email'),
                        phone=customer_data.get('phone'),
                        currency_code=currency_code,
                        payment_terms=customer_data.get('payment_terms', ''),
                        salesperson_id=salesperson_id,
                        price_list_id=price_list_id,
                        outstanding_receivable_amount=Decimal(str(customer_data.get('outstanding_receivable_amount', 0))),
                        billing_address_line1=billing_address.get('address', ''),
                        billing_city=billing_address.get('city', ''),
                        billing_state=billing_address.get('state', ''),
                        billing_country=billing_address.get('country', ''),
                        billing_postal_code=billing_address.get('zip', ''),
                        shipping_address_line1=shipping_address.get('address', ''),
                        shipping_city=shipping_address.get('city', ''),
                        shipping_state=shipping_address.get('state', ''),
                        shipping_country=shipping_address.get('country', ''),
                        shipping_postal_code=shipping_address.get('zip', ''),
                        is_active=customer_data.get('status', 'active').lower() == 'active',
                        zoho_contact_id=customer_data.get('contact_id'),
                        zoho_last_sync=datetime.utcnow()
                    )
                    self.db.add(customer)
                
                self.db.flush()
                
                record.target_id = customer.id
                record.status = MigrationStatusEnum.COMPLETED
                record.processed_at = datetime.utcnow()
                
                self.logger.info(f"Migrated customer: {customer.display_name} - Salesperson: {salesperson_id}")
                
            except Exception as e:
                record.status = MigrationStatusEnum.FAILED
                record.error_message = str(e)
                record.processed_at = datetime.utcnow()
                self.logger.error(f"Failed to migrate customer {customer_data.get('display_name', '')}: {str(e)}")
            
            results.append(record)
        
        self.db.commit()
        return results
    
    def migrate_vendors(self, batch_id: int, vendors_data: List[Dict]) -> List[MigrationRecord]:
        """هجرة الموردين"""
        results = []
        
        for vendor_data in vendors_data:
            record = MigrationRecord(
                batch_id=batch_id,
                entity_type="VENDOR",
                source_id=vendor_data.get('vendor_id', ''),
                source_data=json.dumps(vendor_data),
                status=MigrationStatusEnum.PENDING
            )
            self.db.add(record)
            self.db.flush()
            
            try:
                # Check if vendor already exists
                existing = self.db.query(Vendor).filter(
                    or_(
                        Vendor.zoho_vendor_id == vendor_data.get('vendor_id'),
                        Vendor.code == vendor_data.get('vendor_name', '')
                    )
                ).first()
                
                if existing:
                    # Update existing vendor
                    existing.name_ar = vendor_data.get('name_ar', existing.name_ar)
                    existing.name_en = vendor_data.get('vendor_name', existing.name_en)
                    existing.email = vendor_data.get('email')
                    existing.phone = vendor_data.get('phone')
                    existing.currency = vendor_data.get('currency', 'USD')
                    existing.outstanding_payable = Decimal(str(vendor_data.get('outstanding_payable', 0)))
                    existing.updated_at = datetime.utcnow()
                    existing.zoho_last_sync = datetime.utcnow()
                    vendor = existing
                else:
                    # Create new vendor
                    vendor = Vendor(
                        code=vendor_data.get('vendor_name', f"VEND-{vendor_data.get('vendor_id', '')}"),
                        name_ar=vendor_data.get('name_ar', vendor_data.get('vendor_name', '')),
                        name_en=vendor_data.get('vendor_name', ''),
                        email=vendor_data.get('email'),
                        phone=vendor_data.get('phone'),
                        contact_person=vendor_data.get('contact_person'),
                        address_ar=vendor_data.get('address_ar'),
                        address_en=vendor_data.get('address'),
                        currency=vendor_data.get('currency', 'USD'),
                        outstanding_payable=Decimal(str(vendor_data.get('outstanding_payable', 0))),
                        is_active=vendor_data.get('status', 'active').lower() == 'active',
                        zoho_vendor_id=vendor_data.get('vendor_id'),
                        zoho_last_sync=datetime.utcnow()
                    )
                    self.db.add(vendor)
                
                self.db.flush()
                
                record.target_id = vendor.id
                record.status = MigrationStatusEnum.COMPLETED
                record.processed_at = datetime.utcnow()
                
                self.logger.info(f"Migrated vendor: {vendor.name_en} - {vendor.currency}")
                
            except Exception as e:
                record.status = MigrationStatusEnum.FAILED
                record.error_message = str(e)
                record.processed_at = datetime.utcnow()
                self.logger.error(f"Failed to migrate vendor {vendor_data.get('vendor_name', '')}: {str(e)}")
            
            results.append(record)
        
        self.db.commit()
        return results
    
    def migrate_vendors_from_data(self, batch_id: int, vendors_data: List[Dict[str, Any]]) -> List[MigrationRecord]:
        """Migrate vendors from extracted Zoho data"""
        results = []
        
        for vendor_data in vendors_data:
            record = MigrationRecord(
                batch_id=batch_id,
                entity_type="VENDOR",
                source_id=vendor_data.get('contact_id', ''),
                source_data=json.dumps(vendor_data),
                status=MigrationStatusEnum.PENDING
            )
            self.db.add(record)
            self.db.flush()
            
            try:
                # Check if vendor already exists
                existing = self.db.query(Vendor).filter(
                    or_(
                        Vendor.zoho_contact_id == vendor_data.get('contact_id'),
                        Vendor.email == vendor_data.get('email')
                    )
                ).first()
                
                # Handle currency
                currency_code = vendor_data.get('currency_code', 'USD')
                
                # Extract address information
                address = vendor_data.get('address', {})
                
                if existing:
                    # Update existing vendor
                    existing.display_name = vendor_data.get('display_name', existing.display_name)
                    existing.company_name = vendor_data.get('company_name', existing.company_name)
                    existing.email = vendor_data.get('email', existing.email)
                    existing.phone = vendor_data.get('phone', existing.phone)
                    existing.currency_code = currency_code
                    existing.outstanding_payable_amount = Decimal(str(vendor_data.get('outstanding_payable_amount', 0)))
                    existing.zoho_last_sync = datetime.utcnow()
                    existing.updated_at = datetime.utcnow()
                    vendor = existing
                else:
                    # Create new vendor
                    vendor = Vendor(
                        display_name=vendor_data.get('display_name', vendor_data.get('company_name', '')),
                        company_name=vendor_data.get('company_name'),
                        email=vendor_data.get('email'),
                        phone=vendor_data.get('phone'),
                        currency_code=currency_code,
                        payment_terms=vendor_data.get('payment_terms', ''),
                        outstanding_payable_amount=Decimal(str(vendor_data.get('outstanding_payable_amount', 0))),
                        address_line1=address.get('address', ''),
                        city=address.get('city', ''),
                        state=address.get('state', ''),
                        country=address.get('country', ''),
                        postal_code=address.get('zip', ''),
                        is_active=vendor_data.get('status', 'active').lower() == 'active',
                        zoho_contact_id=vendor_data.get('contact_id'),
                        zoho_last_sync=datetime.utcnow()
                    )
                    self.db.add(vendor)
                
                self.db.flush()
                
                record.target_id = vendor.id
                record.status = MigrationStatusEnum.COMPLETED
                record.processed_at = datetime.utcnow()
                
                self.logger.info(f"Migrated vendor: {vendor.display_name}")
                
            except Exception as e:
                record.status = MigrationStatusEnum.FAILED
                record.error_message = str(e)
                record.processed_at = datetime.utcnow()
                self.logger.error(f"Failed to migrate vendor {vendor_data.get('display_name', '')}: {str(e)}")
            
            results.append(record)
        
        self.db.commit()
        return results
    
    def migrate_stock_from_data(self, batch_id: int, stock_data: List[Dict[str, Any]]) -> List[MigrationRecord]:
        """Migrate stock data from extracted data"""
        results = []
        
        # Get default warehouse
        default_warehouse = self.db.query(Warehouse).first()
        if not default_warehouse:
            raise ValueError("No warehouse found for stock migration")
        
        for stock_item in stock_data:
            record = MigrationRecord(
                batch_id=batch_id,
                entity_type="STOCK",
                source_id=stock_item.get('item_id', ''),
                source_data=json.dumps(stock_item),
                status=MigrationStatusEnum.PENDING
            )
            self.db.add(record)
            self.db.flush()
            
            try:
                # Find the corresponding item
                item = self.db.query(Item).filter(
                    or_(
                        Item.zoho_item_id == stock_item.get('item_id'),
                        Item.name_en == stock_item.get('item_name')
                    )
                ).first()
                
                if not item:
                    raise ValueError(f"Item not found for stock: {stock_item.get('item_name', '')}")
                
                # Find warehouse or use default
                warehouse = default_warehouse
                if stock_item.get('warehouse_name'):
                    warehouse = self.db.query(Warehouse).filter(
                        Warehouse.name == stock_item.get('warehouse_name')
                    ).first() or default_warehouse
                
                # Check if stock record already exists
                existing_stock = self.db.query(MigrationStock).filter(
                    and_(
                        MigrationStock.item_id == item.id,
                        MigrationStock.warehouse_id == warehouse.id
                    )
                ).first()
                
                quantity_on_hand = Decimal(str(stock_item.get('quantity_on_hand', 0)))
                quantity_available = Decimal(str(stock_item.get('quantity_available', quantity_on_hand)))
                reorder_level = Decimal(str(stock_item.get('reorder_level', 0)))
                
                if existing_stock:
                    # Update existing stock
                    existing_stock.quantity_on_hand = quantity_on_hand
                    existing_stock.quantity_available = quantity_available
                    existing_stock.reorder_level = reorder_level
                    existing_stock.updated_at = datetime.utcnow()
                    stock = existing_stock
                else:
                    # Create new stock record
                    stock = MigrationStock(
                        item_id=item.id,
                        warehouse_id=warehouse.id,
                        quantity_on_hand=quantity_on_hand,
                        quantity_available=quantity_available,
                        quantity_reserved=Decimal('0'),
                        reorder_level=reorder_level,
                        unit_of_measure=stock_item.get('unit', 'PCS')
                    )
                    self.db.add(stock)
                
                self.db.flush()
                
                record.target_id = stock.id
                record.status = MigrationStatusEnum.COMPLETED
                record.processed_at = datetime.utcnow()
                
                self.logger.info(f"Migrated stock: {item.name_en} - Qty: {quantity_on_hand}")
                
            except Exception as e:
                record.status = MigrationStatusEnum.FAILED
                record.error_message = str(e)
                record.processed_at = datetime.utcnow()
                self.logger.error(f"Failed to migrate stock {stock_item.get('item_name', '')}: {str(e)}")
            
            results.append(record)
        
        self.db.commit()
        return results
    
    def migrate_price_lists_from_data(self, batch_id: int, price_lists_data: List[Dict[str, Any]]) -> List[MigrationRecord]:
        """Migrate price lists from extracted data"""
        results = []
        
        for price_list_data in price_lists_data:
            record = MigrationRecord(
                batch_id=batch_id,
                entity_type="PRICE_LIST",
                source_id=price_list_data.get('price_list_id', ''),
                source_data=json.dumps(price_list_data),
                status=MigrationStatusEnum.PENDING
            )
            self.db.add(record)
            self.db.flush()
            
            try:
                # Check if price list already exists
                existing = self.db.query(PriceList).filter(
                    PriceList.zoho_price_list_id == price_list_data.get('price_list_id')
                ).first()
                
                currency_code = price_list_data.get('currency_code', 'USD')
                
                if existing:
                    # Update existing price list
                    existing.name = price_list_data.get('name', existing.name)
                    existing.description = price_list_data.get('description', existing.description)
                    existing.currency_code = currency_code
                    existing.is_default = price_list_data.get('is_default', existing.is_default)
                    existing.is_active = price_list_data.get('status', 'active').lower() == 'active'
                    existing.updated_at = datetime.utcnow()
                    price_list = existing
                else:
                    # Create new price list
                    price_list = PriceList(
                        name=price_list_data.get('name', ''),
                        description=price_list_data.get('description', ''),
                        currency_code=currency_code,
                        rounding_type=price_list_data.get('rounding_type', 'none'),
                        is_default=price_list_data.get('is_default', False),
                        is_active=price_list_data.get('status', 'active').lower() == 'active',
                        zoho_price_list_id=price_list_data.get('price_list_id')
                    )
                    self.db.add(price_list)
                
                self.db.flush()
                
                record.target_id = price_list.id
                record.status = MigrationStatusEnum.COMPLETED
                record.processed_at = datetime.utcnow()
                
                self.logger.info(f"Migrated price list: {price_list.name}")
                
            except Exception as e:
                record.status = MigrationStatusEnum.FAILED
                record.error_message = str(e)
                record.processed_at = datetime.utcnow()
                self.logger.error(f"Failed to migrate price list {price_list_data.get('name', '')}: {str(e)}")
            
            results.append(record)
        
        self.db.commit()
        return results
    
    def _find_or_create_category(self, category_name: str) -> Optional[ItemCategory]:
        """البحث عن فئة أو إنشاؤها"""
        if not category_name:
            return None
        
        # Try to find existing category
        category = self.db.query(ItemCategory).filter(
            or_(
                ItemCategory.name_en.ilike(f"%{category_name}%"),
                ItemCategory.name_ar.ilike(f"%{category_name}%")
            )
        ).first()
        
        if not category:
            # Create new category
            category = ItemCategory(
                code=f"CAT-{category_name.upper().replace(' ', '')}",
                name_en=category_name,
                name_ar=category_name,  # TODO: Add proper Arabic translation
                is_active=True
            )
            self.db.add(category)
            self.db.flush()
        
        return category


class CustomerMigrationService(MigrationService):
    """خدمة هجرة العملاء"""
    
    def migrate_price_lists(self, batch_id: int, price_lists_data: List[Dict]) -> List[MigrationRecord]:
        """هجرة قوائم الأسعار"""
        results = []
        
        for price_list_data in price_lists_data:
            record = MigrationRecord(
                batch_id=batch_id,
                entity_type="PRICE_LIST",
                source_id=price_list_data.get('price_list_id', ''),
                source_data=json.dumps(price_list_data),
                status=MigrationStatusEnum.PENDING
            )
            self.db.add(record)
            self.db.flush()
            
            try:
                # Check if price list already exists
                existing = self.db.query(PriceList).filter(
                    or_(
                        PriceList.code == price_list_data.get('name', ''),
                        PriceList.zoho_price_list_id == price_list_data.get('price_list_id', '')
                    )
                ).first()
                
                if existing:
                    # Update existing price list
                    existing.name_ar = price_list_data.get('name_ar', existing.name_ar)
                    existing.name_en = price_list_data.get('name', existing.name_en)
                    existing.description_ar = price_list_data.get('description_ar')
                    existing.description_en = price_list_data.get('description')
                    existing.currency = price_list_data.get('currency', 'IQD')
                    existing.updated_at = datetime.utcnow()
                    existing.zoho_last_sync = datetime.utcnow()
                    price_list = existing
                else:
                    # Create new price list
                    price_list = PriceList(
                        code=price_list_data.get('name', f"PL-{price_list_data.get('price_list_id', '')}"),
                        name_ar=price_list_data.get('name_ar', price_list_data.get('name', '')),
                        name_en=price_list_data.get('name', ''),
                        description_ar=price_list_data.get('description_ar'),
                        description_en=price_list_data.get('description'),
                        currency=price_list_data.get('currency', 'IQD'),
                        is_active=price_list_data.get('status', 'active').lower() == 'active',
                        zoho_price_list_id=price_list_data.get('price_list_id'),
                        zoho_last_sync=datetime.utcnow()
                    )
                    self.db.add(price_list)
                
                self.db.flush()
                
                record.target_id = price_list.id
                record.status = MigrationStatusEnum.COMPLETED
                record.processed_at = datetime.utcnow()
                
                self.logger.info(f"Migrated price list: {price_list.name_en}")
                
            except Exception as e:
                record.status = MigrationStatusEnum.FAILED
                record.error_message = str(e)
                record.processed_at = datetime.utcnow()
                self.logger.error(f"Failed to migrate price list {price_list_data.get('name', '')}: {str(e)}")
            
            results.append(record)
        
        self.db.commit()
        return results
    
    def migrate_customers(self, batch_id: int, customers_data: List[Dict]) -> List[MigrationRecord]:
        """هجرة العملاء مع تعيين مندوبي المبيعات"""
        results = []
        
        for customer_data in customers_data:
            record = MigrationRecord(
                batch_id=batch_id,
                entity_type="CUSTOMER",
                source_id=customer_data.get('customer_id', ''),
                source_data=json.dumps(customer_data),
                status=MigrationStatusEnum.PENDING
            )
            self.db.add(record)
            self.db.flush()
            
            try:
                # Check if customer already exists
                existing = self.db.query(Customer).filter(
                    or_(
                        Customer.zoho_customer_id == customer_data.get('customer_id'),
                        Customer.code == customer_data.get('customer_name', '')
                    )
                ).first()
                
                # Determine salesperson from deposit account
                deposit_account = customer_data.get('deposit_account', '').lower()
                salesperson_username = None
                
                for deposit_key, username in self.SALESPERSON_DEPOSIT_MAPPING.items():
                    if deposit_key in deposit_account:
                        salesperson_username = username
                        break
                
                salesperson = None
                if salesperson_username:
                    salesperson = self.db.query(User).filter(
                        User.name.ilike(f"%{salesperson_username}%")
                    ).first()
                
                # Find price list
                price_list = None
                if customer_data.get('price_list_name'):
                    price_list = self.db.query(PriceList).filter(
                        PriceList.name_en.ilike(f"%{customer_data.get('price_list_name')}%")
                    ).first()
                
                if existing:
                    # Update existing customer
                    existing.name_ar = customer_data.get('name_ar', existing.name_ar)
                    existing.name_en = customer_data.get('customer_name', existing.name_en)
                    existing.email = customer_data.get('email')
                    existing.phone = customer_data.get('phone')
                    existing.currency = customer_data.get('currency', 'IQD')
                    existing.outstanding_receivable = Decimal(str(customer_data.get('outstanding_receivable', 0)))
                    existing.salesperson_id = salesperson.id if salesperson else existing.salesperson_id
                    existing.price_list_id = price_list.id if price_list else existing.price_list_id
                    existing.zoho_deposit_account = customer_data.get('deposit_account')
                    existing.updated_at = datetime.utcnow()
                    existing.zoho_last_sync = datetime.utcnow()
                    customer = existing
                else:
                    # Create new customer
                    customer = Customer(
                        code=customer_data.get('customer_name', f"CUST-{customer_data.get('customer_id', '')}"),
                        name_ar=customer_data.get('name_ar', customer_data.get('customer_name', '')),
                        name_en=customer_data.get('customer_name', ''),
                        email=customer_data.get('email'),
                        phone=customer_data.get('phone'),
                        address_ar=customer_data.get('address_ar'),
                        address_en=customer_data.get('billing_address', {}).get('address'),
                        city=customer_data.get('billing_address', {}).get('city'),
                        currency=customer_data.get('currency', 'IQD'),
                        outstanding_receivable=Decimal(str(customer_data.get('outstanding_receivable', 0))),
                        salesperson_id=salesperson.id if salesperson else None,
                        price_list_id=price_list.id if price_list else None,
                        is_active=customer_data.get('status', 'active').lower() == 'active',
                        zoho_customer_id=customer_data.get('customer_id'),
                        zoho_deposit_account=customer_data.get('deposit_account'),
                        zoho_last_sync=datetime.utcnow()
                    )
                    self.db.add(customer)
                
                self.db.flush()
                
                record.target_id = customer.id
                record.status = MigrationStatusEnum.COMPLETED
                record.processed_at = datetime.utcnow()
                
                salesperson_info = f" -> {salesperson.name}" if salesperson else " (No salesperson assigned)"
                self.logger.info(f"Migrated customer: {customer.name_en}{salesperson_info}")
                
            except Exception as e:
                record.status = MigrationStatusEnum.FAILED
                record.error_message = str(e)
                record.processed_at = datetime.utcnow()
                self.logger.error(f"Failed to migrate customer {customer_data.get('customer_name', '')}: {str(e)}")
            
            results.append(record)
        
        self.db.commit()
        return results
    
    def migrate_vendors(self, batch_id: int, vendors_data: List[Dict]) -> List[MigrationRecord]:
        """هجرة الموردين"""
        results = []
        
        for vendor_data in vendors_data:
            record = MigrationRecord(
                batch_id=batch_id,
                entity_type="VENDOR",
                source_id=vendor_data.get('vendor_id', ''),
                source_data=json.dumps(vendor_data),
                status=MigrationStatusEnum.PENDING
            )
            self.db.add(record)
            self.db.flush()
            
            try:
                # Check if vendor already exists
                existing = self.db.query(Vendor).filter(
                    or_(
                        Vendor.zoho_vendor_id == vendor_data.get('vendor_id'),
                        Vendor.code == vendor_data.get('vendor_name', '')
                    )
                ).first()
                
                if existing:
                    # Update existing vendor
                    existing.name_ar = vendor_data.get('name_ar', existing.name_ar)
                    existing.name_en = vendor_data.get('vendor_name', existing.name_en)
                    existing.email = vendor_data.get('email')
                    existing.phone = vendor_data.get('phone')
                    existing.currency = vendor_data.get('currency', 'USD')
                    existing.outstanding_payable = Decimal(str(vendor_data.get('outstanding_payable', 0)))
                    existing.updated_at = datetime.utcnow()
                    existing.zoho_last_sync = datetime.utcnow()
                    vendor = existing
                else:
                    # Create new vendor
                    vendor = Vendor(
                        code=vendor_data.get('vendor_name', f"VEND-{vendor_data.get('vendor_id', '')}"),
                        name_ar=vendor_data.get('name_ar', vendor_data.get('vendor_name', '')),
                        name_en=vendor_data.get('vendor_name', ''),
                        email=vendor_data.get('email'),
                        phone=vendor_data.get('phone'),
                        contact_person=vendor_data.get('contact_person'),
                        address_ar=vendor_data.get('address_ar'),
                        address_en=vendor_data.get('address'),
                        currency=vendor_data.get('currency', 'USD'),
                        outstanding_payable=Decimal(str(vendor_data.get('outstanding_payable', 0))),
                        is_active=vendor_data.get('status', 'active').lower() == 'active',
                        zoho_vendor_id=vendor_data.get('vendor_id'),
                        zoho_last_sync=datetime.utcnow()
                    )
                    self.db.add(vendor)
                
                self.db.flush()
                
                record.target_id = vendor.id
                record.status = MigrationStatusEnum.COMPLETED
                record.processed_at = datetime.utcnow()
                
                self.logger.info(f"Migrated vendor: {vendor.name_en} - {vendor.currency}")
                
            except Exception as e:
                record.status = MigrationStatusEnum.FAILED
                record.error_message = str(e)
                record.processed_at = datetime.utcnow()
                self.logger.error(f"Failed to migrate vendor {vendor_data.get('vendor_name', '')}: {str(e)}")
            
            results.append(record)
        
        self.db.commit()
        return results


class MigrationReportService:
    """خدمة تقارير الهجرة"""
    
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(__name__)
    
    def get_migration_summary(self, batch_id: Optional[int] = None) -> Dict[str, Any]:
        """الحصول على ملخص الهجرة"""
        query = self.db.query(MigrationBatch)
        if batch_id:
            query = query.filter(MigrationBatch.id == batch_id)
        
        batches = query.all()
        
        total_batches = len(batches)
        total_records = sum(b.total_records or 0 for b in batches)
        successful_records = sum(b.successful_records or 0 for b in batches)
        failed_records = sum(b.failed_records or 0 for b in batches)
        
        return {
            'summary': {
                'total_batches': total_batches,
                'total_records': total_records,
                'successful_records': successful_records,
                'failed_records': failed_records,
                'success_rate': f"{(successful_records/total_records*100):.2f}%" if total_records > 0 else "0%"
            },
            'batches': [
                {
                    'id': batch.id,
                    'batch_number': batch.batch_number,
                    'batch_name': batch.batch_name,
                    'status': batch.status.value,
                    'total_records': batch.total_records or 0,
                    'successful_records': batch.successful_records or 0,
                    'failed_records': batch.failed_records or 0,
                    'start_time': batch.start_time,
                    'end_time': batch.end_time
                }
                for batch in batches
            ]
        }
    
    def get_failed_records(self, batch_id: int) -> List[Dict[str, Any]]:
        """الحصول على السجلات الفاشلة"""
        failed_records = self.db.query(MigrationRecord).filter(
            and_(
                MigrationRecord.batch_id == batch_id,
                MigrationRecord.status == MigrationStatusEnum.FAILED
            )
        ).all()
        
        return [
            {
                'id': record.id,
                'entity_type': record.entity_type,
                'source_id': record.source_id,
                'error_message': record.error_message,
                'source_data': json.loads(record.source_data) if record.source_data else None,
                'processed_at': record.processed_at
            }
            for record in failed_records
        ]
    
    def get_salesperson_customer_mapping(self) -> Dict[str, Any]:
        """الحصول على خريطة ربط مندوبي المبيعات بالعملاء"""
        customers_with_salespeople = self.db.query(Customer, User).join(
            User, Customer.salesperson_id == User.id, isouter=True
        ).all()
        
        mapping = {}
        unmapped_customers = []
        
        for customer, salesperson in customers_with_salespeople:
            if salesperson:
                if salesperson.name not in mapping:
                    mapping[salesperson.name] = []
                mapping[salesperson.name].append({
                    'customer_name': customer.name_en,
                    'customer_code': customer.code,
                    'deposit_account': customer.zoho_deposit_account,
                    'outstanding_receivable': float(customer.outstanding_receivable or 0)
                })
            else:
                unmapped_customers.append({
                    'customer_name': customer.name_en,
                    'customer_code': customer.code,
                    'deposit_account': customer.zoho_deposit_account
                })
        
        return {
            'mapped_customers': mapping,
            'unmapped_customers': unmapped_customers,
            'mapping_summary': {
                'total_customers': len(customers_with_salespeople),
                'mapped_customers': sum(len(customers) for customers in mapping.values()),
                'unmapped_customers': len(unmapped_customers)
            }
        }
    
    # ====== Async Zoho Integration Methods ======
    
    async def extract_zoho_data_async(
        self, 
        zoho_config: ZohoConfigCreate, 
        data_types: List[str],
        progress_callback: Optional[callable] = None
    ) -> Dict[str, List[Dict]]:
        """Extract data from Zoho APIs asynchronously"""
        try:
            async with ZohoAsyncService(zoho_config) as zoho_service:
                # Test connection first
                connection_test = await zoho_service.test_connection()
                if not (connection_test.get('books_api') or connection_test.get('inventory_api')):
                    raise ZohoAPIError("Failed to connect to Zoho APIs")
                
                # Extract data
                results = await zoho_service.extract_all_data(
                    data_types=data_types,
                    batch_size=200,
                    progress_callback=progress_callback
                )
                
                self.logger.info(f"Successfully extracted data from Zoho: {', '.join(data_types)}")
                return results
                
        except Exception as e:
            self.logger.error(f"Failed to extract data from Zoho: {str(e)}")
            raise ZohoAPIError(f"Zoho data extraction failed: {str(e)}")
    
    async def migrate_from_zoho_async(
        self, 
        batch_id: int, 
        zoho_config: ZohoConfigCreate,
        data_types: List[str],
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """Migrate data from Zoho APIs asynchronously"""
        try:
            # Extract data from Zoho
            extracted_data = await self.extract_zoho_data_async(
                zoho_config, data_types, progress_callback
            )
            
            # Migrate each data type
            migration_results = {}
            total_successful = 0
            total_failed = 0
            
            for data_type, data in extracted_data.items():
                self.logger.info(f"Starting migration of {len(data)} {data_type} records")
                
                try:
                    if data_type == 'items':
                        results = self.migrate_items_from_data(batch_id, data)
                    elif data_type == 'customers':
                        results = self.migrate_customers_from_data(batch_id, data)
                    elif data_type == 'vendors':
                        results = self.migrate_vendors_from_data(batch_id, data)
                    elif data_type == 'price_lists':
                        results = self.migrate_price_lists_from_data(batch_id, data)
                    elif data_type == 'stock':
                        results = self.migrate_stock_from_data(batch_id, data)
                    else:
                        self.logger.warning(f"Unsupported data type for migration: {data_type}")
                        continue
                    
                    successful = len([r for r in results if r.status == MigrationStatusEnum.COMPLETED])
                    failed = len([r for r in results if r.status == MigrationStatusEnum.FAILED])
                    
                    migration_results[data_type] = {
                        'total_records': len(data),
                        'successful_records': successful,
                        'failed_records': failed,
                        'success_rate': (successful / len(data)) * 100 if data else 0
                    }
                    
                    total_successful += successful
                    total_failed += failed
                    
                    self.logger.info(
                        f"Completed migration of {data_type}: "
                        f"{successful} successful, {failed} failed"
                    )
                    
                except Exception as e:
                    self.logger.error(f"Failed to migrate {data_type}: {str(e)}")
                    migration_results[data_type] = {
                        'total_records': len(data),
                        'successful_records': 0,
                        'failed_records': len(data),
                        'success_rate': 0,
                        'error': str(e)
                    }
                    total_failed += len(data)
            
            # Update batch status
            batch = self.get_batch(batch_id)
            if batch:
                batch.total_records = total_successful + total_failed
                batch.successful_records = total_successful
                batch.failed_records = total_failed
                
                if total_failed == 0:
                    batch.status = MigrationStatusEnum.COMPLETED
                elif total_successful > 0:
                    batch.status = MigrationStatusEnum.PARTIAL
                else:
                    batch.status = MigrationStatusEnum.FAILED
                
                batch.completed_at = datetime.utcnow()
                self.db.commit()
            
            return {
                'batch_id': batch_id,
                'total_successful': total_successful,
                'total_failed': total_failed,
                'overall_success_rate': (total_successful / (total_successful + total_failed)) * 100 if (total_successful + total_failed) > 0 else 0,
                'data_type_results': migration_results,
                'completion_time': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            # Update batch to failed status
            batch = self.get_batch(batch_id)
            if batch:
                batch.status = MigrationStatusEnum.FAILED
                batch.error_message = str(e)
                batch.completed_at = datetime.utcnow()
                self.db.commit()
            
            self.logger.error(f"Async migration failed for batch {batch_id}: {str(e)}")
            raise
    
    async def test_zoho_connection_async(self, zoho_config: ZohoConfigCreate) -> Dict[str, Any]:
        """Test connection to Zoho APIs asynchronously"""
        try:
            async with ZohoAsyncService(zoho_config) as zoho_service:
                results = await zoho_service.test_connection()
                
                self.logger.info(f"Zoho connection test results: {results}")
                return results
                
        except Exception as e:
            self.logger.error(f"Zoho connection test failed: {str(e)}")
            return {
                'books_api': False,
                'inventory_api': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def extract_and_preview_zoho_data(
        self, 
        zoho_config: ZohoConfigCreate,
        data_type: str,
        limit: int = 10
    ) -> Dict[str, Any]:
        """Extract a preview of data from Zoho for validation"""
        try:
            async with ZohoAsyncService(zoho_config) as zoho_service:
                if data_type == 'items':
                    items, has_more = await zoho_service.extract_items(page=1, per_page=limit)
                    return {
                        'data_type': data_type,
                        'preview_data': items,
                        'has_more_data': has_more,
                        'total_preview_records': len(items)
                    }
                elif data_type == 'customers':
                    customers, has_more = await zoho_service.extract_customers(page=1, per_page=limit)
                    return {
                        'data_type': data_type,
                        'preview_data': customers,
                        'has_more_data': has_more,
                        'total_preview_records': len(customers)
                    }
                elif data_type == 'vendors':
                    vendors, has_more = await zoho_service.extract_vendors(page=1, per_page=limit)
                    return {
                        'data_type': data_type,
                        'preview_data': vendors,
                        'has_more_data': has_more,
                        'total_preview_records': len(vendors)
                    }
                elif data_type == 'stock':
                    stock, has_more = await zoho_service.extract_stock(page=1, per_page=limit)
                    return {
                        'data_type': data_type,
                        'preview_data': stock,
                        'has_more_data': has_more,
                        'total_preview_records': len(stock)
                    }
                elif data_type == 'price_lists':
                    price_lists, has_more = await zoho_service.extract_price_lists(page=1, per_page=limit)
                    return {
                        'data_type': data_type,
                        'preview_data': price_lists,
                        'has_more_data': has_more,
                        'total_preview_records': len(price_lists)
                    }
                else:
                    raise ValueError(f"Unsupported data type: {data_type}")
                    
        except Exception as e:
            self.logger.error(f"Failed to preview {data_type} data from Zoho: {str(e)}")
            raise ZohoAPIError(f"Data preview failed: {str(e)}")
