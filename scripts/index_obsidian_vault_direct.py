#!/usr/bin/env python3
"""
Index Obsidian vault markdown files directly into Qdrant (bypassing Mem0).

Uses OpenAI embeddings + Qdrant client directly for faster, simpler indexation.
"""

import os
import sys
import hashlib
from pathlib import Path
from datetime import datetime
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

# Configuration
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
VAULT_PATH = Path.home() / "Documents/APP_HOME/CascadeProjects/windsurf-project/Memories/vault"
COLLECTION_NAME = "obsidian_vault"
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIM = 1536

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

# Initialize clients
try:
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
    qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    print(f"{GREEN}✅ Clients initialized (OpenAI + Qdrant){NC}")
except Exception as e:
    print(f"{RED}❌ Failed to initialize: {e}{NC}")
    sys.exit(1)

def extract_project_from_path(rel_path):
    """Extract project ID from file path."""
    parts = Path(rel_path).parts

    if len(parts) >= 3 and parts[0] == 'projects' and parts[1] == 'dev':
        project_name = parts[2]
        if project_name == 'second-brain':
            return 'SecondBrain'
        elif project_name == 'youtube-transcript':
            return 'yt-transcript'
        else:
            return project_name

    return 'SecondBrain'

def create_embedding(text):
    """Create embedding using OpenAI."""
    try:
        response = openai_client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text[:8000]  # Limit to 8k chars
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"{RED}Embedding error: {e}{NC}")
        return None

def generate_point_id(file_path):
    """Generate deterministic point ID from file path."""
    hash_obj = hashlib.md5(file_path.encode())
    # Convert first 8 bytes to integer for Qdrant point ID
    return int.from_bytes(hash_obj.digest()[:8], byteorder='big')

def index_vault(vault_path, recreate=False):
    """Index all markdown files in vault."""
    vault_path = Path(vault_path).resolve()

    if not vault_path.exists():
        print(f"{RED}❌ Vault path does not exist: {vault_path}{NC}")
        return False

    print(f"{BLUE}{'='*70}{NC}")
    print(f"{BLUE}  Obsidian Vault → Qdrant Direct Indexation{NC}")
    print(f"{BLUE}{'='*70}{NC}")
    print(f"Vault: {vault_path}")
    print(f"Collection: {COLLECTION_NAME}")
    print()

    # Create or recreate collection
    try:
        collections = qdrant_client.get_collections().collections
        exists = any(c.name == COLLECTION_NAME for c in collections)

        if exists:
            if recreate:
                print(f"{YELLOW}Recreating collection...{NC}")
                qdrant_client.delete_collection(COLLECTION_NAME)
                exists = False
            else:
                print(f"{YELLOW}Collection exists, will update existing points{NC}")

        if not exists:
            print(f"{GREEN}Creating collection...{NC}")
            qdrant_client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE)
            )
    except Exception as e:
        print(f"{RED}Collection error: {e}{NC}")
        return False

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
    points = []

    for file_path in md_files:
        rel_path = os.path.relpath(file_path, vault_path)

        try:
            # Read file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Skip empty files
            if not content.strip():
                continue

            # Extract metadata
            is_index = file_path.endswith('_INDEX.md')
            file_type = "INDEX" if is_index else "DOC"
            project_id = extract_project_from_path(rel_path)

            # Create text for embedding (with metadata prefix)
            text_for_embedding = f"""[OBSIDIAN:{file_type}] {rel_path}
Project: {project_id}

{content[:6000]}"""  # Limit to 6k chars for embedding

            # Generate embedding
            embedding = create_embedding(text_for_embedding)
            if not embedding:
                error_count += 1
                continue

            # Create point
            point_id = generate_point_id(rel_path)
            point = PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    'source': 'obsidian',
                    'file_path': rel_path,
                    'full_path': str(file_path),
                    'file_type': file_type,
                    'project_id': project_id,
                    'indexed_at': datetime.now().isoformat(),
                    'content_preview': content[:500]  # First 500 chars for preview
                }
            )
            points.append(point)

            indexed_count += 1

            # Batch upload every 10 points
            if len(points) >= 10:
                qdrant_client.upsert(
                    collection_name=COLLECTION_NAME,
                    points=points
                )
                print(f"{YELLOW}Uploaded {indexed_count}/{len(md_files)}...{NC}")
                points = []

        except Exception as e:
            print(f"{RED}Error indexing {rel_path}: {e}{NC}")
            error_count += 1

    # Upload remaining points
    if points:
        qdrant_client.upsert(
            collection_name=COLLECTION_NAME,
            points=points
        )

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
    print(f"{YELLOW}Collection '{COLLECTION_NAME}' ready in Qdrant{NC}")
    print(f"{BOLD}{'='*70}{NC}")

    return error_count == 0

if __name__ == "__main__":
    recreate = '--recreate' in sys.argv
    success = index_vault(VAULT_PATH, recreate=recreate)
    sys.exit(0 if success else 1)
