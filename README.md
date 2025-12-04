# Second Brain

Personal knowledge base for Claude Code sessions, combining Mem0 (working memory) and Obsidian (permanent wiki).

**📦 NEW USER?** → See [INSTALL.md](INSTALL.md) for complete installation guide

## Repos GitHub

| Projet | Repo |
|--------|------|
| SecondBrain | [lolomaraboo/SecondBrain](https://github.com/lolomaraboo/SecondBrain) |
| windsurf-project | [lolomaraboo/windsurf-project](https://github.com/lolomaraboo/windsurf-project) |
| recording-studio-manager | [lolomaraboo/recording-studio-manager](https://github.com/lolomaraboo/recording-studio-manager) |
| claude-code-champion-v4 | [lolomaraboo/claude-code-champion-v4](https://github.com/lolomaraboo/claude-code-champion-v4) |

## Structure

```
SecondBrain/
├── .claude/           # Config Claude Code (synchronisée depuis ~/.claude)
├── projects/          # Notes par projet
├── wiki/
│   ├── patterns/      # Best practices
│   ├── tools/         # Documentation outils
│   ├── secrets/       # Annuaire secrets (PAS les valeurs!)
│   └── troubleshooting/
├── ideas/             # Brainstorming
├── daily/             # Notes quotidiennes
└── templates/         # Templates pour nouvelles notes
```

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

### Mem0 - Solution 2A (Queue Locale)

**Composants :**
- Queue locale : `~/.claude/mem0_queue.json`
- Lock file : `~/.claude/mem0_queue.lock` (file locking)
- Worker : `~/scripts/mem0_queue_worker.py`
- Cron : Exécution automatique toutes les 10 minutes
- Logs : `~/.claude/logs/mem0_worker.log`

**Fonctionnement :**
1. `mem0_save` → Écriture immédiate dans queue locale (avec lock)
2. Worker cron → Synchronisation VPS toutes les 10 minutes (avec lock)
3. Délai max : 10 minutes entre sauvegarde et sync VPS

**Sécurité multi-instances :**
- File locking (`fcntl`) empêche les race conditions
- Timeout de 5 secondes pour éviter blocages infinis
- ✅ **Safe pour 2+ instances Claude Code en parallèle**

**Commandes :**
```bash
# Vérifier statut de la queue
mem0_queue_status

# Forcer synchronisation immédiate
python3 ~/scripts/mem0_queue_worker.py

# Voir logs du worker
tail -f ~/.claude/logs/mem0_worker.log
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

**Queue bloquée ?**
```bash
# Vérifier le statut
mem0_queue_status

# Forcer sync manuelle
python3 ~/scripts/mem0_queue_worker.py
```

**Sync échoue ?**
```bash
# Vérifier les backups
ls -la .claude/.backups/

# Restaurer un backup
cp -r .claude/.backups/YYYYMMDD_HHMMSS/* .claude/
```

**Lock bloqué ?**
```bash
# Nettoyer le lock
rm .claude/.sync.lock
```
