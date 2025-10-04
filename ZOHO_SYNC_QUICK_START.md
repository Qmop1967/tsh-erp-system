# Zoho Sync System - Quick Start Guide

## 🚀 Getting Started in 5 Minutes

This guide will help you set up and start using the Zoho Synchronization System immediately.

---

## Step 1: Configure Zoho Credentials (2 minutes)

The credentials are already configured in your system:

```json
{
  "organization_id": "748369814",
  "client_id": "1000.SLY5X93N58VN46HXQIIZSOQKG8J3ZJ",
  "client_secret": "a8b7e31f0e5dde07ea5c3baeb8bff14bcb04c57d78",
  "refresh_token": "1000.afc90b60e7e1f02e2ffed9f71cfb1cc2.d93b0e2c9d1bca3abe7df14d5ce38f3c"
}
```

✅ **Already Done!** Your Zoho integration is configured and ready.

---

## Step 2: Access the Sync Mappings Page (30 seconds)

1. Start your frontend application:
```bash
cd frontend
npm run dev
```

2. Navigate to: **Settings → Integrations → Zoho Integration**

3. Click on **"Sync Mappings"** tab

---

## Step 3: Enable Sync for Items (1 minute)

### Option A: Via UI (Recommended)
1. Go to the **Items** tab
2. Click **"Enable"** button
3. Click **"Analyze"** to check Zoho data
4. Click **"Sync Now"** to start synchronization

### Option B: Via API
```bash
curl -X POST http://localhost:8000/api/settings/integrations/zoho/sync/item/toggle \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}'
```

---

## Step 4: Test the Sync (1 minute)

### Analyze Data First
```bash
curl -X POST http://localhost:8000/api/settings/integrations/zoho/sync/item/analyze
```

**Expected Response:**
```json
{
  "status": "success",
  "analysis": {
    "entity_type": "item",
    "total_records": 500,
    "new_records": 50,
    "updated_records": 25,
    "matched_records": 425
  }
}
```

### Execute Sync
```bash
curl -X POST http://localhost:8000/api/settings/integrations/zoho/sync/item/execute
```

**Expected Response:**
```json
{
  "status": "success",
  "sync_id": "sync_item_20251004_143022",
  "message": "Sync initiated for item"
}
```

---

## Step 5: Monitor Sync Status (30 seconds)

### Check Sync Status
```bash
curl http://localhost:8000/api/settings/integrations/zoho/sync/item/status
```

### View Sync Logs
```bash
curl http://localhost:8000/api/settings/integrations/zoho/sync/logs?entity_type=item&limit=10
```

### Get Statistics
```bash
curl http://localhost:8000/api/settings/integrations/zoho/sync/statistics
```

---

## 📊 What Gets Synced?

### Items (Products)
- ✅ Product name, SKU, description
- ✅ Prices (unit price, cost price)
- ✅ Stock levels (quantity on hand)
- ✅ Categories, brands, manufacturers
- ✅ Product images (auto-downloaded)
- ✅ Tax information
- ✅ Units of measure

### Customers (Ready to Enable)
- ✅ Customer name, company name
- ✅ Contact information (email, phone, mobile)
- ✅ Billing address details
- ✅ Credit limits and payment terms
- ✅ Tax ID
- ✅ Currency and language preferences

### Vendors (Ready to Enable)
- ✅ Vendor name, company name
- ✅ Contact information
- ✅ Billing address details
- ✅ Payment terms
- ✅ Tax information
- ✅ Currency preferences

---

## 🎯 Common Tasks

### Enable Sync for All Entities
```bash
# Enable Items
curl -X POST http://localhost:8000/api/settings/integrations/zoho/sync/item/toggle \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}'

# Enable Customers
curl -X POST http://localhost:8000/api/settings/integrations/zoho/sync/customer/toggle \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}'

# Enable Vendors
curl -X POST http://localhost:8000/api/settings/integrations/zoho/sync/vendor/toggle \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}'
```

### View All Sync Mappings
```bash
curl http://localhost:8000/api/settings/integrations/zoho/sync/mappings
```

### Reset Mapping to Default
```bash
curl -X POST http://localhost:8000/api/settings/integrations/zoho/sync/mappings/item/reset
```

### Clear Sync Logs
```bash
curl -X DELETE http://localhost:8000/api/settings/integrations/zoho/sync/logs
```

---

## ⚙️ Configure Sync Control

### Update Sync Control Settings
```bash
curl -X POST http://localhost:8000/api/settings/integrations/zoho/sync/control \
  -H "Content-Type: application/json" \
  -d '{
    "webhook_enabled": true,
    "batch_size": 100,
    "retry_attempts": 3,
    "retry_delay": 60,
    "error_threshold": 10,
    "validate_data": true,
    "backup_before_sync": true
  }'
```

