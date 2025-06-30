# Configuration Files

This folder contains all configuration files and credentials for the TSH ERP System.

## Contents:
- `env.example` - Environment variables template
- `requirements.txt` - Python dependencies
- `encryption.key` - Encryption key for secure data
- `zoho_credentials.enc` - Encrypted Zoho API credentials

## Security Note:
⚠️ **Important**: This folder contains sensitive configuration files. 
- Keep encryption keys secure
- Never commit actual credentials to version control
- Use environment variables for production deployments

## Setup:
1. Copy `env.example` to `.env` in the project root
2. Configure your environment variables
3. Ensure proper file permissions for sensitive files

```bash
# Set proper permissions for sensitive files
chmod 600 config/encryption.key
chmod 600 config/zoho_credentials.enc
```
