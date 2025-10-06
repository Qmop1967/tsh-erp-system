"""
ChatGPT Service for TSH ERP System
Integrates OpenAI's ChatGPT API for intelligent assistance
"""

import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import openai
from openai import OpenAI
from pydantic import BaseModel
from sqlalchemy.orm import Session

class ChatMessage(BaseModel):
    role: str  # system, user, assistant
    content: str
    timestamp: Optional[datetime] = None

class ChatGPTService:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.organization = os.getenv("OPENAI_ORG_ID")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o")
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "2000"))
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
        self.max_history = int(os.getenv("CHATGPT_MAX_HISTORY", "10"))
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        # Initialize OpenAI client
        self.client = OpenAI(
            api_key=self.api_key,
            organization=self.organization
        )
        
        # System prompts
        self.system_prompts = {
            "general": """You are an AI assistant for TSH ERP System, a comprehensive business management platform. 
            You help users with:
            - Sales and order management
            - Inventory tracking
            - Customer relationship management
            - Financial reporting
            - HR and employee management
            
            Provide clear, professional, and helpful responses in both English and Arabic.
            Always be polite and efficient.""",
            
            "sales": """You are a sales expert AI assistant for TSH ERP System.
            Help users with:
            - Creating sales orders
            - Managing quotations
            - Processing invoices
            - Tracking payments
            - Customer inquiries
            
            Provide actionable advice and step-by-step guidance.""",
            
            "inventory": """You are an inventory management expert for TSH ERP System.
            Help users with:
            - Stock level tracking
            - Product catalog management
            - Warehouse operations
            - Stock movements
            - Low stock alerts
            
            Provide practical solutions for inventory challenges.""",
            
            "financial": """You are a financial advisor AI for TSH ERP System.
            Help users with:
            - Financial reports
            - Budget planning
            - Cash flow management
            - Expense tracking
            - Accounting queries
            
            Provide accurate financial guidance.""",
        }
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        context_type: str = "general",
        user_context: Optional[Dict[str, Any]] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Send a chat completion request to OpenAI
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            context_type: Type of system prompt (general, sales, inventory, financial)
            user_context: Additional context about the user
            stream: Whether to stream the response
            
        Returns:
            Dictionary with response and metadata
        """
        try:
            # Prepare system message
            system_message = self.system_prompts.get(context_type, self.system_prompts["general"])
            
            # Add user context if provided
            if user_context:
                context_str = f"\n\nUser Context:\n{json.dumps(user_context, indent=2)}"
                system_message += context_str
            
            # Prepare messages
            full_messages = [
                {"role": "system", "content": system_message}
            ] + messages[-self.max_history:]  # Limit history
            
            # Make API call
            response = self.client.chat.completions.create(
                model=self.model,
                messages=full_messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                stream=stream
            )
            
            if stream:
                return {"stream": response}
            else:
                # Extract response
                assistant_message = response.choices[0].message.content
                finish_reason = response.choices[0].finish_reason
                
                return {
                    "success": True,
                    "message": assistant_message,
                    "finish_reason": finish_reason,
                    "model": response.model,
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens
                    },
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to get response from ChatGPT",
                "timestamp": datetime.now().isoformat()
            }
    
    async def generate_response(
        self,
        user_message: str,
        conversation_history: Optional[List[ChatMessage]] = None,
        context_type: str = "general",
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a response for a user message
        
        Args:
            user_message: The user's input message
            conversation_history: Previous messages in the conversation
            context_type: Type of assistance needed
            user_context: User information and context
            
        Returns:
            Response dictionary with message and metadata
        """
        # Prepare messages
        messages = []
        
        # Add conversation history
        if conversation_history:
            for msg in conversation_history[-self.max_history:]:
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        # Get completion
        return await self.chat_completion(
            messages=messages,
            context_type=context_type,
            user_context=user_context
        )
    
    async def analyze_intent(self, message: str) -> Dict[str, Any]:
        """
        Analyze user intent using ChatGPT
        
        Args:
            message: User message to analyze
            
        Returns:
            Dictionary with intent and confidence
        """
        analysis_prompt = f"""Analyze the following user message and determine the intent.
        
        Message: "{message}"
        
        Respond ONLY with a JSON object containing:
        - intent: One of [sales, inventory, financial, hr, support, general]
        - confidence: A number between 0 and 1
        - entities: List of important entities mentioned (products, dates, numbers, etc.)
        - language: Detected language (en or ar)
        
        JSON Response:"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an intent analyzer. Respond only with JSON."},
                    {"role": "user", "content": analysis_prompt}
                ],
                max_tokens=200,
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            return {
                "success": True,
                **result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "intent": "general",
                "confidence": 0.5
            }
    
    async def generate_email(
        self,
        subject: str,
        recipient_name: str,
        context: Dict[str, Any],
        tone: str = "professional"
    ) -> Dict[str, Any]:
        """Generate an email using ChatGPT"""
        prompt = f"""Write a professional email with the following details:
        
        Subject: {subject}
        Recipient: {recipient_name}
        Tone: {tone}
        Context: {json.dumps(context, indent=2)}
        
        Generate the email body:"""
        
        return await self.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            context_type="general"
        )
    
    async def generate_report_summary(
        self,
        report_data: Dict[str, Any],
        report_type: str
    ) -> Dict[str, Any]:
        """Generate a summary of a report"""
        prompt = f"""Analyze the following {report_type} report data and provide a concise summary with key insights:
        
        {json.dumps(report_data, indent=2)}
        
        Provide:
        1. Key highlights
        2. Important trends
        3. Actionable recommendations
        """
        
        return await self.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            context_type="financial"
        )
    
    async def translate_text(
        self,
        text: str,
        source_language: str,
        target_language: str
    ) -> Dict[str, Any]:
        """Translate text between languages"""
        prompt = f"""Translate the following text from {source_language} to {target_language}:
        
        {text}
        
        Translation:"""
        
        return await self.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            context_type="general"
        )
    
    async def get_product_recommendations(
        self,
        customer_history: List[Dict[str, Any]],
        current_inventory: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Get AI-powered product recommendations"""
        prompt = f"""Based on the customer's purchase history and current inventory, recommend products:
        
        Customer History:
        {json.dumps(customer_history, indent=2)}
        
        Available Inventory:
        {json.dumps(current_inventory, indent=2)}
        
        Provide 5 product recommendations with reasoning:"""
        
        return await self.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            context_type="sales"
        )


# Initialize global service instance
_chatgpt_service = None

def get_chatgpt_service() -> ChatGPTService:
    """Get or create ChatGPT service instance"""
    global _chatgpt_service
    if _chatgpt_service is None:
        _chatgpt_service = ChatGPTService()
    return _chatgpt_service
