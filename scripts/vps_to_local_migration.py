#!/usr/bin/env python3
"""
vps_to_local_migration.py

Migre les mémoires depuis le VPS Mem0 vers le stockage local JSON.

Usage:
    python3 vps_to_local_migration.py dev--second-brain
    python3 vps_to_local_migration.py dev--recording-studio-manager
"""

import sys
import json
import requests
from pathlib import Path
from datetime import datetime

# Configuration
VPS_BASE_URL = "http://31.220.104.244:8081"
MEMORIES_DIR = Path(__file__).parent.parent / "memories"

def fetch_all_memories(project_id: str) -> list:
    """Récupère toutes les mémoires d'un projet depuis le VPS."""
    print(f"📡 Récupération des mémoires de {project_id}...")

    try:
        url = f"{VPS_BASE_URL}/memory/{project_id}"
        response = requests.get(url, params={'limit': 10000}, timeout=60)
        response.raise_for_status()

        data = response.json()
        memories = data.get('memories', {}).get('results', [])

        print(f"✓ {len(memories)} mémoires récupérées")
        return memories

    except requests.exceptions.Timeout:
        print(f"⚠️  Timeout lors de la récupération (VPS trop lent)")
        return []
    except Exception as e:
        print(f"✗ Erreur: {e}")
        return []

def save_to_local(project_id: str, memories: list):
    """Sauvegarde les mémoires en JSON local."""
    if not memories:
        print("⚠️  Aucune mémoire à sauvegarder")
        return

    MEMORIES_DIR.mkdir(parents=True, exist_ok=True)

    # Nom de fichier avec timestamp
    filename = f"{project_id}.json"
    filepath = MEMORIES_DIR / filename

    # Backup si fichier existe déjà
    if filepath.exists():
        backup = MEMORIES_DIR / f"{project_id}.backup.{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        filepath.rename(backup)
        print(f"💾 Ancien fichier → {backup.name}")

    # Structure du fichier local
    data = {
        "project_id": project_id,
        "migrated_at": datetime.now().isoformat(),
        "source": "VPS Mem0",
        "count": len(memories),
        "memories": memories
    }

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✓ Sauvegardé: {filepath}")
    print(f"  {len(memories)} mémoires ({filepath.stat().st_size / 1024:.1f} KB)")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 vps_to_local_migration.py <project_id>")
        print("\nExemples:")
        print("  python3 vps_to_local_migration.py dev--second-brain")
        print("  python3 vps_to_local_migration.py dev--recording-studio-manager")
        sys.exit(1)

    project_id = sys.argv[1]

    print(f"\n{'='*60}")
    print(f"Migration VPS → Local: {project_id}")
    print(f"{'='*60}\n")

    # Fetch
    memories = fetch_all_memories(project_id)

    # Save
    if memories:
        save_to_local(project_id, memories)
        print(f"\n✓ Migration terminée")
    else:
        print(f"\n✗ Migration échouée (aucune mémoire récupérée)")
        sys.exit(1)

if __name__ == "__main__":
    main()
