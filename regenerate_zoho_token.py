#!/usr/bin/env python3
"""
Zoho Token Regenerator
======================

Regenerates Zoho access token using refresh token and updates .env files.

Usage:
    python3 regenerate_zoho_token.py
    python3 regenerate_zoho_token.py --update-production

يجدد رمز الوصول إلى Zoho
"""

import requests
import os
import sys
from pathlib import Path

# Zoho Credentials (Found in codebase)
ZOHO_CLIENT_ID = "1000.RYRPK7578ZRKN6K4HKNF4LKL2CC9IQ"
ZOHO_CLIENT_SECRET = "a39a5dcdc057a8490cb7960d1400f62ce14edd6455"
ZOHO_REFRESH_TOKEN = "1000.2e358f3c53d3e22ac2d134c5c93d9c5b.118c5e88cd0a4ed2a1143056f2d09e68"
ZOHO_ORGANIZATION_ID = "748369814"

# Alternative credentials (from fetch_zoho_product_images.py)
ALT_CLIENT_ID = "1000.SLY5X93N58VN46HXQIIZSOQKG8J3ZJ"
ALT_CLIENT_SECRET = "0581c245cd951e1453042ff2bcf223768e128fed9f"
ALT_REFRESH_TOKEN = "1000.456d43e0209a40ba2d580747be746a54.1aa75b48b965e8a8562dc89d2a15e517"


