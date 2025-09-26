#!/bin/bash

echo "🔐 Generating Certificate Signing Request (CSR) for iOS Development"
echo ""

# Create certificate request configuration file
cat > csr_config.conf << EOF
[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[req_distinguished_name]
C=SA
ST=Riyadh
L=Riyadh
O=TSH
OU=Development
CN=Khaleel Ahmed
emailAddress=khaleel_ahm@yahoo.com

[v3_req]
keyUsage = critical,digitalSignature,keyEncipherment
extendedKeyUsage = codeSigning
EOF

# Generate private key and CSR
openssl genrsa -out TSH_iOS_Private_Key.key 2048
openssl req -new -key TSH_iOS_Private_Key.key -out TSH_iOS_Certificate_Request.csr -config csr_config.conf

echo ""
echo "✅ Certificate Signing Request generated!"
echo ""
echo "Files created:"
echo "  - TSH_iOS_Private_Key.key (keep this secure!)"
echo "  - TSH_iOS_Certificate_Request.csr (upload to Apple)"
echo ""
echo "Next steps:"
echo "1. Go to: https://developer.apple.com/account/resources/certificates/list"
echo "2. Click '+' to add new certificate"
echo "3. Select 'iOS Development' certificate"
echo "4. Upload the TSH_iOS_Certificate_Request.csr file"
echo "5. Download the certificate and double-click to install"
echo ""
