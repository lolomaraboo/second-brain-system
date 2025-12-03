# Migration Mem0 VPS → LOCAL

**Date :** 2025-12-02
**Statut :** ✅ TERMINÉE (1,413/1,902 mémoires stockées)

## Objectif

Migrer l'architecture Mem0 depuis VPS (31.220.104.244) vers architecture 100% LOCAL avec Qdrant + OpenAI.

## Architecture finale

### Avant (VPS)
```
MCP Server → Queue → Worker → VPS API (31.220.104.244:8081)
                                ↓
                              Qdrant VPS
```

### Après (LOCAL)
```
MCP Server → Qdrant Docker (localhost:6333)
    ↓
JSON Backup (Git versioning)
```

## Composants installés

### 1. Qdrant Docker
- **Container :** qdrant-secondbrain
- **Port :** localhost:6333
- **Storage :** `~/.claude/qdrant_storage/` (110M)
- **Image :** qdrant/qdrant:latest
- **Collections :** mem0 (1,413 vectors), mem0migrations

### 2. MCP Server LOCAL
- **Fichier :** `~/scripts/mem0_mcp_server_local.py`
- **Config :**
  - LLM: gpt-4o-mini (OpenAI)
  - Embeddings: text-embedding-3-small (OpenAI)
  - Vector Store: Qdrant (localhost:6333)
- **Backup :** JSON automatique dans `SecondBrain/memories/[project]/`

### 3. Script de migration
- **Fichier :** `SecondBrain/scripts/migrate_json_to_qdrant.py`
- **Fonction :** Migrer 1,902 mémoires JSON → Qdrant avec embeddings
- **Coût estimé :** ~$0.004 (OpenAI embeddings)

## Configuration

### MCP Config
Deux fichiers mis à jour :
- `~/.mcp.json`
- `~/Documents/.../windsurf-project/.mcp.json`

```json
{
  "mcpServers": {
    "mem0": {
      "command": "python3",
      "args": ["/Users/marabook_m1/scripts/mem0_mcp_server_local.py"],
      "type": "stdio"
    }
  }
}
```

### .gitignore
```
# Qdrant vector storage (ne pas versionner)
qdrant_storage/
```

## Migration des données

### Résultats finaux
- **Total traité :** 1,902 mémoires JSON
- **Stockées dans Qdrant :** 1,413 mémoires
- **Dédupliquées automatiquement :** 489 (25.7%)
- **Erreurs UPDATE :** 6 (0.3% - IDs non-UUID)
- **Durée :** 3h50min (13,841 secondes)
- **Coût OpenAI :** ~$0.0038

### Projets migrés
1. ClaudeCodeChampion (367 fichiers)
2. yt-transcript (43 fichiers)
3. recording-studio-manager (799 fichiers)
4. second-brain (372 fichiers)
5. windsurf-project (321 fichiers)

## Nettoyage VPS LOCAL

### Worker arrêté
```bash
launchctl unload ~/Library/LaunchAgents/com.mem0.worker.plist
rm ~/Library/LaunchAgents/com.mem0.worker.plist
```

### Fichiers archivés
- **Queue :** `~/.claude/archive/vps-queue-20251202/`
  - mem0_queue.json
  - mem0_queue_dlq.json
  - mem0_emergency.json
  - mem0_queue_backup.json

- **Scripts :** `~/scripts/archive/vps-20251202/`
  - mem0_mcp_server.py (ancien)
  - mem0_queue_worker.py
  - sync-to-vps.sh

### VPS distant intact
Le VPS (31.220.104.244) reste opérationnel avec :
- ✅ Recording Studio Manager (PRODUCTION)
- ✅ PostgreSQL 16
- ✅ n8n automation
- ⚠️ Mem0 API (à désinstaller si souhaité)
- ⚠️ Qdrant VPS (à désinstaller si souhaité)

## Tests validés

Tous les tools MCP testés et fonctionnels :
- ✅ `mem0_health` : Qdrant + OpenAI OK
- ✅ `mem0_recall` : Récupération mémoires
- ✅ `mem0_search` : Recherche sémantique
- ✅ `mem0_save` : Sauvegarde Qdrant + JSON
- ✅ `mem0_list_projects` : Liste des projets

## Statut final

### ✅ Terminé
1. Migration complète (1,902 fichiers → 1,413 mémoires)
2. Qdrant Docker déployé dans `~/.claude/qdrant_storage/`
3. MCP Server LOCAL opérationnel
4. Tous les tools MCP testés et fonctionnels
5. Worker VPS arrêté et archivé
6. Documentation complète

### 🔧 Optionnel (VPS distant)
- Désinstaller Mem0 API du VPS (31.220.104.244)
- Supprimer Qdrant du VPS
- Note: RSM, PostgreSQL, n8n restent intacts

## Avantages

| Critère | VPS | LOCAL |
|---------|-----|-------|
| Latence | 100-500ms | <10ms |
| Dépendance réseau | ⚠️ Requise | ✅ Aucune |
| Coût | VPS + API | ✅ OpenAI uniquement |
| Complexité | Queue + Worker + API | ✅ Direct |
| Backup | VPS API | ✅ Git (JSON) |
| Recherche sémantique | ✅ | ✅ |

## Références

- [[mem0-auto-sync-architecture]] - Ancienne architecture VPS
- [[second-brain]] - Utilisation du système
- Code: `~/scripts/mem0_mcp_server_local.py`
- Migration: `SecondBrain/scripts/migrate_json_to_qdrant.py`
