# ============================================================================
# TSH NeuroLink - Simplified Dockerfile
# Production-ready FastAPI notification service
# ============================================================================

FROM python:3.14-slim

LABEL maintainer="TSH ERP Team"
LABEL description="TSH NeuroLink - Central Communication & Notification System"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./app ./app
COPY ./migrations ./migrations

# Create necessary directories
RUN mkdir -p /app/logs /app/firebase

# Create non-root user for security
RUN groupadd -r neurolink && \
    useradd -r -g neurolink -s /bin/bash -d /app neurolink && \
    chown -R neurolink:neurolink /app

# Switch to non-root user
USER neurolink

# Expose port
EXPOSE 8002

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8002/health || exit 1

# Start application with Uvicorn
CMD ["uvicorn", "app.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8002", \
     "--workers", "4", \
     "--log-level", "info", \
     "--access-log", \
     "--use-colors"]
