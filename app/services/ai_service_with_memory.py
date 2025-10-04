#!/usr/bin/env python3
"""
AI Service with Conversation Memory for TSH ERP System
Enables Claude to remember context across interactions
"""

from anthropic import Anthropic
import os
from typing import Dict, List, Optional
from datetime import datetime
import json
from collections import defaultdict

class ConversationMemory:
    """Manages conversation history for different contexts"""
    
    def __init__(self, max_messages: int = 50):
        self.conversations = defaultdict(list)
        self.max_messages = max_messages
    
    def add_message(self, conversation_id: str, role: str, content: str):
        """Add a message to conversation history"""
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []
        
        self.conversations[conversation_id].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only recent messages to avoid token limits
        if len(self.conversations[conversation_id]) > self.max_messages:
            self.conversations[conversation_id] = self.conversations[conversation_id][-self.max_messages:]
    
    def get_history(self, conversation_id: str) -> List[Dict]:
        """Get conversation history"""
        if conversation_id not in self.conversations:
            return []
        
        # Return only role and content for Claude API
        return [
            {"role": msg["role"], "content": msg["content"]}
            for msg in self.conversations[conversation_id]
        ]
    
    def clear_history(self, conversation_id: str):
        """Clear conversation history"""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
    
    def save_to_file(self, filepath: str):
        """Save conversations to file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(dict(self.conversations), f, ensure_ascii=False, indent=2)
    
    def load_from_file(self, filepath: str):
        """Load conversations from file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.conversations = defaultdict(list, data)
        except FileNotFoundError:
            pass


class TSHAIServiceWithMemory:
    """AI Service with persistent conversation memory"""
    
    def __init__(self, memory_file: Optional[str] = None):
        self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.model = "claude-3-5-sonnet-20241022"
        self.memory = ConversationMemory()
        self.memory_file = memory_file or "data/ai_conversations.json"
        
        # Load existing conversations
        if os.path.exists(self.memory_file):
            self.memory.load_from_file(self.memory_file)
    
    def chat(self, 
             conversation_id: str, 
             message: str,
             system_prompt: Optional[str] = None,
             max_tokens: int = 1024,
             save_history: bool = True) -> str:
        """
        Chat with Claude with memory of previous messages
        
        Args:
            conversation_id: Unique ID for this conversation (e.g., "user_123_sales")
            message: User's message
            system_prompt: Optional system instructions
            max_tokens: Maximum response tokens
            save_history: Whether to save this exchange to memory
        
        Returns:
            Claude's response
        """
        
        # Get conversation history
        history = self.memory.get_history(conversation_id)
        
        # Add current message to history
        history.append({"role": "user", "content": message})
        
        # Create message with history
        api_params = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": history
        }
        
        if system_prompt:
            api_params["system"] = system_prompt
        
        response = self.client.messages.create(**api_params)
        
        assistant_message = response.content[0].text
        
        # Save to memory
        if save_history:
            self.memory.add_message(conversation_id, "user", message)
            self.memory.add_message(conversation_id, "assistant", assistant_message)
            
            # Save to file
            os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
            self.memory.save_to_file(self.memory_file)
        
        return assistant_message
    
    def clear_conversation(self, conversation_id: str):
        """Clear a specific conversation history"""
        self.memory.clear_history(conversation_id)
        self.memory.save_to_file(self.memory_file)
    
    # ===== Specialized Functions with Memory =====
    
    def customer_support_chat(self, 
                             customer_id: int, 
                             message: str,
                             customer_context: Optional[Dict] = None) -> str:
        """Customer support with memory of previous interactions"""
        
        conversation_id = f"customer_support_{customer_id}"
        
        system_prompt = f"""
        You are a helpful TSH ERP customer support assistant.
        
        Guidelines:
        - Always be polite and professional
        - Respond in Arabic or English based on customer's language
        - Remember previous conversations with this customer
        - Provide accurate information about orders, products, and services
        - If you don't know something, say so and offer to connect them with a human agent
        
        Customer Context:
        {json.dumps(customer_context, ensure_ascii=False) if customer_context else "No context"}
        """
        
        return self.chat(conversation_id, message, system_prompt)
    
    def sales_assistant_chat(self,
                            salesperson_id: int,
                            customer_id: int,
                            message: str,
                            context: Optional[Dict] = None) -> str:
        """Sales assistant with memory of customer interactions"""
        
        conversation_id = f"sales_{salesperson_id}_{customer_id}"
        
        system_prompt = f"""
        You are an AI sales assistant for TSH ERP.
        
        Your role:
        - Help salesperson close deals
        - Provide product recommendations
        - Remember customer preferences and history
        - Suggest upselling and cross-selling opportunities
        - Generate sales pitches and handle objections
        
        Context:
        {json.dumps(context, ensure_ascii=False) if context else "No context"}
        """
        
        return self.chat(conversation_id, message, system_prompt)
    
    def business_analyst_chat(self,
                             user_id: int,
                             query: str,
                             data_context: Optional[Dict] = None) -> str:
        """Business intelligence assistant with conversation memory"""
        
        conversation_id = f"analyst_{user_id}"
        
        system_prompt = f"""
        You are an AI business analyst for TSH ERP System.
        
        Your role:
        - Analyze business data and provide insights
        - Answer questions about sales, inventory, and financial metrics
        - Remember previous analysis requests
        - Provide data-driven recommendations
        - Explain complex metrics in simple terms
        - Support both Arabic and English
        
        Current Data Context:
        {json.dumps(data_context, ensure_ascii=False) if data_context else "No context"}
        """
        
        return self.chat(conversation_id, query, system_prompt, max_tokens=2048)
    
    def inventory_assistant_chat(self,
                                user_id: int,
                                query: str,
                                inventory_context: Optional[Dict] = None) -> str:
        """Inventory management assistant with memory"""
        
        conversation_id = f"inventory_{user_id}"
        
        system_prompt = f"""
        You are an AI inventory management assistant for TSH ERP.
        
        Your role:
        - Help manage inventory levels
        - Provide reorder recommendations
        - Analyze stock movements and trends
        - Remember previous inventory discussions
        - Suggest optimizations
        - Alert about potential issues
        
        Inventory Context:
        {json.dumps(inventory_context, ensure_ascii=False) if inventory_context else "No context"}
        """
        
        return self.chat(conversation_id, query, system_prompt)
    
    def invoice_assistant_chat(self,
                              user_id: int,
                              query: str,
                              invoice_context: Optional[Dict] = None) -> str:
        """Invoice processing assistant with memory"""
        
        conversation_id = f"invoice_{user_id}"
        
        system_prompt = f"""
        You are an AI invoice assistant for TSH ERP.
        
        Your role:
        - Help with invoice creation and management
        - Generate invoice descriptions and emails
        - Track payment status
        - Remember previous invoice discussions
        - Provide payment reminders
        - Answer invoice-related questions
        
        Invoice Context:
        {json.dumps(invoice_context, ensure_ascii=False) if invoice_context else "No context"}
        """
        
        return self.chat(conversation_id, query, system_prompt)
    
    # ===== Utility Functions =====
    
    def get_conversation_summary(self, conversation_id: str) -> str:
        """Get AI-generated summary of a conversation"""
        
        history = self.memory.get_history(conversation_id)
        
        if not history:
            return "No conversation history available."
        
        # Create summary prompt
        conversation_text = "\n\n".join([
            f"{msg['role'].upper()}: {msg['content']}"
            for msg in history
        ])
        
        summary_prompt = f"""
        Summarize this conversation in both Arabic and English:
        
        {conversation_text}
        
        Provide:
        1. Main topics discussed
        2. Key decisions or outcomes
        3. Action items (if any)
        4. Important context for future conversations
        """
        
        # Don't save summary request to history
        return self.chat(f"{conversation_id}_summary", summary_prompt, save_history=False)
    
    def export_conversations(self, output_file: str):
        """Export all conversations to a file"""
        self.memory.save_to_file(output_file)
        return f"Conversations exported to {output_file}"
    
    def get_active_conversations(self) -> List[str]:
        """Get list of active conversation IDs"""
        return list(self.memory.conversations.keys())


