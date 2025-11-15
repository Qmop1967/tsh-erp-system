# ============================================================================
# TSH NeuroLink - Multi-Stage Production Dockerfile
# Production-ready FastAPI notification service with optimized build
# ============================================================================

# Stage 1: Builder
FROM python:3.11-slim AS builder

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user --upgrade pip setuptools wheel && \
    pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

LABEL maintainer="TSH ERP Team"
LABEL description="TSH NeuroLink - Central Communication & Notification System"
LABEL version="1.0"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd -r neurolink && \
    useradd -r -g neurolink -s /bin/bash -d /app neurolink

# Copy Python packages from builder
COPY --from=builder /root/.local /home/neurolink/.local

# Make sure scripts in .local are usable
ENV PATH=/home/neurolink/.local/bin:$PATH

# Copy application code
COPY --chown=neurolink:neurolink ./app ./app
COPY --chown=neurolink:neurolink ./migrations ./migrations

# Create necessary directories
RUN mkdir -p /app/logs /app/firebase && \
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
