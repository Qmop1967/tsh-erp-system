#!/bin/bash

# 🛡️ TSH ERP System - Setup & Protection Script
# Run this script to set up Git repository and automated backups

echo "🏢 TSH ERP System - Protection Setup"
echo "==================================="

# Get current directory
PROJECT_DIR="/Users/khaleelal-mulla/Desktop/TSH ERP System"
cd "$PROJECT_DIR"

# Check if Git is already initialized
if [ ! -d ".git" ]; then
    echo "📦 Initializing Git repository..."
    git init
    
    # Create .gitignore
    cat > .gitignore << EOF
# Dependencies
node_modules/
__pycache__/
*.pyc
*.pyo
*.pyd

# Build outputs
dist/
build/
*.egg-info/

# Environment variables
.env
.env.local
.env.production

# IDE files
.vscode/
.idea/
*.swp
*.swo

# OS files
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Database
*.db
*.sqlite3

# Temporary files
*.tmp
*.temp
EOF

    echo "✅ Git repository initialized"
else
    echo "📦 Git repository already exists"
fi

# Create initial commit with current working state
echo "💾 Creating backup commit..."
git add .
git commit -m "🎉 WORKING VERSION - TSH ERP System fully functional with modern UI ($(date))"

# Create a working tag
git tag "v1.0-working-$(date +%Y%m%d-%H%M)"

echo "✅ Backup commit created"

# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
# Daily backup script for TSH ERP System

cd "/Users/khaleelal-mulla/Desktop/TSH ERP System"

echo "📦 Creating daily backup..."
git add .
git commit -m "📅 Daily backup: $(date)"

# Create a timestamped tag
git tag "backup-$(date +%Y%m%d-%H%M)"

echo "✅ Backup completed: backup-$(date +%Y%m%d-%H%M)"

# Show recent commits
echo "📋 Recent commits:"
git log --oneline -5
EOF

chmod +x backup.sh

echo "🔄 Created backup.sh script"

# Create development helper script
cat > dev-start.sh << 'EOF'
#!/bin/bash
# Development server startup script

echo "🚀 Starting TSH ERP System Development Environment"
echo "================================================="

# Check if in correct directory
if [ ! -f "PROJECT_STATE_WORKING.md" ]; then
    echo "❌ Please run this script from the TSH ERP System directory"
    exit 1
fi

# Start frontend development server
echo "🌐 Starting frontend development server..."
cd frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

# Start dev server
echo "🚀 Starting Vite dev server..."
npm run dev

echo "✅ Frontend running on http://localhost:3003 (or next available port)"
EOF

chmod +x dev-start.sh

echo "🚀 Created dev-start.sh script"

# Create quick status check script
cat > status-check.sh << 'EOF'
#!/bin/bash
# Quick status check for TSH ERP System

echo "🏢 TSH ERP System - Status Check"
echo "==============================="

cd "/Users/khaleelal-mulla/Desktop/TSH ERP System"

# Check Git status
echo "📦 Git Status:"
git status --porcelain
echo ""

# Check if dev server is running
echo "🌐 Development Server Status:"
if lsof -Pi :3003 -sTCP:LISTEN -t >/dev/null ; then
    echo "✅ Frontend dev server is running on port 3003"
else
    echo "❌ Frontend dev server is not running"
    echo "💡 Run './dev-start.sh' to start it"
fi

# Check recent commits
echo ""
echo "📋 Recent Commits:"
git log --oneline -3

# Check working files
echo ""
echo "🔍 Critical Files Status:"
if [ -f "frontend/src/App.tsx" ]; then
    echo "✅ App.tsx exists"
else
    echo "❌ App.tsx missing!"
fi

if [ -f "frontend/src/main.tsx" ]; then
    echo "✅ main.tsx exists"
else
    echo "❌ main.tsx missing!"
fi

if [ -f "frontend/src/components/layout/NewLayout.tsx" ]; then
    echo "✅ NewLayout.tsx exists"
else
    echo "❌ NewLayout.tsx missing!"
fi

echo ""
echo "🎯 Ready for development!"
EOF

chmod +x status-check.sh

echo "📊 Created status-check.sh script"

echo ""
echo "🎉 Setup Complete!"
echo "=================="
echo ""
echo "📝 Available commands:"
echo "  ./backup.sh       - Create daily backup"
echo "  ./dev-start.sh    - Start development server"
echo "  ./status-check.sh - Check system status"
echo ""
echo "🛡️ Your project is now protected with:"
echo "✅ Git repository with working state backup"
echo "✅ Automated backup scripts"
echo "✅ Development helper scripts"
echo "✅ Comprehensive documentation"
echo ""
echo "💡 Next steps:"
echo "1. Run './status-check.sh' to verify everything is working"
echo "2. Run './dev-start.sh' to start development"
echo "3. Run './backup.sh' daily to create backups"
echo ""
echo "🔗 Consider setting up a GitHub repository for remote backups:"
echo "   git remote add origin https://github.com/yourusername/TSH-ERP-System.git"
echo "   git push -u origin main"
