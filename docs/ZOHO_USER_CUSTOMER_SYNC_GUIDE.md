# Zoho User and Customer-Salesperson Sync Guide

**Date:** November 16, 2025
**Version:** 1.0.0
**Status:** Production Ready

---

## Overview

This document describes the implementation of user syncing from Zoho Books and customer-salesperson relationship mapping in the TSH ERP system.

### What This Feature Does

1. **Syncs users from Zoho Books** to TSH ERP with proper role mapping
2. **Maps Zoho contact owners** (owner_id) to TSH ERP salespersons (salesperson_id)
3. **Maintains bidirectional relationship** between Zoho users and TSH ERP users
4. **Automatically assigns customers** to their designated salespersons

---

## Architecture

### Database Changes

#### Users Table (New Fields)

```sql
-- Added to users table
zoho_user_id VARCHAR(100) UNIQUE  -- Zoho Books/Inventory user ID
zoho_last_sync TIMESTAMP          -- Last sync timestamp with Zoho
```

#### Customers Table (New Fields)

```sql
-- Added to customers table
zoho_contact_id VARCHAR(100) UNIQUE    -- Zoho Books contact ID
zoho_owner_id VARCHAR(100)             -- Zoho user ID (owner/salesperson)
zoho_last_sync TIMESTAMP               -- Last sync timestamp
```

### Data Flow

```
Zoho Books API
    ↓
1. Fetch Users → Transform → Upsert to TSH ERP users table
    ↓
2. Fetch Customers (with owner_id) → Transform → Map owner_id to salesperson_id
    ↓
3. Update customers.salesperson_id based on mapping
```

---

## Implementation Files

### Core Components

1. **Models** (`app/models/`)
   - `user.py` - Added zoho_user_id and zoho_last_sync fields
   - `customer.py` - Added zoho_contact_id, zoho_owner_id, zoho_last_sync fields

2. **Processors** (`app/tds/integrations/zoho/processors/`)
   - `users.py` - Transform and validate Zoho user data
   - `customers.py` - Enhanced to extract owner_id from Zoho

3. **Sync Service** (`app/tds/integrations/zoho/`)
   - `user_customer_sync.py` - Core sync logic for users and customer assignments

4. **API Endpoints** (`app/tds/api/`)
   - `user_sync.py` - REST API endpoints for triggering sync operations

5. **Database Migration** (`database/alembic/versions/`)
   - `add_zoho_sync_fields_users_customers.py` - Schema migration for new fields

---

## API Endpoints

### 1. Sync Users from Zoho

```http
POST /api/tds/sync/users
Content-Type: application/json
Authorization: Bearer <admin_or_manager_token>

{
  "full_sync": false  // Optional: true for full sync, false for incremental
}
```

**Response:**
```json
{
  "success": true,
  "message": "User sync completed",
  "result": {
    "total_fetched": 25,
    "created": 5,
    "updated": 18,
    "skipped": 2,
    "errors": [],
    "started_at": "2025-11-16T10:00:00Z",
    "completed_at": "2025-11-16T10:02:15Z"
  },
  "triggered_by": "admin@tsh.sale"
}
```

### 2. Update Customer Salesperson Assignments

```http
POST /api/tds/sync/customer-assignments
Content-Type: application/json
Authorization: Bearer <admin_or_manager_token>

{
  "resync_all": false  // Optional: true to update all, false for only unassigned
}
```

**Response:**
```json
{
  "success": true,
  "message": "Customer salesperson assignments updated",
  "result": {
    "total_checked": 500,
    "updated": 450,
    "skipped": 50,
    "errors": []
  },
  "triggered_by": "manager@tsh.sale"
}
```

### 3. Full Sync Pipeline (Admin Only)

```http
POST /api/tds/sync/full-pipeline
Authorization: Bearer <admin_token>
```

**Response:**
```json
{
  "success": true,
  "message": "Full sync pipeline completed",
  "result": {
    "user_sync": { ... },
    "customer_assignment_update": { ... },
    "started_at": "2025-11-16T10:00:00Z",
    "completed_at": "2025-11-16T10:05:30Z"
  },
  "triggered_by": "admin@tsh.sale"
}
```

### 4. Get User Mapping

```http
GET /api/tds/sync/user-mapping
Authorization: Bearer <admin_or_manager_token>
```

**Response:**
```json
{
  "success": true,
  "mapping": {
    "748369814000000001": 1,  // Zoho user ID → TSH ERP user ID
    "748369814000000002": 5,
    "748369814000000003": 12
  },
  "total_mapped_users": 3
}
```

---

## Usage Instructions

### Initial Setup (First Time)

1. **Run Database Migration**

```bash
# Apply the schema changes
cd database
alembic upgrade head
```

2. **Sync Users from Zoho**

```bash
curl -X POST https://erp.tsh.sale/api/tds/sync/users \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"full_sync": true}'
```

3. **Update Customer Assignments**

```bash
curl -X POST https://erp.tsh.sale/api/tds/sync/customer-assignments \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"resync_all": true}'
```

### Scheduled/Automated Sync

For ongoing operations, you can set up a cron job or scheduled task:

```bash
# Add to TDS Core cron jobs
# Sync users daily at 2 AM
0 2 * * * curl -X POST http://localhost:8000/api/tds/sync/users -H "Authorization: Bearer INTERNAL_TOKEN"

# Update customer assignments daily at 3 AM
0 3 * * * curl -X POST http://localhost:8000/api/tds/sync/customer-assignments -H "Authorization: Bearer INTERNAL_TOKEN"
```

---

## Technical Details

### User Sync Logic

