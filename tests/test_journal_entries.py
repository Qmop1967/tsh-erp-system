#!/usr/bin/env python3
"""
Test Journal Entry Creation and Posting
This script tests the journal entry creation, validation, and posting functionality.
"""

import requests
import json
from decimal import Decimal
from datetime import datetime, date

# Configuration
BASE_URL = "http://localhost:8000/api/accounting"
HEADERS = {"Content-Type": "application/json"}

def test_journal_entry_workflow():
    """Test complete journal entry workflow: create, validate, and post"""
    
    print("🧾 Testing Journal Entry Workflow")
    print("=" * 50)
    
    # Step 1: Get available journals
    print("\n1️⃣ Getting available journals...")
    try:
        response = requests.get(f"{BASE_URL}/journals")
        if response.status_code == 200:
            journals = response.json()
            print(f"✅ Found {len(journals)} journals")
            general_journal = next(j for j in journals if j['code'] == 'GJ')
            print(f"   Using General Journal (ID: {general_journal['id']})")
        else:
            print(f"❌ Failed to get journals: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error getting journals: {e}")
        return False
    
    # Step 2: Get chart of accounts
    print("\n2️⃣ Getting chart of accounts...")
    try:
        response = requests.get(f"{BASE_URL}/chart-of-accounts")
        if response.status_code == 200:
            charts = response.json()
            print(f"✅ Found {len(charts)} chart of accounts")
            main_chart = charts[0]  # Use first chart
            print(f"   Using chart: {main_chart['name_en']}")
        else:
            print(f"❌ Failed to get charts: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error getting charts: {e}")
        return False
    
    # Step 3: Get accounts from the chart
    print("\n3️⃣ Getting accounts...")
    try:
        response = requests.get(f"{BASE_URL}/accounts?chart_id={main_chart['id']}")
        if response.status_code == 200:
            accounts = response.json()
            print(f"✅ Found {len(accounts)} accounts")
            
            # Find suitable accounts for our test transaction
            # We need at least one asset account and one expense/revenue account
            cash_account = next((a for a in accounts if 'cash' in a['name_en'].lower()), None)
            expense_account = next((a for a in accounts if 'expense' in a['name_en'].lower()), None)
            
            if not cash_account:
                cash_account = next((a for a in accounts if a['account_type'] == 'ASSET'), None)
            if not expense_account:
                expense_account = next((a for a in accounts if a['account_type'] == 'EXPENSE'), None)
            
            if not cash_account or not expense_account:
                print("❌ Could not find suitable accounts for testing")
                print("   Available accounts:")
                for account in accounts[:5]:  # Show first 5
                    print(f"     - {account['name_en']} ({account['account_type']})")
                return False
            
            print(f"   Using Cash Account: {cash_account['name_en']} (ID: {cash_account['id']})")
            print(f"   Using Expense Account: {expense_account['name_en']} (ID: {expense_account['id']})")
            
        else:
            print(f"❌ Failed to get accounts: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error getting accounts: {e}")
        return False
    
    # Step 4: Get fiscal year and periods
    print("\n4️⃣ Getting fiscal year and periods...")
    try:
        response = requests.get(f"{BASE_URL}/fiscal-years")
        if response.status_code == 200:
            fiscal_years = response.json()
            if fiscal_years:
                current_fy = fiscal_years[0]
                print(f"✅ Using fiscal year: {current_fy['name']}")
                
                # Get periods for this fiscal year
                response = requests.get(f"{BASE_URL}/accounting-periods?fiscal_year_id={current_fy['id']}")
                if response.status_code == 200:
                    periods = response.json()
                    if periods:
                        current_period = periods[0]
                        print(f"   Using period: {current_period['name']}")
                    else:
                        print("❌ No accounting periods found")
                        return False
                else:
                    print(f"❌ Failed to get periods: {response.status_code}")
                    return False
            else:
                print("❌ No fiscal years found")
                return False
        else:
            print(f"❌ Failed to get fiscal years: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error getting fiscal year: {e}")
        return False
    
    # Step 5: Get currencies
    print("\n5️⃣ Getting currencies...")
    try:
        response = requests.get(f"{BASE_URL}/currencies")
        if response.status_code == 200:
            currencies = response.json()
            base_currency = next(c for c in currencies if c['is_base_currency'])
            print(f"✅ Using base currency: {base_currency['code']}")
        else:
            print(f"❌ Failed to get currencies: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error getting currencies: {e}")
        return False
    
    # Step 6: Create a journal entry
    print("\n6️⃣ Creating journal entry...")
    entry_data = {
        "journal_id": general_journal['id'],
        "period_id": current_period['id'],
        "currency_id": base_currency['id'],
        "entry_number": f"JE-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "reference": "TEST-001",
        "description_ar": "اختبار قيد يومية",
        "description_en": "Test journal entry",
        "entry_date": date.today().isoformat(),
        "journal_lines": [
            {
                "account_id": expense_account['id'],
                "description_ar": "مصروف اختبار",
                "description_en": "Test expense",
                "debit_amount": 1000.00,
                "credit_amount": 0.00
            },
            {
                "account_id": cash_account['id'],
                "description_ar": "نقدية",
                "description_en": "Cash",
                "debit_amount": 0.00,
                "credit_amount": 1000.00
            }
        ]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/journal-entries", json=entry_data, headers=HEADERS)
        if response.status_code == 200:
            created_entry = response.json()
            print(f"✅ Journal entry created successfully")
            print(f"   Entry ID: {created_entry['id']}")
            print(f"   Entry Number: {created_entry['entry_number']}")
            print(f"   Status: {created_entry['status']}")
            print(f"   Total Debit: {created_entry['total_debit']}")
            print(f"   Total Credit: {created_entry['total_credit']}")
        else:
            print(f"❌ Failed to create journal entry: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error creating journal entry: {e}")
        return False
    
    # Step 7: Post the journal entry
    print("\n7️⃣ Posting journal entry...")
    try:
        response = requests.post(f"{BASE_URL}/journal-entries/{created_entry['id']}/post")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Journal entry posted successfully")
            print(f"   Message: {result['message']}")
            
            # Verify the entry status changed
            response = requests.get(f"{BASE_URL}/journal-entries/{created_entry['id']}")
            if response.status_code == 200:
                updated_entry = response.json()
                print(f"   Updated Status: {updated_entry['status']}")
                if updated_entry.get('posted_at'):
                    print(f"   Posted At: {updated_entry['posted_at']}")
            
        else:
            print(f"❌ Failed to post journal entry: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error posting journal entry: {e}")
        return False
    
    # Step 8: Test creating an unbalanced entry (should fail)
    print("\n8️⃣ Testing validation (unbalanced entry)...")
    unbalanced_entry = {
        "journal_id": general_journal['id'],
        "period_id": current_period['id'],
        "currency_id": base_currency['id'],
        "entry_number": f"JE-UNBAL-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "reference": "TEST-UNBALANCED",
        "description_ar": "اختبار قيد غير متوازن",
        "description_en": "Test unbalanced entry",
        "entry_date": date.today().isoformat(),
        "journal_lines": [
            {
                "account_id": expense_account['id'],
                "description_ar": "مصروف",
                "description_en": "Expense",
                "debit_amount": 1000.00,
                "credit_amount": 0.00
            },
            {
                "account_id": cash_account['id'],
                "description_ar": "نقدية",
                "description_en": "Cash",
                "debit_amount": 0.00,
                "credit_amount": 500.00  # Intentionally unbalanced
            }
        ]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/journal-entries", json=unbalanced_entry, headers=HEADERS)
        if response.status_code == 400:
            print("✅ Validation working: Unbalanced entry correctly rejected")
            error_detail = response.json().get('detail', 'Unknown error')
            print(f"   Error: {error_detail}")
        else:
            print(f"❌ Validation failed: Unbalanced entry was accepted (status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Error testing validation: {e}")
        return False
    
    print("\n🎉 Journal Entry Workflow Test Completed Successfully!")
    return True

def show_journal_entry_summary():
    """Show summary of existing journal entries"""
    
    print("\n📊 Journal Entry Summary")
    print("=" * 30)
    
    try:
        response = requests.get(f"{BASE_URL}/journal-entries")
        if response.status_code == 200:
            entries = response.json()
            print(f"Total Journal Entries: {len(entries)}")
            
            if entries:
                print("\nRecent Entries:")
                for entry in entries[-5:]:  # Show last 5 entries
                    print(f"  • {entry['entry_number']} - {entry['description_en']} "
                          f"({entry['status']}) - {entry['total_debit']}")
        else:
            print(f"❌ Failed to get journal entries: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting journal entries: {e}")

if __name__ == "__main__":
    print("🧪 TSH ERP Accounting System - Journal Entry Testing")
    print("=" * 60)
    
    # Test the complete workflow
    success = test_journal_entry_workflow()
    
    # Show summary
    show_journal_entry_summary()
    
    if success:
        print("\n✅ All tests passed! Journal entry functionality is working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the error messages above.")
