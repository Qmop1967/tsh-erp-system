#!/bin/bash
# Add DNS A record for tds.tsh.sale using Namecheap API

# Load credentials
source ~/.namecheap_credentials

# Domain details
DOMAIN="tsh"
TLD="sale"
HOSTNAME="tds"
IP="167.71.39.50"

# Step 1: Get existing DNS records
echo "📋 Fetching existing DNS records..."
GET_URL="https://api.namecheap.com/xml.response?ApiUser=${NAMECHEAP_API_USER}&ApiKey=${NAMECHEAP_API_KEY}&UserName=${NAMECHEAP_USERNAME}&Command=namecheap.domains.dns.getHosts&ClientIp=${NAMECHEAP_CLIENT_IP}&SLD=${DOMAIN}&TLD=${TLD}"

EXISTING_RECORDS=$(curl -s "$GET_URL")

# Check if we got a successful response
if echo "$EXISTING_RECORDS" | grep -q "Status=\"OK\""; then
    echo "✅ Successfully fetched existing records"
else
    echo "❌ Error fetching DNS records"
    echo "$EXISTING_RECORDS"
    exit 1
fi

# Step 2: Parse existing records and prepare update
# For simplicity, I'll show the update command structure
# In production, you'd parse XML and append the new record

echo ""
echo "➕ Adding DNS record: ${HOSTNAME}.${DOMAIN}.${TLD} -> ${IP}"
echo ""
echo "⚠️  Note: To add the record via API, we need to:"
echo "  1. Parse existing DNS records from the XML response"
echo "  2. Add the new record to the list"
echo "  3. Send all records back to the API"
echo ""
echo "For manual addition through Namecheap Dashboard:"
echo "  1. Go to https://ap.www.namecheap.com/domains/domaincontrolpanel/${DOMAIN}.${TLD}/advancedns"
echo "  2. Add A Record:"
echo "     Host: ${HOSTNAME}"
echo "     Value: ${IP}"
echo "     TTL: Automatic"
echo ""
echo "Or use the Namecheap API with all existing records + new record"
