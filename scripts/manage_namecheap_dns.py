#!/usr/bin/env python3
"""
Namecheap DNS Management Script
Manage DNS records for Namecheap domains via API

Usage:
    python3 manage_namecheap_dns.py list
    python3 manage_namecheap_dns.py get-records tsh.sale
    python3 manage_namecheap_dns.py add-record tsh.sale A erp 167.71.39.50
    python3 manage_namecheap_dns.py update-record tsh.sale A erp 167.71.39.50
    python3 manage_namecheap_dns.py delete-record tsh.sale A erp
"""

import os
import sys
import argparse
from typing import List, Dict
from namecheap import NamecheapClient


def create_client() -> NamecheapClient:
    """Create and return authenticated Namecheap client"""
    api_user = os.getenv('NAMECHEAP_API_USER')
    api_key = os.getenv('NAMECHEAP_API_KEY')
    username = os.getenv('NAMECHEAP_USERNAME')
    client_ip = os.getenv('NAMECHEAP_CLIENT_IP')
    sandbox = os.getenv('NAMECHEAP_SANDBOX', 'false').lower() == 'true'

    if not all([api_user, api_key, username, client_ip]):
        print("❌ Error: Missing Namecheap API credentials")
        print("Please set the following environment variables:")
        print("  - NAMECHEAP_API_USER")
        print("  - NAMECHEAP_API_KEY")
        print("  - NAMECHEAP_USERNAME")
        print("  - NAMECHEAP_CLIENT_IP")
        print("\nLoad credentials with:")
        print("  source ~/.namecheap_credentials")
        sys.exit(1)

    return NamecheapClient(
        api_user=api_user,
        api_key=api_key,
        username=username,
        client_ip=client_ip,
        sandbox=sandbox
    )


def list_domains(client: NamecheapClient):
    """List all domains in the account"""
    print("📋 Fetching domains...")
    try:
        domains = client.domains_getList()
        print(f"\n✅ Found {len(domains)} domain(s):\n")
        for domain in domains:
            name = domain.get('Name', 'Unknown')
            expires = domain.get('Expires', 'Unknown')
            auto_renew = domain.get('IsAutoRenew', False)
            locked = domain.get('IsLocked', False)

            status = []
            if auto_renew:
                status.append("Auto-Renew")
            if locked:
                status.append("Locked")

            status_str = f" [{', '.join(status)}]" if status else ""
            print(f"  • {name} (Expires: {expires}){status_str}")
    except Exception as e:
        print(f"❌ Error listing domains: {e}")
        sys.exit(1)


def get_records(client: NamecheapClient, domain: str):
    """Get DNS records for a domain"""
    print(f"📋 Fetching DNS records for {domain}...")

    # Split domain into SLD and TLD
    parts = domain.split('.')
    if len(parts) < 2:
        print(f"❌ Error: Invalid domain format: {domain}")
        sys.exit(1)

    sld = '.'.join(parts[:-1])
    tld = parts[-1]

    try:
        records = client.domains_dns_getHosts(sld=sld, tld=tld)
        print(f"\n✅ Found {len(records)} DNS record(s):\n")

        # Group by type
        record_types = {}
        for record in records:
            rec_type = record.get('Type', 'Unknown')
            if rec_type not in record_types:
                record_types[rec_type] = []
            record_types[rec_type].append(record)

        # Display grouped records
        for rec_type in sorted(record_types.keys()):
            print(f"  {rec_type} Records:")
            for record in record_types[rec_type]:
                hostname = record.get('Name', '@')
                address = record.get('Address', '')
                ttl = record.get('TTL', '')
                full_name = f"{hostname}.{domain}" if hostname != '@' else domain
                print(f"    • {full_name} -> {address} (TTL: {ttl})")
            print()
    except Exception as e:
        print(f"❌ Error getting DNS records: {e}")
        sys.exit(1)


def add_record(client: NamecheapClient, domain: str, record_type: str,
               hostname: str, value: str, ttl: int = 300):
    """Add a DNS record"""
    parts = domain.split('.')
    sld = '.'.join(parts[:-1])
    tld = parts[-1]

    print(f"➕ Adding {record_type} record: {hostname}.{domain} -> {value}")

    try:
        # Get existing records
        existing_records = client.domains_dns_getHosts(sld=sld, tld=tld)

        # Add new record
        new_record = {
            'HostName': hostname,
            'RecordType': record_type,
            'Address': value,
            'TTL': ttl
        }

        # Combine existing and new
        all_records = existing_records + [new_record]

        # Update DNS
        client.domains_dns_setHosts(sld=sld, tld=tld, host_records=all_records)
        print(f"✅ Successfully added {record_type} record")
    except Exception as e:
        print(f"❌ Error adding DNS record: {e}")
        sys.exit(1)


