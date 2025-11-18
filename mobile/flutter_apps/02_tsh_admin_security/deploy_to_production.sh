#!/bin/bash

# TSH Security App - Production Deployment Script
# Deploys Flutter web app to production server

set -e

echo "🚀 TSH Security App - Production Deployment"
echo "=========================================="

# Configuration
APP_NAME="tsh-security-app"
SERVER_IP="167.71.39.50"
SERVER_USER="root"
DEPLOY_PATH="/var/www/${APP_NAME}"
BUILD_DIR="build/web"
TAR_FILE="/tmp/${APP_NAME}-web.tar.gz"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Build for production
echo -e "${YELLOW}Step 1: Building Flutter web app for production...${NC}"
cd "$(dirname "$0")"
flutter build web --release --dart-define=ENVIRONMENT=production

if [ ! -d "$BUILD_DIR" ]; then
    echo -e "${RED}❌ Build directory not found!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Build complete!${NC}"

# Step 2: Create tar archive
echo -e "${YELLOW}Step 2: Creating deployment archive...${NC}"
tar -czf "$TAR_FILE" -C "$BUILD_DIR" .

if [ ! -f "$TAR_FILE" ]; then
    echo -e "${RED}❌ Failed to create archive!${NC}"
    exit 1
fi

ARCHIVE_SIZE=$(du -h "$TAR_FILE" | cut -f1)
echo -e "${GREEN}✅ Archive created: $TAR_FILE (${ARCHIVE_SIZE})${NC}"

# Step 3: Upload to server
echo -e "${YELLOW}Step 3: Uploading to production server...${NC}"
scp "$TAR_FILE" "${SERVER_USER}@${SERVER_IP}:/tmp/"

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to upload archive!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Upload complete!${NC}"

# Step 4: Deploy on server
echo -e "${YELLOW}Step 4: Deploying on production server...${NC}"
ssh "${SERVER_USER}@${SERVER_IP}" << EOF
    set -e
    
    # Create directory if it doesn't exist
    mkdir -p ${DEPLOY_PATH}
    
    # Backup existing deployment (if any)
    if [ -d "${DEPLOY_PATH}" ] && [ "\$(ls -A ${DEPLOY_PATH})" ]; then
        echo "📦 Backing up existing deployment..."
        tar -czf /tmp/${APP_NAME}-backup-\$(date +%Y%m%d-%H%M%S).tar.gz -C ${DEPLOY_PATH} .
    fi
    
    # Extract new deployment
    echo "📂 Extracting new deployment..."
    cd ${DEPLOY_PATH}
    tar -xzf /tmp/${APP_NAME}-web.tar.gz
    
    # Set permissions
    chown -R www-data:www-data ${DEPLOY_PATH}
    chmod -R 755 ${DEPLOY_PATH}
    
    # Cleanup
    rm -f /tmp/${APP_NAME}-web.tar.gz
    
    echo "✅ Deployment complete on server!"
EOF

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Deployment failed on server!${NC}"
    exit 1
fi

# Step 5: Cleanup local archive
rm -f "$TAR_FILE"

echo ""
echo -e "${GREEN}🎉 Deployment Complete!${NC}"
echo ""
echo "📋 Next Steps:"
echo "1. Configure Nginx to serve the app"
echo "2. Set up SSL certificate (if needed)"
echo "3. Test the app at: https://security.tsh.sale (or configured domain)"
echo ""
echo "To configure Nginx, add this server block:"
echo ""
echo "server {"
echo "    listen 443 ssl http2;"
echo "    server_name security.tsh.sale;"
echo "    root ${DEPLOY_PATH};"
echo "    index index.html;"
echo ""
echo "    location / {"
echo "        try_files \$uri \$uri/ /index.html;"
echo "    }"
echo "}"
echo ""

