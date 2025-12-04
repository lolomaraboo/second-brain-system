#!/usr/bin/env python3
"""
Mem0 Queue Worker - Solution 2A
Processes local queue and syncs to VPS Mem0
Retries failed entries on each run
"""

import json
import time
import fcntl
import requests
from pathlib import Path
from datetime import datetime

# Configuration
QUEUE_FILE = Path.home() / ".claude/mem0_queue.json"
LOCK_FILE = Path.home() / ".claude/mem0_queue.lock"
MEM0_API_URL = "http://31.220.104.244:8081"
MAX_RETRIES = 3
BACKOFF_BASE = 2  # seconds
LOCK_TIMEOUT = 5  # seconds

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
    except:
        return False

def process_queue():
    """Process all entries in queue AND retry failed entries"""
    # Acquire lock before processing
    LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(LOCK_FILE, 'w') as lock:
        if not acquire_lock_with_timeout(lock):
            print("⚠️  Could not acquire lock (timeout). Queue might be busy. Skipping this run.")
            return

        queue = load_queue()

        print(f"📤 Processing queue: {len(queue['queue'])} pending, {len(queue['failed'])} failed")

        # 1. Process normal queue
        for entry in queue["queue"][:]:  # Copy for safe modification
            success = try_upload(entry)

            if success:
                queue["queue"].remove(entry)
                queue["stats"]["total_synced"] += 1
                queue["stats"]["last_sync"] = datetime.now().isoformat()
                print(f"  ✅ Synced: {entry['project_id']} (ID: {entry['id'][:8]}...)")
            else:
                entry["retries"] += 1
                if entry["retries"] >= MAX_RETRIES:
                    queue["queue"].remove(entry)
                    queue["failed"].append(entry)
                    queue["stats"]["total_failed"] += 1
                    print(f"  ❌ Failed (3x): {entry['project_id']} → moved to failed")
                else:
                    print(f"  ⏳ Retry {entry['retries']}/{MAX_RETRIES}: {entry['project_id']}")
                    time.sleep(BACKOFF_BASE ** entry["retries"])

        # 2. Retry failed entries (give them a new chance)
        if queue["failed"]:
            print(f"\n🔄 Retrying {len(queue['failed'])} failed entries...")

        for entry in queue["failed"][:]:
            entry["retries"] = 0  # Reset counter for new chance
            success = try_upload(entry)

            if success:
                queue["failed"].remove(entry)
                queue["stats"]["total_synced"] += 1
                queue["stats"]["total_failed"] -= 1
                queue["stats"]["last_sync"] = datetime.now().isoformat()
                print(f"  ✅ Recovered: {entry['project_id']} (ID: {entry['id'][:8]}...)")
            else:
                print(f"  ⏸️  Still failed: {entry['project_id']} (will retry next time)")

        # Save updated queue
        save_queue(queue)

        # Final summary
        print(f"\n✨ Worker done:")
        print(f"   Queue: {len(queue['queue'])} pending")
        print(f"   Failed: {len(queue['failed'])} failed")
        print(f"   Total synced: {queue['stats']['total_synced']}")

        # Lock is automatically released when exiting the 'with' block

if __name__ == "__main__":
    try:
        process_queue()
    except Exception as e:
        print(f"❌ Worker error: {e}")
        exit(1)
