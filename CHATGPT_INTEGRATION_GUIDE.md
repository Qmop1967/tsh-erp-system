# ChatGPT Integration for TSH ERP System

## 🎯 Overview
This document provides comprehensive instructions for integrating OpenAI's ChatGPT API with the TSH ERP System.

## ✅ Completed Implementation

### Backend Integration
1. **Service Layer** (`app/services/chatgpt_service.py`)
   - OpenAI API client initialization
   - Chat completion with conversation history
   - Intent analysis
   - Email generation
   - Report summarization
   - Translation services
   - Product recommendations
   - Context-aware prompts for different modules (sales, inventory, financial)

2. **API Router** (`app/routers/chatgpt.py`)
   - `/api/chatgpt/chat` - Main chat endpoint
   - `/api/chatgpt/intent` - Intent analysis
   - `/api/chatgpt/email` - Email generation
   - `/api/chatgpt/report/summary` - Report summarization
   - `/api/chatgpt/translate` - Translation
   - `/api/chatgpt/products/recommend` - Product recommendations
   - `/api/chatgpt/conversations` - Get user conversations
   - `/api/chatgpt/conversations/{id}` - Delete conversation
   - `/api/chatgpt/health` - Health check

3. **Main App Registration** (`app/main.py`)
   - ChatGPT router registered at `/api/chatgpt`
   - Properly integrated with existing auth and middleware

### Frontend Components
1. **ChatGPTButton.tsx** - Floating action button to open chat
2. **ChatGPTAssistant.tsx** - Full chat interface (needs manual creation due to file size)

## 📋 Setup Instructions

### Step 1: Environment Configuration

1. Copy the example environment file:
```bash
cp .env.chatgpt.example .env.chatgpt
```

2. Edit `.env` or `.env.chatgpt` and add your OpenAI credentials:
```bash
# OpenAI API Configuration
OPENAI_API_KEY=sk-your-actual-api-key-here
OPENAI_ORG_ID=org-your-organization-id-here  # Optional
OPENAI_MODEL=gpt-4o  # or gpt-4, gpt-3.5-turbo
OPENAI_MAX_TOKENS=2000
OPENAI_TEMPERATURE=0.7

# ChatGPT Features Configuration
CHATGPT_ENABLED=true
CHATGPT_SYSTEM_ROLE=You are a helpful AI assistant for TSH ERP system
CHATGPT_MAX_HISTORY=10
CHATGPT_TIMEOUT=30

# Rate Limiting
CHATGPT_MAX_REQUESTS_PER_MINUTE=60
CHATGPT_MAX_REQUESTS_PER_DAY=1000

# Context Settings
CHATGPT_INCLUDE_USER_CONTEXT=true
CHATGPT_INCLUDE_COMPANY_CONTEXT=true
```

### Step 2: Install Dependencies

```bash
# Backend
cd /Users/khaleelal-mulla/TSH_ERP_System_Local
pip install openai

# Frontend (if needed)
cd frontend
npm install lucide-react
```

### Step 3: Restart Services

```bash
# Restart backend
# Stop the current backend server (Ctrl+C)
# Then start it again
uvicorn app.main:app --reload --port 8000

# Frontend should automatically reload
```

### Step 4: Test the Integration

#### Test ChatGPT Health
```bash
curl -X GET "http://localhost:8000/api/chatgpt/health" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### Test Chat Endpoint
```bash
curl -X POST "http://localhost:8000/api/chatgpt/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "message": "What are the top selling products this month?",
    "context_type": "sales",
    "include_user_context": true
  }'
```

#### Test Intent Analysis
```bash
curl -X POST "http://localhost:8000/api/chatgpt/intent" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "message": "Show me the inventory levels for product ABC123"
  }'
```

## 🎨 Frontend Integration

### Option 1: Add to Header/Sidebar

Edit `frontend/src/components/layout/Header.tsx` or `Sidebar.tsx`:

```tsx
import { ChatGPTButton } from '../chatgpt/ChatGPTButton';
import { useState } from 'react';

// Inside your component:
const [isChatOpen, setIsChatOpen] = useState(false);

// Add this to your JSX:
<ChatGPTButton onOpenChat={() => setIsChatOpen(true)} />

// Add the chat modal (you'll need to create ChatGPTModal component)
{isChatOpen && <ChatGPTModal onClose={() => setIsChatOpen(false)} />}
```

### Option 2: Create a Dedicated Chat Page

Create `frontend/src/pages/ChatGPTPage.tsx`:

```tsx
import React from 'react';
import { ChatGPTButton } from '../components/chatgpt/ChatGPTButton';

