#!/bin/bash
# ============================================
# TSH ERP - Docker Build Cache Warming Script
# ============================================
# Purpose: Pre-pull base images to speed up Docker builds
# Usage: Run before deployment to warm the cache
# Benefits: Eliminates network download time during builds (saves 30-60 seconds)
#
# Created: 2025-11-17
# ============================================

set -e

echo "🔥 Warming Docker build cache for TSH ERP..."
echo "============================================"

# Define base images used in the project
BASE_IMAGES=(
    "python:3.11-slim"
    "postgres:15-alpine"
    "redis:7-alpine"
    "nginx:alpine"
    "node:18-alpine"
)

# Pre-pull each image
for image in "${BASE_IMAGES[@]}"; do
    echo "📦 Pulling $image..."
    if docker pull "$image" --quiet; then
        echo "   ✅ $image pulled successfully"
    else
        echo "   ⚠️  Failed to pull $image (non-critical)"
    fi
done

echo ""
echo "============================================"
echo "✅ Cache warming complete!"
echo ""

# Show cached images
echo "📊 Currently cached images:"
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | grep -E "python|postgres|redis|nginx|node" | head -10

echo ""
echo "🚀 You can now run faster builds with:"
echo "   DOCKER_BUILDKIT=1 docker-compose build"
echo "   or"
echo "   docker-compose up -d --build"
