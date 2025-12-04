#!/usr/bin/env python3
"""
Mem0 Queue Worker - Option C
Always-running worker with VPS health checks, DLQ, and infinite retry
Systemd service replaces cron
"""

import json
import time
import fcntl
import requests
import os
from pathlib import Path
from datetime import datetime

# Configuration
QUEUE_FILE = Path.home() / ".claude/mem0_queue.json"
DLQ_FILE = Path.home() / ".claude/mem0_queue_dlq.json"
METRICS_FILE = Path.home() / ".claude/mem0_metrics.json"
LOCK_FILE = Path.home() / ".claude/mem0_queue.lock"
MEM0_API_URL = "http://31.220.104.244:8081"
VPS_HEALTH_URL = f"{MEM0_API_URL}/health"

# Option C settings
HEALTH_CHECK_INTERVAL = 30  # seconds
MAX_BACKOFF = 3600  # 1 hour max
LOCK_TIMEOUT = 30  # increased from 5s
DLQ_THRESHOLD = 5  # Move to DLQ after 5 failed attempts

def acquire_lock_with_timeout(lock_file, timeout=LOCK_TIMEOUT):
    """Acquire file lock with timeout to prevent blocking indefinitely"""
    start = time.time()

    while time.time() - start < timeout:
        try:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True  # Lock acquired
        except BlockingIOError:
            time.sleep(0.1)  # Wait 100ms and retry

    return False  # Timeout

def load_queue() -> dict:
    """Load queue from JSON file"""
    if not QUEUE_FILE.exists():
        return {
            "queue": [],
            "last_100": [],
            "failed": [],
            "stats": {
                "total_queued": 0,
                "total_synced": 0,
                "total_failed": 0,
                "last_sync": None
            }
        }

    try:
        with open(QUEUE_FILE, 'r') as f:
            return json.load(f)
    except:
        # Corrupted file, start fresh
        return {
            "queue": [],
            "last_100": [],
            "failed": [],
            "stats": {
                "total_queued": 0,
                "total_synced": 0,
                "total_failed": 0,
                "last_sync": None
            }
        }

def save_queue(queue_data: dict):
    """Save queue to JSON file (atomic write)"""
    tmp_file = QUEUE_FILE.with_suffix('.tmp')
    try:
        with open(tmp_file, 'w') as f:
            json.dump(queue_data, f, indent=2)
        tmp_file.replace(QUEUE_FILE)
    except:
        if tmp_file.exists():
            tmp_file.unlink()

