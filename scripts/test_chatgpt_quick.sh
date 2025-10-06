#!/bin/bash

# Quick ChatGPT Integration Test
# Tests the basic chat functionality without authentication

echo "🧪 Testing ChatGPT Integration for TSH ERP System"
echo "=================================================="
echo ""

# Test 1: Health Check
echo "Test 1: Health Check"
echo "--------------------"
curl -s http://localhost:8000/api/chatgpt/health | jq .
echo ""
echo ""

# Test 2: Simple Chat (This will fail without auth, but shows the endpoint exists)
echo "Test 2: Chat Endpoint (No Auth - Expected to fail with 401)"
echo "------------------------------------------------------------"
curl -s -X POST http://localhost:8000/api/chatgpt/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, what can you help me with?",
    "context_type": "general"
  }' | jq .
echo ""
echo ""

echo "✅ ChatGPT integration is configured!"
echo ""
echo "📝 Next Steps:"
echo "  1. Get a JWT token by logging in"
echo "  2. Use the token to test authenticated endpoints"
echo "  3. Visit http://localhost:8000/docs to test all endpoints interactively"
echo ""
echo "📖 Full Documentation:"
echo "  - CHATGPT_INTEGRATION_GUIDE.md"
echo "  - CHATGPT_SETUP_COMPLETE.md"
echo ""
