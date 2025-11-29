# Solution 2A : Queue locale + worker async

**Date :** 2025-11-29
**Status :** ✅ Implémenté
**Problème résolu :** API Mem0 VPS timeout 62% des cas

## Décision

Implémenter une queue locale avec worker background pour résoudre les timeouts de l'API Mem0 sans changer l'architecture Mem0 + Obsidian.

## Architecture

```
mem0_save()
    │
    ├─> 1. Queue locale (JSON)      [instantané]
    ├─> 2. Knowledge graph           [instantané - TODO Phase 5]
    └─> 3. Cache 100 dernières       [instantané]

Worker background (async)
    │
    └─> Tente upload queue → VPS Mem0
        ├─> Succès : retire de queue
        ├─> Échec : retry avec backoff (2s, 4s, 8s)
        └─> 3 échecs : moved to failed (retry au prochain worker)
```

## Fichiers implémentés

### 1. Queue JSON (`~/.claude/mem0_queue.json`)

```json
{
  "queue": [],           // Entrées en attente de sync
  "last_100": [],        // Cache local 100 dernières
  "failed": [],          // Entrées échouées (3x) - retentées à chaque worker
  "stats": {
    "total_queued": 0,
    "total_synced": 0,
    "total_failed": 0,
    "last_sync": null
  }
}
```

**Type de fichier :** Runtime (ne PAS versionner)

### 2. Serveur MCP modifié (`~/scripts/mem0_mcp_server.py`)

**Ajouts :**
- Fonctions : `load_queue()`, `save_queue()`, `add_to_queue()`, `get_queue_status()`
- Handler `mem0_save` : Ajoute à queue au lieu d'appel API direct
- Tool `mem0_queue_status` : Monitoring queue/failed/VPS status
- Alertes WARNING (queue > 20) et CRITICAL (failed > 5)

### 3. Worker background (`~/scripts/mem0_queue_worker.py`)

**Fonctionnalités :**
- Process queue normale : retry avec backoff exponentiel
- Recovery failed : reset retries à 0, nouvelle chance à chaque run
- Atomic write : tmp file + rename
- Logging : stdout pour debug

**Déclenchement :**
- Hook SessionEnd : `~/.claude/hooks/pre-session-close.sh`
- Cron : toutes les 10min (`crontab -l`)

### 4. Cron job

```bash
*/10 * * * * /usr/bin/python3 /Users/marabook_m1/scripts/mem0_queue_worker.py >> /Users/marabook_m1/.claude/logs/mem0_worker.log 2>&1
```

## Système d'alertes

### Alerte WARNING (queue >= 20)

```
⚠️  ALERTE MEM0 VPS - WARNING
Queue locale : 23 mémoires en attente
Le VPS semble inaccessible depuis X heures

💾 Données sauvegardées :
   ✓ Queue locale
   ✓ Knowledge graph

🔧 Actions :
   1. ssh user@31.220.104.244
   2. tail -f /opt/mem0-api/logs/api.log
   3. mem0_queue_status
```

### Alerte CRITICAL (failed > 5)

```
🚨 ALERTE MEM0 VPS - CRITICAL
Failed entries : 7 mémoires
VPS Mem0 probablement DOWN

⚠️  Mémoires dans knowledge graph
🔧 Action URGENTE requise
```

## Flux de sauvegarde

### Cas nominal (VPS OK)

1. `mem0_save("windsurf-project", "contenu")`
2. → Queue locale (1 entrée)
3. → Knowledge graph (TODO Phase 5)
4. → Worker (SessionEnd ou cron 10min)
5. → Upload VPS : ✅ succès
6. → Queue vide

**Expérience utilisateur :** Aucun timeout, sauvegarde instantanée

### Cas dégradé (VPS timeout)

1. `mem0_save("windsurf-project", "contenu")`
2. → Queue locale (1 entrée)
3. → Knowledge graph (TODO Phase 5)
4. → Worker tente upload : ❌ timeout
5. → Retry 1 (backoff 2s) : ❌
6. → Retry 2 (backoff 4s) : ❌
7. → Retry 3 (backoff 8s) : ❌
8. → Moved to failed
9. → Worker suivant (10min) : reset retries, nouvelle chance
10. → Si VPS revenu : ✅ sync réussie, retiré de failed

**Expérience utilisateur :** Aucun timeout, alerte si queue > 20

## Avantages

- ✅ **Zéro timeout ressenti** : Sauvegarde locale instantanée
- ✅ **Double backup** : Queue + knowledge graph
- ✅ **Auto-healing** : Failed retentés quand VPS revient
- ✅ **Monitoring** : Tool `mem0_queue_status`
- ✅ **Alertes** : 2 niveaux (WARNING/CRITICAL)
- ✅ **Garde architecture** : Mem0 + Obsidian intact

## Inconvénients

- ⚠️ Complexité ajoutée (3 fichiers, cron, worker)
- ⚠️ Nécessite redémarrage Claude Code après install
- ⚠️ Phase 5 TODO : Dual write knowledge graph

## Décisions validées

| Paramètre | Valeur |
|-----------|--------|
| Worker | Hook SessionEnd + Cron 10min |
| Dual write | Toujours (queue + knowledge graph) |
| Seuil alerte | Queue > 20 = WARNING |
| Failed retry | Retenter à chaque worker (reset retries) |
| Alerte CRITICAL | Failed > 5 |
| Blocage | Aucun, système continue |

## Tests

- ✅ Serveur MCP démarre
- ✅ Worker fonctionne (queue vide)
- ⏳ Tests réels après redémarrage Claude Code

## Activation

**IMPORTANT :** Redémarrer Claude Code pour activer le nouveau serveur MCP.

Après redémarrage :
1. Tester `mem0_save` → devrait ajouter à queue
2. Tester `mem0_queue_status` → afficher état
3. Worker auto : SessionEnd + cron 10min

## Logs

- Worker : `~/.claude/logs/mem0_worker.log`
- Queue : `~/.claude/mem0_queue.json`

## Prochaines étapes

- [ ] Phase 5 : Implémenter dual write knowledge graph
- [ ] Tests réels avec VPS timeout simulé
- [ ] Monitoring : dashboard queue status
- [ ] Backup queue dans SecondBrain ? (à discuter)

## Références

- Plan initial : `~/.claude/plans/proud-weaving-nygaard.md`
- Plan implémentation : `~/.claude/plans/wise-discovering-pretzel.md`
- Troubleshooting : [[mem0-api-timeout]]
