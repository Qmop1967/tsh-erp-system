# ============================================================================
# TSH NeuroLink - Multi-stage Dockerfile
# Production-ready FastAPI notification service
# ============================================================================

# Stage 1: Builder
FROM python:3.11-slim as builder

LABEL maintainer="TSH ERP Team"
LABEL description="TSH NeuroLink - Central Communication & Notification System"

# Set working directory
WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir --user -r requirements.txt

# ============================================================================
# Stage 2: Production
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Set working directory
WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd -r neurolink && \
    useradd -r -g neurolink -s /bin/bash -d /app neurolink && \
    chown -R neurolink:neurolink /app

# Copy Python dependencies from builder
COPY --from=builder --chown=neurolink:neurolink /root/.local /home/neurolink/.local

# Make sure scripts in .local are usable
ENV PATH=/home/neurolink/.local/bin:$PATH

# Copy application code
COPY --chown=neurolink:neurolink ./app ./app
COPY --chown=neurolink:neurolink ./migrations ./migrations

# Create necessary directories
RUN mkdir -p /app/logs /app/firebase && \
    chown -R neurolink:neurolink /app/logs /app/firebase

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
