# 5. Update .gitignore for ignored patterns
```

#### 3.3 Project Size Targets

**Optimal Sizes:**

| Component | Target Size | Max Size | Action if Exceeded |
|-----------|------------|----------|-------------------|
| Single File | < 300 lines | 500 lines | Split into modules |
| Function | < 50 lines | 100 lines | Extract subfunctions |
| Class | < 300 lines | 500 lines | Split responsibilities |
| Module | < 10 files | 20 files | Create subpackages |
| Dependencies | < 50 packages | 75 packages | Remove unused |

**Monitoring Script:**

```python
# scripts/size_monitor.py
import os
from pathlib import Path

def analyze_file_sizes(root_dir="app/"):
    """Analyze and report file sizes"""
    large_files = []

    for path in Path(root_dir).rglob("*.py"):
        lines = len(path.read_text().splitlines())

        if lines > 500:
            large_files.append((str(path), lines))

    # Sort by size
    large_files.sort(key=lambda x: x[1], reverse=True)

    print("⚠️  Files exceeding 500 lines:")
    for file, lines in large_files:
        print(f"   {file}: {lines} lines")

    return large_files

if __name__ == "__main__":
    analyze_file_sizes()
```

---

### 4. Daily Data Investigation System

**Philosophy**: Trust but verify - daily data consistency checks

#### 4.1 Automated Daily Comparison

**Implementation**: `scripts/daily_data_investigation.py`

```python
#!/usr/bin/env python3
"""
Daily Data Investigation System
================================

Compares data counts between Zoho and TSH ERP
Alerts on discrepancies

Run daily at 3 AM via cron:
0 3 * * * /usr/bin/python3 /path/to/daily_data_investigation.py
"""

import asyncio
import os
from datetime import datetime
from typing import Dict, Any

from app.tds.integrations.zoho import UnifiedZohoClient, ZohoAPI
from app.db.database import get_async_db

class DataInvestigator:
    """Daily data consistency checker"""

    async def investigate(self) -> Dict[str, Any]:
        """Run full investigation"""

        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "healthy",
            "discrepancies": [],
            "entities": {}
        }

        # Check each entity type
        entities_to_check = [
            ("products", "items", "products"),
            ("customers", "contacts", "customers"),
            ("invoices", "invoices", "invoices"),
            ("orders", "salesorders", "sales_orders")
        ]

        for entity_name, zoho_endpoint, db_table in entities_to_check:
            result = await self._compare_entity(
                entity_name, zoho_endpoint, db_table
            )
            report["entities"][entity_name] = result

            if result["discrepancy"]:
                report["discrepancies"].append(result)
                report["status"] = "warning"

        # Save report
        await self._save_report(report)

        # Send alert if discrepancies found
        if report["discrepancies"]:
            await self._send_alert(report)

        return report

    async def _compare_entity(
        self,
        entity_name: str,
        zoho_endpoint: str,
        db_table: str
    ) -> Dict[str, Any]:
        """Compare counts for single entity type"""

        # Get Zoho count
        zoho_count = await self._get_zoho_count(zoho_endpoint)

        # Get database count
        db_count = await self._get_db_count(db_table)

        # Calculate discrepancy
        difference = abs(zoho_count - db_count)
        percentage = (difference / zoho_count * 100) if zoho_count > 0 else 0

        result = {
            "entity": entity_name,
            "zoho_count": zoho_count,
            "db_count": db_count,
            "difference": difference,
            "discrepancy_percentage": round(percentage, 2),
            "discrepancy": percentage > 1.0,  # Alert if > 1% difference
            "timestamp": datetime.utcnow().isoformat()
        }

        return result

    async def _get_zoho_count(self, endpoint: str) -> int:
        """Get entity count from Zoho"""
        # Initialize Zoho client
        zoho_client = await self._get_zoho_client()

        response = await zoho_client.get(
            api_type=ZohoAPI.BOOKS,
            endpoint=endpoint,
            params={"per_page": 1, "page": 1}
        )

        page_context = response.get('page_context', {})
        return page_context.get('total', 0)

    async def _get_db_count(self, table: str) -> int:
        """Get entity count from database"""
        from sqlalchemy import text

        async for db in get_async_db():
            try:
                query = text(f"SELECT COUNT(*) FROM {table}")
                result = await db.execute(query)
                count = result.scalar()
                return count
            finally:
                break

        return 0

    async def _save_report(self, report: Dict[str, Any]):
        """Save investigation report to database"""
        from sqlalchemy import text

        async for db in get_async_db():
            try:
                query = text("""
                    INSERT INTO data_investigation_reports
                    (report_date, status, report_data, created_at)
                    VALUES (CURRENT_DATE, :status, :report_data, NOW())
                """)

                await db.execute(query, {
                    "status": report["status"],
                    "report_data": json.dumps(report)
                })

                await db.commit()
            finally:
                break

    async def _send_alert(self, report: Dict[str, Any]):
        """Send alert if discrepancies found"""
        # Email alert
        subject = f"⚠️ TSH ERP Data Discrepancy Alert - {datetime.utcnow().date()}"

        body = f"""
        Data Investigation Report
        =========================

        Status: {report['status']}
        Timestamp: {report['timestamp']}

        Discrepancies Found:
        """

        for disc in report['discrepancies']:
            body += f"""

            Entity: {disc['entity']}
            - Zoho Count: {disc['zoho_count']}
            - Database Count: {disc['db_count']}
            - Difference: {disc['difference']} ({disc['discrepancy_percentage']}%)
            """

        # Send email (implement email sending logic)
        # await send_email(subject, body)

        # Log alert
        print(f"🚨 ALERT: {subject}")
        print(body)