def check_vps_health() -> bool:
    """Check if VPS is accessible and healthy"""
    try:
        response = requests.get(VPS_HEALTH_URL, timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ VPS health check failed: {e}")
        return False

def load_dlq() -> list:
    """Load Dead Letter Queue from file"""
    if not DLQ_FILE.exists():
        return []

    try:
        with open(DLQ_FILE, 'r') as f:
            data = json.load(f)
            return data.get('items', [])
    except:
        return []

def save_dlq(items: list):
    """Save Dead Letter Queue to file"""
    DLQ_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(DLQ_FILE, 'w') as f:
            json.dump({
                'items': items,
                'last_update': datetime.now().isoformat()
            }, f, indent=2)
    except Exception as e:
        print(f"❌ Failed to save DLQ: {e}")

def move_to_dlq(entry: dict):
    """Move failed entry from queue to DLQ"""
    dlq = load_dlq()
    entry['moved_to_dlq_at'] = time.time()
    entry['last_attempt'] = time.time()
    dlq.append(entry)
    save_dlq(dlq)
    print(f"📋 Moved to DLQ: {entry['project_id']} (ID: {entry['id'][:8]}...) after {entry.get('retries', 0)} retries")

def update_metrics(queue_data: dict, dlq_items: list):
    """Update metrics file with current stats"""
    try:
        metrics = {
            'last_update': datetime.now().isoformat(),
            'vps_status': 'healthy' if check_vps_health() else 'down',
            'queue_size': len(queue_data.get('queue', [])),
            'dlq_size': len(dlq_items),
            'total_synced': queue_data.get('stats', {}).get('total_synced', 0),
            'total_queued': queue_data.get('stats', {}).get('total_queued', 0)
        }

        with open(METRICS_FILE, 'w') as f:
            json.dump(metrics, f, indent=2)
    except Exception as e:
        print(f"⚠️  Failed to update metrics: {e}")

def try_upload(entry: dict) -> bool:
    """Attempt to upload entry to VPS Mem0"""
    try:
        response = requests.post(
            f"{MEM0_API_URL}/memory",
            json={
                "user_id": entry["project_id"],
                "content": entry["content"]
            },
            timeout=30
        )
        return response.json().get("success", False)
    except Exception as e:
        print(f"  ⚠️  Upload failed: {e}")
        return False

def process_dlq():
    """Process DLQ items with infinite retry and exponential backoff"""
    dlq = load_dlq()

    if not dlq:
        return

    print(f"\n🔄 Processing DLQ: {len(dlq)} items")

    recovered_items = []

    for item in dlq[:]:  # Copy for safe modification
        # Calculate backoff delay
        retry_count = item.get('retry_count', 0)
        delay = min(2 ** retry_count * 30, MAX_BACKOFF)
        last_attempt = item.get('last_attempt', 0)
        age = time.time() - last_attempt

        # Skip if backoff not elapsed
        if age < delay:
            next_retry_in = int(delay - age)
            print(f"  ⏸️  Waiting backoff: {item['project_id']} (retry in {next_retry_in}s)")
            continue

        # Retry upload
        success = try_upload(item)

        if success:
            recovered_items.append(item)
            print(f"  ✅ DLQ recovered: {item['project_id']} (ID: {item['id'][:8]}...) after {retry_count} retries")
        else:
            item['retry_count'] = retry_count + 1
            item['last_attempt'] = time.time()
            print(f"  ⏳ DLQ retry {item['retry_count']}: {item['project_id']} (next in {delay}s)")

    # Remove recovered items from DLQ
    for item in recovered_items:
        dlq.remove(item)

    # Save updated DLQ
    if recovered_items or any(item.get('retry_count', 0) > 0 for item in dlq):
        save_dlq(dlq)

def process_queue():
    """Process normal queue with DLQ threshold (Option C)"""
    # Acquire lock before processing
    LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(LOCK_FILE, 'w') as lock:
        if not acquire_lock_with_timeout(lock):
            print("⚠️  Could not acquire lock (timeout). Queue might be busy. Skipping this run.")
            return

        queue = load_queue()

        print(f"\n📤 Processing queue: {len(queue['queue'])} pending")

        # Process normal queue with DLQ threshold
        for entry in queue["queue"][:]:  # Copy for safe modification
            success = try_upload(entry)

            if success:
                queue["queue"].remove(entry)
                queue["stats"]["total_synced"] += 1
                queue["stats"]["last_sync"] = datetime.now().isoformat()
                print(f"  ✅ Synced: {entry['project_id']} (ID: {entry['id'][:8]}...)")
            else:
                entry["retries"] += 1
                if entry["retries"] >= DLQ_THRESHOLD:
                    # Move to DLQ after threshold retries
                    queue["queue"].remove(entry)
                    move_to_dlq(entry)
                else:
                    print(f"  ⏳ Retry {entry['retries']}/{DLQ_THRESHOLD}: {entry['project_id']}")

        # Save updated queue
        save_queue(queue)

        # Update metrics
        dlq = load_dlq()
        update_metrics(queue, dlq)

        # Final summary
        print(f"\n✨ Queue processed:")
        print(f"   Pending: {len(queue['queue'])}")
        print(f"   DLQ: {len(dlq)}")
        print(f"   Total synced: {queue['stats']['total_synced']}")

        # Lock is automatically released when exiting the 'with' block

def main_loop():
    """Main loop - always running with VPS health checks (Option C)"""
    print("🚀 Mem0 Worker Option C starting...")
    print(f"   Health check interval: {HEALTH_CHECK_INTERVAL}s")
    print(f"   VPS URL: {MEM0_API_URL}")
    print(f"   DLQ threshold: {DLQ_THRESHOLD} retries")
    print(f"   Max backoff: {MAX_BACKOFF}s (1 hour)")
    print("")

    while True:
        try:
            # 1. VPS health check
            vps_healthy = check_vps_health()

            if vps_healthy:
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] ✅ VPS healthy - processing queues...")

                # 2. Process DLQ first (priority to old failed items)
                process_dlq()

                # 3. Process normal queue
                process_queue()
            else:
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] ❌ VPS unhealthy - waiting {HEALTH_CHECK_INTERVAL}s...")

                # Update metrics even when VPS down
                queue = load_queue()
                dlq = load_dlq()
                update_metrics(queue, dlq)

        except Exception as e:
            print(f"\n❌ Worker error: {e}")
            print(f"   Will retry in {HEALTH_CHECK_INTERVAL}s...")

        # Sleep before next cycle
        time.sleep(HEALTH_CHECK_INTERVAL)

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        print("\n\n🛑 Worker stopped by user (Ctrl+C)")
        exit(0)
    except Exception as e:
        print(f"\n❌ Worker fatal error: {e}")
        exit(1)
