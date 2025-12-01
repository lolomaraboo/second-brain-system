# Mem0 DLQ Management

**Contexte:** [[mem0-auto-sync-architecture]]

## Qu'est-ce que la DLQ?

**Dead Letter Queue** = File d'attente pour items échoués avec retry infini et exponential backoff.

## Quand un item va en DLQ?

Un item est déplacé vers la DLQ après **5 échecs consécutifs** de synchronisation vers le VPS.

## Comment fonctionne le retry?

### Exponential Backoff

```python
delay = min(2^retry_count × 30, 3600)
```

**Exemples:**
- Retry 1: 60s (1 min)
- Retry 2: 120s (2 min)
- Retry 3: 240s (4 min)
- Retry 4: 480s (8 min)
- Retry 5: 960s (16 min)
- Retry 6: 1920s (32 min)
- Retry 7+: 3600s (1h max)

### Retry Infini

⚠️ **Pas d'archivage** - Les items restent en DLQ et retentent indéfiniment jusqu'au succès.

**Garantie:** Eventual consistency absolue.

## Inspecter la DLQ

### Fichier DLQ

```bash
cat ~/.claude/mem0_queue_dlq.json
```

**Format:**
```json
{
  "items": [
    {
      "id": "uuid-abc123...",
      "project_id": "recording-studio-manager",
      "content": "Mémoire à synchroniser",
      "timestamp": 1732942000,
      "retry_count": 3,
      "last_attempt": 1732945600,
      "moved_to_dlq_at": 1732943000
    }
  ],
  "last_update": "2025-11-30T04:38:18"
}
```

### Via Metrics

```bash
cat ~/.claude/mem0_metrics.json | python3 -c "import json,sys; print(f'DLQ size: {json.load(sys.stdin)[\"dlq_size\"]}')"
```

### Via Worker Logs

```bash
tail -100 ~/.claude/logs/mem0_worker.log | grep DLQ
```

**Chercher:**
- `📋 Moved to DLQ:` - Item déplacé vers DLQ
- `✅ DLQ recovered:` - Item récupéré avec succès
- `⏳ DLQ retry X:` - Tentative de retry
- `⏸️ Waiting backoff:` - En attente de backoff

## Diagnostiquer un item bloqué

### Vérifier l'item

```bash
cat ~/.claude/mem0_queue_dlq.json | python3 -c "
import json, sys, time
dlq = json.load(sys.stdin)
for item in dlq['items']:
    age = time.time() - item.get('last_attempt', 0)
    print(f'ID: {item[\"id\"][:8]}')
    print(f'Project: {item[\"project_id\"]}')
    print(f'Retries: {item.get(\"retry_count\", 0)}')
    print(f'Last attempt: {int(age)}s ago')
    print('---')
"
```

### Causes possibles

1. **VPS down prolongé**
   - Vérifier: `cat ~/.claude/mem0_metrics.json | grep vps_status`
   - Si "down": Attendre VPS recovery

2. **Problème réseau local**
   - Tester: `curl http://31.220.104.244:8081/health`
   - Doit retourner 200 OK

3. **Contenu invalide**
   - Vérifier le champ `content` de l'item
   - Possible caractères non-UTF8 ou JSON malformé

4. **VPS rejette l'item**
   - Vérifier logs VPS côté serveur
   - Possible project_id invalide ou quota dépassé

## Forcer retry immédiat (debug)

⚠️ **Pour debug seulement** - Le worker retry automatiquement.

```bash
# Supprimer le backoff en réinitialisant last_attempt
python3 << 'EOF'
import json
from pathlib import Path

dlq_file = Path.home() / ".claude/mem0_queue_dlq.json"
with open(dlq_file, 'r') as f:
    dlq = json.load(f)

# Reset last_attempt pour tous les items
for item in dlq['items']:
    item['last_attempt'] = 0

with open(dlq_file, 'w') as f:
    json.dump(dlq, f, indent=2)

print(f"Reset {len(dlq['items'])} items - retry au prochain cycle")
EOF
```

## Supprimer un item (cas extrême)

⚠️ **Perte de mémoire définitive** - À utiliser en dernier recours.

```bash
# 1. Sauvegarder d'abord
cp ~/.claude/mem0_queue_dlq.json ~/.claude/mem0_queue_dlq.backup.json

# 2. Éditer et supprimer l'item manuellement
nano ~/.claude/mem0_queue_dlq.json

# 3. Vérifier format JSON valide
cat ~/.claude/mem0_queue_dlq.json | python3 -m json.tool
```

## Statistiques DLQ

### Items par projet

```bash
cat ~/.claude/mem0_queue_dlq.json | python3 -c "
import json, sys
from collections import Counter
dlq = json.load(sys.stdin)
projects = Counter(item['project_id'] for item in dlq['items'])
for project, count in projects.most_common():
    print(f'{project}: {count}')
"
```

### Distribution retry counts

```bash
cat ~/.claude/mem0_queue_dlq.json | python3 -c "
import json, sys
from collections import Counter
dlq = json.load(sys.stdin)
retries = Counter(item.get('retry_count', 0) for item in dlq['items'])
for count, freq in sorted(retries.items()):
    print(f'{count} retries: {freq} items')
"
```

## Monitoring DLQ

### Dashboard simple

```bash
# ~/scripts/mem0_dlq_dashboard.sh
#!/bin/bash
clear
echo "=== Mem0 DLQ Dashboard ==="
echo ""
echo "VPS Status: $(cat ~/.claude/mem0_metrics.json | python3 -c "import json,sys; print(json.load(sys.stdin)['vps_status'])")"
echo "DLQ Size: $(cat ~/.claude/mem0_metrics.json | python3 -c "import json,sys; print(json.load(sys.stdin)['dlq_size'])")"
echo ""
echo "Recent DLQ activity:"
tail -20 ~/.claude/logs/mem0_worker.log | grep -E "(DLQ|Moved to DLQ)"
```

### Alertes (optionnel)

Si DLQ size > threshold pendant X temps, envoyer alerte:

```bash
# Cron job check DLQ size
*/30 * * * * [ $(cat ~/.claude/mem0_metrics.json | python3 -c "import json,sys; print(json.load(sys.stdin)['dlq_size'])") -gt 10 ] && echo "⚠️ DLQ > 10 items" | mail -s "Mem0 DLQ Alert" user@example.com
```

## Best Practices

✅ **Laisser le worker gérer** - Pas d'intervention manuelle sauf debug
✅ **Monitor metrics** - Vérifier dlq_size régulièrement
✅ **Investiguer si dlq_size > 5** - Problème récurrent possible
⚠️ **Ne jamais supprimer items** - Perte de mémoire définitive
⚠️ **Ne pas modifier retry_count** - Casse le backoff

## Références

- [[mem0-auto-sync-architecture]] - Architecture complète
- [[mem0-troubleshooting]] - Guide troubleshooting
- Code: `~/scripts/mem0_queue_worker.py` (process_dlq function)
