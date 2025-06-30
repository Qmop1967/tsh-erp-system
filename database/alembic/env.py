from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
import sys
from dotenv import load_dotenv

# إضافة مسار التطبيق إلى sys.path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# تحميل متغيرات البيئة
load_dotenv()

# إستيراد النماذج
from app.db.database import Base
from app.models import (
    Branch, Warehouse, Role, User,
    Category, Product, Customer, Supplier,
    InventoryItem, StockMovement,
    SalesOrder, SalesItem, PurchaseOrder, PurchaseItem,
    # Accounting models
    Currency, ExchangeRate, ChartOfAccounts, Account, 
    Journal, JournalEntry, JournalLine, FiscalYear, AccountingPeriod,
    # POS models
    POSTerminal, POSSession, POSTransaction, POSTransactionItem,
    POSPayment, POSDiscount, POSPromotion,
    # Invoice models
    SalesInvoice, SalesInvoiceItem, PurchaseInvoice, PurchaseInvoiceItem, InvoicePayment
)

# هذا الكائن يحتوي على إعدادات Alembic
config = context.config

# تحديد URL قاعدة البيانات من متغيرات البيئة
config.set_main_option(
    "sqlalchemy.url", 
    os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/erp_db")
)

# تفسير ملف الإعدادات للـ logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# إضافة كائن MetaData للـ 'autogenerate'
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """تشغيل الهجرات في وضع 'offline'.

    هذا يكوّن السياق مع URL فقط
    وليس Engine، على الرغم من أن Engine متوافق هنا أيضاً.
    
    من خلال تخطي إنشاء Engine، لا نحتاج حتى لتوفر DBAPI.
    
    يستدعي context.execute() لإخراج SQL إلى stdout.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """تشغيل الهجرات في وضع 'online'.

    في هذا السيناريو نحتاج لإنشاء Engine
    وربط connection بالسياق.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online() 