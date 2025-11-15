"""
Zoho Entity Processors
======================

Entity-specific processors for transforming and validating Zoho data.

معالجات الكيانات المخصصة لتحويل والتحقق من بيانات Zoho

Author: TSH ERP Team
Date: November 6, 2025
"""

from .products import ProductProcessor
from .inventory import InventoryProcessor
from .customers import CustomerProcessor
from .orders import OrderProcessor
from .invoices import InvoiceProcessor
from .payments import PaymentProcessor
from .credit_notes import CreditNoteProcessor
from .bills import BillProcessor
from .vendors import VendorProcessor
from .users import UserProcessor

__all__ = [
    'ProductProcessor',
    'InventoryProcessor',
    'CustomerProcessor',
    'OrderProcessor',
    'InvoiceProcessor',
    'PaymentProcessor',
    'CreditNoteProcessor',
    'BillProcessor',
    'VendorProcessor',
    'UserProcessor',
]
