from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Numeric, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from decimal import Decimal
from app.db.database import Base

class AIConversation(Base):
    __tablename__ = "ai_conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    customer_phone = Column(String, nullable=False)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.now)
    last_activity = Column(DateTime, default=datetime.now)
    message_count = Column(Integer, default=0)
    escalated_at = Column(DateTime)
    escalated_reason = Column(Text)
    
    # Relationships
    messages = relationship("AIConversationMessage", back_populates="conversation")
    customer = relationship("Customer")

class AIConversationMessage(Base):
    __tablename__ = "ai_conversation_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("ai_conversations.id"))
    message_content = Column(Text, nullable=False)
    message_type = Column(String, default="text")
    language = Column(String, default="ar")
    platform = Column(String, default="whatsapp")
    is_from_customer = Column(Boolean, default=True)
    intent = Column(String)
    confidence_score = Column(Numeric(5, 2))
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    conversation = relationship("AIConversation", back_populates="messages")

class AIGeneratedOrder(Base):
    __tablename__ = "ai_generated_orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String, unique=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    customer_phone = Column(String, nullable=False)
    total_amount = Column(Numeric(15, 2))
    delivery_address = Column(Text)
    payment_method = Column(String)
    order_items = Column(JSON)
    language = Column(String, default="ar")
    notes = Column(Text)
    status = Column(String, default="pending_confirmation")
    confirmed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    customer = relationship("Customer")

class AISupportTicket(Base):
    __tablename__ = "ai_support_tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_number = Column(String, unique=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    issue_type = Column(String, nullable=False)
    description = Column(Text)
    priority = Column(String, default="medium")
    language = Column(String, default="ar")
    status = Column(String, default="open")
    assigned_to = Column(Integer, ForeignKey("users.id"))
    resolved_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    customer = relationship("Customer")
    assigned_user = relationship("User") 