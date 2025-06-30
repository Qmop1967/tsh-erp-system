#!/usr/bin/env python3
"""
TSH ERP Accounting System Status Check
فحص حالة النظام المحاسبي لشركة TSH
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json
from typing import Dict, Any


def test_endpoint(endpoint: str, description: str) -> Dict[str, Any]:
    """Test an API endpoint"""
    try:
        response = requests.get(f"http://localhost:8000{endpoint}")
        success = response.status_code == 200
        
        if success:
            data = response.json()
            count = len(data) if isinstance(data, list) else 1
            print(f"✅ {description}: {count} record(s)")
            return {"success": True, "count": count, "data": data}
        else:
            print(f"❌ {description}: HTTP {response.status_code}")
            return {"success": False, "status_code": response.status_code}
            
    except Exception as e:
        print(f"❌ {description}: {str(e)}")
        return {"success": False, "error": str(e)}


def main():
    """Main function to check accounting system status"""
    print("=== TSH ERP Accounting System Status ===")
    print("=== حالة النظام المحاسبي لشركة TSH ===\n")
    
    # Test endpoints
    endpoints = [
        ("/api/accounting/currencies", "Currencies (العملات)"),
        ("/api/accounting/chart-of-accounts", "Chart of Accounts (دليل الحسابات)"),
        ("/api/accounting/exchange-rates", "Exchange Rates (أسعار الصرف)"),
    ]
    
    print("Testing API endpoints:")
    print("-" * 50)
    
    results = {}
    for endpoint, description in endpoints:
        results[endpoint] = test_endpoint(endpoint, description)
    
    print("\nDetailed Results:")
    print("-" * 50)
    
    # Currency details
    if results["/api/accounting/currencies"]["success"]:
        currencies = results["/api/accounting/currencies"]["data"]
        print(f"\n📈 Currencies ({len(currencies)}):")
        for currency in currencies:
            status = "✅ Base" if currency["is_base_currency"] else "💱 Secondary"
            print(f"   {status} {currency['code']} - {currency['name_en']} ({currency['symbol']})")
            print(f"      Rate: {currency['exchange_rate']} | Active: {currency['is_active']}")
    
    # Chart of Accounts summary
    if results["/api/accounting/chart-of-accounts"]["success"]:
        accounts = results["/api/accounting/chart-of-accounts"]["data"]
        print(f"\n📊 Chart of Accounts ({len(accounts)}):")
        
        # Group by account type
        by_type = {}
        for account in accounts:
            acc_type = account["account_type"]
            if acc_type not in by_type:
                by_type[acc_type] = []
            by_type[acc_type].append(account)
        
        type_names = {
            "ASSET": "Assets (الأصول)",
            "LIABILITY": "Liabilities (الخصوم)",
            "EQUITY": "Equity (حقوق الملكية)",
            "REVENUE": "Revenue (الإيرادات)",
            "EXPENSE": "Expenses (المصروفات)"
        }
        
        for acc_type, type_accounts in by_type.items():
            type_name = type_names.get(acc_type, acc_type)
            print(f"   {type_name}: {len(type_accounts)} accounts")
            
            # Show main accounts (level 1)
            main_accounts = [acc for acc in type_accounts if acc["level"] == 1]
            for main_acc in main_accounts:
                posting = "✏️ " if main_acc["allow_posting"] else "📁 "
                print(f"      {posting}{main_acc['code']} - {main_acc['name_en']}")
    
    print(f"\n🔧 System Status:")
    success_count = sum(1 for result in results.values() if result["success"])
    total_count = len(results)
    
    if success_count == total_count:
        print("✅ All systems operational")
        print("✅ جميع الأنظمة تعمل بشكل طبيعي")
    else:
        print(f"⚠️  {success_count}/{total_count} systems operational")
        print(f"⚠️  {success_count}/{total_count} من الأنظمة تعمل")
    
    print("\n=== Report Complete ===")
    print("=== انتهى التقرير ===")


if __name__ == "__main__":
    main()
