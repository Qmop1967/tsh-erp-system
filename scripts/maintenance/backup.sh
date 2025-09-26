#!/bin/bash
# Daily backup script for TSH ERP System

cd "/Users/khaleelal-mulla/Desktop/TSH ERP System"

echo "📦 Creating daily backup..."
git add .
git commit -m "📅 Daily backup: $(date)"

# Create a timestamped tag
git tag "backup-$(date +%Y%m%d-%H%M)"

echo "✅ Backup completed: backup-$(date +%Y%m%d-%H%M)"

# Show recent commits
echo "📋 Recent commits:"
git log --oneline -5
