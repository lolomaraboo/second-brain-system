#!/usr/bin/env python3
"""
Migration Script: JSON Files → Qdrant Vector Store
Migrates all existing memory JSON files to Qdrant with embeddings
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from mem0 import Memory

# Configuration
MEMORIES_DIR = Path.home() / "Documents/APP_HOME/CascadeProjects/windsurf-project/SecondBrain/memories"
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333

# Load OpenAI API key
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
if not OPENAI_API_KEY:
    env_file = Path.home() / ".claude" / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if line.startswith('OPENAI_API_KEY='):
                OPENAI_API_KEY = line.split('=', 1)[1].strip()
                break

if not OPENAI_API_KEY:
    print("❌ OPENAI_API_KEY not found in environment or ~/.claude/.env")
    sys.exit(1)

# Initialize Mem0
config = {
    'llm': {
        'provider': 'openai',
        'config': {
            'model': 'gpt-4o-mini',
            'temperature': 0.1,
            'max_tokens': 2000,
            'api_key': OPENAI_API_KEY
        }
    },
    'vector_store': {
        'provider': 'qdrant',
        'config': {
            'host': QDRANT_HOST,
            'port': QDRANT_PORT,
        }
    },
    'embedder': {
        'provider': 'openai',
        'config': {
            'model': 'text-embedding-3-small',
            'api_key': OPENAI_API_KEY
        }
    }
}

print("🔧 Initializing Mem0 with Qdrant...")
try:
    memory = Memory.from_config(config)
    print(f"✅ Mem0 initialized (Qdrant: {QDRANT_HOST}:{QDRANT_PORT})")
except Exception as e:
    print(f"❌ Failed to initialize Mem0: {e}")
    sys.exit(1)

def migrate_project(project_name: str, dry_run: bool = False):
    """Migrate all memories for a project"""
    project_dir = MEMORIES_DIR / project_name

    if not project_dir.exists():
        print(f"⚠️  Project directory not found: {project_dir}")
        return 0, 0

    json_files = list(project_dir.glob("*.json"))

    if not json_files:
        print(f"⚠️  No JSON files found in {project_name}")
        return 0, 0

    print(f"\n📦 Migrating project: {project_name}")
    print(f"   Found {len(json_files)} memory files")

    success_count = 0
    error_count = 0

    for i, json_file in enumerate(json_files, 1):
        try:
            # Read memory from JSON
            with open(json_file, 'r') as f:
                memory_data = json.load(f)

            memory_text = memory_data.get('memory', '')
            if not memory_text:
                print(f"   ⚠️  [{i}/{len(json_files)}] Empty memory: {json_file.name}")
                error_count += 1
                continue

            if dry_run:
                print(f"   🔍 [{i}/{len(json_files)}] Would migrate: {memory_text[:50]}...")
                success_count += 1
            else:
                # Add to Qdrant via Mem0
                result = memory.add(memory_text, user_id=project_name, metadata={
                    'source': 'migration',
                    'original_id': memory_data.get('id', ''),
                    'created_at': memory_data.get('created_at', ''),
                })

                if result:
                    if i % 10 == 0:
                        print(f"   ✓ [{i}/{len(json_files)}] Migrated")
                    success_count += 1
                else:
                    print(f"   ❌ [{i}/{len(json_files)}] Failed: {json_file.name}")
                    error_count += 1

        except Exception as e:
            print(f"   ❌ [{i}/{len(json_files)}] Error: {json_file.name} - {e}")
            error_count += 1

    return success_count, error_count

def main():
    """Main migration function"""
    import argparse

    parser = argparse.ArgumentParser(description='Migrate memory JSON files to Qdrant')
    parser.add_argument('--project', help='Migrate specific project only')
    parser.add_argument('--dry-run', action='store_true', help='Dry run (no actual migration)')
    parser.add_argument('--yes', '-y', action='store_true', help='Skip confirmation prompt')
    args = parser.parse_args()

    print("=" * 70)
    print("  JSON → Qdrant Migration")
    print("=" * 70)
    print(f"Source: {MEMORIES_DIR}")
    print(f"Target: Qdrant ({QDRANT_HOST}:{QDRANT_PORT})")
    if args.dry_run:
        print("Mode: DRY RUN (no changes)")
    print("=" * 70)

    # Discover projects
    if args.project:
        projects = [args.project]
    else:
        projects = [d.name for d in MEMORIES_DIR.iterdir()
                   if d.is_dir() and not d.name.startswith('.') and d.name not in ['comparison-report.json', 'merge-report.json', 'final-merge-report.json', 'vps-full-scan.json', 'vps-projects-found.json', 'vps-real-projects.json']]

    print(f"\n📋 Projects to migrate: {len(projects)}")
    for proj in projects:
        print(f"   - {proj}")

    if not args.dry_run and not args.yes:
        response = input("\n⚠️  This will create embeddings (OpenAI cost ~$0.004). Continue? [y/N] ")
        if response.lower() != 'y':
            print("❌ Migration cancelled")
            sys.exit(0)

    # Migrate each project
    total_success = 0
    total_errors = 0

    start_time = datetime.now()

    for project in projects:
        success, errors = migrate_project(project, dry_run=args.dry_run)
        total_success += success
        total_errors += errors

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    # Summary
    print("\n" + "=" * 70)
    print("  Migration Summary")
    print("=" * 70)
    print(f"✅ Successfully migrated: {total_success}")
    print(f"❌ Errors: {total_errors}")
    print(f"⏱️  Duration: {duration:.2f}s")
    print(f"💰 Estimated OpenAI cost: ~${(total_success * 0.000002):.4f}")
    print("=" * 70)

    if not args.dry_run and total_success > 0:
        print("\n✨ Migration complete! Memories are now in Qdrant.")
        print("   You can now use mem0_search for semantic search.")

if __name__ == "__main__":
    main()
