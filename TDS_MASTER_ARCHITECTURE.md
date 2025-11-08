# TDS (TSH Data Sync) - Master Architecture Document
## Unified Overseas Integration Platform

**Version:** 4.0.0 (Comprehensive Statistics & Comparison System)
**Date:** January 7, 2025
**Status:** 🚧 In Development
**Author:** TSH ERP Senior Engineering Team

---

## 🎯 Executive Summary

**TDS (TSH Data Sync)** is the centralized, enterprise-grade platform responsible for ALL overseas integrations in the TSH ERP Ecosystem. It consolidates scattered services, provides unified authentication, implements comprehensive statistics and comparison engines, and ensures data consistency across systems.

### Key Objectives
- ✅ **Single Source of Truth** for all overseas data synchronization
- ✅ **Unified Authentication** for all external systems (Zoho, future APIs)
- ✅ **Statistics & Comparison Engine** for data quality monitoring
- ✅ **Event-Driven Architecture** for real-time sync and notifications
- ✅ **Production-Ready** with monitoring, alerts, and metrics
- ✅ **Extensible** for future integrations (Alibaba, Amazon, etc.)

---

## 📊 Current State Analysis

### ✅ What's Already Built (TDS v3.0.0)

```
app/tds/
├── core/
│   ├── service.py          ✅ TDS Core Service (sync orchestration)
│   ├── queue.py            ✅ Queue management with locking
│   └── events.py           ✅ Event system for pub/sub
│
├── integrations/
│   ├── base.py             ✅ Base integration interface
│   └── zoho/
│       ├── auth.py         ✅ OAuth 2.0 authentication
│       ├── client.py       ✅ Unified API client
│       ├── sync.py         ✅ Sync orchestrator (1,378 lines)
│       ├── stock_sync.py   ✅ Stock synchronization
│       ├── image_sync.py   ✅ Image synchronization
│       ├── webhooks.py     ✅ Webhook handling
│       ├── processors/     ✅ Data transformation
│       │   ├── products.py
│       │   ├── customers.py
│       │   ├── inventory.py
│       │   └── pricelists.py
│       └── utils/          ✅ Rate limiting, retry logic
│
├── services/
│   ├── alerts.py           ✅ Alert management
│   └── monitoring.py       ✅ System monitoring
│
├── handlers/
│   └── sync_handlers.py    ✅ Event handlers
│
└── zoho.py                 ✅ Unified facade for Zoho operations
```

### ❌ What Needs to Be Done (TDS v4.0.0)

**1. Consolidation (Remove Duplication)**
```
❌ app/services/zoho_queue.py       → Move to TDS
❌ app/services/zoho_processor.py   → Move to TDS
⚠️  app/routers/zoho_webhooks.py    → Update to use TDS
⚠️  app/routers/zoho_bulk_sync.py   → Update to use TDS
```

**2. New Features Required**
```
❌ Statistics & Comparison Engine
❌ Data Quality Monitoring
❌ Automated Sync Scheduler
❌ TDS Dashboard (statistics, health, metrics)
❌ TDS CLI Tool
❌ Migration Documentation
```

---

## 🏗️ TDS v4.0.0 Architecture

### Directory Structure

