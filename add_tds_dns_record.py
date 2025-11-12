#!/usr/bin/env python3
"""
Add TDS subdomain DNS record to Namecheap
"""
import os
import sys
import requests
import xml.etree.ElementTree as ET

# Load credentials from environment
API_USER = os.getenv('NAMECHEAP_API_USER')
API_KEY = os.getenv('NAMECHEAP_API_KEY')
USERNAME = os.getenv('NAMECHEAP_USERNAME')
CLIENT_IP = os.getenv('NAMECHEAP_CLIENT_IP')

if not all([API_USER, API_KEY, USERNAME, CLIENT_IP]):
    print("❌ Error: Missing Namecheap credentials")
    print("Run: source ~/.namecheap_credentials")
    sys.exit(1)

# Domain configuration
SLD = "tsh"
TLD = "sale"
NEW_HOST = "tds"
NEW_IP = "167.71.39.50"
NEW_TTL = "300"

# Namecheap API base URL
BASE_URL = "https://api.namecheap.com/xml.response"

def build_url(command, **params):
    """Build Namecheap API URL with authentication"""
    url_params = {
        'ApiUser': API_USER,
        'ApiKey': API_KEY,
        'UserName': USERNAME,
        'ClientIp': CLIENT_IP,
        'Command': command,
        **params
    }
    param_str = '&'.join(f"{k}={v}" for k, v in url_params.items())
    return f"{BASE_URL}?{param_str}"

def get_existing_hosts():
    """Get existing DNS hosts for the domain"""
    url = build_url(
        'namecheap.domains.dns.getHosts',
        SLD=SLD,
        TLD=TLD
    )

    print("📋 Fetching existing DNS records...")
    response = requests.get(url)

    if response.status_code != 200:
        print(f"❌ HTTP Error: {response.status_code}")
        sys.exit(1)

    root = ET.fromstring(response.content)

    # Check for API errors
    errors = root.findall('.//{http://api.namecheap.com/xml.response}Error')
    if errors:
        for error in errors:
            print(f"❌ API Error: {error.text}")
        sys.exit(1)

    # Parse existing hosts
    hosts = []
    for host in root.findall('.//{http://api.namecheap.com/xml.response}host'):
        hosts.append({
            'HostId': host.get('HostId', ''),
            'Name': host.get('Name', '@'),
            'Type': host.get('Type'),
            'Address': host.get('Address'),
            'TTL': host.get('TTL', '1800'),
            'MXPref': host.get('MXPref', '10') if host.get('Type') == 'MX' else ''
        })

    print(f"✅ Found {len(hosts)} existing DNS records")
    return hosts

def set_hosts(hosts):
    """Set all DNS hosts for the domain"""
    params = {
        'SLD': SLD,
        'TLD': TLD
    }

    # Add each host as numbered parameters
    for i, host in enumerate(hosts, 1):
        params[f'HostName{i}'] = host['Name']
        params[f'RecordType{i}'] = host['Type']
        params[f'Address{i}'] = host['Address']
        params[f'TTL{i}'] = host['TTL']
        if host['Type'] == 'MX' and host.get('MXPref'):
            params[f'MXPref{i}'] = host['MXPref']

    url = build_url('namecheap.domains.dns.setHosts', **params)

    print(f"📝 Updating DNS records...")
    response = requests.get(url)

    if response.status_code != 200:
        print(f"❌ HTTP Error: {response.status_code}")
        sys.exit(1)

    root = ET.fromstring(response.content)

    # Check for API errors
    errors = root.findall('.//{http://api.namecheap.com/xml.response}Error')
    if errors:
        for error in errors:
            print(f"❌ API Error: {error.text}")
        sys.exit(1)

    # Check for success
    result = root.find('.//{http://api.namecheap.com/xml.response}DomainDNSSetHostsResult')
    if result is not None and result.get('IsSuccess') == 'true':
        print(f"✅ DNS records updated successfully!")
        return True
    else:
        print(f"❌ Failed to update DNS records")
        return False

def main():
    """Main function"""
    print(f"\n🌐 Adding DNS record for tds.{SLD}.{TLD}")
    print(f"   IP Address: {NEW_IP}")
    print()

    # Get existing hosts
    hosts = get_existing_hosts()

    # Check if TDS record already exists
    existing_tds = next((h for h in hosts if h['Name'] == NEW_HOST and h['Type'] == 'A'), None)

    if existing_tds:
        print(f"\n⚠️  Record already exists: {NEW_HOST}.{SLD}.{TLD} -> {existing_tds['Address']}")
        response = input("Update to new IP? (y/N): ")
        if response.lower() != 'y':
            print("Cancelled.")
            return
        # Update existing record
        existing_tds['Address'] = NEW_IP
        existing_tds['TTL'] = NEW_TTL
    else:
        # Add new record
        print(f"\n➕ Adding new A record: {NEW_HOST}.{SLD}.{TLD} -> {NEW_IP}")
        new_record = {
            'Name': NEW_HOST,
            'Type': 'A',
            'Address': NEW_IP,
            'TTL': NEW_TTL
        }
        hosts.append(new_record)

    # Update DNS records
    if set_hosts(hosts):
        print(f"\n✅ Success! DNS record added:")
        print(f"   {NEW_HOST}.{SLD}.{TLD} -> {NEW_IP}")
        print(f"\n⏱️  DNS propagation may take 5-30 minutes")
        print(f"\nVerify with:")
        print(f"   dig {NEW_HOST}.{SLD}.{TLD}")
        print(f"   nslookup {NEW_HOST}.{SLD}.{TLD}")
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()
