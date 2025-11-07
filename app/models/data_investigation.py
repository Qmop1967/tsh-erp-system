"""
Data Investigation Models
========================

Models for daily data investigation and monitoring.
نماذج التحقيق اليومي للبيانات

Author: TSH ERP Team
Date: November 7, 2025
"""

from sqlalchemy import Column, Integer, String, JSON, DateTime, Boolean, Text
from sqlalchemy.sql import func
from app.db.database import Base


class DataInvestigationReport(Base):
    """
    Daily data investigation report
    تقرير التحقيق اليومي للبيانات

    Stores comparison between Zoho and TSH ERP data counts.
    """
    __tablename__ = "data_investigation_reports"

    id = Column(Integer, primary_key=True, index=True)

    # Report metadata
    report_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    investigation_type = Column(String(50), default="daily_comparison", nullable=False)

    # Entity counts
    entity_type = Column(String(50), nullable=False)  # products, customers, invoices, etc.
    zoho_count = Column(Integer, nullable=False)
    tsh_erp_count = Column(Integer, nullable=False)
    difference = Column(Integer, nullable=False)
    difference_percentage = Column(String(10))

    # Status
    status = Column(String(20), nullable=False)  # matched, mismatch, error
    is_critical = Column(Boolean, default=False)  # True if difference > threshold

    # Details
    details = Column(JSON, nullable=True)  # Additional investigation details
    error_message = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<DataInvestigationReport(entity={self.entity_type}, status={self.status}, diff={self.difference})>"
