# Webhook URL Comparison - Quick Reference

## THE PROBLEM

Your screenshot shows Zoho is sending webhooks to the **WRONG** URLs:

```
❌ WRONG: https://erp.tsh.sale/api/tds/webhooks/products
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
          This path no longer exists!
```

Result: **"Bad Gateway" (502 error)**

---

## THE FIX

Change all webhook URLs in Zoho Books from `/api/tds/` to `/api/zoho/`:

```
✅ CORRECT: https://erp.tsh.sale/api/zoho/webhooks/products
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
            This is the active endpoint!
```

Result: **202 Accepted - Webhook processed successfully**

---

## ALL 7 URLS TO UPDATE

Copy and paste these into Zoho Books webhook settings:

### 1. Products Webhook
```
https://erp.tsh.sale/api/zoho/webhooks/products
```

### 2. Customers Webhook
```
https://erp.tsh.sale/api/zoho/webhooks/customers
```

### 3. Invoices Webhook
```
https://erp.tsh.sale/api/zoho/webhooks/invoices
```

### 4. Bills Webhook
```
https://erp.tsh.sale/api/zoho/webhooks/bills
```

### 5. Credit Notes Webhook
```
https://erp.tsh.sale/api/zoho/webhooks/credit-notes
```

### 6. Stock Webhook
```
https://erp.tsh.sale/api/zoho/webhooks/stock
```

### 7. Prices Webhook
```
https://erp.tsh.sale/api/zoho/webhooks/prices
```

---

## WHERE TO UPDATE

1. Go to **Zoho Books** → **Settings** → **Automation** → **Webhooks**
2. Click each webhook name to edit
3. Find the **URL** field
4. Replace `/api/tds/webhooks/` with `/api/zoho/webhooks/`
5. Click **Save**

---

## BEFORE vs AFTER

| Webhook | Old URL (BROKEN) | New URL (WORKING) |
|---------|-----------------|-------------------|
| Products | `https://erp.tsh.sale/api/tds/webhooks/products` | `https://erp.tsh.sale/api/zoho/webhooks/products` |
| Customers | `https://erp.tsh.sale/api/tds/webhooks/customers` | `https://erp.tsh.sale/api/zoho/webhooks/customers` |
| Invoices | `https://erp.tsh.sale/api/tds/webhooks/invoices` | `https://erp.tsh.sale/api/zoho/webhooks/invoices` |
| Bills | `https://erp.tsh.sale/api/tds/webhooks/bills` | `https://erp.tsh.sale/api/zoho/webhooks/bills` |
| Credit Notes | `https://erp.tsh.sale/api/tds/webhooks/credit-notes` | `https://erp.tsh.sale/api/zoho/webhooks/credit-notes` |
| Stock | `https://erp.tsh.sale/api/tds/webhooks/stock` | `https://erp.tsh.sale/api/zoho/webhooks/stock` |
| Prices | `https://erp.tsh.sale/api/tds/webhooks/prices` | `https://erp.tsh.sale/api/zoho/webhooks/prices` |

**Simple rule:** Change `tds` to `zoho` in all webhook URLs!

---

## WHY DID THIS HAPPEN?

During the **Monolithic Unification** (deployed today), we merged TDS Core into the main ERP system:

- **Old architecture:** TDS Core had separate endpoints at `/api/tds/webhooks/`
- **New architecture:** Unified system uses `/api/zoho/webhooks/`

The code changed, but Zoho Books still had the old URLs configured.

---

## WHAT HAPPENS AFTER THE FIX?

**Within 1 minute:**
- ✅ Webhooks start working (no more "Bad Gateway")
- ✅ Zoho can send data to TSH ERP again

**Within 5 minutes:**
- ✅ New changes in Zoho appear in TSH ERP
- ✅ Queue starts processing backlog
- ✅ Sync delay drops from 3+ days to < 5 minutes

**Within 1 hour:**
- ✅ All recent Zoho data synced to TSH ERP
- ✅ System fully caught up
- ✅ Normal operation restored

---

**Time to fix:** 10 minutes
**Difficulty:** Easy
**Risk:** None (just URL change)

**Do this now!** Then tell me when done so I can verify it's working.
