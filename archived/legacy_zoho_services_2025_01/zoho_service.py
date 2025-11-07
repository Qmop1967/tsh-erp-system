"""
Zoho API Integration Service for TSH ERP System
خدمة تكامل Zoho API لنظام TSH ERP

Enhanced service for extracting data from Zoho Books and Zoho Inventory
with async support, comprehensive error handling, and data transformation.
"""

import asyncio
import aiohttp
import json
import logging
import requests
import decimal
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import csv
import io
import pandas as pd
from urllib.parse import urlencode

from ..schemas.migration import (
    ZohoConfigCreate,
    ZohoDataExtractRequest,
    MigrationStatusEnum
)
from .config_service import SecureConfigService, ZohoCredentials

logger = logging.getLogger(__name__)


class ZohoAPIError(Exception):
    """خطأ في API Zoho"""
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(self.message)


@dataclass
class ZohoConfig:
    """Zoho API configuration - Legacy sync version"""
    books_api_base: str = "https://www.zohoapis.com/books/v3"
    inventory_api_base: str = "https://www.zohoapis.com/inventory/v1"
    organization_id: str = ""
    access_token: str = ""
    refresh_token: str = ""
    client_id: str = ""
    client_secret: str = ""


class ZohoAsyncService:
    """خدمة Zoho API غير المتزامنة - Modern async version"""
    
    def __init__(self, config: Optional[ZohoConfigCreate] = None):
        if config:
            self.config = config
        else:
            # Load from secure config
            config_service = SecureConfigService()
            creds = config_service.get_zoho_credentials()
            if not creds:
                raise ZohoAPIError("No Zoho credentials found. Please configure credentials first.")
            
            # Convert to ZohoConfigCreate format
            self.config = ZohoConfigCreate(
                organization_id=creds.organization_id,
                access_token=creds.access_token,
                refresh_token=creds.refresh_token,
                client_id=creds.client_id,
                client_secret=creds.client_secret,
                books_api_base=creds.books_api_base,
                inventory_api_base=creds.inventory_api_base
            )
        
        self.session = None
        self.rate_limit_delay = 1.0  # ثانية واحدة بين الطلبات
        self.max_retries = 3
        self.config_service = SecureConfigService()
        
    async def __aenter__(self):
        """بدء جلسة HTTP"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                'Authorization': f'Zoho-oauthtoken {self.config.access_token}',
                'Content-Type': 'application/json'
            }
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """إنهاء جلسة HTTP"""
        if self.session:
            await self.session.close()
    
    async def _make_request(
        self, 
        url: str, 
        method: str = 'GET', 
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        retry_count: int = 0
    ) -> Dict[str, Any]:
        """تنفيذ طلب HTTP مع إعادة المحاولة"""
        try:
            # تأخير للحد من معدل الطلبات
            await asyncio.sleep(self.rate_limit_delay)
            
            if method.upper() == 'GET':
                async with self.session.get(url, params=params) as response:
                    response_data = await response.json()
            elif method.upper() == 'POST':
                async with self.session.post(url, params=params, json=data) as response:
                    response_data = await response.json()
            else:
                raise ZohoAPIError(f"Unsupported HTTP method: {method}")
            
            # التحقق من حالة الاستجابة
            if response.status == 200:
                return response_data
            elif response.status == 429:  # Rate limit exceeded
                if retry_count < self.max_retries:
                    wait_time = (retry_count + 1) * 2  # تأخير متزايد
                    logger.warning(f"Rate limit exceeded, waiting {wait_time}s before retry {retry_count + 1}")
                    await asyncio.sleep(wait_time)
                    return await self._make_request(url, method, params, data, retry_count + 1)
                else:
                    raise ZohoAPIError("Rate limit exceeded, max retries reached", response.status, response_data)
            elif response.status == 401:  # Unauthorized
                # Attempt to refresh access token
                if await self._refresh_access_token():
                    # Retry the request with new access token
                    return await self._make_request(url, method, params, data, retry_count)
                else:
                    raise ZohoAPIError("Invalid or expired access token, and failed to refresh", response.status, response_data)
            else:
                raise ZohoAPIError(f"API request failed: {response.status}", response.status, response_data)
                
        except aiohttp.ClientError as e:
            if retry_count < self.max_retries:
                logger.warning(f"Network error, retrying {retry_count + 1}: {str(e)}")
                await asyncio.sleep((retry_count + 1) * 2)
                return await self._make_request(url, method, params, data, retry_count + 1)
            else:
                raise ZohoAPIError(f"Network error after {self.max_retries} retries: {str(e)}")
    
    async def _refresh_access_token(self) -> bool:
        """تحديث رمز الوصول المنتهي الصلاحية"""
        try:
            refresh_url = "https://accounts.zoho.com/oauth/v2/token"
            refresh_data = {
                'refresh_token': self.config.refresh_token,
                'client_id': self.config.client_id,
                'client_secret': self.config.client_secret,
                'grant_type': 'refresh_token'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(refresh_url, data=refresh_data) as response:
                    if response.status == 200:
                        token_data = await response.json()
                        new_access_token = token_data.get('access_token')
                        
                        if new_access_token:
                            # Update the config with new token
                            self.config.access_token = new_access_token
                            
                            # Update session headers
                            if self.session:
                                self.session.headers.update({
                                    'Authorization': f'Zoho-oauthtoken {new_access_token}'
                                })
                            
                            # Save updated credentials
                            creds = ZohoCredentials(
                                organization_id=self.config.organization_id,
                                access_token=new_access_token,
                                refresh_token=self.config.refresh_token,
                                client_id=self.config.client_id,
                                client_secret=self.config.client_secret,
                                books_api_base=self.config.books_api_base,
                                inventory_api_base=self.config.inventory_api_base
                            )
                            self.config_service.save_zoho_credentials(creds)
                            
                            logger.info("Access token refreshed successfully")
                            return True
                        else:
                            logger.error("No access token in refresh response")
                            return False
                    else:
                        logger.error(f"Token refresh failed: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error refreshing token: {str(e)}")
            return False
    
    # ====== Items Extraction ======
    
    async def extract_items(
        self, 
        page: int = 1, 
        per_page: int = 200,
        filters: Optional[Dict] = None
    ) -> Tuple[List[Dict], bool]:
        """استخراج الأصناف من Zoho Inventory"""
        try:
            params = {
                'organization_id': self.config.organization_id,
                'page': page,
                'per_page': per_page
            }
            
            # إضافة المرشحات إذا توفرت
            if filters:
                params.update(filters)
            
            url = f"{self.config.inventory_api_base}/items"
            response_data = await self._make_request(url, params=params)
            
            items = response_data.get('items', [])
            has_more = response_data.get('page_context', {}).get('has_more_page', False)
            
            # تحويل بيانات الأصناف
            converted_items = []
            for item in items:
                converted_item = await self._convert_zoho_item(item)
                converted_items.append(converted_item)
            
            logger.info(f"Extracted {len(converted_items)} items from page {page}")
            return converted_items, has_more
            
        except Exception as e:
            logger.error(f"Failed to extract items from page {page}: {str(e)}")
            raise ZohoAPIError(f"Items extraction failed: {str(e)}")
    
    def _safe_decimal(self, value, default=0):
        """Safely convert value to Decimal"""
        try:
            if value is None or value == '' or value == 'null':
                return Decimal(str(default))
            return Decimal(str(value))
        except (ValueError, TypeError, decimal.InvalidOperation):
            return Decimal(str(default))
    
    async def _convert_zoho_item(self, zoho_item: Dict) -> Dict:
        """تحويل صنف Zoho إلى تنسيق النظام"""
        return {
            'zoho_item_id': zoho_item.get('item_id'),
            'code': zoho_item.get('sku') or zoho_item.get('item_id'),
            'name_en': zoho_item.get('name', ''),
            'name_ar': zoho_item.get('name', ''),
            'description_en': zoho_item.get('description', ''),
            'description_ar': zoho_item.get('description', ''),
            'brand': zoho_item.get('brand'),
            'model': zoho_item.get('model'),
            'unit_of_measure': zoho_item.get('unit') or 'PCS',
            'cost_price_usd': self._safe_decimal(zoho_item.get('purchase_rate')),
            'selling_price_usd': self._safe_decimal(zoho_item.get('rate')),
            'track_inventory': zoho_item.get('is_inventory_tracked', True),
            'reorder_level': self._safe_decimal(zoho_item.get('reorder_level')),
            'weight': self._safe_decimal(zoho_item.get('weight')) if zoho_item.get('weight') else None,
            'dimensions': zoho_item.get('dimensions'),
            'is_active': zoho_item.get('status') == 'active',
            'specifications': {
                'category': zoho_item.get('category_name'),
                'tax_id': zoho_item.get('tax_id'),
                'hsn_or_sac': zoho_item.get('hsn_or_sac'),
                'item_type': zoho_item.get('item_type'),
                'source': zoho_item.get('source')
            }
        }
    
    async def test_connection(self) -> Dict[str, Any]:
        """اختبار الاتصال مع Zoho APIs"""
        results = {
            'books_api': False,
            'inventory_api': False,
            'organization_id': self.config.organization_id,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # اختبار Books API
            books_url = f"{self.config.books_api_base}/organizations/{self.config.organization_id}"
            books_response = await self._make_request(books_url)
            results['books_api'] = True
            results['books_organization'] = books_response.get('organization', {}).get('name')
            
        except Exception as e:
            results['books_error'] = str(e)
        
        try:
            # اختبار Inventory API
            inventory_url = f"{self.config.inventory_api_base}/organizations/{self.config.organization_id}"
            inventory_response = await self._make_request(inventory_url)
            results['inventory_api'] = True
            results['inventory_organization'] = inventory_response.get('organization', {}).get('name')
            
        except Exception as e:
            results['inventory_error'] = str(e)
        
        return results
    
    # ====== Customers Extraction ======
    
    async def extract_customers(
        self, 
        page: int = 1, 
        per_page: int = 200,
        filters: Optional[Dict] = None
    ) -> Tuple[List[Dict], bool]:
        """استخراج العملاء من Zoho Books"""
        try:
            params = {
                'organization_id': self.config.organization_id,
                'page': page,
                'per_page': per_page
            }
            
            if filters:
                params.update(filters)
            
            url = f"{self.config.books_api_base}/contacts"
            response_data = await self._make_request(url, params=params)
            
            contacts = response_data.get('contacts', [])
            has_more = response_data.get('page_context', {}).get('has_more_page', False)
            
            # فلترة العملاء فقط (استبعاد الموردين)
            customers = [c for c in contacts if c.get('contact_type') == 'customer']
            
            # تحويل بيانات العملاء
            converted_customers = []
            for customer in customers:
                converted_customer = await self._convert_zoho_customer(customer)
                converted_customers.append(converted_customer)
            
            logger.info(f"Extracted {len(converted_customers)} customers from page {page}")
            return converted_customers, has_more
            
        except Exception as e:
            logger.error(f"Failed to extract customers from page {page}: {str(e)}")
            raise ZohoAPIError(f"Customers extraction failed: {str(e)}")
    
    async def _convert_zoho_customer(self, zoho_customer: Dict) -> Dict:
        """تحويل عميل Zoho إلى تنسيق النظام"""
        # استخراج العنوان الأول
        billing_address = {}
        if zoho_customer.get('billing_address'):
            billing_address = zoho_customer['billing_address']
        
        return {
            'zoho_customer_id': zoho_customer.get('contact_id'),
            'code': zoho_customer.get('contact_id'),
            'name_en': zoho_customer.get('contact_name', ''),
            'name_ar': zoho_customer.get('contact_name', ''),
            'email': zoho_customer.get('email'),
            'phone': zoho_customer.get('phone'),
            'mobile': zoho_customer.get('mobile'),
            'address_en': billing_address.get('address', ''),
            'address_ar': billing_address.get('address', ''),
            'city': billing_address.get('city'),
            'region': billing_address.get('state'),
            'postal_code': billing_address.get('zip'),
            'country': billing_address.get('country', 'Iraq'),
            'tax_number': zoho_customer.get('tax_id'),
            'currency': self._convert_currency(zoho_customer.get('currency_code', 'USD')),
            'credit_limit': self._safe_decimal(zoho_customer.get('credit_limit')),
            'payment_terms': zoho_customer.get('payment_terms_label'),
            'outstanding_receivable': self._safe_decimal(zoho_customer.get('outstanding_receivable_amount')),
            'is_active': zoho_customer.get('status') == 'active',
            'zoho_deposit_account': self._extract_deposit_account(zoho_customer)
        }
    
    def _extract_deposit_account(self, zoho_customer: Dict) -> Optional[str]:
        """استخراج حساب الإيداع من بيانات العميل"""
        # البحث عن حساب الإيداع في الحقول المخصصة أو الملاحظات
        custom_fields = zoho_customer.get('custom_fields', [])
        for field in custom_fields:
            if 'deposit' in field.get('label', '').lower():
                return field.get('value')
        
        # البحث في الملاحظات
        notes = zoho_customer.get('notes', '')
        if 'deposit' in notes.lower():
            return notes
        
        return None
    
    # ====== Vendors Extraction ======
    
    async def extract_vendors(
        self, 
        page: int = 1, 
        per_page: int = 200,
        filters: Optional[Dict] = None
    ) -> Tuple[List[Dict], bool]:
        """استخراج الموردين من Zoho Books"""
        try:
            params = {
                'organization_id': self.config.organization_id,
                'page': page,
                'per_page': per_page,
                'contact_type': 'vendor'
            }
            
            if filters:
                params.update(filters)
            
            url = f"{self.config.books_api_base}/contacts"
            response_data = await self._make_request(url, params=params)
            
            contacts = response_data.get('contacts', [])
            has_more = response_data.get('page_context', {}).get('has_more_page', False)
            
            # تحويل بيانات الموردين
            converted_vendors = []
            for vendor in contacts:
                converted_vendor = await self._convert_zoho_vendor(vendor)
                converted_vendors.append(converted_vendor)
            
            logger.info(f"Extracted {len(converted_vendors)} vendors from page {page}")
            return converted_vendors, has_more
            
        except Exception as e:
            logger.error(f"Failed to extract vendors from page {page}: {str(e)}")
            raise ZohoAPIError(f"Vendors extraction failed: {str(e)}")
    
    async def _convert_zoho_vendor(self, zoho_vendor: Dict) -> Dict:
        """تحويل مورد Zoho إلى تنسيق النظام"""
        billing_address = {}
        if zoho_vendor.get('billing_address'):
            billing_address = zoho_vendor['billing_address']
        
        return {
            'zoho_vendor_id': zoho_vendor.get('contact_id'),
            'code': zoho_vendor.get('contact_id'),
            'name_en': zoho_vendor.get('contact_name', ''),
            'name_ar': zoho_vendor.get('contact_name', ''),
            'email': zoho_vendor.get('email'),
            'phone': zoho_vendor.get('phone'),
            'contact_person': zoho_vendor.get('contact_person_details', [{}])[0].get('first_name') if zoho_vendor.get('contact_person_details') else None,
            'address_en': billing_address.get('address', ''),
            'address_ar': billing_address.get('address', ''),
            'city': billing_address.get('city'),
            'country': billing_address.get('country'),
            'tax_number': zoho_vendor.get('tax_id'),
            'currency': self._convert_currency(zoho_vendor.get('currency_code', 'USD')),
            'payment_terms': zoho_vendor.get('payment_terms_label'),
            'outstanding_payable': self._safe_decimal(zoho_vendor.get('outstanding_payable_amount')),
            'is_active': zoho_vendor.get('status') == 'active'
        }
    
    # ====== Stock Extraction ======
    
    async def extract_stock(
        self, 
        page: int = 1, 
        per_page: int = 200,
        warehouse_id: Optional[str] = None
    ) -> Tuple[List[Dict], bool]:
        """استخراج المخزون من Zoho Inventory"""
        try:
            params = {
                'organization_id': self.config.organization_id,
                'page': page,
                'per_page': per_page
            }
            
            if warehouse_id:
                params['warehouse_id'] = warehouse_id
            
            url = f"{self.config.inventory_api_base}/items"
            response_data = await self._make_request(url, params=params)
            
            items = response_data.get('items', [])
            has_more = response_data.get('page_context', {}).get('has_more_page', False)
            
            # استخراج بيانات المخزون من الأصناف
            stock_records = []
            for item in items:
                if item.get('is_inventory_tracked', False):
                    stock_record = await self._convert_zoho_stock(item)
                    stock_records.append(stock_record)
            
            logger.info(f"Extracted {len(stock_records)} stock records from page {page}")
            return stock_records, has_more
            
        except Exception as e:
            logger.error(f"Failed to extract stock from page {page}: {str(e)}")
            raise ZohoAPIError(f"Stock extraction failed: {str(e)}")
    
    async def _convert_zoho_stock(self, zoho_item: Dict) -> Dict:
        """تحويل بيانات مخزون Zoho إلى تنسيق النظام"""
        return {
            'zoho_item_id': zoho_item.get('item_id'),
            'quantity_on_hand': Decimal(str(zoho_item.get('stock_on_hand', 0))),
            'quantity_available': Decimal(str(zoho_item.get('available_stock', 0))),
            'quantity_reserved': Decimal(str(zoho_item.get('reserved_stock', 0))),
            'average_cost': Decimal(str(zoho_item.get('average_cost', 0))),
            'last_cost': Decimal(str(zoho_item.get('purchase_rate', 0))),
            'reorder_level': Decimal(str(zoho_item.get('reorder_level', 0))),
            'warehouse_name': zoho_item.get('warehouse_name', 'Main Warehouse')
        }
    
    # ====== Price Lists Extraction ======
    
    async def extract_price_lists(
        self, 
        page: int = 1, 
        per_page: int = 200
    ) -> Tuple[List[Dict], bool]:
        """استخراج قوائم الأسعار من Zoho Inventory"""
        try:
            params = {
                'organization_id': self.config.organization_id,
                'page': page,
                'per_page': per_page
            }
            
            url = f"{self.config.inventory_api_base}/pricelists"
            response_data = await self._make_request(url, params=params)
            
            price_lists = response_data.get('pricelists', [])
            has_more = response_data.get('page_context', {}).get('has_more_page', False)
            
            # تحويل بيانات قوائم الأسعار
            converted_price_lists = []
            for price_list in price_lists:
                converted_price_list = await self._convert_zoho_price_list(price_list)
                converted_price_lists.append(converted_price_list)
            
            logger.info(f"Extracted {len(converted_price_lists)} price lists from page {page}")
            return converted_price_lists, has_more
            
        except Exception as e:
            logger.error(f"Failed to extract price lists from page {page}: {str(e)}")
            raise ZohoAPIError(f"Price lists extraction failed: {str(e)}")
    
    async def _convert_zoho_price_list(self, zoho_price_list: Dict) -> Dict:
        """تحويل قائمة أسعار Zoho إلى تنسيق النظام"""
        return {
            'zoho_price_list_id': zoho_price_list.get('pricelist_id'),
            'code': zoho_price_list.get('pricelist_id'),
            'name_en': zoho_price_list.get('name', ''),
            'name_ar': zoho_price_list.get('name', ''),
            'description_en': zoho_price_list.get('description', ''),
            'description_ar': zoho_price_list.get('description', ''),
            'currency': self._convert_currency(zoho_price_list.get('currency_code', 'USD')),
            'is_default': zoho_price_list.get('is_default', False),
            'is_active': zoho_price_list.get('status') == 'active',
            'effective_from': self._parse_date(zoho_price_list.get('effective_from')),
            'effective_to': self._parse_date(zoho_price_list.get('effective_to'))
        }
    
    # ====== Utility Methods ======
    
    def _convert_currency(self, zoho_currency: str) -> str:
        """تحويل رمز العملة من Zoho إلى النظام"""
        currency_mapping = {
            'USD': 'USD',
            'IQD': 'IQD',
            'CNY': 'RMB',
            'RMB': 'RMB'
        }
        return currency_mapping.get(zoho_currency, 'USD')
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """تحويل تاريخ من نص إلى datetime"""
        if not date_str:
            return None
        
        try:
            # تجربة تنسيقات مختلفة للتاريخ
            formats = ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%d/%m/%Y', '%m/%d/%Y']
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            
            logger.warning(f"Could not parse date: {date_str}")
            return None
            
        except Exception as e:
            logger.error(f"Error parsing date {date_str}: {str(e)}")
            return None
    
    # ====== Batch Extraction Methods ======
    
    async def extract_all_data(
        self, 
        data_types: List[str], 
        batch_size: int = 200,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, List[Dict]]:
        """استخراج جميع البيانات المطلوبة"""
        results = {}
        
        for data_type in data_types:
            logger.info(f"Starting extraction of {data_type}")
            
            if data_type == 'items':
                results[data_type] = await self._extract_all_items(batch_size, progress_callback)
            elif data_type == 'customers':
                results[data_type] = await self._extract_all_customers(batch_size, progress_callback)
            elif data_type == 'vendors':
                results[data_type] = await self._extract_all_vendors(batch_size, progress_callback)
            elif data_type == 'price_lists':
                results[data_type] = await self._extract_all_price_lists(batch_size, progress_callback)
            elif data_type == 'stock':
                results[data_type] = await self._extract_all_stock(batch_size, progress_callback)
            else:
                logger.warning(f"Unknown data type: {data_type}")
                continue
            
            logger.info(f"Completed extraction of {data_type}: {len(results[data_type])} records")
        
        return results
    
    async def _extract_all_items(self, batch_size: int, progress_callback: Optional[callable] = None) -> List[Dict]:
        """استخراج جميع الأصناف"""
        all_items = []
        page = 1
        has_more = True
        
        while has_more:
            items, has_more = await self.extract_items(page, batch_size)
            all_items.extend(items)
            
            if progress_callback:
                progress_callback('items', page, len(all_items))
            
            page += 1
        
        return all_items
    
    async def _extract_all_customers(self, batch_size: int, progress_callback: Optional[callable] = None) -> List[Dict]:
        """استخراج جميع العملاء"""
        all_customers = []
        page = 1
        has_more = True
        
        while has_more:
            customers, has_more = await self.extract_customers(page, batch_size)
            all_customers.extend(customers)
            
            if progress_callback:
                progress_callback('customers', page, len(all_customers))
            
            page += 1
        
        return all_customers
    
    async def _extract_all_vendors(self, batch_size: int, progress_callback: Optional[callable] = None) -> List[Dict]:
        """استخراج جميع الموردين"""
        all_vendors = []
        page = 1
        has_more = True
        
        while has_more:
            vendors, has_more = await self.extract_vendors(page, batch_size)
            all_vendors.extend(vendors)
            
            if progress_callback:
                progress_callback('vendors', page, len(all_vendors))
            
            page += 1
        
        return all_vendors
    
    async def _extract_all_price_lists(self, batch_size: int, progress_callback: Optional[callable] = None) -> List[Dict]:
        """استخراج جميع قوائم الأسعار"""
        all_price_lists = []
        page = 1
        has_more = True
        
        while has_more:
            price_lists, has_more = await self.extract_price_lists(page, batch_size)
            all_price_lists.extend(price_lists)
            
            if progress_callback:
                progress_callback('price_lists', page, len(all_price_lists))
            
            page += 1
        
        return all_price_lists
    
    async def _extract_all_stock(self, batch_size: int, progress_callback: Optional[callable] = None) -> List[Dict]:
        """استخراج جميع بيانات المخزون"""
        all_stock = []
        page = 1
        has_more = True
        
        while has_more:
            stock, has_more = await self.extract_stock(page, batch_size)
            all_stock.extend(stock)
            
            if progress_callback:
                progress_callback('stock', page, len(all_stock))
            
            page += 1
        
        return all_stock




class ZohoAPIService:
    """خدمة Zoho API التقليدية - Legacy sync version"""
    
    def __init__(self, config: ZohoConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self._setup_session()
    
    def _setup_session(self):
        """Setup HTTP session with default headers"""
        self.session.headers.update({
            'Authorization': f'Zoho-oauthtoken {self.config.access_token}',
            'Content-Type': 'application/json'
        })
    
    def refresh_access_token(self) -> bool:
        """Refresh access token using refresh token"""
        try:
            url = "https://accounts.zoho.com/oauth/v2/token"
            data = {
                'refresh_token': self.config.refresh_token,
                'client_id': self.config.client_id,
                'client_secret': self.config.client_secret,
                'grant_type': 'refresh_token'
            }
            
            response = requests.post(url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self.config.access_token = token_data['access_token']
            self._setup_session()
            
            self.logger.info("Access token refreshed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to refresh access token: {e}")
            return False
    
    def _make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Make API request with error handling and token refresh"""
        try:
            response = self.session.request(method, url, **kwargs)
            
            # Check if token expired
            if response.status_code == 401:
                self.logger.warning("Access token expired, attempting refresh")
                if self.refresh_access_token():
                    response = self.session.request(method, url, **kwargs)
                else:
                    raise Exception("Failed to refresh access token")
            
            response.raise_for_status()
            return response
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request failed: {e}")
            raise
    
    # ====== Zoho Books API Methods ======
    
    def get_books_items(self, page: int = 1, per_page: int = 200) -> Dict[str, Any]:
        """Get items from Zoho Books"""
        url = f"{self.config.books_api_base}/items"
        params = {
            'organization_id': self.config.organization_id,
            'page': page,
            'per_page': per_page
        }
        
        response = self._make_request('GET', url, params=params)
        return response.json()
    
    def get_books_customers(self, page: int = 1, per_page: int = 200) -> Dict[str, Any]:
        """Get customers from Zoho Books"""
        url = f"{self.config.books_api_base}/contacts"
        params = {
            'organization_id': self.config.organization_id,
            'contact_type': 'customer',
            'page': page,
            'per_page': per_page
        }
        
        response = self._make_request('GET', url, params=params)
        return response.json()
    
    def get_books_vendors(self, page: int = 1, per_page: int = 200) -> Dict[str, Any]:
        """Get vendors from Zoho Books"""
        url = f"{self.config.books_api_base}/contacts"
        params = {
            'organization_id': self.config.organization_id,
            'contact_type': 'vendor',
            'page': page,
            'per_page': per_page
        }
        
        response = self._make_request('GET', url, params=params)
        return response.json()
    
    def get_books_receivables(self, customer_id: str) -> Dict[str, Any]:
        """Get receivables for a specific customer"""
        url = f"{self.config.books_api_base}/contacts/{customer_id}/receivables"
        params = {
            'organization_id': self.config.organization_id
        }
        
        response = self._make_request('GET', url, params=params)
        return response.json()
    
    def get_books_payables(self, vendor_id: str) -> Dict[str, Any]:
        """Get payables for a specific vendor"""
        url = f"{self.config.books_api_base}/contacts/{vendor_id}/payables"
        params = {
            'organization_id': self.config.organization_id
        }
        
        response = self._make_request('GET', url, params=params)
        return response.json()
    
    def get_books_price_lists(self) -> Dict[str, Any]:
        """Get price lists from Zoho Books"""
        url = f"{self.config.books_api_base}/pricelists"
        params = {
            'organization_id': self.config.organization_id
        }
        
        response = self._make_request('GET', url, params=params)
        return response.json()
    
    # ====== Zoho Inventory API Methods ======
    
    def get_inventory_items(self, page: int = 1, per_page: int = 200) -> Dict[str, Any]:
        """Get items from Zoho Inventory"""
        url = f"{self.config.inventory_api_base}/items"
        params = {
            'organization_id': self.config.organization_id,
            'page': page,
            'per_page': per_page
        }
        
        response = self._make_request('GET', url, params=params)
        return response.json()
    
    def get_inventory_stock(self, item_id: str) -> Dict[str, Any]:
        """Get stock information for a specific item"""
        url = f"{self.config.inventory_api_base}/items/{item_id}/stock"
        params = {
            'organization_id': self.config.organization_id
        }
        
        response = self._make_request('GET', url, params=params)
        return response.json()
    
    def get_inventory_warehouses(self) -> Dict[str, Any]:
        """Get warehouses from Zoho Inventory"""
        url = f"{self.config.inventory_api_base}/warehouses"
        params = {
            'organization_id': self.config.organization_id
        }
        
        response = self._make_request('GET', url, params=params)
        return response.json()
    
    def test_connection(self) -> Dict[str, Any]:
        """Test connection to Zoho APIs"""
        results = {
            'books_api': False,
            'inventory_api': False,
            'organization_id': self.config.organization_id,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Test Books API
            books_url = f"{self.config.books_api_base}/organizations/{self.config.organization_id}"
            books_response = self._make_request('GET', books_url)
            results['books_api'] = True
            results['books_organization'] = books_response.json().get('organization', {}).get('name')
            
        except Exception as e:
            results['books_error'] = str(e)
        
        try:
            # Test Inventory API
            inventory_url = f"{self.config.inventory_api_base}/organizations/{self.config.organization_id}"
            inventory_response = self._make_request('GET', inventory_url)
            results['inventory_api'] = True
            results['inventory_organization'] = inventory_response.json().get('organization', {}).get('name')
            
        except Exception as e:
            results['inventory_error'] = str(e)
        
        return results



class ZohoDataExtractor:
    """خدمة استخراج البيانات من Zoho"""
    
    def __init__(self, zoho_service: ZohoAPIService):
        self.zoho_service = zoho_service
        self.logger = logging.getLogger(__name__)
    
    def extract_all_items(self) -> List[Dict[str, Any]]:
        """Extract all items from Zoho Books and Inventory"""
        all_items = []
        
        try:
            # Get items from Zoho Books
            page = 1
            while True:
                response = self.zoho_service.get_books_items(page=page)
                items = response.get('items', [])
                
                if not items:
                    break
                
                all_items.extend(items)
                
                # Check if there are more pages
                page_context = response.get('page_context', {})
                if not page_context.get('has_more_page', False):
                    break
                
                page += 1
            
            self.logger.info(f"Extracted {len(all_items)} items from Zoho Books")
            
            # Enhance with inventory data
            for item in all_items:
                try:
                    item_id = item.get('item_id')
                    if item_id:
                        stock_data = self.zoho_service.get_inventory_stock(item_id)
                        item['stock_data'] = stock_data
                except Exception as e:
                    self.logger.warning(f"Failed to get stock for item {item_id}: {e}")
                    item['stock_data'] = {}
            
            return all_items
            
        except Exception as e:
            self.logger.error(f"Failed to extract items: {e}")
            raise
    
    def extract_all_customers(self) -> List[Dict[str, Any]]:
        """Extract all customers from Zoho Books"""
        all_customers = []
        
        try:
            page = 1
            while True:
                response = self.zoho_service.get_books_customers(page=page)
                customers = response.get('contacts', [])
                
                if not customers:
                    break
                
                # Enhance with receivables data
                for customer in customers:
                    try:
                        customer_id = customer.get('contact_id')
                        if customer_id:
                            receivables = self.zoho_service.get_books_receivables(customer_id)
                            customer['receivables'] = receivables
                    except Exception as e:
                        self.logger.warning(f"Failed to get receivables for customer {customer_id}: {e}")
                        customer['receivables'] = {}
                
                all_customers.extend(customers)
                
                # Check if there are more pages
                page_context = response.get('page_context', {})
                if not page_context.get('has_more_page', False):
                    break
                
                page += 1
            
            self.logger.info(f"Extracted {len(all_customers)} customers from Zoho Books")
            return all_customers
            
        except Exception as e:
            self.logger.error(f"Failed to extract customers: {e}")
            raise
    
    def extract_all_vendors(self) -> List[Dict[str, Any]]:
        """Extract all vendors from Zoho Books"""
        all_vendors = []
        
        try:
            page = 1
            while True:
                response = self.zoho_service.get_books_vendors(page=page)
                vendors = response.get('contacts', [])
                
                if not vendors:
                    break
                
                # Enhance with payables data
                for vendor in vendors:
                    try:
                        vendor_id = vendor.get('contact_id')
                        if vendor_id:
                            payables = self.zoho_service.get_books_payables(vendor_id)
                            vendor['payables'] = payables
                    except Exception as e:
                        self.logger.warning(f"Failed to get payables for vendor {vendor_id}: {e}")
                        vendor['payables'] = {}
                
                all_vendors.extend(vendors)
                
                # Check if there are more pages
                page_context = response.get('page_context', {})
                if not page_context.get('has_more_page', False):
                    break
                
                page += 1
            
            self.logger.info(f"Extracted {len(all_vendors)} vendors from Zoho Books")
            return all_vendors
            
        except Exception as e:
            self.logger.error(f"Failed to extract vendors: {e}")
            raise
    
    def extract_price_lists(self) -> List[Dict[str, Any]]:
        """Extract price lists from Zoho Books"""
        try:
            response = self.zoho_service.get_books_price_lists()
            price_lists = response.get('pricelists', [])
            
            self.logger.info(f"Extracted {len(price_lists)} price lists from Zoho Books")
            return price_lists
            
        except Exception as e:
            self.logger.error(f"Failed to extract price lists: {e}")
            raise


class ZohoFileParser:
    """خدمة تحليل ملفات Zoho المصدرة"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def parse_csv_file(self, file_content: bytes, file_type: str) -> List[Dict[str, Any]]:
        """Parse CSV file content based on file type"""
        try:
            # Convert bytes to string
            content_str = file_content.decode('utf-8')
            
            # Use pandas to parse CSV
            df = pd.read_csv(io.StringIO(content_str))
            
            # Convert to list of dictionaries
            data = df.to_dict('records')
            
            # Clean and validate data based on file type
            if file_type == 'items':
                data = self._clean_items_data(data)
            elif file_type == 'customers':
                data = self._clean_customers_data(data)
            elif file_type == 'vendors':
                data = self._clean_vendors_data(data)
            elif file_type == 'stock':
                data = self._clean_stock_data(data)
            elif file_type == 'price_lists':
                data = self._clean_price_lists_data(data)
            
            self.logger.info(f"Parsed {len(data)} records from {file_type} CSV file")
            return data
            
        except Exception as e:
            self.logger.error(f"Failed to parse CSV file: {e}")
            raise
    
    def parse_excel_file(self, file_content: bytes, file_type: str) -> List[Dict[str, Any]]:
        """Parse Excel file content based on file type"""
        try:
            # Use pandas to parse Excel
            df = pd.read_excel(io.BytesIO(file_content))
            
            # Convert to list of dictionaries
            data = df.to_dict('records')
            
            # Clean and validate data based on file type
            if file_type == 'items':
                data = self._clean_items_data(data)
            elif file_type == 'customers':
                data = self._clean_customers_data(data)
            elif file_type == 'vendors':
                data = self._clean_vendors_data(data)
            elif file_type == 'stock':
                data = self._clean_stock_data(data)
            elif file_type == 'price_lists':
                data = self._clean_price_lists_data(data)
            
            self.logger.info(f"Parsed {len(data)} records from {file_type} Excel file")
            return data
            
        except Exception as e:
            self.logger.error(f"Failed to parse Excel file: {e}")
            raise
    
    def _clean_items_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Clean and validate items data"""
        cleaned_data = []
        
        for item in data:
            try:
                # Map common field names
                cleaned_item = {
                    'item_id': str(item.get('Item ID', item.get('id', ''))),
                    'name': str(item.get('Item Name', item.get('name', ''))),
                    'sku': str(item.get('SKU', item.get('sku', ''))),
                    'description': str(item.get('Description', item.get('description', ''))),
                    'unit': str(item.get('Unit', item.get('unit', 'PCS'))),
                    'rate': float(item.get('Rate', item.get('rate', 0))),
                    'currency_code': str(item.get('Currency', item.get('currency_code', 'USD'))),
                    'category': str(item.get('Category', item.get('category', ''))),
                    'status': str(item.get('Status', item.get('status', 'active'))),
                    'is_taxable': bool(item.get('Taxable', item.get('is_taxable', True))),
                    'tax_id': str(item.get('Tax ID', item.get('tax_id', ''))),
                }
                
                # Validate required fields
                if cleaned_item['name'] and cleaned_item['rate'] >= 0:
                    cleaned_data.append(cleaned_item)
                
            except Exception as e:
                self.logger.warning(f"Failed to clean item data: {e}")
                continue
        
        return cleaned_data
    
    def _clean_customers_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Clean and validate customers data"""
        cleaned_data = []
        
        for customer in data:
            try:
                cleaned_customer = {
                    'contact_id': str(customer.get('Contact ID', customer.get('id', ''))),
                    'display_name': str(customer.get('Display Name', customer.get('name', ''))),
                    'company_name': str(customer.get('Company Name', customer.get('company_name', ''))),
                    'email': str(customer.get('Email', customer.get('email', ''))),
                    'phone': str(customer.get('Phone', customer.get('phone', ''))),
                    'currency_code': str(customer.get('Currency', customer.get('currency_code', 'USD'))),
                    'payment_terms': str(customer.get('Payment Terms', customer.get('payment_terms', ''))),
                    'price_list_id': str(customer.get('Price List ID', customer.get('price_list_id', ''))),
                    'outstanding_receivable_amount': float(customer.get('Outstanding Receivables', customer.get('outstanding_receivable_amount', 0))),
                    'status': str(customer.get('Status', customer.get('status', 'active'))),
                    'billing_address': {
                        'address': str(customer.get('Billing Address', '')),
                        'city': str(customer.get('Billing City', '')),
                        'state': str(customer.get('Billing State', '')),
                        'country': str(customer.get('Billing Country', '')),
                        'zip': str(customer.get('Billing Zip', ''))
                    },
                    'shipping_address': {
                        'address': str(customer.get('Shipping Address', '')),
                        'city': str(customer.get('Shipping City', '')),
                        'state': str(customer.get('Shipping State', '')),
                        'country': str(customer.get('Shipping Country', '')),
                        'zip': str(customer.get('Shipping Zip', ''))
                    }
                }
                
                # Validate required fields
                if cleaned_customer['display_name']:
                    cleaned_data.append(cleaned_customer)
                
            except Exception as e:
                self.logger.warning(f"Failed to clean customer data: {e}")
                continue
        
        return cleaned_data
    
    def _clean_vendors_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Clean and validate vendors data"""
        cleaned_data = []
        
        for vendor in data:
            try:
                cleaned_vendor = {
                    'contact_id': str(vendor.get('Contact ID', vendor.get('id', ''))),
                    'display_name': str(vendor.get('Display Name', vendor.get('name', ''))),
                    'company_name': str(vendor.get('Company Name', vendor.get('company_name', ''))),
                    'email': str(vendor.get('Email', vendor.get('email', ''))),
                    'phone': str(vendor.get('Phone', vendor.get('phone', ''))),
                    'currency_code': str(vendor.get('Currency', vendor.get('currency_code', 'USD'))),
                    'payment_terms': str(vendor.get('Payment Terms', vendor.get('payment_terms', ''))),
                    'outstanding_payable_amount': float(vendor.get('Outstanding Payables', vendor.get('outstanding_payable_amount', 0))),
                    'status': str(vendor.get('Status', vendor.get('status', 'active'))),
                    'address': {
                        'address': str(vendor.get('Address', '')),
                        'city': str(vendor.get('City', '')),
                        'state': str(vendor.get('State', '')),
                        'country': str(vendor.get('Country', '')),
                        'zip': str(vendor.get('Zip', ''))
                    }
                }
                
                # Validate required fields
                if cleaned_vendor['display_name']:
                    cleaned_data.append(cleaned_vendor)
                
            except Exception as e:
                self.logger.warning(f"Failed to clean vendor data: {e}")
                continue
        
        return cleaned_data
    
    def _clean_stock_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Clean and validate stock data"""
        cleaned_data = []
        
        for stock in data:
            try:
                cleaned_stock = {
                    'item_id': str(stock.get('Item ID', stock.get('id', ''))),
                    'item_name': str(stock.get('Item Name', stock.get('name', ''))),
                    'warehouse_id': str(stock.get('Warehouse ID', stock.get('warehouse_id', ''))),
                    'warehouse_name': str(stock.get('Warehouse Name', stock.get('warehouse_name', ''))),
                    'quantity_available': float(stock.get('Available Stock', stock.get('quantity_available', 0))),
                    'quantity_on_hand': float(stock.get('Stock on Hand', stock.get('quantity_on_hand', 0))),
                    'reorder_level': float(stock.get('Reorder Level', stock.get('reorder_level', 0))),
                    'unit': str(stock.get('Unit', stock.get('unit', 'PCS'))),
                }
                
                # Validate required fields
                if cleaned_stock['item_id'] and cleaned_stock['quantity_on_hand'] >= 0:
                    cleaned_data.append(cleaned_stock)
                
            except Exception as e:
                self.logger.warning(f"Failed to clean stock data: {e}")
                continue
        
        return cleaned_data
    
    def _clean_price_lists_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Clean and validate price lists data"""
        cleaned_data = []
        
        for price_list in data:
            try:
                cleaned_price_list = {
                    'price_list_id': str(price_list.get('Price List ID', price_list.get('id', ''))),
                    'name': str(price_list.get('Price List Name', price_list.get('name', ''))),
                    'description': str(price_list.get('Description', price_list.get('description', ''))),
                    'currency_code': str(price_list.get('Currency', price_list.get('currency_code', 'USD'))),
                    'rounding_type': str(price_list.get('Rounding Type', price_list.get('rounding_type', 'none'))),
                    'is_default': bool(price_list.get('Is Default', price_list.get('is_default', False))),
                    'status': str(price_list.get('Status', price_list.get('status', 'active'))),
                }
                
                # Validate required fields
                if cleaned_price_list['name']:
                    cleaned_data.append(cleaned_price_list)
                
            except Exception as e:
                self.logger.warning(f"Failed to clean price list data: {e}")
                continue
        
        return cleaned_data
