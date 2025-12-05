# Second Brain

Personal knowledge base for Claude Code sessions, combining Mem0 (working memory) and Obsidian (permanent wiki).

**📦 NEW USER?** → Run `./install.sh` for automatic installation (or see [INSTALL.md](docs/INSTALL.md))

## Repos GitHub

| Projet | Repo |
|--------|------|
| SecondBrain | [lolomaraboo/SecondBrain](https://github.com/lolomaraboo/SecondBrain) |
| windsurf-project | [lolomaraboo/windsurf-project](https://github.com/lolomaraboo/windsurf-project) |
| recording-studio-manager | [lolomaraboo/recording-studio-manager](https://github.com/lolomaraboo/recording-studio-manager) |
| claude-code-champion-v4 | [lolomaraboo/claude-code-champion-v4](https://github.com/lolomaraboo/claude-code-champion-v4) |

## Structure

**SecondBrain/** = Config + scripts only (versioned in Git)
```
SecondBrain/
├── claude-config/     # Backup de ~/.claude/ (read-only)
├── commands/          # Slash commands (/start, /end, /wiki)
├── hooks/             # System hooks
├── scripts/           # Scripts (MCP server, monitoring, migration)
├── templates/         # Obsidian templates
├── docs/              # Documentation
└── backups/           # Pre-migration backups
```

**Memories/** = All data (gitignored, not in this repo)
```
Memories/
├── vault/             # Obsidian notes (markdown)
│   ├── projects/      # Project notes
│   ├── wiki/          # Tools, patterns, secrets directory, troubleshooting
│   ├── ideas/         # Brainstorming
│   └── daily/         # Daily notes
├── memories/          # Mem0 context (JSON files)
└── qdrant_storage/    # Qdrant vector database
```

See [architecture-memories.md](../Memories/vault/wiki/architecture-memories.md) for full details.

## Usage

| Commande | Action |
|----------|--------|
| `/start` | Charge le contexte (Mem0 + Obsidian) |
| `/end` | Sauvegarde le contexte |
| `/wiki [note]` | Ajoute une note au wiki |

## Rules

1. **Mem0** = automatique, sans confirmation
2. **Obsidian** = avec confirmation
3. **Secrets** = JAMAIS dans Obsidian, toujours dans .env
4. **Fichiers** = atomiques, max 50-100 lignes
5. **Index** = maintenu automatiquement par Claude

## Architecture

### Mem0 - Architecture Locale (Qdrant)

**Composants :**
- **Qdrant Vector Store :** localhost:6333 (Docker)
- **Mem0 Library :** Gestion embeddings + LLM
- **OpenAI API :** GPT-4o-mini (LLM) + text-embedding-3-small (embeddings)
- **JSON Backups :** `Memories/memories/{project_id}/{uuid}.json` (Git-versionnable)
- **MCP Server :** `SecondBrain/scripts/mem0_mcp_server_local.py`

**Fonctionnement :**
1. `mem0_save` → Sauvegarde dans Qdrant local + backup JSON simultané
2. **Auto-Doc:** `analyze_for_documentation()` analyse le contenu via GPT-4o-mini
3. Si pattern détecté (confidence > 0.7) → Suggestion avec draft pré-généré
4. `mem0_search` → Recherche sémantique dans Qdrant local (offline)

**Auto-Doc - Documentation Automatique Intelligente (2025-12-04) :**
- **Pattern detection automatique** via GPT-4o-mini
- **Patterns détectés:** Bug résolu, Décision technique, Config/Secret, Nouveau tool, Pattern réutilisable, Migration
- **Filesystem watcher:** Re-indexation automatique du vault Obsidian à chaque modification .md
- **LaunchAgent macOS:** Service 24/7 pour watcher (`com.secondbrain.obsidian-watcher.plist`)
- **Coût:** ~$0.58/mois pour 100 mem0_save/jour

**Commandes :**
```bash
# Vérifier santé du système
mcp__mem0__mem0_health

# Lister tous les projets
mcp__mem0__mem0_list_projects

# Vérifier status du watcher (LaunchAgent)
launchctl list | grep obsidian-watcher

# Voir logs du watcher
tail -f SecondBrain/logs/obsidian-watcher.error.log
```

### Synchronisation Config

**Architecture :**
```
~/.claude/           → Master (configuration locale)
    ↓ sync-config.sh
SecondBrain/.claude/ → Backup versionné (Git)
```

**Script : `sync-config.sh`**
```bash
# Synchronisation normale (auto si changements)
./sync-config.sh

# Options
./sync-config.sh --force      # Force sync
./sync-config.sh --dry-run    # Simulation
./sync-config.sh --no-backup  # Sans backup
./sync-config.sh --help       # Aide
```

**Fichiers synchronisés :**
- Config : `CLAUDE.md`, `settings.json`, `.setup-status`, `.todowrite-init`
- Dossiers : `agents/`, `commands/`, `hooks/`, `config/`, `shell-config/`, `output-styles/`
- Docs : `metrics/README.md`, `QUICK-START.md`, `SYNC-GUIDE.md`

**Sécurités :**
- Lock anti-concurrence (`.sync.lock`)
- Backup automatique avant sync (`.backups/`)
- Garde les 10 derniers backups

### Hooks

**Hooks disponibles :**
- `startup` : Exécuté au démarrage de Claude Code
- `pre-session-close` : Exécuté avant fermeture de session
- `user-prompt-submit` : Exécuté à chaque soumission utilisateur

**Configuration :** `~/.claude/hooks/`

### Setup Multi-Machines

**Fichier de statut :** `~/.claude/.setup-status`

Mémorise les machines configurées (hostname, username, date, version).

**Pour configurer une nouvelle machine :**
```bash
cd ~/.claude/shell-config
./setup.sh
```

## Infrastructure

- **Mem0 API:** `http://31.220.104.244:8081` (v2.0.0)
- **MCP Server:** `~/scripts/mem0_mcp_server.py`
- **Worker Cron:** `*/10 * * * *` (toutes les 10 minutes)
- **Vector Store:** Qdrant (qdrant:6333)
- **LLM:** OpenAI GPT-4o-mini

## Troubleshooting

**Qdrant ne répond pas ?**
```bash
# Vérifier que le container Docker tourne
docker ps | grep qdrant

# Redémarrer Qdrant
docker restart qdrant

# Vérifier la santé du système
mcp__mem0__mem0_health
```

**Filesystem watcher ne fonctionne pas ?**
```bash
# Vérifier le service LaunchAgent
launchctl list | grep obsidian-watcher

# Redémarrer le watcher
launchctl unload ~/Library/LaunchAgents/com.secondbrain.obsidian-watcher.plist
launchctl load ~/Library/LaunchAgents/com.secondbrain.obsidian-watcher.plist

# Voir les logs
tail -f SecondBrain/logs/obsidian-watcher.error.log
```

**mem0_save ne retourne pas de suggestion ?**
```bash
# Vérifier que OPENAI_API_KEY est configuré
grep OPENAI_API_KEY ~/.claude/.env

# Tester manuellement l'analyse
python3 -c "from SecondBrain.scripts.mem0_mcp_server_local import analyze_for_documentation; print(analyze_for_documentation('Bug résolu: crash MCP', 'test'))"
```

**Obsidian search ne trouve rien ?**
```bash
# Vérifier que le vault est indexé
python3 SecondBrain/scripts/index_obsidian_vault_direct.py

# Vérifier la collection Qdrant
docker exec -it qdrant curl http://localhost:6333/collections/obsidian_vault
```