1. **Fetch** all users from Zoho Books API (`/users` endpoint)
2. **Validate** each user has required fields (user_id, name, email)
3. **Transform** Zoho user data to TSH ERP format
4. **Upsert** users:
   - **Match by**: `zoho_user_id` OR `email`
   - **Create new** if no match found (with default password `ChangeMe123!`)
   - **Update existing** if match found
5. **Map roles**: Zoho role → TSH ERP role
   - `admin` → `admin`
   - `manager` → `manager`
   - `salesperson` → `salesperson`
   - `accountant` → `accountant`
   - Default → `employee`

### Customer Assignment Logic

1. **Query** customers with `zoho_owner_id` set
2. **Map** `zoho_owner_id` to local `salesperson_id` using `users.zoho_user_id`
3. **Update** `customers.salesperson_id` with mapped value
4. **Skip** customers where owner_id cannot be mapped (log warning)

---

## Error Handling

### Common Issues

#### Issue: "No TSH ERP user found for Zoho owner_id"

**Cause:** Customer has a Zoho owner assigned, but that Zoho user hasn't been synced to TSH ERP yet.

**Solution:**
```bash
# Run user sync first
curl -X POST /api/tds/sync/users -H "Authorization: Bearer TOKEN" -d '{"full_sync": true}'

# Then run customer assignment update
curl -X POST /api/tds/sync/customer-assignments -H "Authorization: Bearer TOKEN" -d '{"resync_all": true}'
```

#### Issue: "Invalid user data: missing required field"

**Cause:** Zoho user data is incomplete or malformed.

**Solution:** Check Zoho Books for users with missing email or name. Fix in Zoho, then resync.

#### Issue: "Role not found for mapped role name"

**Cause:** The role doesn't exist in TSH ERP.

**Solution:**
```sql
-- Ensure all required roles exist
INSERT INTO roles (name, description) VALUES
  ('admin', 'Administrator'),
  ('manager', 'Manager'),
  ('salesperson', 'Salesperson'),
  ('employee', 'Employee'),
  ('accountant', 'Accountant')
ON CONFLICT (name) DO NOTHING;
```

---

## Monitoring and Logging

### Log Locations

- **Backend logs**: `/var/www/tsh-erp/logs/backend.log`
- **TDS Core logs**: `/var/www/tds-core/logs/tds_core.log`

### Key Log Messages

```
INFO: Starting user sync from Zoho Books
INFO: Fetched 25 users from Zoho Books
INFO: Created new user: sales@tsh.sale
INFO: Updated user: manager@tsh.sale
WARNING: No TSH ERP user found for Zoho owner_id: 748369814000000099
INFO: User sync completed: {"created": 5, "updated": 18}
```

---

## Testing

### Manual Testing

1. **Test User Sync**

```bash
# Trigger sync
curl -X POST http://localhost:8000/api/tds/sync/users \
  -H "Authorization: Bearer TOKEN"

# Verify in database
psql -d tsh_erp_production -c "SELECT id, name, email, zoho_user_id FROM users WHERE zoho_user_id IS NOT NULL;"
```

2. **Test Customer Assignment**

```bash
# Trigger assignment update
curl -X POST http://localhost:8000/api/tds/sync/customer-assignments \
  -H "Authorization: Bearer TOKEN"

# Verify in database
psql -d tsh_erp_production -c "SELECT id, name, salesperson_id, zoho_owner_id FROM customers WHERE zoho_owner_id IS NOT NULL LIMIT 10;"
```

3. **Verify Mapping**

```bash
curl -X GET http://localhost:8000/api/tds/sync/user-mapping \
  -H "Authorization: Bearer TOKEN"
```

---

## Security Considerations

### Authentication Requirements

- **User Sync**: Admin or Manager role required
- **Customer Assignment Update**: Admin or Manager role required
- **Full Pipeline**: Admin role only
- **User Mapping**: Admin or Manager role required

### Data Privacy

- User passwords are NOT synced from Zoho
- New users get default password `ChangeMe123!` (must be changed on first login)
- User email addresses are treated as sensitive data
- All sync operations are logged with user audit trail

---

## Performance Considerations

### Sync Batch Sizes

- **Users**: Process all at once (typically < 100 users)
- **Customers**: Process in batches of 100
- **API Rate Limits**: Zoho Books allows 100 requests/minute

### Optimization Tips

1. Run full sync during off-peak hours (2-4 AM)
2. Use incremental sync for daily updates
3. Monitor sync duration and adjust batch sizes if needed

---

## Rollback Procedure

If issues occur after deployment:

1. **Rollback Database Migration**

```bash
cd database
alembic downgrade -1
```

2. **Revert Code Changes**

```bash
git checkout HEAD~1 -- app/models/user.py
git checkout HEAD~1 -- app/models/customer.py
git checkout HEAD~1 -- app/tds/integrations/zoho/processors/customers.py
```

3. **Restart Services**

```bash
systemctl restart tsh-erp
systemctl restart tds-core
```

---

## Future Enhancements

- [ ] Webhook support for real-time user updates
- [ ] Bulk user import from CSV
- [ ] User deactivation sync (when user is deactivated in Zoho)
- [ ] Conflict resolution UI for duplicate mappings
- [ ] TDS Dashboard integration for sync monitoring

---

## Support

For issues or questions:
- **Technical Lead**: Khaleel Al-Mulla
- **Documentation**: `/docs/ZOHO_USER_CUSTOMER_SYNC_GUIDE.md`
- **Logs**: Check `/var/www/tsh-erp/logs/` and `/var/www/tds-core/logs/`

---

**END OF GUIDE**
