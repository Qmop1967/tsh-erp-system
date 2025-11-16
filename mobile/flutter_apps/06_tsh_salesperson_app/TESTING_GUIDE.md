# TSH Salesperson App - Backend API Testing Guide

**Date:** November 15, 2025
**Backend Endpoints:** 33 BFF endpoints ready for testing
**API Base URL:** `https://erp.tsh.sale/api/bff/salesperson`

---

## Table of Contents

1. [Setup](#setup)
2. [Authentication](#authentication)
3. [GPS Tracking Endpoints (8)](#gps-tracking-endpoints)
4. [Money Transfer Endpoints (12)](#money-transfer-endpoints)
5. [Commission Endpoints (13)](#commission-endpoints)
6. [Integration Testing](#integration-testing)
7. [Troubleshooting](#troubleshooting)

---

## Setup

### Prerequisites

1. **Backend Running:** Ensure TSH ERP backend is running
2. **Database Migrated:** Run migrations to create new tables
3. **User Account:** Have a salesperson user account
4. **JWT Token:** Obtain authentication token

### Environment Variables

```bash
export API_BASE_URL="https://erp.tsh.sale/api/bff/salesperson"
export AUTH_TOKEN="your_jwt_token_here"
export SALESPERSON_ID=5  # Your salesperson user ID
```

### Quick Health Check

```bash
# Check if endpoints are registered
curl -X GET "https://erp.tsh.sale/api/bff/salesperson/gps/health"
curl -X GET "https://erp.tsh.sale/api/bff/salesperson/transfers/health"
curl -X GET "https://erp.tsh.sale/api/bff/salesperson/commissions/health"
```

Expected response:
```json
{
  "status": "healthy",
  "service": "gps-tracking-bff",
  "version": "1.0.0"
}
```

---

## Authentication

### Get JWT Token

```bash
# Login to get token
curl -X POST "https://erp.tsh.sale/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "salesperson@tsh.sale",
    "password": "your_password"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 5,
    "name": "Ahmed Ali",
    "email": "salesperson@tsh.sale",
    "role": "salesperson"
  }
}
```

### Set Token for All Requests

```bash
export AUTH_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

## GPS Tracking Endpoints (8)

### 1. Track Single Location

**Endpoint:** `POST /api/bff/salesperson/gps/track`

```bash
curl -X POST "$API_BASE_URL/gps/track" \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 33.3152,
    "longitude": 44.3661,
    "timestamp": "2025-11-15T10:30:00Z",
    "accuracy": 5.0,
    "altitude": 34.0,
    "speed": 15.5,
    "heading": 180,
    "activity_type": "driving",
    "battery_level": 75,
    "is_charging": false,
    "device_id": "iPhone-12345"
  }'
```

Expected response:
```json
{
  "success": true,
  "location_id": 123,
  "message": "Location tracked successfully"
}
```

### 2. Batch Upload Locations (Offline Sync)

**Endpoint:** `POST /api/bff/salesperson/gps/track/batch`

```bash
curl -X POST "$API_BASE_URL/gps/track/batch" \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "locations": [
      {
        "latitude": 33.3152,
        "longitude": 44.3661,
        "timestamp": "2025-11-15T10:00:00Z",
        "accuracy": 5.0
      },
      {
        "latitude": 33.3160,
        "longitude": 44.3670,
        "timestamp": "2025-11-15T10:05:00Z",
        "accuracy": 4.5
      }
    ]
  }'
```

### 3. Get Location History

**Endpoint:** `GET /api/bff/salesperson/gps/history`

```bash
curl -X GET "$API_BASE_URL/gps/history?salesperson_id=$SALESPERSON_ID&start_date=2025-11-15&end_date=2025-11-15&limit=100" \
  -H "Authorization: Bearer $AUTH_TOKEN"
```

### 4. Get Daily Summary

**Endpoint:** `GET /api/bff/salesperson/gps/summary/daily`

```bash
curl -X GET "$API_BASE_URL/gps/summary/daily?salesperson_id=$SALESPERSON_ID&summary_date=2025-11-15" \
  -H "Authorization: Bearer $AUTH_TOKEN"
```

Expected response:
```json
{
  "date": "2025-11-15",
  "total_distance_km": 45.32,
  "total_duration_hours": 6.5,
  "customer_visits": 8,
  "verified_visits": 7,
  "route": [...],
  "start_time": "2025-11-15T08:00:00Z",
  "end_time": "2025-11-15T14:30:00Z"
}
```

### 5. Get Weekly Summary

**Endpoint:** `GET /api/bff/salesperson/gps/summary/weekly`

```bash
curl -X GET "$API_BASE_URL/gps/summary/weekly?salesperson_id=$SALESPERSON_ID&week_start=2025-11-11" \
  -H "Authorization: Bearer $AUTH_TOKEN"
```

### 6. Verify Customer Visit

**Endpoint:** `POST /api/bff/salesperson/gps/verify-visit`

```bash
curl -X POST "$API_BASE_URL/gps/verify-visit" \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 123,
    "latitude": 33.3152,
    "longitude": 44.3661,
    "visit_time": "2025-11-15T10:30:00Z",
    "notes": "Met with store manager"
  }'
```

Expected response:
```json
{
  "verified": true,
  "distance_from_customer": 12.5,
  "within_geofence": true,
  "customer_name": "Baghdad Super Market",
  "customer_address": "Al-Karrada, Baghdad",
  "visit_id": 456
}
```

### 7. Get Sync Status

**Endpoint:** `GET /api/bff/salesperson/gps/sync-status`

```bash
curl -X GET "$API_BASE_URL/gps/sync-status?salesperson_id=$SALESPERSON_ID" \
  -H "Authorization: Bearer $AUTH_TOKEN"
```

### 8. Delete Location

**Endpoint:** `DELETE /api/bff/salesperson/gps/locations/{location_id}`

```bash
curl -X DELETE "$API_BASE_URL/gps/locations/123" \
  -H "Authorization: Bearer $AUTH_TOKEN"
```

---

## Money Transfer Endpoints (12)

### 1. Create Transfer

**Endpoint:** `POST /api/bff/salesperson/transfers`

```bash
curl -X POST "$API_BASE_URL/transfers" \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount_usd": 2500.00,
    "amount_iqd": 3250000,
    "exchange_rate": 1300,
    "gross_sales": 111111.11,
    "claimed_commission": 2500.00,
    "transfer_platform": "ALTaif Bank",
    "platform_reference": "ALT123456789",
    "transfer_fee": 0,
    "gps_latitude": 33.3152,
    "gps_longitude": 44.3661,
    "location_name": "TSH Office Baghdad"
  }'
```

Expected response:
```json
{
  "id": 789,
  "transfer_uuid": "550e8400-e29b-41d4-a716-446655440000",
  "salesperson_id": 5,
  "salesperson_name": "Ahmed Ali",
  "amount_usd": 2500.00,
  "amount_iqd": 3250000,
  "exchange_rate": 1300,
  "gross_sales": 111111.11,
  "commission_rate": 2.25,
  "calculated_commission": 2500.00,
  "claimed_commission": 2500.00,
  "commission_verified": false,
  "transfer_platform": "ALTaif Bank",
  "platform_reference": "ALT123456789",
  "status": "pending",
  "is_suspicious": false,
  "fraud_alert_reason": null,
  "created_at": "2025-11-15T10:30:00Z"
}
```

### 2. Get Transfer List

**Endpoint:** `GET /api/bff/salesperson/transfers`

```bash
# Get all transfers for salesperson
curl -X GET "$API_BASE_URL/transfers?salesperson_id=$SALESPERSON_ID&limit=100" \
  -H "Authorization: Bearer $AUTH_TOKEN"

# Filter by status
curl -X GET "$API_BASE_URL/transfers?salesperson_id=$SALESPERSON_ID&status=pending" \
  -H "Authorization: Bearer $AUTH_TOKEN"

# Filter by date range
curl -X GET "$API_BASE_URL/transfers?salesperson_id=$SALESPERSON_ID&start_date=2025-11-01&end_date=2025-11-15" \
  -H "Authorization: Bearer $AUTH_TOKEN"
```

### 3. Get Transfer Details

**Endpoint:** `GET /api/bff/salesperson/transfers/{transfer_id}`

```bash
curl -X GET "$API_BASE_URL/transfers/789" \
  -H "Authorization: Bearer $AUTH_TOKEN"
```

### 4. Update Transfer

**Endpoint:** `PUT /api/bff/salesperson/transfers/{transfer_id}`

```bash
curl -X PUT "$API_BASE_URL/transfers/789" \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "verified",
    "verification_notes": "Receipt verified"
  }'
```

### 5. Delete Transfer

**Endpoint:** `DELETE /api/bff/salesperson/transfers/{transfer_id}`

```bash
curl -X DELETE "$API_BASE_URL/transfers/789" \
  -H "Authorization: Bearer $AUTH_TOKEN"
```

### 6. Upload Receipt Photo

**Endpoint:** `POST /api/bff/salesperson/transfers/{transfer_id}/receipt`

```bash
curl -X POST "$API_BASE_URL/transfers/789/receipt" \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -F "receipt_photo=@/path/to/receipt.jpg"
```

Expected response:
```json
{
  "success": true,
  "photo_url": "/uploads/transfer_receipts/transfer_789_xxx.jpg",
  "uploaded_at": "2025-11-15T10:35:00Z"
}
```

### 7. Verify Transfer (Manager Only)

**Endpoint:** `POST /api/bff/salesperson/transfers/{transfer_id}/verify`

```bash
curl -X POST "$API_BASE_URL/transfers/789/verify" \
  -H "Authorization: Bearer $MANAGER_TOKEN"
```

### 8. Complete Transfer (Manager Only)

**Endpoint:** `POST /api/bff/salesperson/transfers/{transfer_id}/complete`

```bash
curl -X POST "$API_BASE_URL/transfers/789/complete" \
  -H "Authorization: Bearer $MANAGER_TOKEN"
```

### 9. Batch Sync Transfers

**Endpoint:** `POST /api/bff/salesperson/transfers/batch-sync`

```bash
curl -X POST "$API_BASE_URL/transfers/batch-sync" \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "transfers": [
      {
        "amount_usd": 1000.00,
        "amount_iqd": 1300000,
        "exchange_rate": 1300,
        "gross_sales": 44444.44,
        "claimed_commission": 1000.00,
        "transfer_platform": "ZAIN Cash",
        "gps_latitude": 33.3152,
        "gps_longitude": 44.3661
      }
    ]
  }'
```

### 10. Get Statistics

**Endpoint:** `GET /api/bff/salesperson/transfers/statistics`

```bash
curl -X GET "$API_BASE_URL/transfers/statistics?salesperson_id=$SALESPERSON_ID&period=month" \
  -H "Authorization: Bearer $AUTH_TOKEN"
```

Expected response:
```json
{
  "period": "month",
  "total_transfers": 12,
  "total_amount_usd": 35000.00,
  "total_amount_iqd": 45500000,
  "pending_count": 3,
  "verified_count": 5,
  "received_count": 4,
  "average_amount_usd": 2916.67,
  "platform_breakdown": {
    "ALTaif Bank": {"count": 5, "total_usd": 15000},
    "ZAIN Cash": {"count": 4, "total_usd": 12000},
    "SuperQi": {"count": 3, "total_usd": 8000}
  }
}
```

### 11. Get Cash Box Balance

**Endpoint:** `GET /api/bff/salesperson/transfers/cash-box`

```bash
curl -X GET "$API_BASE_URL/transfers/cash-box?salesperson_id=$SALESPERSON_ID" \
  -H "Authorization: Bearer $AUTH_TOKEN"
```

Expected response:
```json
{
  "cashIQD": 0,
  "cashUSD": 0,
  "altaifIQD": 1500000,
  "zainCashIQD": 800000,
  "superQiIQD": 500000,
  "totalIQD": 2800000,
  "totalUSD": 0
}
```

### 12. Reconcile Transfers (Manager Only)

**Endpoint:** `POST /api/bff/salesperson/transfers/reconcile`

```bash
curl -X POST "$API_BASE_URL/transfers/reconcile?salesperson_id=$SALESPERSON_ID&date=2025-11-15" \
  -H "Authorization: Bearer $MANAGER_TOKEN"
```

---

## Commission Endpoints (13)

### 1. Get Commission Summary

**Endpoint:** `GET /api/bff/salesperson/commissions/summary`

```bash
# Monthly summary
curl -X GET "$API_BASE_URL/commissions/summary?salesperson_id=$SALESPERSON_ID&period=month" \
  -H "Authorization: Bearer $AUTH_TOKEN"

# Weekly summary
curl -X GET "$API_BASE_URL/commissions/summary?salesperson_id=$SALESPERSON_ID&period=week" \
  -H "Authorization: Bearer $AUTH_TOKEN"

# All-time summary
curl -X GET "$API_BASE_URL/commissions/summary?salesperson_id=$SALESPERSON_ID&period=all" \
  -H "Authorization: Bearer $AUTH_TOKEN"
```

Expected response:
```json
{
  "salesperson_id": 5,
  "salesperson_name": "Ahmed Ali",
  "period": "month",
  "period_start": "2025-11-01",
  "period_end": "2025-11-30",
  "total_sales": 150000000,
  "commission_rate": 2.25,
  "total_commission": 3375000,
  "pending_commission": 2000000,
  "paid_commission": 1375000,
  "total_orders": 45,
  "total_customers": 30,
  "avg_order_value": 3333333.33,
  "target_sales": 200000000,
  "target_achievement_percentage": 75.0,
  "rank": 3
}
```

### 2. Get Commission History

**Endpoint:** `GET /api/bff/salesperson/commissions/history`

```bash
curl -X GET "$API_BASE_URL/commissions/history?salesperson_id=$SALESPERSON_ID&limit=100" \
  -H "Authorization: Bearer $AUTH_TOKEN"
```

### 3. Get Commission Details

**Endpoint:** `GET /api/bff/salesperson/commissions/{commission_id}`

```bash
curl -X GET "$API_BASE_URL/commissions/123" \
  -H "Authorization: Bearer $AUTH_TOKEN"
```

### 4. Calculate Commission Preview

**Endpoint:** `POST /api/bff/salesperson/commissions/calculate`

```bash
curl -X POST "$API_BASE_URL/commissions/calculate" \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "sales_amount": 10000000,
    "commission_rate": 2.25
  }'
