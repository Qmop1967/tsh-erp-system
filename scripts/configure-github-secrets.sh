#!/bin/bash

# GitHub Secrets Configuration Script for TSH ERP
# This script helps configure the required GitHub secrets for CI/CD workflows

set -e

echo "=================================================="
echo "  GitHub Secrets Configuration for TSH ERP"
echo "=================================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to set secret
set_secret() {
    local name=$1
    local prompt=$2
    local default=$3

    echo -e "${YELLOW}Setting: ${name}${NC}"
    echo "${prompt}"

    if [ -n "$default" ]; then
        read -p "Enter value (default: ${default}): " value
        value=${value:-$default}
    else
        read -sp "Enter value (hidden): " value
        echo ""
    fi

    if [ -n "$value" ]; then
        echo "$value" | gh secret set "$name"
        echo -e "${GREEN}✓ ${name} set successfully${NC}"
    else
        echo -e "${RED}✗ Skipped ${name}${NC}"
    fi
    echo ""
}

echo "This script will configure GitHub secrets for your repository."
echo "Press Enter to skip any secret you don't want to set now."
echo ""

# Check if gh is authenticated
if ! gh auth status > /dev/null 2>&1; then
    echo -e "${RED}Error: GitHub CLI is not authenticated${NC}"
    echo "Run: gh auth login"
    exit 1
fi

echo "=== Database Secrets ==="
echo ""

set_secret "PROD_DB_USER" "Production database user" "tsh_app_user"
set_secret "PROD_DB_NAME" "Production database name" "tsh_erp_production"
set_secret "PROD_DB_PASSWORD" "Production database password (required)" ""

set_secret "STAGING_DB_USER" "Staging database user" "tsh_app_user"
set_secret "STAGING_DB_NAME" "Staging database name" "tsh_erp_staging"
set_secret "STAGING_DB_PASSWORD" "Staging database password (required)" ""

echo "=== Notification Secrets ==="
echo ""

set_secret "TELEGRAM_BOT_TOKEN" "Telegram Bot Token (from @BotFather)" ""
set_secret "TELEGRAM_CHAT_ID" "Telegram Chat ID (your chat or group ID)" ""

echo "=== Optional: AWS S3 for Backups ==="
echo ""

read -p "Do you want to configure AWS S3 for database backups? (y/n): " configure_aws

if [ "$configure_aws" == "y" ]; then
    set_secret "AWS_ACCESS_KEY_ID" "AWS Access Key ID" ""
    set_secret "AWS_SECRET_ACCESS_KEY" "AWS Secret Access Key" ""
    set_secret "AWS_REGION" "AWS Region" "eu-north-1"
    set_secret "AWS_S3_BUCKET" "S3 Bucket name" "tsh-erp-backups"
fi

echo "=== Optional: Email Notifications ==="
echo ""

read -p "Do you want to configure email notifications? (y/n): " configure_email

if [ "$configure_email" == "y" ]; then
    set_secret "EMAIL_SMTP_HOST" "SMTP Host (e.g., smtp.gmail.com)" ""
    set_secret "EMAIL_SMTP_PORT" "SMTP Port" "587"
    set_secret "EMAIL_FROM" "From email address" ""
    set_secret "EMAIL_PASSWORD" "Email password or app password" ""
    set_secret "EMAIL_TO" "Notification recipient email" ""
fi

echo ""
echo "=================================================="
echo -e "${GREEN}Configuration Complete!${NC}"
echo "=================================================="
echo ""
echo "Configured secrets:"
gh secret list
echo ""
echo "Next steps:"
echo "1. Verify secrets are configured: gh secret list"
echo "2. Trigger a workflow: gh workflow run ci.yml"
echo "3. Monitor workflow: gh run watch"
echo ""
echo "For a complete list of all secrets, see:"
echo "docs/ci-cd/github-secrets-setup.md"
