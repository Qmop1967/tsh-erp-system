"""
TDS Core - Database Connection Management
Async SQLAlchemy connection pooling and session management
"""
from typing import AsyncGenerator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool, QueuePool
from contextlib import asynccontextmanager
import logging

from core.config import settings

logger = logging.getLogger(__name__)

# ============================================================================
# DATABASE ENGINE
# ============================================================================

# Create async engine with connection pooling
engine = create_async_engine(
    settings.get_database_url,
    echo=settings.debug,  # Log all SQL in debug mode
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    pool_timeout=settings.database_pool_timeout,
    pool_pre_ping=True,  # Verify connections before using
    poolclass=QueuePool,
    connect_args={
        "server_settings": {
            "application_name": f"{settings.app_name}_API",
            "jit": "off"  # Disable JIT for better cold start performance
        }
    }
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Base class for all ORM models
Base = declarative_base()

# ============================================================================
# SESSION MANAGEMENT
# ============================================================================

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for FastAPI routes to get database session

    Usage:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Item))
            return result.scalars().all()
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_db_context():
    """
    Context manager for database sessions (for non-FastAPI code)

    Usage:
        async with get_db_context() as db:
            result = await db.execute(select(Item))
            items = result.scalars().all()
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

async def init_db():
    """Initialize database connection and create tables if needed"""
    try:
        async with engine.begin() as conn:
            # Test connection
            await conn.execute(text("SELECT 1"))
            logger.info("✅ Database connection established")
            logger.info(f"📊 Database: {settings.database_name} @ {settings.database_host}")
            logger.info(f"🔗 Pool size: {settings.database_pool_size} (max overflow: {settings.database_max_overflow})")

            # Note: We don't create tables here since we're using Alembic migrations
            # await conn.run_sync(Base.metadata.create_all)

    except Exception as e:
        logger.error(f"❌ Failed to connect to database: {e}")
        raise


async def close_db():
    """Close database connections gracefully"""
    try:
        await engine.dispose()
        logger.info("✅ Database connections closed")
    except Exception as e:
        logger.error(f"❌ Error closing database: {e}")


# ============================================================================
# DATABASE HEALTH CHECK
# ============================================================================

async def check_db_health() -> dict:
    """
    Check database connection health

    Returns:
        dict with status, latency, and pool info
    """
    import time

    try:
        start_time = time.time()

        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT 1"))
            result.scalar()

        latency_ms = (time.time() - start_time) * 1000

        # Get pool statistics
        pool = engine.pool
        pool_stats = {
            "size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "max_overflow": settings.database_max_overflow
        }

        return {
            "status": "healthy",
            "latency_ms": round(latency_ms, 2),
            "database": settings.database_name,
            "host": settings.database_host,
            "pool": pool_stats
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "database": settings.database_name,
            "host": settings.database_host
        }


# ============================================================================
# DATABASE UTILITIES
# ============================================================================

async def execute_raw_sql(sql: str, params: dict = None) -> any:
    """
    Execute raw SQL query

    Args:
        sql: SQL query string
        params: Query parameters (dict)

    Returns:
        Query result
    """
    async with get_db_context() as db:
        result = await db.execute(sql, params or {})
        return result


async def execute_raw_sql_fetch_all(sql: str, params: dict = None) -> list:
    """
    Execute raw SQL and fetch all results

    Args:
        sql: SQL query string
        params: Query parameters (dict)

    Returns:
        List of result rows
    """
    async with get_db_context() as db:
        result = await db.execute(sql, params or {})
        return result.fetchall()


async def execute_raw_sql_fetch_one(sql: str, params: dict = None) -> any:
    """
    Execute raw SQL and fetch single result

    Args:
        sql: SQL query string
        params: Query parameters (dict)

    Returns:
        Single result row or None
    """
    async with get_db_context() as db:
        result = await db.execute(sql, params or {})
        return result.fetchone()


# ============================================================================
# TRANSACTION HELPERS
# ============================================================================

@asynccontextmanager
async def db_transaction():
    """
    Context manager for explicit transactions

    Usage:
        async with db_transaction() as db:
            await db.execute(...)
            await db.execute(...)
            # Auto-commits on success, rolls back on error
    """
    async with AsyncSessionLocal() as session:
        async with session.begin():
            try:
                yield session
            except Exception:
                await session.rollback()
                raise


# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

def configure_db_logging():
    """Configure database-related logging"""
    if settings.debug:
        # Enable SQL query logging in debug mode
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
        logging.getLogger('sqlalchemy.pool').setLevel(logging.DEBUG)
    else:
        # Only log warnings/errors in production
        logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
        logging.getLogger('sqlalchemy.pool').setLevel(logging.WARNING)


# Initialize logging on import
configure_db_logging()


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    import asyncio

    async def test_connection():
        """Test database connection"""
        print("Testing database connection...")

        # Initialize
        await init_db()

        # Health check
        health = await check_db_health()
        print(f"Health: {health}")

        # Close
        await close_db()

    asyncio.run(test_connection())
