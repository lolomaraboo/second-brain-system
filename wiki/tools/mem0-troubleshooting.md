# Mem0 Troubleshooting

**Contexte:** [[mem0-auto-sync-architecture]]

## Diagnostic rapide

### 1. Vérifier que tout fonctionne

```bash
# Worker running?
launchctl list | grep mem0

# VPS accessible?
curl http://31.220.104.244:8081/health

# Queue state?
cat ~/.claude/mem0_metrics.json

# Recent activity?
tail -20 ~/.claude/logs/mem0_worker.log
```

**Résultat attendu:**
```
53628	0	com.mem0.worker          # Worker PID
{"status":"ok"}                   # VPS health
{
  "vps_status": "healthy",
  "queue_size": 0,
  "dlq_size": 0,
  ...
}
[04:38:16] ✅ VPS healthy - processing queues...
```

## Problèmes courants

### Worker ne démarre pas

**Symptômes:**
- `launchctl list | grep mem0` retourne rien
- Pas de logs dans `~/.claude/logs/mem0_worker.log`

**Diagnostic:**
```bash
# Vérifier fichier plist existe
ls -l ~/Library/LaunchAgents/com.mem0.worker.plist

# Vérifier format XML valide
plutil ~/Library/LaunchAgents/com.mem0.worker.plist

# Vérifier errors launchd
tail -50 ~/Library/Logs/launchd.log
```

**Solutions:**
```bash
# Charger service
launchctl load ~/Library/LaunchAgents/com.mem0.worker.plist

# Si erreur "service already loaded"
launchctl unload ~/Library/LaunchAgents/com.mem0.worker.plist
launchctl load ~/Library/LaunchAgents/com.mem0.worker.plist

# Vérifier logs erreur
cat ~/.claude/logs/mem0_worker_error.log
```

### Worker crash en boucle

**Symptômes:**
- Worker redémarre constamment (nouveau PID toutes les 10s)
- Error log rempli d'exceptions Python

**Diagnostic:**
```bash
# Logs d'erreur
cat ~/.claude/logs/mem0_worker_error.log

# Tester worker manuellement
/usr/bin/python3 -u ~/scripts/mem0_queue_worker.py
```

**Solutions:**
- Vérifier syntaxe Python: `python3 -m py_compile ~/scripts/mem0_queue_worker.py`
- Vérifier permissions fichiers queue: `ls -l ~/.claude/mem0_*.json`
- Vérifier espace disque: `df -h ~`
- Restore backup si code corrompu: `cp ~/scripts/mem0_queue_worker.backup.py ~/scripts/mem0_queue_worker.py`

### VPS injoignable

**Symptômes:**
```
❌ VPS health check failed: Connection refused
❌ VPS unhealthy - waiting 30s...
```

**Diagnostic:**
```bash
# Ping VPS
ping 31.220.104.244

# Test port
nc -zv 31.220.104.244 8081

# Test HTTP
curl -v http://31.220.104.244:8081/health
```

**Solutions:**
- Si VPS vraiment down: Attendre recovery (worker retry auto)
- Si firewall local: Vérifier règles firewall macOS
- Si réseau: Vérifier connexion Internet (`ping 8.8.8.8`)
- Si VPS maintenance: Attendre (queue accumule, sync auto dès VPS up)

### Lock timeout persistant

**Symptômes:**
```
⚠️ Could not acquire lock (timeout). Queue might be busy.
```

**Diagnostic:**
```bash
# Worker running multiple times?
ps aux | grep mem0_queue_worker | grep -v grep

# Lock file bloqué?
ls -l ~/.claude/mem0_queue.lock

# Queue JSON corrompu?
cat ~/.claude/mem0_queue.json | python3 -m json.tool
```

**Solutions:**
```bash
# Tuer workers multiples
pkill -f mem0_queue_worker.py
launchctl unload ~/Library/LaunchAgents/com.mem0.worker.plist
launchctl load ~/Library/LaunchAgents/com.mem0.worker.plist

# Supprimer lock file stale
rm -f ~/.claude/mem0_queue.lock

# Réparer queue JSON corrompu
cp ~/.claude/mem0_queue.backup.json ~/.claude/mem0_queue.json
```

### DLQ qui grossit sans arrêt

**Symptômes:**
```json
{
  "dlq_size": 50,  // Augmente chaque cycle
  ...
}
```

**Diagnostic:**
```bash
# Inspecter DLQ
cat ~/.claude/mem0_queue_dlq.json

# Raison des échecs?
tail -100 ~/.claude/logs/mem0_worker.log | grep "Upload failed"

# VPS status?
cat ~/.claude/mem0_metrics.json | grep vps_status
```

**Solutions:**
- Si VPS down: Attendre recovery
- Si erreur upload spécifique: Vérifier logs VPS côté serveur
- Si contenu invalide: Inspecter `content` des items DLQ
- Voir [[mem0-dlq-management]] pour gestion avancée

### Mémoires ne se sauvent pas

**Symptômes:**
- `mem0_save()` retourne succès mais rien dans VPS
- Queue reste vide

**Diagnostic:**
```bash
# MCP server logs
cat ~/.claude/logs/mcp_servers.log | grep mem0

# Queue après mem0_save
cat ~/.claude/mem0_queue.json

# Emergency buffer utilisé?
cat ~/.claude/mem0_emergency.json 2>/dev/null || echo "No emergency buffer"
```

