from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

# URL قاعدة البيانات
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/erp_db")

# إنشاء محرك قاعدة البيانات
engine = create_engine(DATABASE_URL)

# إنشاء جلسة قاعدة البيانات
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# إنشاء قاعدة أساسية للنماذج
Base = declarative_base()

# Dependency للحصول على جلسة قاعدة البيانات
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 