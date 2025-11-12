# ✅ Phase 3 Testing Plan – TDS Enhancements

**Date:** January 2025  
**Status:** Ready for Execution  
**Scope:** Order Sync, Inventory Sync, Image Sync, Scripts Migration

---

## 🎯 Objectives

1. Verify that all newly integrated TDS functionality works as expected
2. Ensure there are no regressions in order creation and inventory management flows
3. Validate that image download and stock sync scripts run end-to-end via TDS
4. Confirm monitoring/event tracking captures key lifecycle events
5. Ensure deprecated scripts are no longer invoked in production jobs

---

## 🧪 Test Matrix Overview

| Area | Component | Test Type | Status |
|------|-----------|-----------|--------|
| Order Sync | `consumer_api.py` `/orders` endpoint | Manual / Integration | ☐ Pending |
| Inventory Sync | `consumer_api.py` `/sync/inventory` endpoint | Manual / Integration | ☐ Pending |
| Image Sync | `scripts/download_zoho_images_tds.py` | Manual / CLI | ☐ Pending |
| Stock Sync | `scripts/unified_stock_sync.py` | Manual / CLI | ☐ Pending |
| Event Tracking | TDS event bus | Observation / Logs | ☐ Pending |
| Cron Jobs | Production task scheduling | Configuration | ☐ Pending |
| Deprecated Scripts | Guardrails/Archival | Verification | ☐ Pending |
| Security | Secrets usage & cleanup | Review | ☐ Pending |

---

## 1. Order Creation Tests

### 1.1 Manual API Test
- Endpoint: `POST /api/consumer/orders`
- Payload sample:
```json
{
  "customer_name": "Test User",
  "customer_email": "test.user@example.com",
  "customer_phone": "+964-700-000-0000",
  "line_items": [
    {
      "item_id": "1234560000000000001",
      "product_name": "Sample Product",
      "quantity": 1,
      "rate": 25.0,
      "amount": 25.0
    }
  ],
  "total_amount": 25.0,
  "notes": "Integration test order"
}
```
- Verify:
  - ✅ HTTP 200 response with order_id and salesorder_number
  - ✅ Database inventory decreased via `update_inventory_after_order`
  - ✅ TDS event log entries: `tds.order.create.started/completed`
  - ✅ Zoho Books dashboard shows order

### 1.2 Negative Test
- Missing required fields (e.g., no line_items)
- Expect HTTP 400 with validation error
- Ensure error is logged and no order is created

### 1.3 Monitoring Verification
- Tail API logs: `docker logs -f tsh_erp_app`
- Confirm order sync events present in log output

---

## 2. Inventory Sync Tests

### 2.1 Manual API Test
- Endpoint: `POST /api/consumer/sync/inventory`
- Parameters: none (optional `active_only`, etc.)
- Verify:
  - ✅ Response contains summary from `UnifiedStockSyncService.stats`
  - ✅ Database product counts match Zoho counts (spot check)
  - ✅ Event log entries: `tds.sync.started/completed`

### 2.2 Error Handling
- Temporarily break Zoho credentials (e.g., invalid token) in staging
- Ensure API returns HTTP 500 with descriptive error
- Check event log for `tds.sync.failed`

---

## 3. Image Download Script Tests

### 3.1 Dry Run (Limited)
```bash
python3 scripts/download_zoho_images_tds.py --limit 5 --with-stock
```
- Verify:
  - ✅ Images saved to configured directory
  - ✅ Database `products.image_url` updated for processed items
  - ✅ Summary stats in console output
  - ✅ Event log entries for image sync

### 3.2 Full Run (Staging)
```bash
python3 scripts/download_zoho_images_tds.py --with-stock
```
- Monitor runtime, success/failed counts
- Confirm permissions set correctly on image directory

### 3.3 Error Scenario
- Simulate network failure (disconnect) mid-run
- Ensure script logs and exits gracefully
- Confirm TDS sync run marked as failed

---

## 4. Stock Sync Script Tests

### 4.1 Incremental Sync
```bash
python3 scripts/unified_stock_sync.py --mode incremental --stats
```
- Verify console output includes TDS stats
- Confirm no direct Zoho calls outside TDS services

### 4.2 Full Sync
```bash
python3 scripts/unified_stock_sync.py --mode full --batch-size 200
```
- Validate database stock levels align with Zoho after completion
- Check event logs for TDS sync events

### 4.3 Specific Items Sync
```bash
python3 scripts/unified_stock_sync.py --items ITEM_ID_1,ITEM_ID_2
```
- Ensure only listed items are updated

---

## 5. Event Tracking & Monitoring

### 5.1 Log Inspection
- Tail logs during each operation:
```bash
docker logs -f tsh_erp_app | grep "tds"
```
- Confirm presence of `tds.sync.*` and `tds.order.*` events

### 5.2 Event Store (Optional)
- If event store database enabled, query for latest events
- Validate metadata (sync_run_id, timestamps) stored correctly

### 5.3 Alerting Hooks (Future)
- Placeholder to connect TDS events to alerting pipeline

---

## 6. Cron Job Verification

### 6.1 Update Production Cron to Use TDS Scripts
```bash
# /etc/crontab (example)
0 3 * * * deploy cd /home/deploy/TSH_ERP_Ecosystem && /usr/bin/python3 scripts/download_zoho_images_tds.py --with-stock
0 4 * * * deploy cd /home/deploy/TSH_ERP_Ecosystem && /usr/bin/python3 scripts/unified_stock_sync.py --mode incremental --stats
```

### 6.2 Remove Legacy Cron Entries
- Remove references to deprecated scripts from cron/automation tools
- Document change in operations wiki

---

## 7. Deprecated Scripts Validation

### 7.1 Guardrails
- Confirm deprecated scripts print warnings when invoked accidentally
- Optionally rename scripts with `.deprecated` suffix once migration is stable

### 7.2 Archive Plan
- After testing completes, move deprecated scripts to `scripts/archived/<date>/`
- Update version control with archival commit

---

## 8. Security Review

### 8.1 Secrets Management
- Ensure `.env` contains valid `ZOHO_CLIENT_ID`, `ZOHO_CLIENT_SECRET`, `ZOHO_REFRESH_TOKEN`, `ZOHO_ORGANIZATION_ID`
- Validate no secrets committed to repo

### 8.2 Session Cleanup
- During tests, confirm Zoho sessions are closed (logs show `close_session`)
- Monitor rate limits to ensure proper cleanup

---

## 9. Automated Checks (Optional)

### 9.1 Unit Tests
```bash
pytest tests/tds/test_zoho_bulk_sync_router.py
pytest tests/tds/test_stock_sync.py
```
- Ensure no regressions in existing tests

### 9.2 Linting
```bash
ruff app/ scripts/
```

### 9.3 Dependency Audit (future)
- Evaluate adding integration tests or contract tests for TDS handlers

---

## ✅ Completion Criteria

- [ ] Order creation endpoint passes manual tests
- [ ] Inventory sync endpoint passes manual tests
- [ ] Image download script succeeds in staging
- [ ] Stock sync script succeeds in staging
- [ ] Event logs confirm lifecycle events
- [ ] Cron jobs updated to use new scripts
- [ ] Deprecated scripts no longer run in production
- [ ] Secrets verified and secured

Once all items are checked, mark TODO #11 as **completed** and proceed to Phase 3 cleanup (archiving deprecated scripts).