# Run investigation
async def main():
    investigator = DataInvestigator()
    report = await investigator.investigate()

    print("=" * 70)
    print("📊 Daily Data Investigation Report")
    print("=" * 70)
    print(json.dumps(report, indent=2))
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
```

**Database Schema for Reports:**

```sql
-- Create investigation reports table
CREATE TABLE IF NOT EXISTS data_investigation_reports (
    id SERIAL PRIMARY KEY,
    report_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL, -- 'healthy', 'warning', 'critical'
    report_data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Index for date queries
CREATE INDEX idx_investigation_date ON data_investigation_reports(report_date DESC);

-- View recent investigations
CREATE VIEW recent_investigations AS
SELECT
    report_date,
    status,
    (report_data->>'timestamp')::TIMESTAMP as investigated_at,
    jsonb_array_length(report_data->'discrepancies') as discrepancy_count
FROM data_investigation_reports
ORDER BY report_date DESC
LIMIT 30;
```

#### 4.2 Cron Job Setup

```bash
# Add to VPS crontab
ssh root@167.71.39.50

# Edit crontab
crontab -e

# Add daily investigation at 3 AM
0 3 * * * cd /home/deploy/TSH_ERP_Ecosystem && /usr/bin/python3 scripts/daily_data_investigation.py >> /var/log/tsh_data_investigation.log 2>&1
```

#### 4.3 Investigation Dashboard

**Endpoint**: `GET /api/admin/data-investigation`

```python
@router.get("/data-investigation")
async def get_investigation_dashboard(
    days: int = 7,
    db: Session = Depends(get_db)
):
    """Get recent investigation reports"""

    from sqlalchemy import text

    query = text("""
        SELECT
            report_date,
            status,
            report_data
        FROM data_investigation_reports
        WHERE report_date >= CURRENT_DATE - :days
        ORDER BY report_date DESC
    """)

    result = db.execute(query, {"days": days})
    reports = result.fetchall()

    return {
        "total_reports": len(reports),
        "healthy_count": sum(1 for r in reports if r[1] == 'healthy'),
        "warning_count": sum(1 for r in reports if r[1] == 'warning'),
        "reports": [
            {
                "date": str(r[0]),
                "status": r[1],
                "data": r[2]
            }
            for r in reports
        ]
    }
```

---

### 5. Consumer App Product Filtering

**Philosophy**: Only show products with available stock

#### 5.1 API Filtering Rules

**Already Implemented**: `app/routers/consumer_api.py:119`

```python
# WHERE clause filters for products with stock
where_conditions = [
    "p.is_active = true",           # Only active products
    "p.actual_available_stock > 0"  # Only products with stock
]
```

**Additional Filters (Optional):**

```python
# Add to where_conditions based on requirements
where_conditions.extend([
    "p.price > 0",                  # Only products with price
    "p.image_url IS NOT NULL",      # Only products with images (optional)
    "p.category IS NOT NULL"        # Only categorized products (optional)
])
```

#### 5.2 Stock Threshold Configuration

**Environment Variable**: `.env`
```bash
# Minimum stock to display
CONSUMER_MIN_STOCK=1

# Low stock warning threshold
CONSUMER_LOW_STOCK_THRESHOLD=10
```

**Implementation**:
```python
min_stock = int(os.getenv('CONSUMER_MIN_STOCK', 1))
where_conditions.append(f"p.actual_available_stock >= {min_stock}")
```

#### 5.3 Real-time Stock Updates

**Webhook Integration**: When stock changes in Zoho, update immediately

```python
@router.post("/webhooks/stock-update")
async def handle_stock_webhook(
    payload: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Handle real-time stock updates from Zoho"""

    item_id = payload.get('item_id')
    new_stock = payload.get('actual_available_stock')

    # Update database
    db.execute(
        "UPDATE products SET actual_available_stock = :stock "
        "WHERE zoho_item_id = :item_id",
        {"stock": new_stock, "item_id": item_id}
    )
    db.commit()

    # Clear cache
    await redis.delete(f"product:{item_id}")

    return {"status": "success"}
```

---

### 6. TDS Core Responsibilities

**Philosophy**: TDS = Single Source of Truth for all sync operations

#### 6.1 TDS Architecture Mandate

**ALL Zoho operations MUST go through TDS:**

```
❌ WRONG: Direct Zoho API calls from routers
app/routers/products.py → zoho_client.get("items")

✅ CORRECT: Through TDS
app/routers/products.py → TDS Sync Orchestrator → Zoho Client
```

#### 6.2 TDS Responsibilities

**TDS Core (`app/tds/`) is responsible for:**

1. **Authentication**:
   - Token management
   - Auto-refresh
   - Rate limiting

2. **API Communication**:
   - All Zoho API calls
   - Request/response handling
   - Error handling and retries

3. **Data Transformation**:
   - Zoho format → TSH format
   - Validation
   - Enrichment

4. **Synchronization**:
   - Webhooks processing
   - Bulk sync operations
   - Queue management

5. **Event Publishing**:
   - Sync events
   - Status updates
   - Error notifications

**Other modules MUST NOT:**
- ❌ Make direct Zoho API calls
- ❌ Handle OAuth tokens
- ❌ Transform Zoho data
- ❌ Manage sync queue

**Migration Plan for Legacy Code:**

```bash
# Find legacy direct Zoho calls
grep -r "zoho_client\|ZohoService" app/routers/ app/services/

# Move to TDS
# Example:
# OLD: app/services/product_service.py → zoho_client.get("items")
# NEW: app/services/product_service.py → tds.sync.sync_entity(EntityType.PRODUCTS)
```

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | Nov 7, 2025 | Senior Engineer | Initial Tronix guide created |
| 1.1.0 | Nov 7, 2025 | Senior Engineer | Added senior engineering standards |
|  |  |  | - Token management strategy |
|  |  |  | - Code consolidation guidelines |
|  |  |  | - Daily data investigation system |
|  |  |  | - Consumer app filtering |
|  |  |  | - TDS core responsibilities |
| 1.2.0 | Nov 7, 2025 | Senior Engineer | Added Core Development Principles |
|  |  |  | - Professional & institutional approach |
|  |  |  | - Clean & unified architecture |
|  |  |  | - Clean & maintainable database |
|  |  |  | - Clean & maintainable backend |
|  |  |  | - Database naming conventions |
|  |  |  | - Code quality examples |
| 1.3.0 | Nov 7, 2025 | Senior Engineer | Added Claude Code Operating Instructions |
|  |  |  | - Mandatory operating protocol |
|  |  |  | - Investigation workflow (Read → Search → Analyze) |
|  |  |  | - TodoWrite tool usage requirements |
|  |  |  | - TDS architecture enforcement |
|  |  |  | - Database access pattern |
|  |  |  | - Code quality standards with examples |
|  |  |  | - Communication & documentation guidelines |
|  |  |  | - Problem-solving approach |
|  |  |  | - Zoho API best practices |
|  |  |  | - Testing & validation checklist |
|  |  |  | - Prohibited actions |
|  |  |  | - Decision-making framework |
|  |  |  | - Mandatory workflow compliance |
|  |  |  | - Accountability & quality standards |

---

## Notes

**This guide is a living document**. Update it whenever:
- Architecture changes
- New features are added
- Deployment process changes
- New issues and solutions are discovered
- Team feedback suggests improvements

**Remember**: As a senior engineer, your responsibility is not just to build and deploy, but to **document, mentor, and ensure the system can be maintained by others**.

---

**🚀 Stay sharp. Deploy smart. Build for the future.**

*End of Tronix Guide*