```

Expected response:
```json
{
  "sales_amount": 10000000,
  "commission_rate": 2.25,
  "commission_amount": 225000,
  "estimated_payout": 225000,
  "tax_amount": null,
  "net_payout": null
}
```

### 5. Get Sales Target

**Endpoint:** `GET /api/bff/salesperson/commissions/targets`

```bash
curl -X GET "$API_BASE_URL/commissions/targets?salesperson_id=$SALESPERSON_ID&period=monthly" \
  -H "Authorization: Bearer $AUTH_TOKEN"
```

### 6. Set Sales Target (Manager Only)

**Endpoint:** `POST /api/bff/salesperson/commissions/targets/set`

```bash
curl -X POST "$API_BASE_URL/commissions/targets/set" \
  -H "Authorization: Bearer $MANAGER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "salesperson_id": 5,
    "period_type": "monthly",
    "period_start": "2025-12-01",
    "period_end": "2025-12-31",
    "target_revenue_iqd": 200000000,
    "target_orders": 50,
    "bonus_enabled": true,
    "bonus_percentage": 1.0,
    "description": "December sales target with 1% bonus"
  }'
```

### 7. Get Leaderboard

**Endpoint:** `GET /api/bff/salesperson/commissions/leaderboard`

```bash
curl -X GET "$API_BASE_URL/commissions/leaderboard?period=month&limit=10" \
  -H "Authorization: Bearer $AUTH_TOKEN"
