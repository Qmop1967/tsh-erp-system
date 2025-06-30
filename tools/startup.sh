#!/bin/bash

# TSH ERP System Startup Script
# سكريبت بدء تشغيل نظام TSH ERP

echo "🚀 Starting TSH ERP System setup..."
echo "🚀 بدء إعداد نظام TSH ERP..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Please create one first."
    echo "❌ البيئة الافتراضية غير موجودة. يرجى إنشاء واحدة أولاً."
    echo "Run: python -m venv .venv"
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Install/upgrade dependencies
echo "📦 Installing dependencies..."
echo "📦 تثبيت المتطلبات..."
pip install -r requirements.txt

# Run database migrations
echo "🗄️ Running database migrations..."
echo "🗄️ تشغيل ترحيل قاعدة البيانات..."
alembic upgrade head

# Initialize default data
echo "📊 Initializing default data..."
echo "📊 تهيئة البيانات الافتراضية..."
python app/init_data.py

# Start the application
echo "🌟 Starting FastAPI application..."
echo "🌟 بدء تطبيق FastAPI..."
echo "📋 API documentation available at: http://localhost:8000/docs"
echo "📋 وثائق API متاحة على: http://localhost:8000/docs"

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
