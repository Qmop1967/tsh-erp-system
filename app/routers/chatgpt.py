"""
ChatGPT API Router for TSH ERP System
Provides endpoints for ChatGPT integration
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime
import json

from app.db.database import get_db
from app.services.chatgpt_service import get_chatgpt_service, ChatMessage
from app.models import User
from app.routers.auth import get_current_user

router = APIRouter(prefix="/chatgpt", tags=["ChatGPT"])

# Request/Response Models
class ChatRequest(BaseModel):
    message: str
    context_type: Optional[str] = "general"  # general, sales, inventory, financial
    conversation_id: Optional[str] = None
    include_user_context: bool = True

class ChatResponse(BaseModel):
    success: bool
    message: str
    conversation_id: str
    timestamp: str
    usage: Optional[Dict[str, int]] = None
    error: Optional[str] = None

class IntentAnalysisRequest(BaseModel):
    message: str

class EmailGenerationRequest(BaseModel):
    subject: str
    recipient_name: str
    context: Dict[str, Any]
    tone: str = "professional"

class ReportSummaryRequest(BaseModel):
    report_data: Dict[str, Any]
    report_type: str

class TranslationRequest(BaseModel):
    text: str
    source_language: str
    target_language: str

class ProductRecommendationRequest(BaseModel):
    customer_id: int


# In-memory conversation storage (consider using Redis or database for production)
conversations: Dict[str, List[ChatMessage]] = {}


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send a message to ChatGPT and get a response
    
    - **message**: User message
    - **context_type**: Type of assistance (general, sales, inventory, financial)
    - **conversation_id**: Optional conversation ID to maintain history
    - **include_user_context**: Include user information in the request
    """
    try:
        chatgpt = get_chatgpt_service()
        
        # Get or create conversation
        conversation_id = request.conversation_id or f"conv_{current_user.id}_{datetime.now().timestamp()}"
        conversation_history = conversations.get(conversation_id, [])
        
        # Prepare user context
        user_context = None
        if request.include_user_context:
            user_context = {
                "user_id": current_user.id,
                "user_name": current_user.name,
                "user_email": current_user.email,
                "user_role": current_user.role.name if current_user.role else "User",
                "branch": current_user.branch.name if current_user.branch else None
            }
        
        # Generate response
        result = await chatgpt.generate_response(
            user_message=request.message,
            conversation_history=conversation_history,
            context_type=request.context_type,
            user_context=user_context
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to get response"))
        
        # Update conversation history
        conversation_history.append(ChatMessage(
            role="user",
            content=request.message,
            timestamp=datetime.now()
        ))
        conversation_history.append(ChatMessage(
            role="assistant",
            content=result["message"],
            timestamp=datetime.now()
        ))
        
        # Keep only last 20 messages
        conversations[conversation_id] = conversation_history[-20:]
        
        return ChatResponse(
            success=True,
            message=result["message"],
            conversation_id=conversation_id,
            timestamp=result["timestamp"],
            usage=result.get("usage")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-intent")
async def analyze_intent(
    request: IntentAnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Analyze the intent of a user message
    
    Returns the detected intent, confidence score, and extracted entities
    """
    try:
        chatgpt = get_chatgpt_service()
        result = await chatgpt.analyze_intent(request.message)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-email")
async def generate_email(
    request: EmailGenerationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate an email using ChatGPT
    
    - **subject**: Email subject
    - **recipient_name**: Recipient's name
    - **context**: Context information for the email
    - **tone**: Email tone (professional, friendly, formal, casual)
    """
    try:
        chatgpt = get_chatgpt_service()
        result = await chatgpt.generate_email(
            subject=request.subject,
            recipient_name=request.recipient_name,
            context=request.context,
            tone=request.tone
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return {
            "success": True,
            "email_body": result["message"],
            "usage": result.get("usage")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-report-summary")
async def generate_report_summary(
    request: ReportSummaryRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate an AI summary of a report
    
    - **report_data**: The report data to summarize
    - **report_type**: Type of report (sales, financial, inventory, etc.)
    """
    try:
        chatgpt = get_chatgpt_service()
        result = await chatgpt.generate_report_summary(
            report_data=request.report_data,
            report_type=request.report_type
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return {
            "success": True,
            "summary": result["message"],
            "usage": result.get("usage")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/translate")
async def translate_text(
    request: TranslationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Translate text between languages
    
    - **text**: Text to translate
    - **source_language**: Source language (en, ar, etc.)
    - **target_language**: Target language
    """
    try:
        chatgpt = get_chatgpt_service()
        result = await chatgpt.translate_text(
            text=request.text,
            source_language=request.source_language,
            target_language=request.target_language
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return {
            "success": True,
            "translated_text": result["message"],
            "usage": result.get("usage")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/product-recommendations")
async def get_product_recommendations(
    request: ProductRecommendationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get AI-powered product recommendations for a customer
    
    - **customer_id**: Customer ID to get recommendations for
    """
    try:
        # Get customer purchase history
        from app.models import Customer, SalesOrder, Product
        
        customer = db.query(Customer).filter(Customer.id == request.customer_id).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # Get customer's order history
        orders = db.query(SalesOrder).filter(
            SalesOrder.customer_id == request.customer_id
        ).limit(10).all()
        
        customer_history = [
            {
                "order_id": order.id,
                "date": order.order_date.isoformat() if order.order_date else None,
                "total": float(order.total_amount) if order.total_amount else 0,
                "items": [
                    {
                        "product_name": item.product.name if item.product else "Unknown",
                        "quantity": item.quantity,
                        "price": float(item.unit_price) if item.unit_price else 0
                    }
                    for item in order.items
                ]
            }
            for order in orders
        ]
        
        # Get current inventory
        products = db.query(Product).filter(Product.is_active == True).limit(50).all()
        current_inventory = [
            {
                "id": product.id,
                "name": product.name,
                "category": product.category.name if product.category else "Uncategorized",
                "price": float(product.selling_price) if product.selling_price else 0,
                "stock": product.stock_quantity or 0
            }
            for product in products
        ]
        
        chatgpt = get_chatgpt_service()
        result = await chatgpt.get_product_recommendations(
            customer_history=customer_history,
            current_inventory=current_inventory
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return {
            "success": True,
            "recommendations": result["message"],
            "usage": result.get("usage")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversation/{conversation_id}")
async def get_conversation_history(
    conversation_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get conversation history
    
    - **conversation_id**: Conversation ID
    """
    conversation = conversations.get(conversation_id, [])
    return {
        "conversation_id": conversation_id,
        "messages": [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat() if msg.timestamp else None
            }
            for msg in conversation
        ]
    }


@router.delete("/conversation/{conversation_id}")
async def clear_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Clear conversation history
    
    - **conversation_id**: Conversation ID to clear
    """
    if conversation_id in conversations:
        del conversations[conversation_id]
        return {"success": True, "message": "Conversation cleared"}
    return {"success": False, "message": "Conversation not found"}


@router.get("/health")
async def chatgpt_health_check():
    """Check if ChatGPT service is configured properly"""
    try:
        chatgpt = get_chatgpt_service()
        return {
            "status": "healthy",
            "model": chatgpt.model,
            "max_tokens": chatgpt.max_tokens,
            "temperature": chatgpt.temperature
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
