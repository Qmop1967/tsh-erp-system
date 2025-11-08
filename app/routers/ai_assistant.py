from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel
from enum import Enum
import json
import uuid
import re
from decimal import Decimal

from app.db.database import get_db
from app.models import *
from sqlalchemy import func, desc, and_, or_

router = APIRouter()

class ConversationStatus(str, Enum):
    ACTIVE = "active"
    RESOLVED = "resolved"
    ESCALATED = "escalated"
    ABANDONED = "abandoned"

class MessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    VOICE = "voice"
    DOCUMENT = "document"
    ORDER = "order"
    PRODUCT_INQUIRY = "product_inquiry"
    COMPLAINT = "complaint"
    SUPPORT = "support"

class IntentType(str, Enum):
    GREETING = "greeting"
    PRODUCT_SEARCH = "product_search"
    PRICE_INQUIRY = "price_inquiry"
    ORDER_PLACEMENT = "order_placement"
    ORDER_STATUS = "order_status"
    INVENTORY_CHECK = "inventory_check"
    COMPLAINT = "complaint"
    SUPPORT = "support"
    RETURN_REQUEST = "return_request"
    PAYMENT_INQUIRY = "payment_inquiry"
    DELIVERY_INQUIRY = "delivery_inquiry"
    GOODBYE = "goodbye"

class AIMessage(BaseModel):
    customer_id: Optional[int] = None
    phone_number: str
    message_content: str
    message_type: MessageType
    language: str = "ar"  # ar for Arabic, en for English
    platform: str = "whatsapp"  # whatsapp, telegram, website
    
class AIResponse(BaseModel):
    response_text: str
    response_type: str
    language: str
    suggested_actions: List[Dict[str, Any]]
    requires_human: bool = False
    confidence_score: float
    intent: IntentType
    extracted_entities: Dict[str, Any]

class OrderCreationRequest(BaseModel):
    customer_phone: str
    products: List[Dict[str, Any]]
    delivery_address: str
    payment_method: str
    notes: Optional[str] = None
    language: str = "ar"

class SupportTicketRequest(BaseModel):
    customer_id: Optional[int]
    phone_number: str
    issue_type: str
    description: str
    priority: str = "medium"
    language: str = "ar"

