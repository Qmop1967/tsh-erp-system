from sqlalchemy import create_engine, URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker as async_sessionmaker
import os
from dotenv import load_dotenv
from urllib.parse import urlparse, unquote

# تحميل متغيرات البيئة
load_dotenv()

# URL قاعدة البيانات
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/erp_db")

# Parse and decode DATABASE_URL to handle URL-encoded passwords
def parse_database_url(url: str) -> URL:
    """
    Parse DATABASE_URL and properly decode URL-encoded components.

    This fixes issues with special characters in passwords (like @ and !)
    which need to be URL-encoded in the connection string but must be
    decoded before passing to psycopg2.
    """
    parsed = urlparse(url)

    # URL-decode username and password
    username = unquote(parsed.username) if parsed.username else None
    password = unquote(parsed.password) if parsed.password else None

    # Build SQLAlchemy URL object
    return URL.create(
        drivername=parsed.scheme,
        username=username,
        password=password,
        host=parsed.hostname,
        port=parsed.port,
        database=parsed.path.lstrip('/')
    )

# Create properly parsed database URL
db_url = parse_database_url(DATABASE_URL)

# إنشاء محرك قاعدة البيانات (Sync)
engine = create_engine(db_url)

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

# Create async database URL (using asyncpg driver)
async_db_url = URL.create(
    drivername="postgresql+asyncpg",
    username=db_url.username,
    password=db_url.password,
    host=db_url.host,
    port=db_url.port,
    database=db_url.database
)

# Create async engine
async_engine = create_async_engine(
    async_db_url,
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