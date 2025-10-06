#!/usr/bin/env python3
"""
Comprehensive Analysis of Extracted Zoho Data
تحليل شامل لبيانات Zoho المستخرجة
"""

import json
from collections import defaultdict
from datetime import datetime

def analyze_inventory_items():
    """Analyze inventory items data"""
    print("📦 INVENTORY ITEMS ANALYSIS")
    print("=" * 50)
    
    try:
        with open('all_zoho_inventory_items.json', 'r', encoding='utf-8') as f:
            items = json.load(f)
        
        total_items = len(items)
        print(f"📊 Total Items: {total_items:,}")
        
        # Status analysis
        active_items = sum(1 for item in items if item.get('is_active', False))
        inactive_items = total_items - active_items
        print(f"   ✅ Active: {active_items:,} ({active_items/total_items*100:.1f}%)")
        print(f"   ❌ Inactive: {inactive_items:,} ({inactive_items/total_items*100:.1f}%)")
        
        # Price analysis
        prices = [float(item.get('selling_price_usd', 0)) for item in items if item.get('selling_price_usd')]
        costs = [float(item.get('cost_price_usd', 0)) for item in items if item.get('cost_price_usd')]
        
        if prices:
            print(f"💰 Selling Price Range: ${min(prices):.2f} - ${max(prices):,.2f}")
            print(f"   Average: ${sum(prices)/len(prices):.2f}")
            
        if costs:
            print(f"💸 Cost Price Range: ${min(costs):.2f} - ${max(costs):,.2f}")
            print(f"   Average: ${sum(costs)/len(costs):.2f}")
        
        # Category analysis
        categories = defaultdict(int)
        for item in items:
            category = item.get('specifications', {}).get('category', 'Uncategorized')
            if not category or category.strip() == '':
                category = 'Uncategorized'
            categories[category] += 1
        
        print(f"\n📂 Categories ({len(categories)} total):")
        for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"   • {category}: {count:,} items")
        
        # Brand analysis
        brands = defaultdict(int)
        for item in items:
            brand = item.get('brand', 'No Brand')
            if not brand or brand.strip() == '':
                brand = 'No Brand'
            brands[brand] += 1
        
        print(f"\n🏷️ Top Brands:")
        for brand, count in sorted(brands.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"   • {brand}: {count:,} items")
        
        # High value items
        high_value_items = sorted([item for item in items if float(item.get('selling_price_usd', 0)) > 50], 
                                key=lambda x: float(x.get('selling_price_usd', 0)), reverse=True)[:10]
        
        print(f"\n💎 Top 10 Most Expensive Items:")
        for i, item in enumerate(high_value_items):
            price = float(item.get('selling_price_usd', 0))
            print(f"   {i+1:2d}. {item.get('name_en', 'N/A')[:45]} - ${price:,.2f}")
        
    except Exception as e:
        print(f"❌ Error analyzing inventory: {e}")

def analyze_customers():
    """Analyze customers data"""
    print("\n\n👥 CUSTOMERS ANALYSIS")
    print("=" * 50)
    
    try:
        with open('all_zoho_customers.json', 'r', encoding='utf-8') as f:
            customers = json.load(f)
        
        total_customers = len(customers)
        print(f"📊 Total Customers: {total_customers:,}")
        
        # Status analysis
        active_customers = sum(1 for customer in customers if customer.get('is_active', False))
        inactive_customers = total_customers - active_customers
        print(f"   ✅ Active: {active_customers:,} ({active_customers/total_customers*100:.1f}%)")
        print(f"   ❌ Inactive: {inactive_customers:,} ({inactive_customers/total_customers*100:.1f}%)")
        
        # Currency analysis
        currencies = defaultdict(int)
        for customer in customers:
            currency = customer.get('currency', 'Unknown')
            currencies[currency] += 1
        
        print(f"\n💱 Currencies:")
        for currency, count in sorted(currencies.items(), key=lambda x: x[1], reverse=True):
            print(f"   • {currency}: {count:,} customers")
        
        # Country analysis
        countries = defaultdict(int)
        for customer in customers:
            country = customer.get('country', 'Unknown')
            countries[country] += 1
        
        print(f"\n🌍 Countries:")
        for country, count in sorted(countries.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"   • {country}: {count:,} customers")
        
        # Credit analysis
        credit_limits = [float(customer.get('credit_limit', 0)) for customer in customers 
                        if customer.get('credit_limit') and float(customer.get('credit_limit', 0)) > 0]
        
        if credit_limits:
            print(f"\n💳 Credit Limits:")
            print(f"   Range: ${min(credit_limits):,.2f} - ${max(credit_limits):,.2f}")
            print(f"   Average: ${sum(credit_limits)/len(credit_limits):,.2f}")
            print(f"   Customers with credit: {len(credit_limits):,}")
        
        # Outstanding receivables
        receivables = [float(customer.get('outstanding_receivable', 0)) for customer in customers 
                      if customer.get('outstanding_receivable') and float(customer.get('outstanding_receivable', 0)) > 0]
        
        if receivables:
            print(f"\n📊 Outstanding Receivables:")
            print(f"   Total: ${sum(receivables):,.2f}")
            print(f"   Average: ${sum(receivables)/len(receivables):,.2f}")
            print(f"   Customers with outstanding: {len(receivables):,}")
        
    except Exception as e:
        print(f"❌ Error analyzing customers: {e}")