```
app/tds/
├── __init__.py                    # TDS main exports
├── config.py                      # 🆕 TDS configuration management
│
├── core/
│   ├── service.py                 # ✅ Core TDS service
│   ├── queue.py                   # ✅ Queue management
│   ├── events.py                  # ✅ Event system
│   ├── scheduler.py               # 🆕 Job scheduling (APScheduler)
│   └── config_manager.py          # 🆕 Dynamic configuration
│
├── integrations/
│   ├── base.py                    # ✅ Base integration interface
│   ├── manager.py                 # 🆕 Integration registry & manager
│   │
│   └── zoho/
│       ├── __init__.py            # Zoho exports
│       ├── auth.py                # ✅ OAuth authentication
│       ├── client.py              # ✅ Unified API client
│       ├── sync.py                # ✅ Sync orchestrator
│       ├── stock_sync.py          # ✅ Stock sync
│       ├── image_sync.py          # ✅ Image sync
│       ├── webhooks.py            # ✅ Webhook manager
│       ├── queue.py               # 🆕 Zoho-specific queue (from services/)
│       ├── processor.py           # 🆕 Zoho processor (from services/)
│       ├── processors/            # ✅ Entity processors
│       │   ├── products.py
│       │   ├── customers.py
│       │   ├── vendors.py         # 🆕 Vendor processor
│       │   ├── pricelists.py
│       │   ├── inventory.py
│       │   └── invoices.py        # 🆕 Invoice processor
│       └── utils/                 # ✅ Utilities
│           ├── rate_limiter.py
│           └── retry.py
│
├── statistics/                    # 🆕 Statistics & Comparison Engine
│   ├── __init__.py
│   ├── engine.py                  # Core comparison engine
│   ├── collectors/                # Data collectors
│   │   ├── zoho_collector.py     # Collect Zoho stats
│   │   └── local_collector.py    # Collect TSH ERP stats
│   ├── comparators/               # Comparison logic
│   │   ├── items_comparator.py
│   │   ├── customers_comparator.py
│   │   ├── stock_comparator.py
│   │   └── pricelist_comparator.py
│   ├── reporters/                 # Report generators
│   │   ├── summary_reporter.py
│   │   ├── detailed_reporter.py
│   │   └── json_reporter.py
│   └── models.py                  # Statistics models
│
├── services/
│   ├── alerts.py                  # ✅ Alert management
│   ├── monitoring.py              # ✅ System monitoring
│   ├── health.py                  # 🆕 Health check service
│   └── metrics.py                 # 🆕 Metrics aggregation
│
├── handlers/
│   ├── sync_handlers.py           # ✅ Sync event handlers
│   └── alert_handlers.py          # 🆕 Alert event handlers
│
├── api/                           # 🆕 TDS API endpoints
│   ├── __init__.py
│   ├── statistics.py              # Statistics endpoints
│   ├── sync.py                    # Sync control endpoints
│   ├── health.py                  # Health check endpoints
│   └── webhooks.py                # Webhook endpoints
│
├── cli/                           # 🆕 TDS CLI Tool
│   ├── __init__.py
│   ├── main.py                    # CLI entry point
│   ├── commands/
│   │   ├── sync.py                # Sync commands
│   │   ├── stats.py               # Statistics commands
│   │   ├── health.py              # Health check commands
│   │   └── compare.py             # Comparison commands
│   └── utils.py                   # CLI utilities
│
└── zoho.py                        # ✅ Zoho facade (single entry point)
```

---

## 🔧 Implementation Plan

### Phase 1: Consolidation (Priority: HIGH)

**Goal:** Move all scattered Zoho services into TDS

#### Task 1.1: Move Zoho Queue to TDS
```bash
# Move file
app/services/zoho_queue.py → app/tds/integrations/zoho/queue.py

# Update imports throughout codebase
❌ from app.services.zoho_queue import ZohoQueue
✅ from app.tds.integrations.zoho import ZohoQueue
```

#### Task 1.2: Move Zoho Processor to TDS
```bash
# Move file
app/services/zoho_processor.py → app/tds/integrations/zoho/processor.py

# Update imports
❌ from app.services.zoho_processor import ZohoProcessor
✅ from app.tds.integrations.zoho import ZohoProcessor
```

#### Task 1.3: Update Routers
```python
# app/routers/zoho_webhooks.py
# Before:
from app.services.zoho_processor import ZohoProcessor
from app.services.zoho_queue import ZohoQueue

# After:
from app.tds.zoho import ZohoService

@router.post("/api/zoho/webhooks")
async def handle_webhook(payload: dict):
    service = ZohoService()
    return await service.process_webhook(payload)
```

---

### Phase 2: Statistics & Comparison Engine (Priority: HIGH)

**Goal:** Build comprehensive statistics and comparison system

#### Component 2.1: Data Collectors