```

Expected response:
```json
{
  "period": "month",
  "period_start": "2025-11-01",
  "period_end": "2025-11-30",
  "leaderboard": [
    {
      "rank": 1,
      "salesperson_id": 3,
      "salesperson_name": "Mohammed Hassan",
      "total_sales": 250000000,
      "total_commission": 5625000,
      "total_orders": 80,
      "total_customers": 50,
      "target_achievement_percentage": 125.0,
      "badge": "top_performer"
    },
    {
      "rank": 2,
      "salesperson_id": 7,
      "salesperson_name": "Ali Karim",
      "total_sales": 180000000,
      "total_commission": 4050000,
      "total_orders": 60,
      "total_customers": 40,
      "target_achievement_percentage": 90.0,
      "badge": "runner_up"
    }
  ],
  "total_participants": 12,
  "my_rank": 3
}
```

### 8. Get Weekly Earnings

**Endpoint:** `GET /api/bff/salesperson/commissions/weekly-earnings`

```bash
curl -X GET "$API_BASE_URL/commissions/weekly-earnings?salesperson_id=$SALESPERSON_ID&week_start=2025-11-11" \
  -H "Authorization: Bearer $AUTH_TOKEN"
```

### 9. Update Commission Status (Manager Only)

**Endpoint:** `PUT /api/bff/salesperson/commissions/{commission_id}/status`

```bash
curl -X PUT "$API_BASE_URL/commissions/123/status" \
  -H "Authorization: Bearer $MANAGER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "approved",
    "notes": "Commission approved for November"
  }'
