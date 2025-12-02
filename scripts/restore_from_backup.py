#!/usr/bin/env python3
"""Restaure les mémoires depuis un backup JSON"""
import json, requests, sys, time

BASE_URL = 'http://31.220.104.244:8081'

def create_memory(project_id, content):
    payload = {'user_id': project_id, 'content': content}
    response = requests.post(f'{BASE_URL}/memory', json=payload, timeout=30)
    response.raise_for_status()
    return response.json()

if len(sys.argv) < 4:
    print("Usage: python3 restore_from_backup.py <backup.json> <source_project> <target_project>")
    sys.exit(1)

backup_file = sys.argv[1]
source_project = sys.argv[2]
target_project = sys.argv[3]

print(f"📦 Chargement backup: {backup_file}")
with open(backup_file, 'r') as f:
    backup_data = json.load(f)

# Extraire le dict des projets
projects_dict = backup_data.get('projects', {})

# Accéder directement au projet (la valeur est la liste des mémoires)
memories_to_restore = projects_dict.get(source_project, [])

if not memories_to_restore:
    print(f"✗ Projet '{source_project}' non trouvé dans backup")
    sys.exit(1)

print(f"✅ Trouvé {len(memories_to_restore)} mémoires pour '{source_project}'")
print(f"🔄 Restauration vers '{target_project}'...\n")

created, failed = [], []
for i, mem in enumerate(memories_to_restore, 1):
    # Les mémoires sont des strings directement
    content = mem if isinstance(mem, str) else mem.get('memory', '')
    print(f"   [{i}/{len(memories_to_restore)}] {content[:50]}...", end=' ', flush=True)
    try:
        create_memory(target_project, content)
        created.append(mem)
        print("✓")
    except Exception as e:
        failed.append(mem)
        print(f"✗ {str(e)[:30]}")
    time.sleep(0.05)  # Rate limiting

print(f"\n{'='*60}")
print(f"✅ Restauration terminée")
print(f"   Créées: {len(created)}")
print(f"   Échecs: {len(failed)}")
print(f"{'='*60}")