# ===== Example Usage Functions =====

def example_customer_support():
    """Example: Customer support with memory"""
    ai_service = TSHAIServiceWithMemory()
    
    customer_id = 123
    
    # First interaction
    response1 = ai_service.customer_support_chat(
        customer_id=customer_id,
        message="مرحباً، أريد معرفة حالة طلبي رقم 5678",
        customer_context={
            "name": "أحمد محمد",
            "orders": [{"order_id": 5678, "status": "shipped"}]
        }
    )
    print("Response 1:", response1)
    
    # Second interaction - Claude remembers the previous order discussion
    response2 = ai_service.customer_support_chat(
        customer_id=customer_id,
        message="متى سيصل الطلب؟"
    )
    print("Response 2:", response2)
    
    # Get conversation summary
    summary = ai_service.get_conversation_summary(f"customer_support_{customer_id}")
    print("Summary:", summary)


def example_sales_assistant():
    """Example: Sales assistant with memory"""
    ai_service = TSHAIServiceWithMemory()
    
    salesperson_id = 456
    customer_id = 789
    
    # First interaction
    response1 = ai_service.sales_assistant_chat(
        salesperson_id=salesperson_id,
        customer_id=customer_id,
        message="Customer is interested in laptops, budget around 5000 SAR",
        context={
            "customer_name": "سارة علي",
            "previous_purchases": ["Dell Mouse", "HP Keyboard"],
            "budget": 5000
        }
    )
    print("Response 1:", response1)
    
    # Follow-up - Claude remembers the laptop discussion
    response2 = ai_service.sales_assistant_chat(
        salesperson_id=salesperson_id,
        customer_id=customer_id,
        message="They're also asking about warranty options"
    )
    print("Response 2:", response2)


def example_business_analyst():
    """Example: Business analyst with memory"""
    ai_service = TSHAIServiceWithMemory()
    
    user_id = 1
    
    # First query
    response1 = ai_service.business_analyst_chat(
        user_id=user_id,
        query="What were our top 5 selling products this month?",
        data_context={
            "top_products": [
                {"name": "Laptop HP", "sales": 1500000},
                {"name": "Mouse Logitech", "sales": 45000},
            ]
        }
    )
    print("Response 1:", response1)
    
    # Follow-up query - Claude remembers the previous analysis
    response2 = ai_service.business_analyst_chat(
        user_id=user_id,
        query="Compare this to last month"
    )
    print("Response 2:", response2)


if __name__ == "__main__":
    print("🤖 TSH ERP AI Service with Memory - Examples")
    print("=" * 70)
    
    # Run examples
    print("\n📞 Customer Support Example:")
    print("-" * 70)
    example_customer_support()
    
    print("\n💼 Sales Assistant Example:")
    print("-" * 70)
    example_sales_assistant()
    
    print("\n📊 Business Analyst Example:")
    print("-" * 70)
    example_business_analyst()