```

### 10. Mark Commission Paid (Manager Only)

**Endpoint:** `PUT /api/bff/salesperson/commissions/{commission_id}/mark-paid`

```bash
curl -X PUT "$API_BASE_URL/commissions/123/mark-paid" \
  -H "Authorization: Bearer $MANAGER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "payment_method": "bank_transfer",
    "payment_reference": "TRF20251115001",
    "paid_date": "2025-11-15",
    "notes": "Commission paid for November"
  }'
```

### 11. Get Statistics

**Endpoint:** `GET /api/bff/salesperson/commissions/statistics`

```bash
curl -X GET "$API_BASE_URL/commissions/statistics?salesperson_id=$SALESPERSON_ID" \
  -H "Authorization: Bearer $AUTH_TOKEN"
```

Expected response:
```json
{
  "lifetime_earnings": 35000000,
  "ytd_earnings": 28000000,
  "mtd_earnings": 3375000,
  "avg_monthly_commission": 3500000,
  "highest_monthly_commission": 5000000,
  "total_orders_all_time": 450,
  "avg_commission_per_order": 77777.78,
  "commission_trend": "increasing"
}
```

### 12. Request Payout

**Endpoint:** `POST /api/bff/salesperson/commissions/request-payout`

```bash
curl -X POST "$API_BASE_URL/commissions/request-payout" \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "commission_ids": [123, 124, 125],
    "payment_method": "bank_transfer",
    "notes": "Please pay November commission"
  }'