---

## 🔍 Monitoring and Troubleshooting

### Check Overall Statistics
```bash
curl http://localhost:8000/api/settings/integrations/zoho/sync/statistics
```

**Expected Response:**
```json
{
  "status": "success",
  "statistics": {
    "total_entities": 3,
    "enabled_entities": 1,
    "total_synced": 500,
    "total_errors": 5,
    "entities": {
      "item": {
        "enabled": true,
        "total_synced": 500,
        "total_errors": 5,
        "success_rate": 99.0
      }
    }
  }
}
```

### Filter Logs by Status
```bash
# Only errors
curl "http://localhost:8000/api/settings/integrations/zoho/sync/logs?status=error"

# Only successful syncs
curl "http://localhost:8000/api/settings/integrations/zoho/sync/logs?status=success"
```

---

## 📁 File Locations

All sync configurations are stored in:

```
app/data/settings/
├── zoho_config.json              # Main credentials
├── zoho_sync_mappings.json       # Field mappings
├── zoho_sync_control.json        # Sync control settings
└── zoho_sync_logs.json           # Sync operation logs
```

---

## 🎨 UI Access

### Main Settings Page
```
http://localhost:3000/settings
```

### Zoho Integration Page
```
http://localhost:3000/settings/integrations/zoho
```

### Sync Mappings Page
```
http://localhost:3000/settings/integrations/zoho/sync-mappings
```

---

## 🚨 Troubleshooting

### Problem: Sync Not Working

**Solution 1:** Check Zoho connection
```bash
curl -X POST http://localhost:8000/api/settings/integrations/zoho/test
```

**Solution 2:** Check if sync is enabled
```bash
curl http://localhost:8000/api/settings/integrations/zoho/sync/item/status
```

**Solution 3:** Review error logs
```bash
curl "http://localhost:8000/api/settings/integrations/zoho/sync/logs?status=error&limit=20"
```

### Problem: Data Not Appearing in TSH ERP

**Check:**
1. Verify sync was successful in logs
2. Check database directly:
```bash
psql -d erp_db -c "SELECT COUNT(*) FROM items WHERE zoho_item_id IS NOT NULL;"
```
3. Review field mappings to ensure correct field names

### Problem: Images Not Downloading

**Check:**
1. Verify `sync_images` is enabled in mapping
2. Check image URLs in Zoho
3. Verify write permissions on image storage directory
4. Review logs for image download errors

---

## 📈 Performance Tips

### For Large Datasets (1000+ records)

1. **Increase batch size:**
```json
{
  "batch_size": 200
}
```

2. **Use scheduled sync instead of real-time:**
```json
{
  "sync_mode": "scheduled",
  "sync_frequency": 30
}
```

3. **Disable image sync initially:**
```json
{
  "sync_images": false
}
```

4. **Sync images in separate batch later**

---

## 🔐 Security Best Practices

### 1. Rotate Credentials Regularly
Update your Zoho credentials every 90 days.

### 2. Enable Webhook Secret
```json
{
  "webhook_enabled": true,
  "webhook_secret": "generate-strong-random-secret"
}
```

### 3. Enable Data Validation
```json
{
  "validate_data": true
}
```

### 4. Enable Backup Before Sync
```json
{
  "backup_before_sync": true
}
```

---

## 📞 Support

For issues or questions:
- **Documentation:** `/ZOHO_SYNC_SYSTEM_DOCUMENTATION.md`
- **API Reference:** `http://localhost:8000/docs`
- **Logs Location:** `app/data/settings/zoho_sync_logs.json`

---

## ✅ Success Checklist

- [ ] Zoho credentials configured
- [ ] Backend server running (port 8000)
- [ ] Frontend server running (port 3000)
- [ ] Items sync enabled
- [ ] Data analyzed successfully
- [ ] First sync executed
- [ ] Sync logs visible
- [ ] Statistics showing correct counts

---

## 🎯 Next Steps

1. **Enable Customer Sync**
   - Navigate to Customers tab
   - Click Analyze → Enable → Sync Now

2. **Enable Vendor Sync**
   - Navigate to Vendors tab
   - Click Analyze → Enable → Sync Now

3. **Configure Webhooks**
   - Set up webhook URL in Zoho
   - Configure webhook secret
   - Test webhook delivery

4. **Monitor Performance**
   - Review sync statistics daily
   - Check error logs weekly
   - Optimize field mappings as needed

---

**Congratulations! 🎉 Your Zoho Sync System is now operational!**

For detailed configuration and advanced features, see: `/ZOHO_SYNC_SYSTEM_DOCUMENTATION.md`