**Solutions:**
```bash
# Vérifier MCP server running
ps aux | grep mem0_mcp_server

# Restart Claude Code pour reload MCP server
# Vérifier permissions queue file
chmod 644 ~/.claude/mem0_queue.json
```

### Logs ne s'affichent pas

**Symptômes:**
- Worker running mais logs vides
- Ou logs en retard (buffer)

**Diagnostic:**
```bash
# Vérifier Python unbuffered dans plist
cat ~/Library/LaunchAgents/com.mem0.worker.plist | grep -A2 ProgramArguments
```

**Solution:**
Doit contenir `-u` flag:
```xml
<key>ProgramArguments</key>
<array>
    <string>/usr/bin/python3</string>
    <string>-u</string>  <!-- REQUIS -->
    <string>/Users/marabook_m1/scripts/mem0_queue_worker.py</string>
</array>
```

Si manquant:
```bash
# Éditer plist
nano ~/Library/LaunchAgents/com.mem0.worker.plist
# Ajouter <string>-u</string>

# Reload
launchctl unload ~/Library/LaunchAgents/com.mem0.worker.plist
launchctl load ~/Library/LaunchAgents/com.mem0.worker.plist
```

## Outils de diagnostic

### Health check complet

```bash
#!/bin/bash
# ~/scripts/mem0_health_check.sh

echo "=== Mem0 Health Check ==="
echo ""

echo "1. Worker Status:"
launchctl list | grep mem0 && echo "✅ Running" || echo "❌ Not running"
echo ""

echo "2. VPS Status:"
curl -s http://31.220.104.244:8081/health && echo " ✅" || echo "❌ Unreachable"
echo ""

echo "3. Metrics:"
cat ~/.claude/mem0_metrics.json
echo ""

echo "4. Queue State:"
cat ~/.claude/mem0_queue.json | python3 -c "
import json, sys
q = json.load(sys.stdin)
print(f'Pending: {len(q[\"queue\"])}')
print(f'Failed: {len(q[\"failed\"])}')
print(f'Total synced: {q[\"stats\"][\"total_synced\"]}')
"
echo ""

echo "5. DLQ State:"
cat ~/.claude/mem0_queue_dlq.json | python3 -c "
import json, sys
dlq = json.load(sys.stdin)
print(f'Items: {len(dlq[\"items\"])}')
"
echo ""

echo "6. Recent Activity (last 10 lines):"
tail -10 ~/.claude/logs/mem0_worker.log
```

### Reset complet (dernier recours)

⚠️ **Perte des queues en attente** - Sauvegarder d'abord.

```bash
#!/bin/bash
# ~/scripts/mem0_full_reset.sh

echo "⚠️ Mem0 Full Reset - Queues will be lost"
read -p "Continue? (yes/no): " confirm
[ "$confirm" != "yes" ] && exit 1

# Stop worker
launchctl unload ~/Library/LaunchAgents/com.mem0.worker.plist

# Backup
cp ~/.claude/mem0_queue.json ~/.claude/mem0_queue.backup.$(date +%s).json
cp ~/.claude/mem0_queue_dlq.json ~/.claude/mem0_queue_dlq.backup.$(date +%s).json

# Clear queues
echo '{"queue":[],"last_100":[],"failed":[],"stats":{"total_queued":0,"total_synced":0,"total_failed":0,"last_sync":null}}' > ~/.claude/mem0_queue.json
echo '{"items":[],"last_update":"'$(date -Iseconds)'"}' > ~/.claude/mem0_queue_dlq.json

# Clear logs
echo "" > ~/.claude/logs/mem0_worker.log
echo "" > ~/.claude/logs/mem0_worker_error.log

# Remove lock
rm -f ~/.claude/mem0_queue.lock

# Restart worker
launchctl load ~/Library/LaunchAgents/com.mem0.worker.plist

echo "✅ Reset complete - Worker restarted"
```

## Monitoring proactif

### Dashboard temps réel

```bash
# ~/scripts/mem0_monitor.sh
#!/bin/bash
while true; do
    clear
    echo "=== Mem0 Monitor ($(date +%H:%M:%S)) ==="
    echo ""
    cat ~/.claude/mem0_metrics.json | python3 -c "
import json, sys
m = json.load(sys.stdin)
print(f'VPS: {m[\"vps_status\"]}')
print(f'Queue: {m[\"queue_size\"]} pending')
print(f'DLQ: {m[\"dlq_size\"]} items')
print(f'Synced: {m[\"total_synced\"]}/{m[\"total_queued\"]}')
"
    echo ""
    echo "Last 5 log lines:"
    tail -5 ~/.claude/logs/mem0_worker.log
    sleep 5
done
```

### Cron check quotidien

```bash
# Vérifier DLQ > 5 items ou VPS down > 1h
0 9 * * * ~/scripts/mem0_daily_check.sh
```

## Références

- [[mem0-auto-sync-architecture]] - Architecture complète
- [[mem0-dlq-management]] - Gestion DLQ
- Logs: `~/.claude/logs/mem0_worker.log`
- Config: `~/Library/LaunchAgents/com.mem0.worker.plist`
- Backups: `~/.claude/mem0_*.backup.*`
