#!/bin/bash
# Development server startup script

echo "🚀 Starting TSH ERP System Development Environment"
echo "================================================="

# Check if in correct directory
if [ ! -f "PROJECT_STATE_WORKING.md" ]; then
    echo "❌ Please run this script from the TSH ERP System directory"
    exit 1
fi

# Kill any existing process on port 3003
echo "🧹 Cleaning up existing processes on port 3003..."
lsof -ti:3003 | xargs kill -9 2>/dev/null || true

# Start frontend development server
echo "🌐 Starting frontend development server..."
cd frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

# Start dev server
echo "🚀 Starting Vite dev server on http://localhost:3003..."
npm run dev

echo "✅ Frontend running on http://localhost:3003"