def regenerate_access_token(client_id, client_secret, refresh_token, label="Primary"):
    """
    Regenerate Zoho access token using refresh token

    Args:
        client_id: Zoho client ID
        client_secret: Zoho client secret
        refresh_token: Zoho refresh token
        label: Label for this credential set

    Returns:
        tuple: (access_token, success)
    """
    print(f"\n{'='*80}")
    print(f"🔄 Attempting to regenerate access token ({label})...")
    print(f"{'='*80}")

    url = "https://accounts.zoho.com/oauth/v2/token"

    params = {
        'refresh_token': refresh_token,
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'refresh_token'
    }

    try:
        print("📡 Sending request to Zoho OAuth endpoint...")
        response = requests.post(url, params=params, timeout=30)

        print(f"   Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            if 'access_token' in data:
                access_token = data['access_token']
                expires_in = data.get('expires_in_sec', 3600)

                print(f"✅ Success! Access token regenerated")
                print(f"   Token: {access_token[:50]}...")
                print(f"   Expires in: {expires_in} seconds ({expires_in // 60} minutes)")

                return access_token, True
            else:
                print(f"❌ No access token in response")
                print(f"   Response: {data}")
                return None, False
        else:
            print(f"❌ Failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return None, False

    except Exception as e:
        print(f"❌ Error: {e}")
        return None, False


def update_env_file(filepath, client_id, client_secret, refresh_token, access_token):
    """Update .env file with Zoho credentials"""

    env_content = f"""# Zoho Configuration (Auto-generated on {os.popen('date').read().strip()})
ZOHO_CLIENT_ID={client_id}
ZOHO_CLIENT_SECRET={client_secret}
ZOHO_REFRESH_TOKEN={refresh_token}
ZOHO_ACCESS_TOKEN={access_token}
ZOHO_ORGANIZATION_ID={ZOHO_ORGANIZATION_ID}
"""

    # Read existing .env
    existing_content = ""
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            existing_content = f.read()

    # Remove old Zoho variables
    lines = []
    for line in existing_content.split('\n'):
        if not line.startswith('ZOHO_'):
            lines.append(line)

    # Add new Zoho variables
    new_content = '\n'.join(lines).strip() + '\n\n' + env_content

    # Write back
    with open(filepath, 'w') as f:
        f.write(new_content)

    print(f"✅ Updated: {filepath}")


def main():
    """Main execution"""

    print("\n" + "="*80)
    print("🔑 ZOHO TOKEN REGENERATOR")
    print("="*80)

    # Try primary credentials first
    access_token, success = regenerate_access_token(
        ZOHO_CLIENT_ID,
        ZOHO_CLIENT_SECRET,
        ZOHO_REFRESH_TOKEN,
        "Primary"
    )

    # Set working credentials
    working_client_id = ZOHO_CLIENT_ID
    working_client_secret = ZOHO_CLIENT_SECRET
    working_refresh_token = ZOHO_REFRESH_TOKEN

    if not success:
        print("\n⚠️  Primary credentials failed. Trying alternative credentials...")
        access_token, success = regenerate_access_token(
            ALT_CLIENT_ID,
            ALT_CLIENT_SECRET,
            ALT_REFRESH_TOKEN,
            "Alternative"
        )

        if success:
            # Use alternative credentials
            working_client_id = ALT_CLIENT_ID
            working_client_secret = ALT_CLIENT_SECRET
            working_refresh_token = ALT_REFRESH_TOKEN

    if not success:
        print("\n" + "="*80)
        print("❌ FAILED TO REGENERATE TOKEN")
        print("="*80)
        print("\n⚠️  Both credential sets failed.")
        print("\nPossible reasons:")
        print("1. Refresh tokens have expired (need to regenerate from Zoho console)")
        print("2. Client credentials are invalid")
        print("3. Network issues")
        print("\n📖 To fix:")
        print("1. Go to: https://api-console.zoho.com/")
        print("2. Generate new refresh token")
        print("3. Update credentials in this script")
        return 1

    # Success! Update .env files
    print("\n" + "="*80)
    print("📝 UPDATING CONFIGURATION FILES")
    print("="*80)

    # Update local .env
    local_env = Path(__file__).parent / '.env'
    update_env_file(
        str(local_env),
        working_client_id,
        working_client_secret,
        working_refresh_token,
        access_token
    )

    # Update production .env if requested
    if '--update-production' in sys.argv:
        print("\n🚀 Updating production server...")

        # Create temporary env file
        temp_env = "/tmp/tsh_zoho.env"
        with open(temp_env, 'w') as f:
            f.write(f"""ZOHO_CLIENT_ID={working_client_id}
ZOHO_CLIENT_SECRET={working_client_secret}
ZOHO_REFRESH_TOKEN={working_refresh_token}
ZOHO_ACCESS_TOKEN={access_token}
ZOHO_ORGANIZATION_ID={ZOHO_ORGANIZATION_ID}
""")

        # SCP to production
        import subprocess
        try:
            subprocess.run([
                'scp',
                temp_env,
                'root@167.71.39.50:/tmp/zoho_credentials.env'
            ], check=True)

            # SSH and update
            subprocess.run([
                'ssh', 'root@167.71.39.50',
                f'''
                cd /root/TSH_ERP_Ecosystem

                # Backup current .env
                cp .env .env.backup.$(date +%Y%m%d_%H%M%S)

                # Remove old Zoho variables
                grep -v "^ZOHO_" .env > .env.tmp || true

                # Add new Zoho variables
                cat /tmp/zoho_credentials.env >> .env.tmp
                mv .env.tmp .env

                # Cleanup
                rm /tmp/zoho_credentials.env

                echo "✅ Production .env updated"
                '''
            ], check=True, shell=True)

            print("✅ Production server updated successfully")

        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to update production: {e}")

    # Final summary
    print("\n" + "="*80)
    print("✅ TOKEN REGENERATION COMPLETE")
    print("="*80)
    print(f"\n🔑 New Access Token: {access_token[:50]}...")
    print(f"📁 Updated: {local_env}")

    if '--update-production' in sys.argv:
        print(f"🚀 Updated: Production server (167.71.39.50)")

    print("\n📋 Next Steps:")
    print("1. Test the connection:")
    print("   python3 tds_compare_and_sync.py")
    print("\n2. If on production, start the scheduler:")
    print("   ssh root@167.71.39.50")
    print("   sudo systemctl start tds-autosync")

    print("\n" + "="*80 + "\n")

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