def analyze_vendors():
    """Analyze vendors data"""
    print("\n\n🏭 VENDORS ANALYSIS")
    print("=" * 50)
    
    try:
        with open('all_zoho_vendors.json', 'r', encoding='utf-8') as f:
            vendors = json.load(f)
        
        total_vendors = len(vendors)
        print(f"📊 Total Vendors: {total_vendors:,}")
        
        # Status analysis
        active_vendors = sum(1 for vendor in vendors if vendor.get('is_active', False))
        inactive_vendors = total_vendors - active_vendors
        print(f"   ✅ Active: {active_vendors:,} ({active_vendors/total_vendors*100:.1f}%)")
        print(f"   ❌ Inactive: {inactive_vendors:,} ({inactive_vendors/total_vendors*100:.1f}%)")
        
        # Currency analysis
        currencies = defaultdict(int)
        for vendor in vendors:
            currency = vendor.get('currency', 'Unknown')
            currencies[currency] += 1
        
        print(f"\n💱 Currencies:")
        for currency, count in sorted(currencies.items(), key=lambda x: x[1], reverse=True):
            print(f"   • {currency}: {count:,} vendors")
        
        # Country analysis
        countries = defaultdict(int)
        for vendor in vendors:
            country = vendor.get('country', 'Unknown')
            countries[country] += 1
        
        print(f"\n🌍 Countries:")
        for country, count in sorted(countries.items(), key=lambda x: x[1], reverse=True):
            print(f"   • {country}: {count:,} vendors")
        
        # Outstanding payables
        payables = [float(vendor.get('outstanding_payable', 0)) for vendor in vendors 
                   if vendor.get('outstanding_payable') and float(vendor.get('outstanding_payable', 0)) > 0]
        
        if payables:
            print(f"\n📊 Outstanding Payables:")
            print(f"   Total: ${sum(payables):,.2f}")
            print(f"   Average: ${sum(payables)/len(payables):,.2f}")
            print(f"   Vendors with outstanding: {len(payables):,}")
        
    except Exception as e:
        print(f"❌ Error analyzing vendors: {e}")

def generate_summary():
    """Generate overall summary"""
    print("\n\n📋 OVERALL SUMMARY")
    print("=" * 50)
    
    try:
        with open('zoho_extraction_summary.json', 'r', encoding='utf-8') as f:
            summary = json.load(f)
        
        print("✅ Zoho Data Successfully Extracted:")
        print(f"   🏢 Organization: Tech Spider Hand Company For General Trading Ltd")
        print(f"   🆔 Organization ID: {summary['organization_id']}")
        print(f"   📅 Extraction Date: {summary['extraction_date'][:19]}")
        print()
        print("📊 Data Totals:")
        totals = summary['totals']
        print(f"   📦 Inventory Items: {totals['inventory_items']:,}")
        print(f"   👥 Customers: {totals['customers']:,}")
        print(f"   🏭 Vendors: {totals['vendors']:,}")
        print(f"   📋 Sales Orders: {totals['sales_orders']:,}")
        
        # Calculate file sizes
        files = [
            'all_zoho_inventory_items.json',
            'all_zoho_customers.json',
            'all_zoho_vendors.json'
        ]
        
        total_size = 0
        print(f"\n📁 Generated Files:")
        for filename in files:
            try:
                import os
                size = os.path.getsize(filename)
                total_size += size
                print(f"   📄 {filename}: {size:,} bytes ({size/1024/1024:.1f} MB)")
            except:
                pass
        
        print(f"   📊 Total Size: {total_size:,} bytes ({total_size/1024/1024:.1f} MB)")
        
    except Exception as e:
        print(f"❌ Error generating summary: {e}")

if __name__ == "__main__":
    print("📊 COMPREHENSIVE ZOHO DATA ANALYSIS")
    print("تحليل شامل لبيانات Zoho")
    print("=" * 60)
    
    analyze_inventory_items()
    analyze_customers()
    analyze_vendors()
    generate_summary()
    
    print("\n" + "=" * 60)
    print("✅ Analysis completed successfully!")
    print(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
