"""
System Settings Schemas
=======================

Pydantic models for system settings endpoints.
"""

from pydantic import BaseModel
from typing import Dict


class TranslationUpdate(BaseModel):
    """Model for updating translations"""
    translations: Dict[str, Dict[str, str]]  # {language: {key: value}}