**Zoho Collector** (`app/tds/statistics/collectors/zoho_collector.py`)
```python
class ZohoDataCollector:
    """Collects statistics from Zoho APIs"""

    async def collect_all_stats(self) -> ZohoStatistics:
        """Collect all statistics from Zoho"""
        return ZohoStatistics(
            items=await self.collect_items_stats(),
            customers=await self.collect_customer_stats(),
            vendors=await self.collect_vendor_stats(),
            price_lists=await self.collect_pricelist_stats(),
            stock=await self.collect_stock_stats(),
            images=await self.collect_image_stats(),
        )

    async def collect_items_stats(self) -> ItemStatistics:
        """Collect item/product statistics"""
        return ItemStatistics(
            total_count=<count>,
            active_count=<count>,
            inactive_count=<count>,
            with_images_count=<count>,
            without_images_count=<count>,
            by_category={...},
            by_brand={...},
        )
```

**Local Collector** (`app/tds/statistics/collectors/local_collector.py`)
```python
class LocalDataCollector:
    """Collects statistics from TSH ERP database"""

    async def collect_all_stats(self) -> LocalStatistics:
        """Collect all statistics from local database"""
        return LocalStatistics(
            items=await self.collect_items_stats(),
            customers=await self.collect_customer_stats(),
            vendors=await self.collect_vendor_stats(),
            price_lists=await self.collect_pricelist_stats(),
            stock=await self.collect_stock_stats(),
            images=await self.collect_image_stats(),
        )
```

#### Component 2.2: Comparators

**Items Comparator** (`app/tds/statistics/comparators/items_comparator.py`)
```python
class ItemsComparator:
    """Compares Zoho items with local items"""

    def compare(
        self,
        zoho_stats: ItemStatistics,
        local_stats: ItemStatistics
    ) -> ComparisonResult:
        """
        Compare item statistics

        Returns:
            ComparisonResult with differences, missing items, sync recommendations
        """
        return ComparisonResult(
            entity_type="items",
            zoho_count=zoho_stats.total_count,
            local_count=local_stats.total_count,
            difference=zoho_stats.total_count - local_stats.total_count,
            match_percentage=self._calculate_match_percentage(),
            missing_in_local=[...],  # Items in Zoho but not locally
            missing_in_zoho=[...],   # Items locally but not in Zoho
            mismatched_data=[...],   # Items with different data
            sync_recommendations=[...],  # What to sync
        )
```

#### Component 2.3: Statistics Engine

**Core Engine** (`app/tds/statistics/engine.py`)
```python
class StatisticsEngine:
    """
    Core statistics and comparison engine

    Responsibilities:
    - Orchestrate data collection from all sources
    - Run comparisons across all entity types
    - Generate sync recommendations
    - Create reports
    - Track statistics over time
    """

    def __init__(self, db: Session):
        self.db = db
        self.zoho_collector = ZohoDataCollector()
        self.local_collector = LocalDataCollector()
        self.comparators = {
            "items": ItemsComparator(),
            "customers": CustomersComparator(),
            "vendors": VendorsComparator(),
            "pricelists": PriceListComparator(),
            "stock": StockComparator(),
        }

    async def collect_and_compare(self) -> FullComparisonReport:
        """
        Collect data from both systems and compare

        Returns:
            Complete comparison report with all entities
        """
        # Collect from both systems
        zoho_stats = await self.zoho_collector.collect_all_stats()
        local_stats = await self.local_collector.collect_all_stats()

        # Run comparisons
        comparisons = {}
        for entity_type, comparator in self.comparators.items():
            comparisons[entity_type] = comparator.compare(
                getattr(zoho_stats, entity_type),
                getattr(local_stats, entity_type)
            )

        # Generate report
        report = FullComparisonReport(
            timestamp=datetime.utcnow(),
            zoho_statistics=zoho_stats,
            local_statistics=local_stats,
            comparisons=comparisons,
            sync_recommendations=self._generate_sync_recommendations(comparisons)
        )

        # Save report
        await self._save_report(report)

        return report

    async def auto_sync_differences(self, report: FullComparisonReport):
        """
        Automatically sync differences found in comparison

        Args:
            report: Comparison report with differences
        """
        sync_service = ZohoService()

        for entity_type, comparison in report.comparisons.items():
            if comparison.requires_sync:
                logger.info(f"Auto-syncing {entity_type}...")
                await sync_service.sync_entity(
                    entity_type=EntityType(entity_type),
                    mode=SyncMode.INCREMENTAL
                )
```