def update_record(client: NamecheapClient, domain: str, record_type: str,
                  hostname: str, value: str, ttl: int = 300):
    """Update an existing DNS record"""
    parts = domain.split('.')
    sld = '.'.join(parts[:-1])
    tld = parts[-1]

    print(f"✏️  Updating {record_type} record: {hostname}.{domain} -> {value}")

    try:
        # Get existing records
        existing_records = client.domains_dns_getHosts(sld=sld, tld=tld)

        # Find and update the record
        updated = False
        new_records = []
        for record in existing_records:
            if (record.get('Type') == record_type and
                record.get('Name') == hostname):
                # Update this record
                record['Address'] = value
                record['TTL'] = ttl
                updated = True
            new_records.append(record)

        if not updated:
            print(f"⚠️  Record not found, adding new record instead")
            new_records.append({
                'HostName': hostname,
                'RecordType': record_type,
                'Address': value,
                'TTL': ttl
            })

        # Update DNS
        client.domains_dns_setHosts(sld=sld, tld=tld, host_records=new_records)
        print(f"✅ Successfully updated {record_type} record")
    except Exception as e:
        print(f"❌ Error updating DNS record: {e}")
        sys.exit(1)


def delete_record(client: NamecheapClient, domain: str, record_type: str,
                  hostname: str):
    """Delete a DNS record"""
    parts = domain.split('.')
    sld = '.'.join(parts[:-1])
    tld = parts[-1]

    print(f"🗑️  Deleting {record_type} record: {hostname}.{domain}")

    try:
        # Get existing records
        existing_records = client.domains_dns_getHosts(sld=sld, tld=tld)

        # Filter out the record to delete
        new_records = [
            record for record in existing_records
            if not (record.get('Type') == record_type and
                   record.get('Name') == hostname)
        ]

        if len(new_records) == len(existing_records):
            print(f"⚠️  Record not found: {hostname}.{domain}")
            sys.exit(1)

        # Update DNS
        client.domains_dns_setHosts(sld=sld, tld=tld, host_records=new_records)
        print(f"✅ Successfully deleted {record_type} record")
    except Exception as e:
        print(f"❌ Error deleting DNS record: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Manage Namecheap DNS records',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all domains
  %(prog)s list

  # Get DNS records for a domain
  %(prog)s get-records tsh.sale

  # Add an A record
  %(prog)s add-record tsh.sale A erp 167.71.39.50

  # Update an existing record
  %(prog)s update-record tsh.sale A erp 167.71.39.50 --ttl 600

  # Delete a record
  %(prog)s delete-record tsh.sale A erp

Environment Variables Required:
  NAMECHEAP_API_USER     - Your Namecheap username
  NAMECHEAP_API_KEY      - Your Namecheap API key
  NAMECHEAP_USERNAME     - Your Namecheap username
  NAMECHEAP_CLIENT_IP    - Your whitelisted IP address
  NAMECHEAP_SANDBOX      - Set to 'true' for sandbox testing (optional)
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # List domains
    subparsers.add_parser('list', help='List all domains')

    # Get records
    get_parser = subparsers.add_parser('get-records', help='Get DNS records for a domain')
    get_parser.add_argument('domain', help='Domain name (e.g., tsh.sale)')

    # Add record
    add_parser = subparsers.add_parser('add-record', help='Add a DNS record')
    add_parser.add_argument('domain', help='Domain name')
    add_parser.add_argument('type', help='Record type (A, AAAA, CNAME, MX, TXT, etc.)')
    add_parser.add_argument('hostname', help='Hostname (use @ for root domain)')
    add_parser.add_argument('value', help='Record value')
    add_parser.add_argument('--ttl', type=int, default=300, help='TTL in seconds (default: 300)')

    # Update record
    update_parser = subparsers.add_parser('update-record', help='Update a DNS record')
    update_parser.add_argument('domain', help='Domain name')
    update_parser.add_argument('type', help='Record type')
    update_parser.add_argument('hostname', help='Hostname')
    update_parser.add_argument('value', help='New record value')
    update_parser.add_argument('--ttl', type=int, default=300, help='TTL in seconds')

    # Delete record
    delete_parser = subparsers.add_parser('delete-record', help='Delete a DNS record')
    delete_parser.add_argument('domain', help='Domain name')
    delete_parser.add_argument('type', help='Record type')
    delete_parser.add_argument('hostname', help='Hostname')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Create client
    client = create_client()

    # Execute command
    if args.command == 'list':
        list_domains(client)
    elif args.command == 'get-records':
        get_records(client, args.domain)
    elif args.command == 'add-record':
        add_record(client, args.domain, args.type, args.hostname, args.value, args.ttl)
    elif args.command == 'update-record':
        update_record(client, args.domain, args.type, args.hostname, args.value, args.ttl)
    elif args.command == 'delete-record':
        delete_record(client, args.domain, args.type, args.hostname)


if __name__ == '__main__':
    main()
