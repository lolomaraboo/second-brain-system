# Mem0 Worker Manuel

**🗄️ DOCUMENT OBSOLÈTE**

**Remplacé par:** [[mem0-auto-sync-architecture]] (depuis 2025-11-30)

**Raison:** Ancien système cron-based avec intervention manuelle. Mem0 Auto-Sync implémente worker always-running, health checks VPS, DLQ, et retry infini.

---

## Archive (ancien système)

**Statut:** ⚠️ Solution PROVISOIRE (amélioration requise)
**Date:** 2025-11-30

## Problème

Worker cron synchronise toutes les 10 minutes. Lors création masse de mémoires (ex: 80+ mémoires), queue devient longue et peut causer lock timeout.

## Solution Provisoire

Déclencher worker manuellement toutes les 20 mémoires au lieu d'attendre cron.

### Commande

```bash
/usr/bin/python3 /Users/marabook_m1/scripts/mem0_queue_worker.py
```

### Vérifier état queue avant

```bash
cat ~/.claude/mem0_queue.json | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'Queue: {len(d[\"queue\"])} pending')"
```

### Vérifier résultat après

Attendre 10-30s puis:
```bash
tail -20 ~/.claude/logs/mem0_worker.log
```

Chercher:
```
✨ Worker done:
   Queue: 0 pending
   Failed: 0 failed
   Total synced: XXX
```

## Stratégie SESSION 2-7

Lors création mémoires en masse:

1. **Créer par batchs de ~20 mémoires**
2. **Après chaque batch:**
   ```bash
   /usr/bin/python3 ~/scripts/mem0_queue_worker.py 2>&1 | tail -10
   ```
3. **Attendre confirmation** "Worker done: Queue: 0 pending"
4. **Continuer** batch suivant

### Exemple SESSION 2

```bash
# Batch 1 (20 mémoires)
# ... création mémoires ...
/usr/bin/python3 ~/scripts/mem0_queue_worker.py

# Batch 2 (20 mémoires)
# ... création mémoires ...
/usr/bin/python3 ~/scripts/mem0_queue_worker.py

# Etc.
```

## Avantages Solution Manuelle

✅ Évite queue > 30 mémoires
✅ Évite lock timeout
✅ Feedback immédiat sur sync
✅ Détection rapide erreurs sync

## Inconvénients

❌ **Non viable long terme** - Intervention manuelle systématique
❌ Risque d'oubli entre batchs
❌ Pas automatique
❌ Dépend discipline développeur

## Solution Long Terme (TODO)

### Option 1: Trigger automatique dans MCP server

Modifier `mem0_mcp_server.py`:

```python
async def mem0_save(...):
    # Ajouter mémoire à queue
    queue.append(memory)

    # Trigger sync auto si queue > seuil
    if len(queue) >= 20:
        subprocess.Popen([
            '/usr/bin/python3',
            '/Users/marabook_m1/scripts/mem0_queue_worker.py'
        ])
```

### Option 2: Watcher continu

Script qui surveille taille queue et déclenche worker:

```python
# ~/scripts/mem0_queue_watcher.py
import time, json, subprocess

QUEUE_FILE = "~/.claude/mem0_queue.json"
THRESHOLD = 20

while True:
    with open(QUEUE_FILE) as f:
        queue_size = len(json.load(f)['queue'])

    if queue_size >= THRESHOLD:
        subprocess.run(['/usr/bin/python3',
                       '~/scripts/mem0_queue_worker.py'])

    time.sleep(30)  # Check toutes les 30s
```

Lancer au boot:
```bash
# ~/Library/LaunchAgents/com.mem0.queuewatcher.plist
```

### Option 3: Réduire fréquence cron

```bash
# Au lieu de */10 (toutes les 10 min)
# Toutes les 2 minutes:
*/2 * * * * /usr/bin/python3 ~/scripts/mem0_queue_worker.py
```

Mais risque de conflicts lock si worker lent.

## Recommandation

**Priorité:** Moyenne
**Effort:** 2-3h développement + tests
**Impact:** Haute (qualité de vie)

Implémenter **Option 1** (trigger auto dans MCP server):
- Moins invasif
- Pas de nouveau process
- Contrôle fin du seuil
- Testable unitairement

## Références

- [[../troubleshooting/mem0-lock-timeout]] - Problème lock
- Script worker: `~/scripts/mem0_queue_worker.py`
- MCP server: `~/scripts/mem0_mcp_server.py`
- Cron actuel: `*/10 * * * *`
