#!/bin/bash
#
# Simple Image Download Monitor
# Monitors the ongoing image download and provides periodic updates
#

LOG_FILE="/tmp/image_download_final.log"
REPORT_INTERVAL=30  # Report every 30 seconds

echo "=========================================="
echo "Zoho Image Download Monitor"
echo "=========================================="
echo "Log file: $LOG_FILE"
echo "Report interval: ${REPORT_INTERVAL}s"
echo "=========================================="
echo ""

while true; do
    if [ ! -f "$LOG_FILE" ]; then
        echo "[$(date '+%H:%M:%S')] ⚠️  Log file not found yet..."
        sleep 5
        continue
    fi

    # Check if process is still running
    if ! pgrep -f "download_zoho_images_paginated.py" > /dev/null; then
        echo ""
        echo "[$(date '+%H:%M:%S')] ✅ Download process completed!"
        echo ""
        echo "=== FINAL SUMMARY ===="
        tail -30 "$LOG_FILE" | grep -E "(Download Complete|Successfully downloaded|Failed|Skipped|Total)"
        echo "======================"
        break
    fi

    # Get current progress
    CURRENT_BATCH=$(tail -50 "$LOG_FILE" | grep "Processing Batch" | tail -1)
    LAST_PRODUCT=$(tail -20 "$LOG_FILE" | grep "^\[" | tail -1)

    echo ""
    echo "[$(date '+%H:%M:%S')] 📊 Progress Update"
    echo "-------------------------------------------"
    if [ ! -z "$CURRENT_BATCH" ]; then
        echo "$CURRENT_BATCH"
    fi
    if [ ! -z "$LAST_PRODUCT" ]; then
        echo "Last: $LAST_PRODUCT" | head -1
    fi

    # Count downloaded/skipped/failed
    DOWNLOADED=$(grep "✅ Downloaded:" "$LOG_FILE" | wc -l)
    SKIPPED=$(grep "⏭️  Image already exists:" "$LOG_FILE" | wc -l)
    FAILED=$(grep "❌ Failed:" "$LOG_FILE" | wc -l)

    echo "Downloaded: $DOWNLOADED | Skipped: $SKIPPED | Failed: $FAILED"
    echo "-------------------------------------------"

    sleep $REPORT_INTERVAL
done

# Final image count
echo ""
echo "📦 Final Image Count:"
ls -1 /var/www/product-images/*.jpg 2>/dev/null | wc -l
echo "images in /var/www/product-images/"
echo ""
echo "🎉 Monitoring complete!"
