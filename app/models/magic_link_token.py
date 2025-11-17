"""
Magic Link Token Model
======================
Database model for magic link authentication tokens.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime

from app.db.database import Base


class MagicLinkToken(Base):
    """Magic Link Token for passwordless authentication"""
    __tablename__ = "magic_link_tokens"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, index=True)
    token = Column(String(255), nullable=False, unique=True, index=True)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
