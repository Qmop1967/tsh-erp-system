from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from decimal import Decimal


# Customer Schemas
class CustomerBase(BaseModel):
    customer_code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=200)
    company_name: Optional[str] = Field(None, max_length=200)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=255)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    tax_number: Optional[str] = Field(None, max_length=50)
    credit_limit: Decimal = Field(0, ge=0)
    payment_terms: int = Field(0, ge=0)
    discount_percentage: Decimal = Field(0, ge=0, le=100)
    currency: str = Field('IQD', max_length=3, description="Customer currency (USD, EUR, IQD, etc.)")
    portal_language: str = Field('en', max_length=5, description="Portal language (en, ar, etc.)")
    salesperson_id: Optional[int] = Field(None, description="Assigned salesperson ID")
    is_active: bool = True
    notes: Optional[str] = None


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    customer_code: Optional[str] = Field(None, max_length=50)
    name: Optional[str] = Field(None, max_length=200)
    company_name: Optional[str] = Field(None, max_length=200)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=255)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    tax_number: Optional[str] = Field(None, max_length=50)
    credit_limit: Optional[Decimal] = Field(None, ge=0)
    payment_terms: Optional[int] = Field(None, ge=0)
    discount_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    currency: Optional[str] = Field(None, max_length=3, description="Customer currency")
    portal_language: Optional[str] = Field(None, max_length=5, description="Portal language")
    salesperson_id: Optional[int] = Field(None, description="Assigned salesperson ID")
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class Customer(CustomerBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Supplier Schemas
class SupplierBase(BaseModel):
    supplier_code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=200)
    company_name: Optional[str] = Field(None, max_length=200)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=255)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    tax_number: Optional[str] = Field(None, max_length=50)
    payment_terms: int = Field(30, ge=0)
    is_active: bool = True
    notes: Optional[str] = None


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    supplier_code: Optional[str] = Field(None, max_length=50)
    name: Optional[str] = Field(None, max_length=200)
    company_name: Optional[str] = Field(None, max_length=200)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=255)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    tax_number: Optional[str] = Field(None, max_length=50)
    payment_terms: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class Supplier(SupplierBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True
