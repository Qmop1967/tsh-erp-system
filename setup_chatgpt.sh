#!/bin/bash

# ChatGPT Integration Setup Script for TSH ERP System
# This script helps set up the ChatGPT integration quickly

echo "========================================="
echo " ChatGPT Integration Setup"
echo " TSH ERP System"
echo "========================================="
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    echo "Creating .env file from .env.chatgpt.example..."
    cp .env.chatgpt.example .env
    echo "✅ .env file created"
    echo ""
fi

# Check if OPENAI_API_KEY is set
if ! grep -q "OPENAI_API_KEY=sk-" .env 2>/dev/null; then
    echo "⚠️  OPENAI_API_KEY not configured in .env file"
    echo ""
    echo "Please follow these steps:"
    echo "1. Go to https://platform.openai.com/api-keys"
    echo "2. Create a new API key"
    echo "3. Copy the key"
    echo "4. Edit .env file and replace 'sk-your-openai-api-key-here' with your actual key"
    echo ""
    read -p "Do you want to open .env file now? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if command -v code &> /dev/null; then
            code .env
        elif command -v nano &> /dev/null; then
            nano .env
        elif command -v vi &> /dev/null; then
            vi .env
        else
            echo "Please edit .env file manually"
        fi
    fi
fi

echo ""
echo "Checking Python dependencies..."

# Check if openai package is installed
if python3 -c "import openai" 2>/dev/null; then
    echo "✅ openai package is installed"
else
    echo "⚠️  openai package not found"
    read -p "Do you want to install it now? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Installing openai..."
        pip install openai
        echo "✅ openai package installed"
    fi
fi

echo ""
echo "Checking backend server..."

# Check if backend is running
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend server is running"
else
    echo "⚠️  Backend server is not running"
    echo ""
    read -p "Do you want to start the backend server? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Starting backend server..."
        echo "Run this command in a new terminal:"
        echo "  cd /Users/khaleelal-mulla/TSH_ERP_System_Local"
        echo "  uvicorn app.main:app --reload --port 8000"
    fi
fi

echo ""
echo "Checking ChatGPT endpoint..."

# Check if ChatGPT endpoint exists
if curl -s http://localhost:8000/api/chatgpt/health > /dev/null 2>&1; then
    echo "✅ ChatGPT endpoint is accessible"
else
    echo "⚠️  ChatGPT endpoint is not accessible"
    echo "   This is normal if backend server is not running or if you haven't logged in"
fi

echo ""
echo "========================================="
echo " Setup Summary"
echo "========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Make sure your OpenAI API key is set in .env file"
echo "   Edit: .env"
echo "   Add: OPENAI_API_KEY=sk-your-actual-key-here"
echo ""
echo "2. Ensure backend server is running:"
echo "   uvicorn app.main:app --reload --port 8000"
echo ""
echo "3. Test the integration:"
echo "   python3 test_chatgpt_integration.py"
echo ""
echo "4. Read the full documentation:"
echo "   cat CHATGPT_INTEGRATION_GUIDE.md"
echo ""
echo "5. Access API documentation:"
echo "   http://localhost:8000/docs#/ChatGPT%20-%20OpenAI%20Integration"
echo ""
echo "========================================="
echo ""
echo "For support, check:"
echo "  - CHATGPT_INTEGRATION_GUIDE.md"
echo "  - https://platform.openai.com/docs"
echo ""
