# Mem0 Queue Lock Errors

## Symptôme

```
Error: Could not acquire queue lock (timeout). Queue might be busy.
```

## Cause

La tentative d'écriture dans la queue Mem0 échoue car le **lock file est déjà pris** par un autre processus (généralement le worker de synchronisation).

### Architecture Mem0

```
~/.claude/
├── mem0_queue.json        # Queue principale
├── mem0_queue_backup.json # Backup automatique
└── mem0_queue.lock        # Lock file (verrou)
```

### Structure Queue

```json
{
  "queue": [],           // Mémoires en attente de sync
  "last_100": [],        // Historique (déjà synchronisées)
  "failed": [],          // Mémoires échouées
  "stats": {
    "total_queued": 243,
    "total_synced": 216,
    "total_failed": 0,
    "last_sync": "2025-11-30T02:32:20"
  }
}
```

## ⚠️ Problème Critique

**Les mémoires avec "queue lock timeout" ne sont PAS sauvegardées automatiquement !**

### Pourquoi ?

1. L'erreur survient **AVANT** l'entrée dans la queue
2. La mémoire n'atteint jamais `mem0_queue.json`
3. Elle n'apparaît pas dans `failed[]`
4. **Elle est perdue définitivement**

### Différence avec autres erreurs

| Type d'erreur | Moment | Sauvegarde | Retry Auto |
|---------------|--------|------------|------------|
| Queue lock timeout | AVANT entrée queue | ❌ Non | ❌ Non |
| Erreur sync VPS | APRÈS entrée queue | ✅ Oui | ✅ Oui |
| Erreur validation | APRÈS entrée queue | ✅ Oui | ✅ Oui |

## Solution

### Procédure de Récupération Manuelle

1. **Attendre la libération de la queue**
```bash
# Vérifier le statut
mem0_queue_status

# Attendre que "Pending: 0 mémoires"
```

2. **Re-créer manuellement les mémoires perdues**
```python
# Les mémoires doivent être recréées via mem0_save
# Il n'y a PAS de mécanisme de récupération automatique
```

3. **Vérifier la synchronisation**
```bash
mem0_queue_status
# Confirmer que les mémoires sont en queue
```

### Exemple (Session 2025-11-30)

**Problème:**
- 20 mémoires perdues avec "queue lock timeout"
- Worker synchronisait pendant tentative d'écriture

**Solution appliquée:**
1. Attendu libération queue (~2 minutes)
2. Recréé manuellement les 20 mémoires
3. ✅ Toutes synchronisées avec succès

## Prévention

### Bonnes Pratiques

1. **Éviter batch trop gros**
   - Créer max 10-15 mémoires à la fois
   - Pause entre batches si worker actif

2. **Vérifier statut avant batch**
```bash
mem0_queue_status
# Si queue > 10, attendre sync
```

3. **Utiliser retry manuel**
   - Garder trace des mémoires créées
   - Re-créer si erreur lock timeout

## Amélioration Possible

### Solutions Techniques

1. **Buffer temporaire**
   - Sauvegarder mémoires dans buffer avant lock
   - Flush buffer après acquisition lock

2. **Retry automatique**
   - Détecter timeout
   - Réessayer après délai (exponential backoff)

3. **Queue sans lock**
   - Architecture append-only
   - Lock-free data structure

### Code Proposé

```python
# Retry automatique avec backoff
def save_with_retry(content, max_retries=3):
    for i in range(max_retries):
        try:
            return mem0_save(content)
        except QueueLockTimeout:
            if i < max_retries - 1:
                time.sleep(2 ** i)  # 1s, 2s, 4s
            else:
                # Sauvegarder dans buffer temporaire
                save_to_temp_buffer(content)
```

## Monitoring

### Vérifications Régulières

```bash
# Status queue
mem0_queue_status

# Logs worker
tail -f ~/.claude/mem0_worker.log

# Backup queue
ls -lh ~/.claude/mem0_queue_backup.json
```

## Références

- Architecture Mem0: `~/.claude/mem0_queue.json`
- Worker MCP: `~/scripts/mem0_mcp_server.py`
- VPS Mem0 API: `31.220.104.244:8000`

---

**Tags:** #troubleshooting #mem0 #queue #errors
**Date:** 2025-11-30
**Résolu:** Retry manuel requis (pas de solution automatique)
