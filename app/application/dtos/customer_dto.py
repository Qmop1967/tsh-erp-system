"""
Customer Data Transfer Objects

DTOs for customer data validation and transfer.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator


class CustomerCreateDTO(BaseModel):
    """DTO for creating a new customer."""

    name: str = Field(..., min_length=1, max_length=255, description="Customer name")
    email: Optional[EmailStr] = Field(None, description="Customer email address")
    phone: Optional[str] = Field(None, max_length=20, description="Customer phone number")
    customer_code: Optional[str] = Field(None, max_length=50, description="Unique customer code")

    # Address information
    address_line1: Optional[str] = Field(None, max_length=255, description="Address line 1")
    address_line2: Optional[str] = Field(None, max_length=255, description="Address line 2")
    city: Optional[str] = Field(None, max_length=100, description="City")
    state: Optional[str] = Field(None, max_length=100, description="State/Province")
    country: Optional[str] = Field(None, max_length=100, description="Country")
    postal_code: Optional[str] = Field(None, max_length=20, description="Postal/ZIP code")

    # Business information
    tax_number: Optional[str] = Field(None, max_length=50, description="Tax identification number")
    credit_limit: Optional[float] = Field(0.0, ge=0, description="Credit limit")
    payment_terms: Optional[int] = Field(30, ge=0, description="Payment terms in days")

    # Assignments
    salesperson_id: Optional[int] = Field(None, description="Assigned salesperson ID")
    pricelist_id: Optional[int] = Field(None, description="Assigned pricelist ID")

    # Integration
    zoho_contact_id: Optional[str] = Field(None, max_length=100, description="Zoho contact ID")

    # Status
    is_active: bool = Field(True, description="Whether customer is active")
    notes: Optional[str] = Field(None, description="Additional notes")

    @validator('email')
    def validate_email(cls, v):
        """Validate email format."""
        if v:
            return v.lower()
        return v

    @validator('phone')
    def validate_phone(cls, v):
        """Validate phone number."""
        if v:
            # Remove common separators
            cleaned = v.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
            if not cleaned.replace('+', '').isdigit():
                raise ValueError('Phone number must contain only digits and optional + prefix')
        return v

    class Config:
        from_attributes = True


class CustomerUpdateDTO(BaseModel):
    """DTO for updating an existing customer."""

    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Customer name")
    email: Optional[EmailStr] = Field(None, description="Customer email address")
    phone: Optional[str] = Field(None, max_length=20, description="Customer phone number")

    # Address information
    address_line1: Optional[str] = Field(None, max_length=255, description="Address line 1")
    address_line2: Optional[str] = Field(None, max_length=255, description="Address line 2")
    city: Optional[str] = Field(None, max_length=100, description="City")
    state: Optional[str] = Field(None, max_length=100, description="State/Province")
    country: Optional[str] = Field(None, max_length=100, description="Country")
    postal_code: Optional[str] = Field(None, max_length=20, description="Postal/ZIP code")

    # Business information
    tax_number: Optional[str] = Field(None, max_length=50, description="Tax identification number")
    credit_limit: Optional[float] = Field(None, ge=0, description="Credit limit")
    payment_terms: Optional[int] = Field(None, ge=0, description="Payment terms in days")

    # Assignments
    salesperson_id: Optional[int] = Field(None, description="Assigned salesperson ID")
    pricelist_id: Optional[int] = Field(None, description="Assigned pricelist ID")

    # Integration
    zoho_contact_id: Optional[str] = Field(None, max_length=100, description="Zoho contact ID")

    # Status
    is_active: Optional[bool] = Field(None, description="Whether customer is active")
    notes: Optional[str] = Field(None, description="Additional notes")

    @validator('email')
    def validate_email(cls, v):
        """Validate email format."""
        if v:
            return v.lower()
        return v

    @validator('phone')
    def validate_phone(cls, v):
        """Validate phone number."""
        if v:
            # Remove common separators
            cleaned = v.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
            if not cleaned.replace('+', '').isdigit():
                raise ValueError('Phone number must contain only digits and optional + prefix')
        return v

    class Config:
        from_attributes = True


class CustomerResponseDTO(BaseModel):
    """DTO for customer response."""

    id: int
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    customer_code: Optional[str] = None

    # Address information
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None

    # Business information
    tax_number: Optional[str] = None
    credit_limit: float = 0.0
    payment_terms: int = 30
    balance: float = 0.0

    # Assignments
    salesperson_id: Optional[int] = None
    pricelist_id: Optional[int] = None

    # Integration
    zoho_contact_id: Optional[str] = None

    # Status
    is_active: bool = True
    notes: Optional[str] = None

    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CustomerListResponseDTO(BaseModel):
    """DTO for customer list response with pagination."""

    items: list[CustomerResponseDTO]
    total: int
    skip: int
    limit: int

    class Config:
        from_attributes = True


class CustomerSearchDTO(BaseModel):
    """DTO for customer search parameters."""

    query: Optional[str] = Field(None, description="Search query")
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    salesperson_id: Optional[int] = Field(None, description="Filter by salesperson")
    pricelist_id: Optional[int] = Field(None, description="Filter by pricelist")
    min_balance: Optional[float] = Field(None, ge=0, description="Minimum balance")
    max_balance: Optional[float] = Field(None, ge=0, description="Maximum balance")
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(100, ge=1, le=1000, description="Maximum records to return")

    class Config:
        from_attributes = True


class CustomerSummaryDTO(BaseModel):
    """DTO for customer summary information."""

    id: int
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    customer_code: Optional[str] = None
    balance: float = 0.0
    credit_limit: float = 0.0
    is_active: bool = True

    class Config:
        from_attributes = True
