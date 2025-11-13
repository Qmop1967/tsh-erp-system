# 🔗 Zoho Webhooks - Simple Setup Instructions

**What:** Configure automatic real-time sync between Zoho Books and TSH ERP  
**Time:** 15-20 minutes  
**Difficulty:** Easy (just copy-paste URLs)

---

## ✅ What's Already Done

Your TSH ERP system has webhook endpoints ready and working:
- ✅ All 8 webhook endpoints deployed
- ✅ Health check passing
- ✅ Ready to receive Zoho webhooks

**You just need to configure them in Zoho Books!**

---

## 🚀 3 Simple Steps

### STEP 1: Open Zoho Books Settings (2 minutes)

1. Go to: **https://books.zoho.com**
2. Login with your credentials
3. Click: **Settings** (gear icon, top right)
4. Click: **Automation** (left sidebar)
5. Click: **Webhooks**

---

### STEP 2: Create 8 Webhooks (10-15 minutes)

For each webhook below, click **"+ New Webhook"** and fill in:

---

#### Webhook #1: Products

**Label:** `TSH Store - Products`  
**URL:** `https://erp.tsh.sale/api/tds/webhooks/products`  
**Method:** POST  
**Module:** Items  
**Events:** Check ALL boxes (Item Created, Updated, Deleted, etc.)

Click: **Save** → **Test Webhook**

---

#### Webhook #2: Customers

**Label:** `TSH Store - Customers`  
**URL:** `https://erp.tsh.sale/api/tds/webhooks/customers`  
**Method:** POST  
**Module:** Contacts  
**Events:** Check ALL boxes

Click: **Save** → **Test Webhook**

---

#### Webhook #3: Invoices

**Label:** `TSH Store - Invoices`  
**URL:** `https://erp.tsh.sale/api/tds/webhooks/invoices`  
**Method:** POST  
**Module:** Invoices  
**Events:** Check ALL boxes

Click: **Save** → **Test Webhook**

---

#### Webhook #4: Sales Orders

**Label:** `TSH Store - Sales Orders`  
**URL:** `https://erp.tsh.sale/api/tds/webhooks/orders`  
**Method:** POST  
**Module:** Sales Orders  
**Events:** Check ALL boxes

Click: **Save** → **Test Webhook**

---

#### Webhook #5: Purchase Bills

**Label:** `TSH Store - Bills`  
**URL:** `https://erp.tsh.sale/api/tds/webhooks/bills`  
**Method:** POST  
**Module:** Bills  
**Events:** Check ALL boxes

Click: **Save** → **Test Webhook**

---

#### Webhook #6: Credit Notes

**Label:** `TSH Store - Credit Notes`  
**URL:** `https://erp.tsh.sale/api/tds/webhooks/credit-notes`  
**Method:** POST  
**Module:** Credit Notes  
**Events:** Check ALL boxes

Click: **Save** → **Test Webhook**

---

#### Webhook #7: Stock Adjustments

**Label:** `TSH Store - Stock`  
**URL:** `https://erp.tsh.sale/api/tds/webhooks/stock`  
**Method:** POST  
**Module:** Inventory Adjustments  
**Events:** Check ALL boxes

Click: **Save** → **Test Webhook**

---

#### Webhook #8: Price Lists

**Label:** `TSH Store - Prices`  
**URL:** `https://erp.tsh.sale/api/tds/webhooks/prices`  
**Method:** POST  
**Module:** Price Lists  
**Events:** Check ALL boxes

Click: **Save** → **Test Webhook**

---

### STEP 3: Test It Works (3 minutes)

1. Go to Zoho Books → Products
2. Edit any product (change the description)
3. Save the product
4. Wait 10 seconds
5. Ask me to check if webhook was received

**OR** I can check it for you right now:

```bash
curl http://localhost:8000/api/tds/webhooks/health
```

---

## 🎉 After Setup is Complete

### What You Get:

✅ **Automatic Real-Time Sync**
- Any change in Zoho Books → Appears in TSH ERP within 10 seconds
- No more manual sync scripts
- Always up-to-date data

✅ **What Syncs Automatically:**
- Product updates (name, price, description, stock)
- Customer updates (contact info, addresses)
- New invoices and orders
- Stock adjustments
- Price changes
- Purchase bills
- Credit notes

✅ **All Mobile Apps Updated:**
- TSH Consumer App
- TSH Retailer Shop App
- Partner Salesman App
- All other apps see changes immediately

---

## 📋 Quick Copy-Paste URLs

Just copy these URLs when creating webhooks:

```
Products:     https://erp.tsh.sale/api/tds/webhooks/products
Customers:    https://erp.tsh.sale/api/tds/webhooks/customers
Invoices:     https://erp.tsh.sale/api/tds/webhooks/invoices
Orders:       https://erp.tsh.sale/api/tds/webhooks/orders
Bills:        https://erp.tsh.sale/api/tds/webhooks/bills
Credit Notes: https://erp.tsh.sale/api/tds/webhooks/credit-notes
Stock:        https://erp.tsh.sale/api/tds/webhooks/stock
Prices:       https://erp.tsh.sale/api/tds/webhooks/prices
```

---

## ❓ Need Help?

If you get stuck:
1. Take a screenshot of the Zoho webhook page
2. Share it with me
3. I'll guide you through it

---

**Ready?** Start with Step 1 above! 🚀

