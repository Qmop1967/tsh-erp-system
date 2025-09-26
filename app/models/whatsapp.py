from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON
from datetime import datetime
from app.db.database import Base

class WhatsAppMessage(Base):
    __tablename__ = "whatsapp_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String, nullable=False, index=True)
    message_type = Column(String, nullable=False)
    content = Column(Text)
    direction = Column(String, nullable=False)  # inbound/outbound
    language = Column(String, default="ar")
    whatsapp_message_id = Column(String, unique=True, index=True)
    media_url = Column(String)
    delivery_status = Column(String, default="sent")
    api_response = Column(JSON)
    status_updated_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)

class WhatsAppBroadcast(Base):
    __tablename__ = "whatsapp_broadcasts"
    
    id = Column(Integer, primary_key=True, index=True)
    broadcast_id = Column(String, unique=True, index=True)
    template_name = Column(String, nullable=False)
    language = Column(String, default="ar")
    total_recipients = Column(Integer, default=0)
    sent_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.now)
    completed_at = Column(DateTime)

class WhatsAppAutoResponse(Base):
    __tablename__ = "whatsapp_auto_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    triggers = Column(JSON)  # List of trigger keywords
    response_text = Column(Text, nullable=False)
    language = Column(String, default="ar")
    active = Column(Boolean, default=True)
    usage_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now) 