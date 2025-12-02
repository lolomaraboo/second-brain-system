#!/usr/bin/env python3
"""Migration Mem0 vers structure hiérarchique"""
import json, requests, os, sys, time
from datetime import datetime

API_KEY = os.environ.get('MEM0_API_KEY')
BASE_URL = 'http://31.220.104.244:8081'
HEADERS = {}

MIGRATION_MAP = {
    'recording-studio-manager': 'dev--recording-studio-manager',
    'claude-code-champion': 'dev--claude-code-champion',
    'second-brain': 'dev--second-brain',
}

def get_all_memories(project_id):
    """Récupère TOUTES les mémoires (API VPS ne supporte pas pagination - ignore offset)."""
    # L'API VPS Mem0 ne supporte pas vraiment la pagination, elle retourne toujours les mêmes résultats
    # On fait un seul appel avec une limite très haute
    response = requests.get(f'{BASE_URL}/memory/{project_id}', headers=HEADERS,
                          params={'limit': 10000}, timeout=30)  # Limite très haute pour tout récupérer
    response.raise_for_status()
    data = response.json()

    if not data.get('success'):
        return []

    memories = data.get('memories', {}).get('results', [])
    print(f"  Récupéré: {len(memories)} mémoires pour '{project_id}'")

    return memories

def create_memory(project_id, content, metadata=None):
    payload = {
        'user_id': project_id,
        'content': content
    }
    if metadata:
        payload['metadata'] = metadata

    response = requests.post(f'{BASE_URL}/memory', headers=HEADERS, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()

def delete_memory(project_id, memory_id):
    response = requests.delete(f'{BASE_URL}/memory/{project_id}/{memory_id}', headers=HEADERS, timeout=30)
    response.raise_for_status()

def migrate_project(old_id, new_id, dry_run=True):
    print(f"\n{'='*60}")
    print(f"Migration: {old_id} → {new_id}")
    print(f"{'='*60}")

    memories = get_all_memories(old_id)
    if not memories:
        print(f"⚠️  Aucune mémoire pour {old_id}")
        return {'status': 'skipped', 'project': old_id}

    print(f"✓ {len(memories)} mémoires trouvées")

    if dry_run:
        print(f"\nDRY RUN - Migrerait:")
        for i, mem in enumerate(memories[:5], 1):
            print(f"  {i}. {mem['memory'][:80]}...")
        if len(memories) > 5:
            print(f"  ... et {len(memories) - 5} de plus")
        return {'status': 'dry_run', 'count': len(memories), 'project': old_id}

    # MIGRATION RÉELLE
    print(f"\n⚠️  MIGRATION RÉELLE")

    # Créer dans nouvelle location
    print(f"Création de {len(memories)} mémoires dans '{new_id}'...")
    created, failed = [], []

    for i, mem in enumerate(memories, 1):
        print(f"   [{i}/{len(memories)}] Création...", end=' ', flush=True)
        try:
            create_memory(new_id, mem['memory'], mem.get('metadata', {}))
            created.append(mem)
            print("✓")
        except Exception as e:
            failed.append(mem)
            print(f"✗ {str(e)[:50]}")
        time.sleep(0.2)

    if failed:
        print(f"\n✗ {len(failed)} échecs - anciennes mémoires conservées")
        return {'status': 'partial_failure', 'failed': len(failed), 'project': old_id}

    # Vérifier que toutes les mémoires sont bien créées
    print(f"\n✓ {len(created)} mémoires créées")
    print(f"Vérification dans nouvelle location...")
    new_memories = get_all_memories(new_id)

    if len(new_memories) != len(memories):
        print(f"✗ ERREUR: {len(new_memories)} trouvées vs {len(memories)} attendues!")
        print("Migration interrompue - anciennes mémoires conservées")
        return {'status': 'verification_failed', 'project': old_id}

    print(f"✓ Vérification OK: {len(new_memories)} mémoires")

    # Supprimer anciennes
    print(f"\nSuppression de {len(memories)} anciennes mémoires...")
    for i, mem in enumerate(memories, 1):
        print(f"   [{i}/{len(memories)}] Suppression...", end=' ')
        try:
            delete_memory(old_id, mem['id'])
            print("✓")
        except:
            print("✗")
        time.sleep(0.2)

    # Vérification finale
    old_check = get_all_memories(old_id)
    print(f"\n✓ Migration complète:")
    print(f"  - Ancien ID ({old_id}): {len(old_check)} mémoires")
    print(f"  - Nouveau ID ({new_id}): {len(new_memories)} mémoires")

    return {'status': 'success', 'created': len(created), 'verified': len(new_memories), 'project': old_id}

# Main
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--execute', action='store_true', help='Execute real migration (not dry run)')
parser.add_argument('--backup', type=str, help='Path to backup file (required for --execute)')
parser.add_argument('--project', type=str, help='Migrate only specific project')
args = parser.parse_args()

dry_run = not args.execute

print(f"{'='*60}")
print(f"Migration Mem0 Hiérarchique")
print(f"MODE: {'EXECUTE' if not dry_run else 'DRY RUN'}")
print(f"{'='*60}\n")

if not dry_run and not args.backup:
    print("✗ --backup requis pour execute")
    sys.exit(1)

# Filter projects if --project specified
projects_to_migrate = MIGRATION_MAP
if args.project:
    if args.project in MIGRATION_MAP:
        projects_to_migrate = {args.project: MIGRATION_MAP[args.project]}
    else:
        print(f"✗ Projet inconnu: {args.project}")
        print(f"Projets disponibles: {', '.join(MIGRATION_MAP.keys())}")
        sys.exit(1)

results = []
for old_id, new_id in projects_to_migrate.items():
    result = migrate_project(old_id, new_id, dry_run=dry_run)
    results.append(result)
    time.sleep(1)

print(f"\n{'='*60}")
print("RÉSUMÉ")
print(f"{'='*60}")
for result in results:
    project = result.get('project', 'unknown')
    status = result['status']
    count = result.get('count', result.get('verified', 0))
    print(f"{project}: {status} ({count} mémoires)")

if dry_run:
    print(f"\nPour exécuter: python3 {sys.argv[0]} --execute --backup ~/.claude/mem0-backup-*.json")
    print(f"Pour un projet: python3 {sys.argv[0]} --execute --backup ~/.claude/mem0-backup-*.json --project recording-studio-manager")
