# Multi-tenancy Models
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.database import Base

class Tenant(Base):
    """Multi-tenant organization model"""
    __tablename__ = "tenants"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    code = Column(String(50), unique=True, nullable=False)  # URL-safe identifier
    domain = Column(String(255))  # Custom domain
    subdomain = Column(String(100), unique=True)  # tenant.tsh-erp.com
    
    # Subscription and billing
    subscription_tier = Column(String(50), default="basic")  # basic, premium, enterprise
    max_users = Column(Integer, default=10)
    max_branches = Column(Integer, default=1)
    max_storage_gb = Column(Integer, default=5)
    
    # Status and metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Settings (JSON)
    settings = Column(Text)  # JSON string for tenant-specific settings
    
    # Relationships
    branches = relationship("Branch", back_populates="tenant")
    users = relationship("User", back_populates="tenant")
    roles = relationship("Role", back_populates="tenant")

class TenantSettings(Base):
    """Tenant-specific configuration settings"""
    __tablename__ = "tenant_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    category = Column(String(100), nullable=False)  # e.g., 'ui', 'features', 'integrations'
    key = Column(String(100), nullable=False)
    value = Column(Text)
    is_encrypted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant")
