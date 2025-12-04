#!/usr/bin/env python3
"""
Index Obsidian vault markdown files into Mem0/Qdrant.

This script indexes all .md files from Memories/vault/ into Qdrant so they become
searchable via mem0_search. Each file is indexed with metadata about its path,
type (_INDEX.md vs regular .md), and project association.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from mem0 import Memory

# Configuration
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
VAULT_PATH = Path.home() / "Documents/APP_HOME/CascadeProjects/windsurf-project/Memories/vault"

# OpenAI API Key
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
if not OPENAI_API_KEY:
    env_file = Path.home() / ".claude" / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if line.startswith('OPENAI_API_KEY='):
                OPENAI_API_KEY = line.split('=', 1)[1].strip()
                break

# ANSI colors
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
BOLD = '\033[1m'
NC = '\033[0m'

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

try:
    memory = Memory.from_config(config)
    print(f"{GREEN}✅ Mem0 initialized (Qdrant: {QDRANT_HOST}:{QDRANT_PORT}){NC}")
except Exception as e:
    print(f"{RED}❌ Failed to initialize Mem0: {e}{NC}")
    sys.exit(1)

def extract_project_from_path(rel_path):
    """
    Extract project ID from file path.

    Examples:
    - projects/dev/recording-studio-manager/... → recording-studio-manager
    - projects/dev/second-brain/... → SecondBrain
    - wiki/tools/... → SecondBrain (wiki is part of SecondBrain)
    - ideas/... → SecondBrain
    """
    parts = Path(rel_path).parts

    if len(parts) >= 3 and parts[0] == 'projects' and parts[1] == 'dev':
        project_name = parts[2]
        # Map to actual project IDs
        if project_name == 'second-brain':
            return 'SecondBrain'
        elif project_name == 'youtube-transcript':
            return 'yt-transcript'
        else:
            return project_name

    # Everything else belongs to SecondBrain (wiki, ideas, daily, etc.)
    return 'SecondBrain'

def create_document_from_file(file_path, vault_path):
    """
    Create a document string from markdown file for indexation.

    Includes:
    - File path (for reference)
    - File type (INDEX vs regular)
    - First 50 lines or full content if shorter
    - Metadata as prefix
    """
    rel_path = os.path.relpath(file_path, vault_path)

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"{RED}Error reading {rel_path}: {e}{NC}")
        return None

    # Determine file type
    is_index = file_path.endswith('_INDEX.md')
    file_type = "INDEX" if is_index else "DOC"

    # Extract project
    project_id = extract_project_from_path(rel_path)

    # Create document with metadata prefix
    doc = f"""[OBSIDIAN:{file_type}] {rel_path}
Project: {project_id}
Path: Memories/vault/{rel_path}

{content}
"""

    return {
        'content': doc,
        'project_id': project_id,
        'rel_path': rel_path,
        'file_type': file_type
    }

def index_vault(vault_path, force_reindex=False):
    """Index all markdown files in vault."""
    vault_path = Path(vault_path).resolve()

    if not vault_path.exists():
        print(f"{RED}❌ Vault path does not exist: {vault_path}{NC}")
        return False

    print(f"{BLUE}{'='*70}{NC}")
    print(f"{BLUE}  Obsidian Vault → Qdrant Indexation{NC}")
    print(f"{BLUE}{'='*70}{NC}")
    print(f"Vault: {vault_path}")
    print()

    # Find all markdown files
    md_files = []
    for root, dirs, files in os.walk(vault_path):
        if '.obsidian' in root:
            continue
        for file in files:
            if file.endswith('.md'):
                md_files.append(os.path.join(root, file))

    print(f"Found {len(md_files)} markdown files")
    print()

    # Index each file
    indexed_count = 0
    error_count = 0

    for file_path in md_files:
        rel_path = os.path.relpath(file_path, vault_path)

        # Create document
        doc_data = create_document_from_file(file_path, vault_path)
        if not doc_data:
            error_count += 1
            continue

        try:
            # Add to Mem0/Qdrant
            # Use project_id as user_id for proper segmentation
            memory.add(
                doc_data['content'],
                user_id=doc_data['project_id'],
                metadata={
                    'source': 'obsidian',
                    'file_path': doc_data['rel_path'],
                    'file_type': doc_data['file_type'],
                    'indexed_at': datetime.now().isoformat()
                }
            )

            indexed_count += 1

            # Show progress
            if indexed_count % 10 == 0:
                print(f"{YELLOW}Indexed {indexed_count}/{len(md_files)}...{NC}")

        except Exception as e:
            print(f"{RED}Error indexing {rel_path}: {e}{NC}")
            error_count += 1

    print()
    print(f"{BOLD}{'='*70}{NC}")
    print(f"{BOLD}Indexation Summary{NC}")
    print(f"{BOLD}{'='*70}{NC}")
    print()
    print(f"{GREEN}✅ Indexed: {indexed_count}{NC}")
    print(f"{RED}❌ Errors: {error_count}{NC}")
    print()

    # Show stats by project
    print(f"{BOLD}Files by Project:{NC}")
    project_counts = {}
    for file_path in md_files:
        rel_path = os.path.relpath(file_path, vault_path)
        project_id = extract_project_from_path(rel_path)
        project_counts[project_id] = project_counts.get(project_id, 0) + 1

    for project_id, count in sorted(project_counts.items()):
        print(f"  {project_id}: {count} files")

    print()
    print(f"{GREEN}✅ Vault indexation complete!{NC}")
    print(f"{YELLOW}Now you can use mem0_search to find Obsidian content{NC}")
    print(f"{BOLD}{'='*70}{NC}")

    return error_count == 0

if __name__ == "__main__":
    force = '--force' in sys.argv
    success = index_vault(VAULT_PATH, force_reindex=force)
    sys.exit(0 if success else 1)