#### Component 2.4: Statistics Models

**Data Models** (`app/tds/statistics/models.py`)
```python
from dataclasses import dataclass
from typing import List, Dict, Any
from datetime import datetime

@dataclass
class ItemStatistics:
    """Item/Product statistics"""
    total_count: int
    active_count: int
    inactive_count: int
    with_images_count: int
    without_images_count: int
    by_category: Dict[str, int]
    by_brand: Dict[str, int]
    average_price: float
    total_stock_value: float

@dataclass
class CustomerStatistics:
    """Customer statistics"""
    total_count: int
    active_count: int
    inactive_count: int
    by_type: Dict[str, int]  # wholesale, retail, etc.
    by_country: Dict[str, int]
    total_credit_limit: float
    with_outstanding_balance: int

@dataclass
class VendorStatistics:
    """Vendor/Supplier statistics"""
    total_count: int
    active_count: int
    by_country: Dict[str, int]
    total_payables: float

@dataclass
class PriceListStatistics:
    """Price list statistics"""
    total_lists: int
    active_lists: int
    total_items_mapped: int
    lists_by_currency: Dict[str, int]
    coverage_percentage: float  # % of items with prices

@dataclass
class StockStatistics:
    """Stock/Inventory statistics"""
    total_items_in_stock: int
    out_of_stock_count: int
    low_stock_count: int
    total_stock_value: float
    average_stock_per_item: float
    by_warehouse: Dict[str, int]

@dataclass
class ImageStatistics:
    """Image statistics"""
    total_items: int
    with_images: int
    without_images: int
    coverage_percentage: float
    total_images_count: int
    average_images_per_item: float

@dataclass
class ZohoStatistics:
    """Complete Zoho statistics"""
    items: ItemStatistics
    customers: CustomerStatistics
    vendors: VendorStatistics
    price_lists: PriceListStatistics
    stock: StockStatistics
    images: ImageStatistics
    collected_at: datetime

@dataclass
class LocalStatistics:
    """Complete local TSH ERP statistics"""
    items: ItemStatistics
    customers: CustomerStatistics
    vendors: VendorStatistics
    price_lists: PriceListStatistics
    stock: StockStatistics
    images: ImageStatistics
    collected_at: datetime

@dataclass
class ComparisonResult:
    """Comparison result for a single entity type"""
    entity_type: str
    zoho_count: int
    local_count: int
    difference: int
    match_percentage: float
    missing_in_local: List[str]  # IDs
    missing_in_zoho: List[str]   # IDs
    mismatched_data: List[Dict[str, Any]]
    requires_sync: bool
    sync_recommendations: List[str]

@dataclass
class FullComparisonReport:
    """Complete comparison report"""
    timestamp: datetime
    zoho_statistics: ZohoStatistics
    local_statistics: LocalStatistics
    comparisons: Dict[str, ComparisonResult]
    overall_match_percentage: float
    sync_recommendations: List[str]
    alerts: List[str]
```

---

### Phase 3: API Endpoints (Priority: MEDIUM)

**Goal:** Expose TDS functionality via REST API

#### Statistics API (`app/tds/api/statistics.py`)

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/tds/statistics", tags=["TDS Statistics"])

@router.get("/overview")
async def get_statistics_overview(db: Session = Depends(get_db)):
    """
    Get high-level statistics overview

    Returns:
        Summary of items, customers, vendors, stock, etc.
    """
    engine = StatisticsEngine(db)
    report = await engine.collect_and_compare()

    return {
        "zoho": {
            "items": report.zoho_statistics.items.total_count,
            "customers": report.zoho_statistics.customers.total_count,
            "vendors": report.zoho_statistics.vendors.total_count,
            "price_lists": report.zoho_statistics.price_lists.total_lists,
            "stock_value": report.zoho_statistics.stock.total_stock_value,
        },
        "local": {
            "items": report.local_statistics.items.total_count,
            "customers": report.local_statistics.customers.total_count,
            "vendors": report.local_statistics.vendors.total_count,
            "price_lists": report.local_statistics.price_lists.total_lists,
            "stock_value": report.local_statistics.stock.total_stock_value,
        },
        "match_percentage": report.overall_match_percentage,
        "last_updated": report.timestamp.isoformat(),
    }