```

### 13. Get Sync Status

**Endpoint:** `GET /api/bff/salesperson/commissions/sync-status`

```bash
curl -X GET "$API_BASE_URL/commissions/sync-status?salesperson_id=$SALESPERSON_ID" \
  -H "Authorization: Bearer $AUTH_TOKEN"
```

---

## Integration Testing

### Test Workflow: Complete Day in Field

```bash
#!/bin/bash
# Complete salesperson day workflow

# 1. Login
TOKEN=$(curl -X POST "https://erp.tsh.sale/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "salesperson@tsh.sale", "password": "password"}' \
  | jq -r '.access_token')

# 2. Start day - track first location
curl -X POST "$API_BASE_URL/gps/track" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"latitude": 33.3152, "longitude": 44.3661, "timestamp": "2025-11-15T08:00:00Z", "accuracy": 5.0}'

# 3. Visit customer - verify location
curl -X POST "$API_BASE_URL/gps/verify-visit" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"customer_id": 123, "latitude": 33.3152, "longitude": 44.3661, "visit_time": "2025-11-15T10:00:00Z"}'

# 4. Make sale - calculate commission
curl -X POST "$API_BASE_URL/commissions/calculate" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"sales_amount": 10000000, "commission_rate": 2.25}'

# 5. End day - send money transfer
curl -X POST "$API_BASE_URL/transfers" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"amount_usd": 2500, "amount_iqd": 3250000, "exchange_rate": 1300, "gross_sales": 111111.11, "claimed_commission": 2500, "transfer_platform": "ALTaif Bank", "gps_latitude": 33.3152, "gps_longitude": 44.3661}'

