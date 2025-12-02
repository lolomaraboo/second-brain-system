#!/usr/bin/env python3
import json, requests, os, time
from datetime import datetime
from pathlib import Path

BASE_URL = 'http://31.220.104.244:8081'
HEADERS = {}

def get_all_memories(project_id):
    """Récupère TOUTES les mémoires (l'API du VPS retourne tout d'un coup)."""
    response = requests.get(f'{BASE_URL}/memory/{project_id}?limit=1000',
                          headers=HEADERS,
                          timeout=30)
    response.raise_for_status()
    data = response.json()

    if not data.get('success'):
        print(f"  Erreur: {data.get('message', 'Unknown error')}")
        return []

    memories = data.get('memories', [])
    print(f"  ✓ {len(memories)} mémoires récupérées")
    return memories

projects = ['recording-studio-manager', 'claude-code-champion']
backup = {'timestamp': datetime.now().isoformat(), 'projects': {}}

for project_id in projects:
    print(f"Backing up {project_id}...")
    memories = get_all_memories(project_id)
    backup['projects'][project_id] = memories
    print(f"  ✓ {len(memories)} mémoires sauvegardées\n")

backup_file = Path.home() / f'.claude/mem0-backup-{datetime.now().strftime("%Y%m%d-%H%M%S")}.json'
with open(backup_file, 'w') as f:
    json.dump(backup, f, indent=2)

print(f"✓ Backup Mem0 sauvegardé: {backup_file}")
