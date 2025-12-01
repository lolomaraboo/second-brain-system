# Mem0 Lock Timeout / Fausse Alerte VPS

**Problème:** Lock file orphelin cause fausse alerte "VPS inaccessible"
**Date:** 2025-11-30
**Statut:** ✅ Résolu

## Symptômes

- Message d'erreur: `Could not acquire queue lock (timeout). Queue might be busy.`
- Alerte: "VPS semble inaccessible depuis X heures"
- API Mem0 fonctionne (test `mem0_health` retourne HEALTHY)
- Worker cron a synchronisé avec succès mais lock file reste

## Diagnostic

### 1. Vérifier état API
```bash
curl -s http://31.220.104.244:8080/health
# ou
mem0_health
```
Si API répond → VPS fonctionne, problème est ailleurs.

### 2. Vérifier lock file
```bash
ls -la ~/.claude/mem0_queue.lock
stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" ~/.claude/mem0_queue.lock
```

### 3. Vérifier processus détenteur lock
```bash
lsof ~/.claude/mem0_queue.lock
```
Si "Aucun processus" → Lock orphelin.

### 4. Vérifier logs worker
```bash
tail -30 ~/.claude/logs/mem0_worker.log
```
Si dernier log montre "Worker done: Queue: 0 pending" → Sync réussie, lock oublié.

## Cause Racine

Worker cron synchronise mémoires avec succès mais ne supprime pas toujours le lock file après terminaison. Probablement:
- Interruption worker avant cleanup
- Exception non catchée
- Race condition multi-instances

## Solution Immédiate

```bash
# 1. Vérifier aucun worker actif
ps aux | grep mem0_queue_worker

# 2. Supprimer lock orphelin
rm -f ~/.claude/mem0_queue.lock

# 3. Vérifier queue
cat ~/.claude/mem0_queue.json | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'Queue: {len(d[\"queue\"])} pending')"

# 4. Déclencher sync manuelle si queue non vide
/usr/bin/python3 ~/scripts/mem0_queue_worker.py
```

## Solution Long Terme (TODO)

### Amélioration 1: Cleanup robuste
Modifier `mem0_queue_worker.py`:
```python
import atexit

def cleanup_lock():
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)

atexit.register(cleanup_lock)
```

### Amélioration 2: Lock timeout
Ajouter timeout au lock (ex: 5 min max):
```python
lock_age = time.time() - os.path.getmtime(LOCK_FILE)
if lock_age > 300:  # 5 minutes
    logger.warning("Lock file stale, removing")
    os.remove(LOCK_FILE)
```

### Amélioration 3: PID check
Stocker PID dans lock, vérifier si processus existe:
```python
with open(LOCK_FILE, 'r') as f:
    pid = int(f.read())
if not psutil.pid_exists(pid):
    os.remove(LOCK_FILE)
```

## Prévention

- **Monitoring:** Alerte si lock file > 10 min
- **Cron cleanup:** Script quotidien supprime locks > 1h
- **Health check:** Inclure check lock file dans `mem0_queue_status`

## Incident 2025-11-30

**Contexte:** SESSION 1 création 80 mémoires ultra-granulaires

**Timeline:**
- 01:23 - Worker sync 64 mémoires, lock file créé
- 01:23-04:30 - Lock orphelin, fausses alertes
- 04:30 - Diagnostic, lock supprimé
- 04:40 - Worker manuel, 36 nouvelles mémoires synchronisées
- Résultat: 103 mémoires totales sur VPS ✅

**Leçon:** Toujours vérifier API health avant diagnostiquer "VPS down"

## Références

- [[../tools/mem0-worker-manual]] - Worker manuel
- Script: `~/scripts/mem0_queue_worker.py`
- Lock file: `~/.claude/mem0_queue.lock`
- Queue file: `~/.claude/mem0_queue.json`
