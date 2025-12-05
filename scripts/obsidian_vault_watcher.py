#!/usr/bin/env python3
"""
Obsidian Vault Filesystem Watcher
Automatically re-indexes Obsidian vault when .md files are created/modified/deleted.

Usage:
    python3 obsidian_vault_watcher.py

Run as LaunchAgent on macOS for automatic startup.
"""

import sys
import time
import subprocess
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configuration
VAULT_PATH = Path.home() / "Documents/APP_HOME/CascadeProjects/windsurf-project/Memories/vault"
INDEX_SCRIPT = Path.home() / "Documents/APP_HOME/CascadeProjects/windsurf-project/SecondBrain/scripts/index_obsidian_vault_direct.py"
DEBOUNCE_SECONDS = 2  # Wait 2s after last change before re-indexing

class ObsidianReindexHandler(FileSystemEventHandler):
    """Handler for Obsidian vault file changes"""

    def __init__(self):
        self.last_event_time = 0
        self.pending_reindex = False

    def on_any_event(self, event):
        """Triggered on any file system event"""
        # Ignore directory events and non-.md files
        if event.is_directory:
            return

        if not event.src_path.endswith('.md'):
            return

        # Ignore _INDEX.md files (they're auto-generated)
        if Path(event.src_path).name == '_INDEX.md':
            return

        # Mark for reindex
        self.last_event_time = time.time()
        self.pending_reindex = True

        event_type = event.event_type
        file_name = Path(event.src_path).name
        print(f"📝 [{event_type}] {file_name}", file=sys.stderr)

    def check_and_reindex(self):
        """Check if enough time has passed and trigger reindex"""
        if not self.pending_reindex:
            return

        # Wait for debounce period
        if time.time() - self.last_event_time < DEBOUNCE_SECONDS:
            return

        # Trigger re-indexation
        print(f"\n🔄 Re-indexing Obsidian vault...", file=sys.stderr)
        try:
            result = subprocess.run(
                ["python3", str(INDEX_SCRIPT)],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                # Extract indexed count from output
                for line in result.stdout.split('\n'):
                    if 'indexed successfully' in line:
                        print(f"✅ {line.strip()}", file=sys.stderr)
                        break
                else:
                    print(f"✅ Re-indexation completed", file=sys.stderr)
            else:
                print(f"❌ Re-indexation failed: {result.stderr}", file=sys.stderr)

        except subprocess.TimeoutExpired:
            print(f"⚠️  Re-indexation timeout (>60s)", file=sys.stderr)
        except Exception as e:
            print(f"❌ Re-indexation error: {e}", file=sys.stderr)

        # Reset state
        self.pending_reindex = False

def main():
    """Main watcher loop"""

    # Validate paths
    if not VAULT_PATH.exists():
        print(f"❌ Vault path not found: {VAULT_PATH}", file=sys.stderr)
        sys.exit(1)

    if not INDEX_SCRIPT.exists():
        print(f"❌ Index script not found: {INDEX_SCRIPT}", file=sys.stderr)
        sys.exit(1)

    print(f"🚀 Obsidian Vault Watcher starting...", file=sys.stderr)
    print(f"   Watching: {VAULT_PATH}", file=sys.stderr)
    print(f"   Debounce: {DEBOUNCE_SECONDS}s", file=sys.stderr)
    print(f"", file=sys.stderr)

    # Create handler and observer
    handler = ObsidianReindexHandler()
    observer = Observer()
    observer.schedule(handler, str(VAULT_PATH), recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(0.5)
            handler.check_and_reindex()

    except KeyboardInterrupt:
        print(f"\n👋 Stopping watcher...", file=sys.stderr)
        observer.stop()

    observer.join()
    print(f"✅ Watcher stopped", file=sys.stderr)

if __name__ == "__main__":
    main()
