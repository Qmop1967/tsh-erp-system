#!/bin/bash

# TSH ERP Frontend Setup Script
# This script sets up the development environment for the TSH ERP frontend

echo "🚀 Setting up TSH ERP Frontend Development Environment"
echo "=================================================="

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18 or higher."
    echo "   Visit: https://nodejs.org/"
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2)
REQUIRED_VERSION="18.0.0"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$NODE_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Node.js version $NODE_VERSION is too old. Required: v$REQUIRED_VERSION or higher"
    exit 1
fi

echo "✅ Node.js version: $NODE_VERSION"

# Check if npm is available
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm."
    exit 1
fi

echo "✅ npm version: $(npm -v)"

# Navigate to frontend directory
cd "$(dirname "$0")"

# Install dependencies
echo "📦 Installing dependencies..."
npm install

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOL
# TSH ERP Frontend Environment Variables
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=TSH ERP System
VITE_APP_VERSION=1.0.0
EOL
    echo "✅ .env file created"
else
    echo "📄 .env file already exists"
fi

# Check if backend is running
echo "🔍 Checking backend connectivity..."
if curl -s http://localhost:8000/docs > /dev/null; then
    echo "✅ Backend is running on http://localhost:8000"
else
    echo "⚠️  Backend is not running. Please start the FastAPI backend first:"
    echo "   cd .. && uvicorn app.main:app --reload"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "To start the development server:"
echo "  npm run dev"
echo ""
echo "The application will be available at:"
echo "  http://localhost:3000"
echo ""
echo "Available scripts:"
echo "  npm run dev      - Start development server"
echo "  npm run build    - Build for production"
echo "  npm run preview  - Preview production build"
echo "  npm run lint     - Run linter"
echo ""
echo "Happy coding! 🚀"
