from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker as async_sessionmaker
import os
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

# URL قاعدة البيانات
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/erp_db")

# إنشاء محرك قاعدة البيانات (Sync)
engine = create_engine(DATABASE_URL)

# إنشاء جلسة قاعدة البيانات (Sync)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# إنشاء قاعدة أساسية للنماذج
Base = declarative_base()

# Dependency للحصول على جلسة قاعدة البيانات (Sync)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================================
# ASYNC DATABASE SUPPORT (for background workers)
# ============================================================================

# Convert DATABASE_URL to async format (postgresql:// -> postgresql+asyncpg://)
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Create async engine
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Async dependency for getting database session
async def get_async_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close() 