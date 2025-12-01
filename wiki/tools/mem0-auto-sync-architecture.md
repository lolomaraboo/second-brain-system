# Mem0 Auto-Sync - Architecture

**Statut:** ✅ PRODUCTION (depuis 2025-11-30)
**Remplace:** [[mem0-worker-manual]] (cron-based)

## Vue d'ensemble

Système de synchronisation automatique Mem0 avec worker always-running, health checks VPS, Dead Letter Queue (DLQ), et retry infini avec exponential backoff.

## Architecture

```
┌─────────────────┐
│  Claude Code    │
│   (MCP client)  │
└────────┬────────┘
         │ mem0_save()
         ▼
┌─────────────────────────────────────────────────┐
│  MCP Server (mem0_mcp_server.py)                │
│  - Lock timeout: 30s                            │
│  - Emergency buffer fallback si lock fail       │
└────────┬───────────────────────┬────────────────┘
         │ success               │ lock timeout
         │ (lock acquired)       │ (after 30s)
         ▼                       ▼
┌─────────────────────┐   ┌──────────────────────┐
│ mem0_queue.json     │   │ mem0_emergency.json  │
│ (queue normale)     │   │ (append-only)        │
│ - Pending items     │   │ - No lock needed     │
│ - Last 100 synced   │   │ - Zero loss guarantee│
│ - Stats             │   └──────────────────────┘
└─────────┬───────────┘
          │
          ▼
┌──────────────────────────────────────────────────┐
│  Worker (mem0_queue_worker.py)                   │
│  - Always running (launchd service)              │
│  - Health check every 30s                        │
│  - Process emergency buffer first                │
│  - Process DLQ second, then queue                │
│  - Auto-retry infinite with backoff              │
│  - Auto-backup before modifications              │
└────────┬────────────────────────┬────────────────┘
         │                        │
         │ success                │ 5 failures
         ▼                        ▼
┌────────────────┐      ┌──────────────────────────┐
│   VPS Mem0     │      │  DLQ (retry ∞)           │
│ 31.220.104.244 │      │  - Backoff: 2^n×30s      │
│    :8081       │      │  - Max: 1 hour           │
└────────────────┘      │  - Auto-backup on move   │
                        └──────────────────────────┘
```

## Composants

### 1. MCP Server (`mem0_mcp_server.py`)

**Rôle:** Interface entre Claude Code et queue locale

**Améliorations Auto-Sync:**
- Lock timeout augmenté: 5s → 30s
- Emergency buffer si lock fail (append-only, no lock)
- Pas de perte de mémoire garantie

**Configuration:**
```python
LOCK_TIMEOUT = 30  # seconds
EMERGENCY_BUFFER = "~/.claude/mem0_emergency.json"
```

**Logique emergency buffer:**
```python
def add_to_queue(project_id: str, content: str) -> dict:
    with open(LOCK_FILE, 'w') as lock:
        if not acquire_lock_with_timeout(lock, LOCK_TIMEOUT):
            # Lock timeout → emergency buffer
            print("⚠️  Queue lock timeout - using emergency buffer", file=sys.stderr)
            return emergency_queue_append(project_id, content)

        # Lock OK → queue normale
        queue = load_queue()
        entry = create_entry(project_id, content)
        queue["queue"].append(entry)
        save_queue(queue)
        return entry

def emergency_queue_append(project_id: str, content: str) -> dict:
    """Append to emergency buffer - no lock needed, append-only"""
    entry = {
        "id": str(uuid.uuid4()),
        "project_id": project_id,
        "content": content,
        "timestamp": int(datetime.now().timestamp()),
        "retries": 0,
        "emergency": True
    }

    # Append-only: safe for concurrent writes
    with open(EMERGENCY_BUFFER, 'a') as f:
        f.write(json.dumps(entry) + '\n')

    return entry
```

### 2. Worker (`mem0_queue_worker.py`)

**Rôle:** Sync background continu queue → VPS

**Mode:** Always-running (launchd service)

**Cycle (30s):**
1. Health check VPS (`GET /health`)
2. Si VPS healthy:
   - Process DLQ (priority)
   - Process queue normale
3. Update metrics
4. Sleep 30s

