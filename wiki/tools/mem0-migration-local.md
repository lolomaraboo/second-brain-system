# Migration Mem0 VPS → LOCAL

**Date :** 2025-12-02
**Statut :** ✅ En cours (286/1902 mémoires migrées)

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
- **Storage :** `~/Documents/.../SecondBrain/qdrant_storage/` (110M)
- **Image :** qdrant/qdrant:latest
- **À faire :** Déplacer vers `~/.claude/qdrant_storage/`

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

### Progression
- **Total :** 1,902 mémoires
- **Migrées :** 286 (15%)
- **Restantes :** ~50 minutes
- **Process :** PID 83464 (stable)

### Projets
1. ClaudeCodeChampion
2. yt-transcript
3. recording-studio-manager
4. second-brain
5. windsurf-project

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

## Prochaines étapes

1. ⏳ Attendre fin migration (~50 min)
2. 🔧 Déplacer qdrant_storage → ~/.claude/
3. 🔧 Reconfigurer Docker avec nouveau path
4. 🗑️ (Optionnel) Désinstaller Mem0 API du VPS
5. 🗑️ (Optionnel) Supprimer Qdrant du VPS

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