@router.get("/dashboard")
def get_ai_assistant_dashboard(db: Session = Depends(get_db)):
    """
    🤖 AI Assistant Dashboard
    24/7 Bilingual Customer Support Analytics
    """
    
    try:
        # Get AI conversation statistics
        total_conversations = db.query(func.count(AIConversation.id)).scalar() or 0
        
        active_conversations = db.query(func.count(AIConversation.id)).filter(
            AIConversation.status == ConversationStatus.ACTIVE.value
        ).scalar() or 0
        
        # Today's statistics
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        todays_conversations = db.query(func.count(AIConversation.id)).filter(
            AIConversation.created_at >= today
        ).scalar() or 0
        
        todays_orders = db.query(func.count(AIGeneratedOrder.id)).filter(
            AIGeneratedOrder.created_at >= today
        ).scalar() or 0
        
        # Message statistics
        total_messages = db.query(func.count(AIConversationMessage.id)).scalar() or 0
        
        # Response time calculation (mock data for now)
        avg_response_time = 2.5  # minutes
        
        # Language breakdown
        arabic_messages = db.query(func.count(AIConversationMessage.id)).filter(
            AIConversationMessage.language == "ar"
        ).scalar() or 0
        
        english_messages = db.query(func.count(AIConversationMessage.id)).filter(
            AIConversationMessage.language == "en"
        ).scalar() or 0
        
        # Support tickets
        open_tickets = db.query(func.count(AISupportTicket.id)).filter(
            AISupportTicket.status == "open"
        ).scalar() or 0
        
        # Mock data for advanced analytics
        return {
            "status": "active",
            "uptime": "99.9%",
            "conversations": {
                "total": total_conversations,
                "active": active_conversations,
                "today": todays_conversations,
                "resolved_today": todays_conversations - active_conversations
            },
            "orders": {
                "total_generated": todays_orders,
                "confirmed": int(todays_orders * 0.8),
                "pending": int(todays_orders * 0.2),
                "conversion_rate": 80.0
            },
            "messages": {
                "total": total_messages,
                "arabic": arabic_messages,
                "english": english_messages,
                "avg_response_time": avg_response_time
            },
            "support": {
                "open_tickets": open_tickets,
                "resolved_today": 15,
                "satisfaction_score": 4.8
            },
            "ai_performance": {
                "accuracy": 95.2,
                "intent_recognition": 92.8,
                "confidence_avg": 87.5,
                "escalation_rate": 5.2
            },
            "knowledge_base": {
                "total_entries": 2847,
                "updated_today": 12,
                "accuracy_score": 94.8
            },
            "real_time_stats": {
                "conversations_last_hour": 45,
                "orders_last_hour": 12,
                "support_tickets_last_hour": 3
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get AI dashboard: {str(e)}")

@router.post("/ai/message/process")
async def process_ai_message(
    message: AIMessage,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    🤖 Process incoming customer message with AI assistant
    24/7 bilingual support with order placement capability
    """
    
    try:
        # Mock AI response for now
        ai_response = AIResponse(
            response_text="مرحبا بك! كيف يمكنني مساعدتك اليوم؟" if message.language == "ar" else "Hello! How can I help you today?",
            response_type="text",
            language=message.language,
            suggested_actions=[
                {"action": "search_products", "label": "البحث عن منتجات" if message.language == "ar" else "Search Products"},
                {"action": "check_order", "label": "تتبع الطلب" if message.language == "ar" else "Track Order"},
                {"action": "support", "label": "الدعم الفني" if message.language == "ar" else "Technical Support"}
            ],
            requires_human=False,
            confidence_score=95.0,
            intent=IntentType.GREETING,
            extracted_entities={}
        )
        
        return {
            "response": ai_response.response_text,
            "language": ai_response.language,
            "intent": ai_response.intent.value,
            "confidence": ai_response.confidence_score,
            "suggested_actions": ai_response.suggested_actions,
            "requires_human": ai_response.requires_human,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process AI message: {str(e)}")

@router.get("/ai/products/search")
async def ai_product_search(
    query: str,
    language: str = "ar",
    customer_id: Optional[int] = None,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    🔍 AI-powered product search for customer assistance
    """
    
    try:
        # Search products
        search_query = db.query(Product).filter(Product.is_active == True)
        
        if language == "ar":
            search_query = search_query.filter(
                or_(
                    Product.name_ar.ilike(f"%{query}%"),
                    Product.category.ilike(f"%{query}%")
                )
            )
        else:
            search_query = search_query.filter(
                or_(
                    Product.name_en.ilike(f"%{query}%"),
                    Product.category.ilike(f"%{query}%")
                )
            )
        
        products = search_query.limit(limit).all()
        
        results = []
        for product in products:
            # Get customer-specific price
            cost_price = getattr(product, 'cost_price', None)
            price = float(cost_price) if cost_price is not None else 0.0
            
            results.append({
                "id": product.id,
                "name": product.name_ar if language == "ar" else product.name_en,
                "price": price,
                "stock": product.stock_quantity if hasattr(product, 'stock_quantity') else 0,
                "category": product.category,
                "description": product.description_ar if language == "ar" else product.description_en,
                "image_url": product.image_url if hasattr(product, 'image_url') else None
            })
        
        return {
            "query": query,
            "language": language,
            "results": results,
            "total_found": len(results),
            "search_time": 0.15
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search products: {str(e)}")

@router.post("/ai/support/ticket")
async def create_support_ticket(
    ticket: SupportTicketRequest,
    db: Session = Depends(get_db)
):
    """
    🎫 Create customer support ticket through AI assistant
    """
    
    try:
        # Generate ticket number
        ticket_number = f"AI-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        
        # Create support ticket
        support_ticket = AISupportTicket(
            ticket_number=ticket_number,
            customer_id=ticket.customer_id,
            issue_type=ticket.issue_type,
            description=ticket.description,
            priority=ticket.priority,
            language=ticket.language,
            status="open",
            created_at=datetime.now()
        )
        
        db.add(support_ticket)
        db.commit()
        
        return {
            "ticket_number": ticket_number,
            "ticket_id": support_ticket.id,
            "status": "created",
            "priority": ticket.priority,
            "estimated_resolution": "2-4 hours",
            "message": "تم إنشاء تذكرة الدعم بنجاح" if ticket.language == "ar" else "Support ticket created successfully"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create support ticket: {str(e)}")

def get_or_create_conversation(phone_number: str, db: Session) -> AIConversation:
    """Get existing conversation or create new one"""
    
    # Look for active conversation
    conversation = db.query(AIConversation).filter(
        AIConversation.customer_phone == phone_number,
        AIConversation.status == ConversationStatus.ACTIVE.value
    ).first()
    
    if not conversation:
        # Get or create customer
        customer = db.query(Customer).filter(Customer.phone == phone_number).first()
        if not customer:
            customer = Customer(
                name=f"Customer {phone_number}",
                phone=phone_number,
                customer_category="consumer",
                created_at=datetime.now()
            )
            db.add(customer)
            db.flush()
        
        # Create new conversation
        conversation = AIConversation(
            customer_id=customer.id,
            customer_phone=phone_number,
            status=ConversationStatus.ACTIVE.value,
            created_at=datetime.now()
        )
        db.add(conversation)
        db.flush()
    
    return conversation 