**Configuration:**
```python
HEALTH_CHECK_INTERVAL = 30  # seconds
MAX_BACKOFF = 3600  # 1 hour
DLQ_THRESHOLD = 5   # retries before DLQ
LOCK_TIMEOUT = 30   # seconds
```

### 3. Dead Letter Queue (DLQ)

**Rôle:** Retry infini pour items échoués

**Fichier:** `~/.claude/mem0_queue_dlq.json`

**Logique:**
- Item échoue 5 fois → déplacé vers DLQ
- DLQ retry avec exponential backoff
- Backoff: `min(2^retry_count × 30s, 3600s)`
- Retry infini (pas d'archivage)

**Format:**
```json
{
  "items": [
    {
      "id": "uuid",
      "project_id": "second-brain",
      "content": "...",
      "retry_count": 3,
      "last_attempt": 1732942000
    }
  ],
  "last_update": "2025-11-30T04:38:18"
}
```

### 4. Emergency Buffer (`mem0_emergency.json`)

**Rôle:** Garantir zéro perte de mémoire en cas de lock timeout

**Fichier:** `~/.claude/mem0_emergency.json`

**Déclenchement:**
- MCP server tente d'acquérir lock sur queue
- Si lock échoue après 30s (timeout)
- → Append vers emergency buffer au lieu de bloquer

**Format:**
```json
{"id": "uuid", "project_id": "...", "content": "...", "timestamp": 123, "retries": 0, "emergency": true}
{"id": "uuid", "project_id": "...", "content": "...", "timestamp": 124, "retries": 0, "emergency": true}
```

**Caractéristiques:**
- Append-only (une ligne JSON par entrée)
- Pas de lock requis (safe pour concurrent writes)
- Traité en priorité par worker au prochain cycle

**Garantie:**
- Même si queue bloquée → aucune perte de mémoire
- Eventual consistency garantie

### 5. Metrics (`mem0_metrics.json`)

**Rôle:** Monitoring temps réel

**Update:** Chaque cycle (30s)

**Format:**
```json
{
  "last_update": "2025-11-30T04:38:50",
  "vps_status": "healthy",
  "queue_size": 0,
  "dlq_size": 0,
  "total_synced": 345,
  "total_queued": 345
}
```

### 6. Backups Automatiques

**Fichiers:**
- `~/.claude/mem0_queue_backup.json` - Backup queue
- `~/.claude/mem0_queue_dlq.backup.json` - Backup DLQ

**Création:**
- Avant chaque modification par worker
- Un seul backup (écrase précédent)

**Restauration (si queue corrompue):**
```bash
# 1. Arrêter worker
launchctl stop com.mem0.worker

# 2. Restaurer backup
cp ~/.claude/mem0_queue_backup.json ~/.claude/mem0_queue.json

# 3. Redémarrer worker
launchctl start com.mem0.worker
```

## Launchd Service

**Fichier:** `~/Library/LaunchAgents/com.mem0.worker.plist`

**Configuration:**
- Auto-start au boot (`RunAtLoad`)
- Auto-restart si crash (`KeepAlive`)
- Throttle restart: 10s
- Python unbuffered (`-u`) pour logs temps réel

**Commandes:**
```bash
# Status
launchctl list | grep mem0

# Restart
launchctl unload ~/Library/LaunchAgents/com.mem0.worker.plist
launchctl load ~/Library/LaunchAgents/com.mem0.worker.plist

# Logs
tail -f ~/.claude/logs/mem0_worker.log
```

## Flux de données

### Création mémoire

```
1. Claude Code appelle mem0_save(project_id, content)
2. MCP server acquiert lock (timeout 30s)
3. Si lock OK: append to queue
4. Si lock FAIL: append to emergency buffer
5. Retourne succès immédiat (queue asynchrone)
```

### Synchronisation (cycle 30s)

```
1. Worker: GET VPS /health
2. Si VPS down: skip processing, wait 30s
3. Si VPS up:
   a. Process emergency buffer (PRIORITÉ 1)
      - Lire mem0_emergency.json ligne par ligne
      - Chaque ligne → ajouter à queue normale
      - Vider emergency buffer après traitement
   b. Process DLQ (PRIORITÉ 2 - items anciens)
      - Vérifier backoff elapsed
      - Retry upload
      - Si succès: remove from DLQ
      - Si échec: increment retry_count, update last_attempt
   c. Process queue normale (PRIORITÉ 3)
      - Créer backup avant modification
      - Retry upload
      - Si succès: remove, increment total_synced
      - Si échec 5x: move to DLQ (avec backup DLQ)
4. Update metrics
5. Sleep 30s
```

## Avantages vs ancien système

| Critère | Ancien (cron) | Auto-Sync |
|---------|---------------|-----------|
| Latence sync | 0-10 min | 0-30s |
| VPS down handling | ❌ Perte mémoires | ✅ Queue + retry |
| Lock timeout | 5s (insuffisant) | 30s + emergency buffer |
| Retry | 3 max | ∞ avec backoff |
| Monitoring | ❌ Aucun | ✅ Metrics temps réel |
| Intervention manuelle | ⚠️ Requise (batches) | ✅ Aucune |

## Monitoring

### Vérifier état système

**Métriques temps réel:**
```bash
cat ~/.claude/mem0_metrics.json
```

**Output:**
```json
{
  "last_update": "2025-12-01T13:05:04",
  "vps_status": "healthy",
  "queue_size": 0,
  "dlq_size": 0,
  "total_synced": 370,
  "total_queued": 370
}
```

**Vérifier emergency buffer:**
```bash
wc -l ~/.claude/mem0_emergency.json 2>/dev/null || echo "Empty"
```

**Logs worker:**
```bash
tail -f ~/.claude/logs/mem0_worker.log
```

**Status service:**
```bash
launchctl list | grep mem0
# Output: 54218	0	com.mem0.worker (PID 54218, running)
```

### Dashboard rapide

```bash
#!/bin/bash
# ~/scripts/mem0_status.sh

echo "=== Mem0 Status Dashboard ==="
echo ""
echo "Service:"
launchctl list | grep mem0 || echo "  ❌ Worker not running"
echo ""
echo "Metrics:"
cat ~/.claude/mem0_metrics.json | python3 -c "
import json, sys
m = json.load(sys.stdin)
print(f'  VPS: {m[\"vps_status\"]}')
print(f'  Queue: {m[\"queue_size\"]} pending')
print(f'  DLQ: {m[\"dlq_size\"]} items')
print(f'  Synced: {m[\"total_synced\"]}/{m[\"total_queued\"]}')
"
echo ""
echo "Emergency Buffer:"
wc -l ~/.claude/mem0_emergency.json 2>/dev/null | awk '{print "  " $1 " entries"}' || echo "  0 entries"
echo ""
echo "Last 5 worker logs:"
tail -5 ~/.claude/logs/mem0_worker.log | sed 's/^/  /'
```

## Garanties

✅ **Zéro perte de mémoire** (emergency buffer + backups)
✅ **Eventual consistency** (retry infini)
✅ **Resilience VPS down** (health checks)
✅ **Performance** (sync 30s max)
✅ **Monitoring** (metrics temps réel)
✅ **Recovery** (backups automatiques)

## Fichiers système

**Queue et buffers:**
- `~/.claude/mem0_queue.json` - Queue principale
- `~/.claude/mem0_queue_dlq.json` - Dead Letter Queue
- `~/.claude/mem0_emergency.json` - Emergency buffer
- `~/.claude/mem0_metrics.json` - Métriques temps réel

**Backups:**
- `~/.claude/mem0_queue_backup.json` - Backup queue
- `~/.claude/mem0_queue_dlq.backup.json` - Backup DLQ

**Logs:**
- `~/.claude/logs/mem0_worker.log` - Logs worker
- `~/.claude/logs/mem0_worker_error.log` - Logs erreurs

**Configuration:**
- `<workspace>/.mcp.json` - Config MCP server
- `~/Library/LaunchAgents/com.mem0.worker.plist` - Service launchd

**Scripts:**
- `~/scripts/mem0_mcp_server.py` - MCP server
- `~/scripts/mem0_queue_worker.py` - Worker

## Références

- [[mem0-dlq-management]] - Gestion DLQ
- [[mem0-troubleshooting]] - Guide troubleshooting
- Code: `~/scripts/mem0_queue_worker.py`
- Code: `~/scripts/mem0_mcp_server.py`
- Service: `~/Library/LaunchAgents/com.mem0.worker.plist`
