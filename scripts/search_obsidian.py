#!/usr/bin/env python3
"""
Search in Obsidian vault Qdrant collection.
"""

import sys
from openai import OpenAI
from qdrant_client import QdrantClient
import os

# Configuration
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
COLLECTION_NAME = "obsidian_vault"
EMBEDDING_MODEL = "text-embedding-3-small"

# OpenAI API Key
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
if not OPENAI_API_KEY:
    env_file = os.path.expanduser("~/.claude/.env")
    if os.path.exists(env_file):
        for line in open(env_file):
            if line.startswith('OPENAI_API_KEY='):
                OPENAI_API_KEY = line.split('=', 1)[1].strip()
                break

# Initialize
openai_client = OpenAI(api_key=OPENAI_API_KEY)
qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

def search(query, limit=5):
    """Search in Obsidian vault."""
    # Create embedding
    response = openai_client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=query
    )
    query_vector = response.data[0].embedding

    # Search
    results = qdrant_client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=limit
    ).points

    print(f"\nFound {len(results)} results for: '{query}'\n")
    print("="*70)

    for i, hit in enumerate(results, 1):
        payload = hit.payload
        print(f"\n{i}. [{hit.score:.3f}] {payload['file_path']}")
        print(f"   Type: {payload['file_type']} | Project: {payload['project_id']}")
        print(f"   Preview: {payload['content_preview'][:200]}...")

    print("\n" + "="*70)

if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "_INDEX.md vides"
    search(query, limit=10)
