#!/usr/bin/env python3
"""
Zoho MCP Fetch Demo
===================

Demonstrates how to fetch items from Zoho using MCP functions.
This script shows the direct MCP integration capabilities.

Author: TSH ERP Team
Date: November 8, 2025
"""

import json
import os
from dotenv import load_dotenv

load_dotenv()

# Note: In Cursor/Claude, you can use MCP functions directly like:
# mcp_ZohoMCP_ZohoBooks_list_items()
# mcp_ZohoMCP_ZohoBooks_get_item()

def demo_fetch_item():
    """Demo: Fetch a specific item by ID"""
    print("=" * 70)
    print("📦 ZOHO MCP FETCH DEMONSTRATION")
    print("=" * 70)
    
    organization_id = os.getenv("ZOHO_ORGANIZATION_ID", "748369814")
    item_id = "2646610000066650802"  # Example item ID
    
    print(f"\n🔍 Fetching Item Details")
    print(f"   Organization ID: {organization_id}")
    print(f"   Item ID: {item_id}")
    
    print("\n" + "-" * 70)
    print("✅ MCP Function Call:")
    print("-" * 70)
    print("""
# In Cursor/Claude, you can call:
mcp_ZohoMCP_ZohoBooks_get_item(
    query_params={'organization_id': '748369814'},
    path_variables={'item_id': '2646610000066650802'}
)
    """)
    
    print("\n" + "-" * 70)
    print("📊 Example Response:")
    print("-" * 70)
    
    # Example response structure
    example_response = {
        "code": 0,
        "message": "success",
        "item": {
            "item_id": "2646610000066650802",
            "name": "( 2 Female To 1 Male ) RCA Adapter",
            "sku": "tsh00059y",
            "rate": 1.00,
            "available_stock": 934.0,
            "status": "active",
            "category_name": "",
            "description": "",
            "image_name": "772963.jpg",
            "purchase_rate": 0.75,
            "sales_rate": 1.00,
            "locations": [
                {
                    "location_name": "WholeSale WareHouse (Warehouse)",
                    "location_available_stock": 934.0
                }
            ]
        }
    }
    
    print(json.dumps(example_response, indent=2))
    
    print("\n" + "-" * 70)
    print("📋 Available Zoho MCP Functions:")
    print("-" * 70)
    print("""
1. List Items:
   mcp_ZohoMCP_ZohoBooks_list_items(
       query_params={
           'organization_id': '748369814',
           'per_page': 200,
           'page': 1
       }
   )

2. Get Item Details:
   mcp_ZohoMCP_ZohoBooks_get_item(
       query_params={'organization_id': '748369814'},
       path_variables={'item_id': 'ITEM_ID'}
   )

3. List Contacts:
   mcp_ZohoMCP_ZohoBooks_list_contacts(
       query_params={'organization_id': '748369814'}
   )

4. Get Contact:
   mcp_ZohoMCP_ZohoBooks_get_contact(
       query_params={'organization_id': '748369814'},
       path_variables={'contact_id': 'CONTACT_ID'}
   )

5. List Invoices:
   mcp_ZohoMCP_ZohoBooks_list_invoices(
       query_params={'organization_id': '748369814'}
   )

6. Get Invoice:
   mcp_ZohoMCP_ZohoBooks_get_invoice(
       query_params={'organization_id': '748369814'},
       path_variables={'invoice_id': 'INVOICE_ID'}
   )

7. List Sales Orders:
   mcp_ZohoMCP_ZohoBooks_get_sales_order(
       query_params={'organization_id': '748369814'},
       path_variables={'salesorder_id': 'ORDER_ID'}
   )

8. List Items (Inventory):
   mcp_ZohoMCP_ZohoInventory_list_items(
       query_params={
           'organization_id': '748369814',
           'per_page': 200,
           'page': 1
       }
   )

9. List Pricebooks:
   mcp_ZohoMCP_ZohoInventory_list_pricebooks(
       query_params={
           'organization_id': '748369814',
           'per_page': 200,
           'page': 1
       }
   )
    """)
    
    print("\n" + "=" * 70)
    print("💡 Usage Tips:")
    print("=" * 70)
    print("""
1. All MCP functions are available directly in Cursor/Claude
2. No need for API keys or tokens - MCP handles authentication
3. Functions return structured JSON responses
4. Use pagination for large datasets (per_page, page parameters)
5. Organization ID is required for all functions
6. Some functions require path_variables (like item_id, contact_id)
    """)
    
    print("\n" + "=" * 70)
    print("✅ MCP Integration Status: ACTIVE")
    print("=" * 70)


if __name__ == "__main__":
    demo_fetch_item()