@router.get("/compare")
async def compare_zoho_vs_local(
    entity_type: str = None,
    db: Session = Depends(get_db)
):
    """
    Compare Zoho data with local data

    Args:
        entity_type: Optional filter (items, customers, vendors, etc.)

    Returns:
        Detailed comparison results
    """
    engine = StatisticsEngine(db)
    report = await engine.collect_and_compare()

    if entity_type:
        return report.comparisons.get(entity_type)

    return report

@router.post("/sync-differences")
async def sync_differences(
    entity_type: str = None,
    auto_resolve: bool = False,
    db: Session = Depends(get_db)
):
    """
    Sync differences found in comparison

    Args:
        entity_type: Optional filter for specific entity
        auto_resolve: Automatically resolve conflicts (Zoho wins)

    Returns:
        Sync results
    """
    engine = StatisticsEngine(db)
    report = await engine.collect_and_compare()

    if auto_resolve:
        await engine.auto_sync_differences(report)

    return {
        "status": "synced",
        "entity_type": entity_type or "all",
        "synced_count": len(report.sync_recommendations)
    }

@router.get("/items")
async def get_items_statistics(db: Session = Depends(get_db)):
    """Get detailed item statistics"""
    collector = ZohoDataCollector()
    zoho_stats = await collector.collect_items_stats()

    local_collector = LocalDataCollector(db)
    local_stats = await local_collector.collect_items_stats()

    comparator = ItemsComparator()
    comparison = comparator.compare(zoho_stats, local_stats)

    return {
        "zoho": zoho_stats,
        "local": local_stats,
        "comparison": comparison
    }

@router.get("/customers")
async def get_customer_statistics(db: Session = Depends(get_db)):
    """Get detailed customer statistics"""
    # Similar to items

@router.get("/vendors")
async def get_vendor_statistics(db: Session = Depends(get_db)):
    """Get detailed vendor statistics"""
    # Similar to items

@router.get("/pricelists")
async def get_pricelist_statistics(db: Session = Depends(get_db)):
    """Get detailed price list statistics"""
    # Similar to items

@router.get("/stock")
async def get_stock_statistics(db: Session = Depends(get_db)):
    """Get detailed stock statistics"""
    # Similar to items

@router.get("/images")
async def get_image_statistics(db: Session = Depends(get_db)):
    """Get detailed image statistics"""
    # Similar to items

@router.get("/history")
async def get_statistics_history(
    days: int = 30,
    db: Session = Depends(get_db)
):
    """
    Get historical statistics (trends over time)

    Args:
        days: Number of days to look back

    Returns:
        Time-series data for statistics
    """
    # Query tds_statistics_history table
    pass
