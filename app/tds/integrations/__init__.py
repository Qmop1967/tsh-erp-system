"""
TDS External Integrations
========================

This module provides unified interfaces for all external system integrations.

Supported Integrations:
- Zoho (Books, Inventory, CRM)
- Future: Add more integrations here

Author: TSH ERP Team
Date: November 6, 2025
"""

from .base import BaseIntegration

__all__ = ['BaseIntegration']
