"""
FastAPI Router for AI Assistant with Memory
Exposes AI capabilities with conversation memory to the API
"""

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import Optional, List, Dict
from pydantic import BaseModel

from app.db.database import get_db
from app.dependencies.auth import get_current_user
from app.services.ai_service_with_memory import TSHAIServiceWithMemory

router = APIRouter(prefix="/ai", tags=["ai-assistant"])

# Initialize AI service with memory
ai_service = TSHAIServiceWithMemory()


# ===== Request/Response Models =====

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    context: Optional[Dict] = None


class ChatResponse(BaseModel):
    response: str
    conversation_id: str


class ConversationSummaryResponse(BaseModel):
    conversation_id: str
    summary: str


# ===== Customer Support Endpoints =====

@router.post("/customer-support/chat", response_model=ChatResponse)
async def customer_support_chat(
    request: ChatRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Chat with AI customer support assistant
    Maintains conversation history for each customer
    """
    try:
        # Use current_user.id if no customer_id provided
        conversation_id = request.conversation_id or f"customer_support_{current_user.id}"
        
        response = ai_service.customer_support_chat(
            customer_id=current_user.id,
            message=request.message,
            customer_context=request.context
        )
        
        return ChatResponse(
            response=response,
            conversation_id=conversation_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== Sales Assistant Endpoints =====

@router.post("/sales-assistant/chat", response_model=ChatResponse)
async def sales_assistant_chat(
    customer_id: int,
    request: ChatRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Chat with AI sales assistant
    Remembers customer preferences and conversation history
    """
    try:
        response = ai_service.sales_assistant_chat(
            salesperson_id=current_user.id,
            customer_id=customer_id,
            message=request.message,
            context=request.context
        )
        
        conversation_id = f"sales_{current_user.id}_{customer_id}"
        
        return ChatResponse(
            response=response,
            conversation_id=conversation_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== Business Analyst Endpoints =====

@router.post("/business-analyst/chat", response_model=ChatResponse)
async def business_analyst_chat(
    request: ChatRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Chat with AI business analyst
    Analyzes data and provides insights with conversation context
    """
    try:
        response = ai_service.business_analyst_chat(
            user_id=current_user.id,
            query=request.message,
            data_context=request.context
        )
        
        conversation_id = f"analyst_{current_user.id}"
        
        return ChatResponse(
            response=response,
            conversation_id=conversation_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/business-analyst/analyze-sales")
async def analyze_sales_with_memory(
    date_from: str,
    date_to: str,
    follow_up_question: Optional[str] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze sales data with AI
    Can ask follow-up questions that reference previous analysis
    """
    try:
        # Get sales data from database
        from app.services.sales_service import SalesService
        
        # This is a simplified example - adjust based on your actual data structure
        sales_orders = SalesService.get_sales_orders(
            db=db,
            date_from=date_from,
            date_to=date_to
        )
        
        sales_data = {
            "total_sales": sum(order.total_amount for order in sales_orders),
            "order_count": len(sales_orders),
            "date_range": f"{date_from} to {date_to}"
        }
        
        if follow_up_question:
            # User is asking a follow-up question
            message = follow_up_question
        else:
            # Initial analysis request
            message = f"Analyze sales performance from {date_from} to {date_to}"
        
        response = ai_service.business_analyst_chat(
            user_id=current_user.id,
            query=message,
            data_context=sales_data
        )
        
        return {
            "analysis": response,
            "conversation_id": f"analyst_{current_user.id}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== Inventory Assistant Endpoints =====

@router.post("/inventory-assistant/chat", response_model=ChatResponse)
async def inventory_assistant_chat(
    request: ChatRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Chat with AI inventory assistant
    Helps with inventory management and optimization
    """
    try:
        response = ai_service.inventory_assistant_chat(
            user_id=current_user.id,
            query=request.message,
            inventory_context=request.context
        )
        
        conversation_id = f"inventory_{current_user.id}"
        
        return ChatResponse(
            response=response,
            conversation_id=conversation_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== Invoice Assistant Endpoints =====

@router.post("/invoice-assistant/chat", response_model=ChatResponse)
async def invoice_assistant_chat(
    request: ChatRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Chat with AI invoice assistant
    Helps with invoice creation, management, and payment tracking
    """
    try:
        response = ai_service.invoice_assistant_chat(
            user_id=current_user.id,
            query=request.message,
            invoice_context=request.context
        )
        
        conversation_id = f"invoice_{current_user.id}"
        
        return ChatResponse(
            response=response,
            conversation_id=conversation_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== Conversation Management Endpoints =====

@router.get("/conversations", response_model=List[str])
async def get_active_conversations(
    current_user = Depends(get_current_user)
):
    """Get list of active conversation IDs for current user"""
    try:
        all_conversations = ai_service.get_active_conversations()
        
        # Filter conversations for current user
        user_conversations = [
            conv_id for conv_id in all_conversations
            if str(current_user.id) in conv_id
        ]
        
        return user_conversations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations/{conversation_id}/summary", response_model=ConversationSummaryResponse)
async def get_conversation_summary(
    conversation_id: str,
    current_user = Depends(get_current_user)
):
    """Get AI-generated summary of a conversation"""
    try:
        summary = ai_service.get_conversation_summary(conversation_id)
        
        return ConversationSummaryResponse(
            conversation_id=conversation_id,
            summary=summary
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/conversations/{conversation_id}")
async def clear_conversation(
    conversation_id: str,
    current_user = Depends(get_current_user)
):
    """Clear a specific conversation history"""
    try:
        # Verify user has access to this conversation
        if str(current_user.id) not in conversation_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        ai_service.clear_conversation(conversation_id)
        
        return {"message": "Conversation cleared successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/conversations/export")
async def export_conversations(
    output_file: str = "data/ai_conversations_export.json",
    current_user = Depends(get_current_user)
):
    """Export all conversations to a file (admin only)"""
    try:
        # Check if user is admin
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        result = ai_service.export_conversations(output_file)
        
        return {"message": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== Generic Chat Endpoint =====

@router.post("/chat", response_model=ChatResponse)
async def generic_chat(
    request: ChatRequest,
    system_prompt: Optional[str] = None,
    current_user = Depends(get_current_user)
):
    """
    Generic chat endpoint with memory
    Use for custom AI interactions
    """
    try:
        conversation_id = request.conversation_id or f"chat_{current_user.id}"
        
        response = ai_service.chat(
            conversation_id=conversation_id,
            message=request.message,
            system_prompt=system_prompt
        )
        
        return ChatResponse(
            response=response,
            conversation_id=conversation_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
