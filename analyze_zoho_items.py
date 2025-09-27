#!/usr/bin/env python3
"""
Analyze Zoho inventory items data
تحليل بيانات مخزون Zoho
"""

import json

def analyze_zoho_items():
    """Analyze the retrieved Zoho items"""
    print("📊 Zoho Items Analysis")
    print("=" * 50)
    
    try:
        with open('zoho_inventory_items.json', 'r', encoding='utf-8') as f:
            items = json.load(f)
        
        print(f"📦 Total items loaded: {len(items)}")
        print()
        
        if not items:
            print("❌ No items found!")
            return
        
        # Sample item details
        print("🔍 Sample Item Details:")
        sample = items[0]
        print(f"   ID: {sample.get('zoho_item_id')}")
        print(f"   Code: {sample.get('code')}")  
        print(f"   Name: {sample.get('name_en')}")
        print(f"   Cost: ${sample.get('cost_price_usd', 0)} USD")
        print(f"   Selling Price: ${sample.get('selling_price_usd', 0)} USD")
        print(f"   Unit: {sample.get('unit_of_measure')}")
        print(f"   Active: {sample.get('is_active')}")
        print()
        
        # Count active vs inactive
        active_count = sum(1 for item in items if item.get('is_active', False))
        inactive_count = len(items) - active_count
        
        print("📈 Status Analysis:")
        print(f"   ✅ Active items: {active_count}")
        print(f"   ❌ Inactive items: {inactive_count}")
        print()
        
        # Price analysis
        selling_prices = []
        cost_prices = []
        
        for item in items:
            if item.get('selling_price_usd'):
                try:
                    selling_prices.append(float(item['selling_price_usd']))
                except:
                    pass
            if item.get('cost_price_usd'):
                try:
                    cost_prices.append(float(item['cost_price_usd']))
                except:
                    pass
        
        if selling_prices:
            print("💰 Price Analysis:")
            print(f"   Selling Price Range: ${min(selling_prices):.2f} - ${max(selling_prices):.2f}")
            print(f"   Average Selling Price: ${sum(selling_prices)/len(selling_prices):.2f}")
            
        if cost_prices:
            print(f"   Cost Price Range: ${min(cost_prices):.2f} - ${max(cost_prices):.2f}")
            print(f"   Average Cost Price: ${sum(cost_prices)/len(cost_prices):.2f}")
        
        print()
        
        # Category analysis
        categories = {}
        for item in items:
            category = item.get('specifications', {}).get('category', 'Uncategorized')
            if not category:
                category = 'Uncategorized'
            categories[category] = categories.get(category, 0) + 1
        
        print("📂 Category Analysis:")
        for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            print(f"   • {category}: {count} items")
        
        print()
        
        # Unit analysis
        units = {}
        for item in items:
            unit = item.get('unit_of_measure', 'Unknown')
            units[unit] = units.get(unit, 0) + 1
        
        print("📏 Unit of Measure Analysis:")
        for unit, count in sorted(units.items(), key=lambda x: x[1], reverse=True):
            print(f"   • {unit}: {count} items")
        
        # Top items by price
        print("\n💎 Top 10 Most Expensive Items:")
        sorted_items = sorted(items, key=lambda x: float(x.get('selling_price_usd', 0)), reverse=True)
        for i, item in enumerate(sorted_items[:10]):
            price = float(item.get('selling_price_usd', 0))
            print(f"   {i+1:2d}. {item.get('name_en', 'N/A')[:40]} - ${price:.2f}")
        
        print("\n" + "=" * 50)
        print("✅ Analysis completed!")
        
    except FileNotFoundError:
        print("❌ zoho_inventory_items.json not found!")
    except Exception as e:
        print(f"❌ Error analyzing data: {e}")

if __name__ == "__main__":
    analyze_zoho_items()