```

---

### Phase 4: Scheduler & Automation (Priority: MEDIUM)

**Goal:** Automate statistics collection and sync operations

#### Scheduler Service (`app/tds/core/scheduler.py`)

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

class TDSScheduler:
    """
    TDS Job Scheduler

    Handles:
    - Daily statistics collection
    - Periodic incremental syncs
    - Automatic comparison and alerts
    - Health checks
    """

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self._setup_jobs()

    def _setup_jobs(self):
        """Setup all scheduled jobs"""

        # Daily full statistics comparison (2 AM)
        self.scheduler.add_job(
            self.daily_statistics_job,
            trigger=CronTrigger(hour=2, minute=0),
            id="daily_statistics",
            name="Daily Statistics Collection & Comparison"
        )

        # Hourly incremental sync (every hour)
        self.scheduler.add_job(
            self.hourly_sync_job,
            trigger=IntervalTrigger(hours=1),
            id="hourly_sync",
            name="Hourly Incremental Sync"
        )

        # Every 15 minutes - stock sync
        self.scheduler.add_job(
            self.stock_sync_job,
            trigger=IntervalTrigger(minutes=15),
            id="stock_sync",
            name="Stock Level Sync"
        )

        # Health check every 5 minutes
        self.scheduler.add_job(
            self.health_check_job,
            trigger=IntervalTrigger(minutes=5),
            id="health_check",
            name="System Health Check"
        )

    async def daily_statistics_job(self):
        """Daily statistics collection and comparison"""
        logger.info("Running daily statistics job...")

        engine = StatisticsEngine()
        report = await engine.collect_and_compare()

        # Check if sync is needed
        if report.overall_match_percentage < 95:
            logger.warning(f"Data mismatch detected: {report.overall_match_percentage}%")
            # Send alert
            await self._send_alert(
                "Data Mismatch",
                f"Zoho vs Local match: {report.overall_match_percentage}%",
                severity="warning"
            )

    async def hourly_sync_job(self):
        """Hourly incremental sync"""
        logger.info("Running hourly sync job...")

        service = ZohoService()
        await service.start()

        results = await service.sync_all(mode=SyncMode.INCREMENTAL)

        logger.info(f"Hourly sync complete: {results}")

    async def stock_sync_job(self):
        """Stock level synchronization"""
        logger.info("Running stock sync job...")

        service = ZohoService()
        result = await service.sync_stock()

        logger.info(f"Stock sync complete: {result.total_succeeded} items updated")

    async def health_check_job(self):
        """System health check"""
        # Check TDS health
        # Check database connection
        # Check Zoho API connectivity
        # Alert if issues detected
        pass

    def start(self):
        """Start the scheduler"""
        self.scheduler.start()
        logger.info("TDS Scheduler started")

    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        logger.info("TDS Scheduler stopped")
```

---

### Phase 5: CLI Tool (Priority: LOW)

**Goal:** Provide command-line interface for TDS operations

#### CLI Main (`app/tds/cli/main.py`)

```python
import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(name="tds", help="TDS (TSH Data Sync) CLI Tool")
console = Console()

@app.command()
def stats(
    entity: str = typer.Option(None, help="Entity type (items, customers, etc.)"),
    detailed: bool = typer.Option(False, help="Show detailed statistics")
):
    """Get statistics overview"""
    # Collect and display statistics
    pass

@app.command()
def compare(
    entity: str = typer.Option(None, help="Entity type to compare"),
    save: bool = typer.Option(False, help="Save report to file")
):
    """Compare Zoho vs Local data"""
    # Run comparison and display results
    pass

@app.command()
def sync(
    entity: str = typer.Argument(..., help="Entity to sync (items, customers, all)"),
    mode: str = typer.Option("incremental", help="Sync mode (full, incremental)"),
    auto: bool = typer.Option(False, help="Auto-resolve conflicts")
):
    """Sync data from Zoho"""
    # Run sync operation
    pass

@app.command()
def health():
    """Check TDS system health"""
    # Display health status
    pass

if __name__ == "__main__":
    app()
```

**Usage:**
```bash
# Get statistics
python -m app.tds.cli stats
python -m app.tds.cli stats --entity items --detailed

# Compare data
python -m app.tds.cli compare
python -m app.tds.cli compare --entity customers --save

# Sync data
python -m app.tds.cli sync items --mode full
python -m app.tds.cli sync all --mode incremental --auto

# Health check
python -m app.tds.cli health
```

---

## 📊 Database Schema Changes

### New Tables for Statistics