export const ChatGPTPage = () => {
  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">AI Assistant</h1>
      <p>Chat with our AI assistant to get help with your ERP system.</p>
      {/* Add full chat interface here */}
    </div>
  );
};
```

## 📊 Features

### 1. Contextual Chat
- **General**: General questions about the system
- **Sales**: Sales-related queries, order management
- **Inventory**: Stock levels, product information
- **Financial**: Financial reports, accounting queries

### 2. Intent Analysis
Automatically understands user intent:
- Product search
- Order placement
- Inventory check
- Report generation
- Translation requests

### 3. Email Generation
Generate professional emails for:
- Customer communications
- Supplier inquiries
- Internal notifications

### 4. Report Summarization
Summarize complex reports:
- Sales reports
- Inventory reports
- Financial statements

### 5. Translation
Translate between English and Arabic automatically.

### 6. Product Recommendations
Get intelligent product recommendations based on:
- Customer history
- Purchase patterns
- Inventory availability

## 🔒 Security Considerations

1. **API Key Protection**
   - Never commit `.env` file with actual keys
   - Use environment variables in production
   - Rotate keys regularly

2. **Rate Limiting**
   - Implement rate limiting to prevent abuse
   - Monitor API usage
   - Set daily/monthly budgets in OpenAI dashboard

3. **User Authentication**
   - All endpoints require JWT token authentication
   - User context is included in requests

4. **Data Privacy**
   - Be careful what data is sent to OpenAI
   - Consider implementing data masking for sensitive information
   - Review OpenAI's data usage policies

## 📈 Monitoring and Optimization

### Track API Usage
```python
# The service automatically logs usage
# Check logs for:
# - Token usage per request
# - Response times
# - Error rates
```

### Optimize Costs
1. Use `gpt-3.5-turbo` for simple queries
2. Implement caching for common questions
3. Set appropriate `max_tokens` limits
4. Use conversation history efficiently (limit to 10 messages)

### Performance Tips
- Cache frequently asked questions
- Implement response streaming for better UX
- Use background tasks for non-critical operations
- Monitor token usage and optimize prompts

## 🐛 Troubleshooting

### Common Issues

1. **"OPENAI_API_KEY environment variable is required"**
   - Solution: Add your API key to `.env` file

2. **401 Unauthorized**
   - Solution: Check if your OpenAI API key is valid
   - Verify your organization ID (if using)

3. **429 Rate Limit Exceeded**
   - Solution: Implement rate limiting
   - Upgrade your OpenAI plan
   - Reduce request frequency

4. **Slow Response Times**
   - Solution: Reduce `max_tokens`
   - Use `gpt-3.5-turbo` instead of `gpt-4`
   - Implement response streaming

5. **Import Error: "No module named 'openai'"**
   - Solution: Install the package: `pip install openai`

## 📝 API Reference

### POST /api/chatgpt/chat
Send a message and get AI response.

**Request:**
```json
{
  "message": "string",
  "context_type": "general|sales|inventory|financial",
  "conversation_id": "string (optional)",
  "include_user_context": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "AI response",
  "conversation_id": "uuid",
  "timestamp": "2024-01-01T12:00:00",
  "usage": {
    "prompt_tokens": 100,
    "completion_tokens": 50,
    "total_tokens": 150
  }
}
```

### POST /api/chatgpt/intent
Analyze user intent.

**Request:**
```json
{
  "message": "string"
}
```

**Response:**
```json
{
  "success": true,
  "intent": "product_search|order_placement|inventory_check|...",
  "confidence": 0.95,
  "entities": {
    "product_name": "ABC123",
    "quantity": 10
  }
}
```

## 🚀 Next Steps

1. **Create Full Chat UI Component**
   - Implement ChatGPTAssistant.tsx with proper formatting
   - Add to main layout or create dedicated page

2. **Add Advanced Features**
   - Voice input/output
   - Multi-language support
   - Context-aware suggestions
   - Integration with other ERP modules

3. **Implement Analytics**
   - Track most asked questions
   - Monitor user satisfaction
   - Analyze conversation patterns

4. **Optimize Performance**
   - Add response caching
   - Implement streaming responses
   - Add typing indicators

5. **Production Deployment**
   - Set up proper API key management
   - Configure rate limiting
   - Implement monitoring and alerting
   - Add usage analytics

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review OpenAI documentation: https://platform.openai.com/docs
3. Check TSH ERP System logs
4. Contact the development team

## 📄 License

This integration is part of the TSH ERP System and follows the same license terms.

---

**Last Updated:** December 2024  
**Version:** 1.0.0  
**Author:** TSH Development Team