# 6. Check daily summary
curl -X GET "$API_BASE_URL/gps/summary/daily?salesperson_id=5&summary_date=2025-11-15" \
  -H "Authorization: Bearer $TOKEN"

# 7. Check commission summary
curl -X GET "$API_BASE_URL/commissions/summary?salesperson_id=5&period=today" \
  -H "Authorization: Bearer $TOKEN"

# 8. View leaderboard
curl -X GET "$API_BASE_URL/commissions/leaderboard?period=month" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Troubleshooting

### Common Issues

#### 1. 401 Unauthorized

```bash
# Issue: Token expired or invalid
# Solution: Login again to get new token
curl -X POST "https://erp.tsh.sale/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "your_email", "password": "your_password"}'
```

#### 2. 403 Forbidden

```bash
# Issue: User doesn't have permission
# Check: Ensure user has is_salesperson=true
# Check: Ensure user is trying to access their own data
```

#### 3. 404 Not Found

```bash
# Issue: Endpoint not registered or resource doesn't exist
# Solution: Check health endpoints first
curl -X GET "$API_BASE_URL/gps/health"
```

#### 4. 422 Validation Error

```bash
# Issue: Invalid request data
# Solution: Check required fields and data types
# Example fix for GPS location:
{
  "latitude": 33.3152,  # Must be -90 to 90
  "longitude": 44.3661,  # Must be -180 to 180
  "timestamp": "2025-11-15T10:30:00Z"  # ISO 8601 format required
}
```

#### 5. 500 Internal Server Error

```bash
# Check backend logs
ssh root@167.71.39.50 "tail -100 /var/www/tsh-erp/logs/backend.log"

# Check database connection
PGPASSWORD='password' psql -h localhost -U tsh_app_user -d tsh_erp_production -c "SELECT 1;"
```

### Debug Mode

```bash
# Add -v flag to curl for verbose output
curl -v -X GET "$API_BASE_URL/gps/health" \
  -H "Authorization: Bearer $AUTH_TOKEN"

# Save response to file for analysis
curl -X GET "$API_BASE_URL/commissions/summary?salesperson_id=5&period=month" \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -o response.json

# Pretty print JSON
curl -X GET "$API_BASE_URL/gps/history?salesperson_id=5" \
  -H "Authorization: Bearer $AUTH_TOKEN" | jq '.'
```

---

## Next Steps

1. **Database Migration**: Run Alembic migration to create new tables
2. **Verify Endpoints**: Run all health checks
3. **Test Authentication**: Ensure JWT tokens work
4. **Test Each Endpoint**: Use curl examples above
5. **Connect Flutter App**: Update API base URL in Flutter app
6. **End-to-End Test**: Complete workflow from mobile app

---

**Questions?** Contact backend team or check documentation at `/docs/BACKEND_INTEGRATION.md`

**Backend Status:** All 33 endpoints implemented and ready for testing!