```sql
-- Statistics history
CREATE TABLE tds_statistics_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    collected_at TIMESTAMP NOT NULL DEFAULT NOW(),
    source_type VARCHAR(50) NOT NULL, -- 'zoho' or 'local'
    entity_type VARCHAR(50) NOT NULL,
    statistics JSONB NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_stats_history_collected ON tds_statistics_history(collected_at DESC);
CREATE INDEX idx_stats_history_entity ON tds_statistics_history(entity_type);

-- Comparison reports
CREATE TABLE tds_comparison_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_date DATE NOT NULL,
    entity_type VARCHAR(50),
    zoho_count INT,
    local_count INT,
    difference INT,
    match_percentage DECIMAL(5,2),
    missing_in_local JSONB,
    missing_in_zoho JSONB,
    mismatched_data JSONB,
    sync_recommendations JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_comparison_reports_date ON tds_comparison_reports(report_date DESC);
CREATE INDEX idx_comparison_reports_entity ON tds_comparison_reports(entity_type);

-- Scheduled jobs tracking
CREATE TABLE tds_scheduled_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id VARCHAR(100) NOT NULL UNIQUE,
    job_name VARCHAR(255) NOT NULL,
    schedule VARCHAR(100) NOT NULL,
    last_run TIMESTAMP,
    next_run TIMESTAMP,
    status VARCHAR(50) NOT NULL, -- 'active', 'paused', 'failed'
    last_result JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

---

## 🚀 Deployment & Migration

### Step 1: Database Migration

```bash
# Create migration
alembic revision -m "Add TDS statistics and comparison tables"

# Apply migration
alembic upgrade head
```

### Step 2: Move Services

```bash
# Backup old services
mkdir -p archived/services
mv app/services/zoho_*.py archived/services/

# Update imports in all files
# Use IDE Find & Replace:
# Find: from app.services.zoho
# Replace: from app.tds.integrations.zoho
```

### Step 3: Update Routers

```python
# app/routers/zoho_bulk_sync.py - Update imports
from app.tds.zoho import ZohoService

# app/routers/zoho_webhooks.py - Update imports
from app.tds.zoho import ZohoService
```

### Step 4: Register TDS API Routes

```python
# app/main.py
from app.tds.api import statistics, sync, health

app.include_router(statistics.router)
app.include_router(sync.router)
app.include_router(health.router)
```

### Step 5: Start Scheduler

```python
# app/main.py - Add on startup
from app.tds.core.scheduler import TDSScheduler

@app.on_event("startup")
async def startup():
    scheduler = TDSScheduler()
    scheduler.start()
```

---

## 📈 Success Metrics

### Key Performance Indicators

1. **Data Consistency**
   - Target: >99% match between Zoho and Local
   - Alert if < 95%

2. **Sync Performance**
   - Full sync: < 5 minutes for 10,000 items
   - Incremental sync: < 30 seconds

3. **System Health**
   - API uptime: >99.9%
   - Auth token refresh success: 100%
   - Webhook processing: < 1 second

4. **Statistics Accuracy**
   - Collection time: < 2 minutes
   - Comparison time: < 30 seconds
   - Report generation: < 10 seconds

---

## 🔐 Security Considerations

1. **Authentication**
   - Zoho OAuth tokens stored encrypted
   - Auto-refresh 5 minutes before expiry
   - Secure credential storage (environment variables)

2. **API Security**
   - Rate limiting on all endpoints
   - JWT authentication required
   - Permission-based access control

3. **Data Protection**
   - Sensitive data masked in logs
   - HTTPS for all external calls
   - Database encryption at rest

---

## 📚 Documentation

### User Documentation
- [ ] TDS Quick Start Guide
- [ ] API Reference (OpenAPI/Swagger)
- [ ] CLI Usage Guide
- [ ] Troubleshooting Guide

### Developer Documentation
- [ ] Architecture Deep Dive
- [ ] Adding New Integrations Guide
- [ ] Testing Guide
- [ ] Contributing Guidelines

---

## 🎯 Next Steps

### Immediate Actions
1. ✅ Complete this architecture document
2. 🔄 Implement Statistics & Comparison Engine
3. 🔄 Move scattered services to TDS
4. 🔄 Create API endpoints
5. 🔄 Build CLI tool
6. 🔄 Write tests
7. 🔄 Write documentation

### Future Enhancements
- Add support for Alibaba integration
- Add support for Amazon Seller Central
- Implement ML-based anomaly detection
- Create React dashboard for statistics
- Mobile app for monitoring

---

## 📞 Support

For questions or issues:
- **Email:** dev@tsh.sale
- **Slack:** #tds-support
- **Documentation:** https://docs.tsh.sale/tds

---

**Status:** Ready for Implementation
**Estimated Timeline:** 2-3 weeks
**Priority:** HIGH (CEO Approved)
