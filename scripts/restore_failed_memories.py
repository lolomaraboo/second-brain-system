#!/usr/bin/env python3
"""Restaure uniquement les mémoires échouées depuis les logs"""
import json, requests, sys, time

BASE_URL = 'http://31.220.104.244:8081'

def create_memory(project_id, content):
    payload = {'user_id': project_id, 'content': content}
    response = requests.post(f'{BASE_URL}/memory', json=payload, timeout=30)
    response.raise_for_status()
    return response.json()

if len(sys.argv) < 4:
    print("Usage: python3 restore_failed_memories.py <backup.json> <source_project> <target_project> <failed_positions>")
    print("Example: python3 restore_failed_memories.py backup.json recording-studio-manager dev--recording-studio-manager 43,44,45,46,47")
    sys.exit(1)

backup_file = sys.argv[1]
source_project = sys.argv[2]
target_project = sys.argv[3]
failed_positions = [int(x) for x in sys.argv[4].split(',')]

print(f"📦 Chargement backup: {backup_file}")
with open(backup_file, 'r') as f:
    backup_data = json.load(f)

projects_dict = backup_data.get('projects', {})
all_memories = projects_dict.get(source_project, [])

if not all_memories:
    print(f"✗ Projet '{source_project}' non trouvé dans backup")
    sys.exit(1)

print(f"✅ Trouvé {len(all_memories)} mémoires totales pour '{source_project}'")
print(f"🔄 Restauration de {len(failed_positions)} mémoires échouées vers '{target_project}'...\n")

created, failed = [], []
for pos in failed_positions:
    idx = pos - 1  # Convert to 0-based index
    if idx >= len(all_memories):
        print(f"   [{pos}] SKIP (position invalide)")
        continue

    mem = all_memories[idx]
    content = mem['memory'] if isinstance(mem, dict) else mem
    print(f"   [{pos}] {content[:60]}...", end=' ', flush=True)

    try:
        create_memory(target_project, content)
        created.append(pos)
        print("✓")
    except Exception as e:
        failed.append(pos)
        print(f"✗ {str(e)[:30]}")

    time.sleep(0.1)  # Rate limiting

print(f"\n{'='*60}")
print(f"✅ Restauration terminée")
print(f"   Créées: {len(created)}")
print(f"   Échecs: {len(failed)}")
if failed:
    print(f"   Positions échouées: {','.join(map(str, failed))}")
print(f"{'='*60}")
