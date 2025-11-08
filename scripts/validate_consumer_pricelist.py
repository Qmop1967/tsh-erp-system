#!/usr/bin/env python3
"""
Consumer Price List Validation Script
=====================================

Validates that all active products with stock have Consumer price list prices.
This script is used in CI/CD pipelines to ensure Consumer app only displays
Consumer price list prices (not base prices).

Usage:
    python scripts/validate_consumer_pricelist.py

Exit Codes:
    0: All validations passed
    1: Validation failed (products missing Consumer prices)
"""

import os
import sys
import asyncio
from typing import Dict, Any, List, Tuple, Optional
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError, DatabaseError

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import get_async_db


class ConsumerPricelistValidator:
    """Validates Consumer price list coverage for products"""

    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []

    async def validate(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Run all validation checks
        
        Returns:
            Tuple of (is_valid, report_dict)
        """
        print("=" * 70)
        print("🔍 Consumer Price List Validation")
        print("=" * 70)
        print()

        # Check 1: Consumer price list exists
        print("[1/4] Checking Consumer price list exists...")
        consumer_pricelist = await self._check_consumer_pricelist_exists()
        if not consumer_pricelist:
            self.errors.append("Consumer price list not found in database")
            print("   ❌ FAILED: Consumer price list not found")
        else:
            print(f"   ✅ Found: {consumer_pricelist['name_en']} (code: {consumer_pricelist['code']})")
        print()

        # Check 2: Count products with stock
        print("[2/4] Counting products with stock > 0...")
        products_with_stock = await self._count_products_with_stock()
        print(f"   ✅ Products with stock: {products_with_stock}")
        print()

        # Check 3: Count products with Consumer prices
        print("[3/4] Counting products with Consumer price list prices...")
        products_with_consumer_price = await self._count_products_with_consumer_price()
        print(f"   ✅ Products with Consumer prices: {products_with_consumer_price}")
        print()

        # Check 4: Find products missing Consumer prices
        print("[4/4] Finding products missing Consumer prices...")
        missing_prices = await self._find_products_missing_consumer_prices()
        if missing_prices:
            self.errors.append(
                f"{len(missing_prices)} products with stock are missing Consumer price list prices"
            )
            print(f"   ❌ FAILED: {len(missing_prices)} products missing Consumer prices")
            print()
            print("   Sample products missing Consumer prices:")
            for product in missing_prices[:10]:  # Show first 10
                print(f"      - {product['name']} (SKU: {product['sku']}, Stock: {product['stock']})")
            if len(missing_prices) > 10:
                print(f"      ... and {len(missing_prices) - 10} more")
        else:
            print("   ✅ All products with stock have Consumer prices")
        print()

        # Calculate coverage percentage
        products_with_stock = products_with_stock or 0
        products_with_consumer_price = products_with_consumer_price or 0
        
        if products_with_stock > 0:
            coverage = (products_with_consumer_price / products_with_stock) * 100
        else:
            coverage = 0

        # Generate report
        report = {
            "consumer_pricelist_exists": consumer_pricelist is not None,
            "consumer_pricelist": consumer_pricelist,
            "products_with_stock": products_with_stock,
            "products_with_consumer_price": products_with_consumer_price,
            "products_missing_consumer_price": len(missing_prices),
            "coverage_percentage": round(coverage, 2),
            "errors": self.errors,
            "warnings": self.warnings,
            "is_valid": len(self.errors) == 0
        }

        # Print summary
        print("=" * 70)
        print("📊 Validation Summary")
        print("=" * 70)
        print(f"Products with stock: {products_with_stock}")
        print(f"Products with Consumer prices: {products_with_consumer_price}")
        print(f"Coverage: {coverage:.2f}%")
        print()

        if report["is_valid"]:
            print("✅ VALIDATION PASSED")
            print("   All products with stock have Consumer price list prices")
        else:
            print("❌ VALIDATION FAILED")
            for error in self.errors:
                print(f"   - {error}")
        print("=" * 70)

        return report["is_valid"], report

    async def _check_consumer_pricelist_exists(self) -> Optional[Dict[str, Any]]:
        """Check if Consumer price list exists"""
        try:
            async for db in get_async_db():
                try:
                    query = text("""
                        SELECT id, code, name_en, name_ar, currency, is_active
                        FROM price_lists
                        WHERE code = 'consumer_iqd'
                           OR name_en ILIKE '%Consumer%'
                        LIMIT 1
                    """)
                    result = await db.execute(query)
                    row = result.first()
                    
                    if row:
                        return {
                            "id": row[0],
                            "code": row[1],
                            "name_en": row[2],
                            "name_ar": row[3],
                            "currency": row[4],
                            "is_active": row[5]
                        }
                    return None
                except Exception as e:
                    print(f"   ⚠️ Error querying price_lists table: {str(e)}")
                    raise
                finally:
                    break
        except Exception as e:
            print(f"   ❌ Database error: {str(e)}")
            raise

    async def _count_products_with_stock(self) -> int:
        """Count products with stock > 0"""
        async for db in get_async_db():
            try:
                query = text("""
                    SELECT COUNT(*)
                    FROM products
                    WHERE is_active = true
                      AND actual_available_stock > 0
                """)
                result = await db.execute(query)
                count = result.scalar() or 0
                return count
            finally:
                break

    async def _count_products_with_consumer_price(self) -> int:
        """Count products with Consumer price list prices"""
        async for db in get_async_db():
            try:
                query = text("""
                    SELECT COUNT(DISTINCT p.id)
                    FROM products p
                    INNER JOIN product_prices pp ON pp.product_id = p.id
                    INNER JOIN price_lists pl ON pp.pricelist_id = pl.id
                    WHERE p.is_active = true
                      AND p.actual_available_stock > 0
                      AND pl.code = 'consumer_iqd'
                      AND (pp.currency = 'IQD' OR pp.currency IS NULL)
                      AND pp.price > 0
                """)
                result = await db.execute(query)
                count = result.scalar() or 0
                return count
            finally:
                break

    async def _find_products_missing_consumer_prices(self) -> List[Dict[str, Any]]:
        """Find products with stock but no Consumer price list prices"""
        async for db in get_async_db():
            try:
                query = text("""
                    SELECT DISTINCT
                        p.id,
                        p.sku,
                        p.name,
                        p.actual_available_stock as stock
                    FROM products p
                    WHERE p.is_active = true
                      AND p.actual_available_stock > 0
                      AND NOT EXISTS (
                          SELECT 1
                          FROM product_prices pp
                          INNER JOIN price_lists pl ON pp.pricelist_id = pl.id
                          WHERE pp.product_id = p.id
                            AND pl.code = 'consumer_iqd'
                            AND (pp.currency = 'IQD' OR pp.currency IS NULL)
                            AND pp.price > 0
                      )
                    ORDER BY p.name
                    LIMIT 100
                """)
                result = await db.execute(query)
                products = []
                for row in result:
                    products.append({
                        "id": str(row[0]),
                        "sku": row[1],
                        "name": row[2],
                        "stock": int(row[3]) if row[3] else 0
                    })
                return products
            finally:
                break


async def main():
    """Main entry point"""
    try:
        # Check database connection first
        print("🔍 Checking database connection...")
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            print("❌ ERROR: DATABASE_URL environment variable not set")
            print("")
            print("Required environment variables:")
            print("  - DATABASE_URL: PostgreSQL connection string")
            print("")
            print("Example:")
            print("  export DATABASE_URL='postgresql://user:pass@host:5432/dbname'")
            sys.exit(1)
        
        # Test database connection
        try:
            async for db in get_async_db():
                try:
                    await db.execute(text("SELECT 1"))
                    print("✅ Database connection successful")
                    break
                finally:
                    break
        except (OperationalError, DatabaseError) as e:
            print(f"❌ ERROR: Database connection failed")
            print(f"   Error: {str(e)}")
            print("")
            print("Please check:")
            print("  1. DATABASE_URL is correct")
            print("  2. Database server is accessible")
            print("  3. Database credentials are valid")
            sys.exit(1)
        except Exception as e:
            print(f"❌ ERROR: Unexpected error connecting to database")
            print(f"   Error: {str(e)}")
            print(f"   Type: {type(e).__name__}")
            sys.exit(1)
        
        # Run validation
        validator = ConsumerPricelistValidator()
        is_valid, report = await validator.validate()
        
        # Exit with appropriate code
        sys.exit(0 if is_valid else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️ Validation interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: Validation script failed unexpectedly")
        print(f"   Error: {str(e)}")
        print(f"   Type: {type(e).__name__}")
        import traceback
        print("\nFull traceback:")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

