FROM python:3.11-slim

# تعيين متغيرات البيئة
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# تعيين مجلد العمل
WORKDIR /app

# تثبيت متطلبات النظام
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# نسخ ملف المتطلبات وتثبيتها
COPY config/requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# نسخ كود التطبيق
COPY . .

# إنشاء مستخدم غير جذر
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser /app
USER appuser

# عرض المنفذ
EXPOSE 8000

# أمر التشغيل
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 