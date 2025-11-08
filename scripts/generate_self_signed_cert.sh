#!/bin/bash

################################################################################
# Generate Self-Signed SSL Certificate
# TSH ERP System
################################################################################
#
# This script generates a self-signed SSL certificate for development/testing
# WARNING: NOT for production use!
#
# Usage:
#   ./scripts/generate_self_signed_cert.sh [domain]
#
################################################################################

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Default domain
DOMAIN="${1:-erp.tsh.sale}"
SSL_DIR="nginx/ssl"

echo -e "${YELLOW}⚠️  WARNING: Self-signed certificates are for DEVELOPMENT/TESTING only!${NC}"
echo -e "${YELLOW}⚠️  For production, use Let's Encrypt (see docs/docker/SSL_SETUP.md)${NC}"
echo ""

# Create SSL directory if it doesn't exist
if [ ! -d "$SSL_DIR" ]; then
    mkdir -p "$SSL_DIR"
    echo -e "${GREEN}Created directory: $SSL_DIR${NC}"
fi

# Check if certificates already exist
if [ -f "$SSL_DIR/fullchain.pem" ] || [ -f "$SSL_DIR/privkey.pem" ]; then
    echo -e "${YELLOW}Certificates already exist in $SSL_DIR${NC}"
    read -p "Do you want to overwrite them? [y/N]: " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cancelled."
        exit 1
    fi
fi

# Generate self-signed certificate
echo -e "${GREEN}Generating self-signed certificate for: $DOMAIN${NC}"
echo ""

openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout "$SSL_DIR/privkey.pem" \
  -out "$SSL_DIR/fullchain.pem" \
  -subj "/C=IQ/ST=Baghdad/L=Baghdad/O=TSH ERP/OU=IT Department/CN=$DOMAIN" \
  -addext "subjectAltName=DNS:$DOMAIN,DNS:www.$DOMAIN"

# Set permissions
chmod 644 "$SSL_DIR/fullchain.pem"
chmod 600 "$SSL_DIR/privkey.pem"

echo ""
echo -e "${GREEN}✅ Self-signed certificate generated successfully!${NC}"
echo ""
echo "Certificate details:"
openssl x509 -in "$SSL_DIR/fullchain.pem" -noout -subject -dates
echo ""
echo "Files created:"
ls -lh "$SSL_DIR/"
echo ""
echo -e "${GREEN}You can now start nginx with SSL:${NC}"
echo "  docker compose --profile proxy up -d"
echo ""
echo -e "${YELLOW}Note: Browsers will show security warnings for self-signed certificates.${NC}"
