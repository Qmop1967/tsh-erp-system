#!/usr/bin/env python3
"""
TDS Core - Run Sync Worker
Simple script to start the sync worker
"""
import asyncio
import logging
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from workers.sync_worker import run_worker

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("=" * 80)
    print("TDS Core - Sync Worker")
    print("=" * 80)
    print("Starting worker...")
    print("Press Ctrl+C to stop")
    print("=" * 80)

    # Run worker
    try:
        asyncio.run(run_worker())
    except KeyboardInterrupt:
        print("\n" + "=" * 80)
        print("Worker stopped")
        print("=" * 80)
