# Mem0 Local → VPS Backup

**Statut:** ✅ PRODUCTION (depuis 2025-12-02)
**Type:** Backup manuel et script automatisable

## Vue d'ensemble

Système de backup des mémoires locales vers VPS. Après la migration VPS → Local, la nouvelle architecture place le stockage local comme source of truth, et le VPS comme backup uniquement.

## Architecture

```
┌────────────────────────────────────────┐
│  SecondBrain/memories/                 │
│  (Source of Truth - LOCAL)             │
│                                        │
│  ├── second-brain/         (372)       │
│  ├── recording-studio-manager/ (799)  │
│  ├── ClaudeCodeChampion/   (367)      │
│  ├── windsurf-project/     (321)      │
│  └── yt-transcript/        (43)       │
│                                        │
│  Total: 1,902 mémoires                │
│  Format: 1 fichier JSON par mémoire   │
└────────────┬───────────────────────────┘
             │
             │ sync-to-vps.sh
             │ (manuel ou cron/launchd)
             ▼
┌────────────────────────────────────────┐
│  VPS Mem0 API                          │
│  http://31.220.104.244:8081           │
│  (Backup Only)                         │
│                                        │
│  POST /memory/{project_id}             │
│  - Crée/Update mémoires                │
│  - Health check: GET /health           │
└────────────────────────────────────────┘
```

## Changement d'Architecture (2025-12-02)

### Avant Migration
- **VPS** = Source of Truth
- **Local** = Queue + Worker → VPS
- **Flow:** `mem0_save()` → Queue → Worker → VPS

### Après Migration
- **Local** = Source of Truth (individual JSON files)
- **VPS** = Backup uniquement
- **Flow:** Local files → `sync-to-vps.sh` → VPS

### Raison du Changement
1. **Performance:** Accès local instantané vs latence VPS
2. **Fiabilité:** Pas de dépendance VPS pour fonctionnement
3. **Semantic Search:** Obsidian built-in (pas besoin VPS)
4. **Portabilité:** Fichiers JSON standards (compatible Mem0)
5. **Git Integration:** Unified repo avec Obsidian vault

## Script: sync-to-vps.sh

**Location:** `SecondBrain/scripts/sync-to-vps.sh`

### Fonctionnalités

- Sync toutes les mémoires locales → VPS
- Health check VPS avant sync
- Support dry-run pour tests
- Support sync par projet
- Logging complet
- Gestion d'erreurs avec compteurs

### Usage

```bash
cd ~/Documents/APP_HOME/CascadeProjects/windsurf-project/SecondBrain

# Sync tous les projets
./scripts/sync-to-vps.sh

# Dry-run (test sans modification)
./scripts/sync-to-vps.sh --dry-run

# Sync un projet spécifique
./scripts/sync-to-vps.sh --project second-brain

# Dry-run d'un projet
./scripts/sync-to-vps.sh --dry-run --project yt-transcript
```

### Configuration

**Variables dans le script:**
```bash
VPS_URL="http://31.220.104.244:8081"
MEMORIES_DIR="$HOME/Documents/APP_HOME/CascadeProjects/windsurf-project/SecondBrain/memories"
LOG_FILE="/tmp/sync-to-vps.log"
```

### Logique de Sync

1. **Health Check VPS**
   ```bash
   curl -s --max-time 5 "${VPS_URL}/health"
   ```
   - Si VPS down → abort sync
   - Si VPS up → proceed

2. **Discovery Projets**
   - Scan `memories/*/` directories
   - Ignore `.backup` et dossiers cachés

3. **Sync par Projet**
   - Pour chaque projet:
     - Count mémoires (fichiers *.json)
     - Pour chaque mémoire:
       - Read JSON file
       - POST to VPS: `/memory/{project_id}`
       - Log succès/échec

4. **Reporting**
   - Total synced / total files
   - Failed count
   - Full logs: `/tmp/sync-to-vps.log`

### Format Mémoire

**Local File:**
```json
{
  "id": "uuid",
  "content": "texte de la mémoire",
  "timestamp": 1234567890,
  "metadata": {...}
}
```

**POST to VPS:**
```json
{
  "content": "texte de la mémoire"
}
```

L'API VPS crée automatiquement l'ID et metadata.

## Automatisation (À Implémenter)

### Option 1: Cron (Simple)

```bash
# Backup quotidien à 3h du matin
0 3 * * * cd ~/Documents/APP_HOME/CascadeProjects/windsurf-project/SecondBrain && ./scripts/sync-to-vps.sh >> /tmp/sync-to-vps-cron.log 2>&1
```

### Option 2: Launchd (Recommandé macOS)

**Fichier:** `~/Library/LaunchAgents/com.mem0.local-vps-backup.plist`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.mem0.local-vps-backup</string>

  <key>ProgramArguments</key>
  <array>
    <string>/Users/marabook_m1/Documents/APP_HOME/CascadeProjects/windsurf-project/SecondBrain/scripts/sync-to-vps.sh</string>
  </array>

  <key>WorkingDirectory</key>
  <string>/Users/marabook_m1/Documents/APP_HOME/CascadeProjects/windsurf-project/SecondBrain</string>

  <key>StandardOutPath</key>
  <string>/tmp/mem0-backup.log</string>

  <key>StandardErrorPath</key>
  <string>/tmp/mem0-backup-error.log</string>

  <!-- Run daily at 3 AM -->
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key>
    <integer>3</integer>
    <key>Minute</key>
    <integer>0</integer>
  </dict>
</dict>
</plist>
```

**Installation:**
```bash
# Load service
launchctl load ~/Library/LaunchAgents/com.mem0.local-vps-backup.plist

# Start now (test)
launchctl start com.mem0.local-vps-backup

# Check logs
tail -f /tmp/mem0-backup.log
```

### Option 3: Git Hook (post-commit)

Sync après chaque commit contenant des changements mémoire:

**`.git/hooks/post-commit`:**
```bash
#!/bin/bash
# Sync to VPS if memories changed

if git diff HEAD^ HEAD --name-only | grep -q "^memories/"; then
  echo "Memories changed, syncing to VPS..."
  ./scripts/sync-to-vps.sh --quiet
fi
```

## Monitoring

### Vérifier Sync Status

```bash
# Comparer counts local vs VPS
cd ~/Documents/APP_HOME/CascadeProjects/windsurf-project/SecondBrain

# Local count
for dir in memories/*/; do
  project=$(basename "$dir")
  count=$(ls -1 "$dir"/*.json 2>/dev/null | wc -l)
  echo "LOCAL  $project: $count"
done

# VPS count (si accessible)
curl -s "http://31.220.104.244:8081/memory/second-brain?limit=1" | \
  python3 -c "import json,sys; print('VPS second-brain:', len(json.load(sys.stdin).get('memories',{}).get('results',[])))"
```

### Logs

- **Sync logs:** `/tmp/sync-to-vps.log`
- **Launchd logs:** `/tmp/mem0-backup.log`
- **Errors:** `/tmp/mem0-backup-error.log`

## Récupération depuis VPS

Si besoin de restaurer depuis VPS vers local:

```bash
# Script de récupération (à créer si nécessaire)
python3 ~/scripts/restore-from-vps.py \
  --project second-brain \
  --output ~/Documents/APP_HOME/CascadeProjects/windsurf-project/SecondBrain/memories/second-brain/
```

## Garanties

✅ **Local = Source of Truth** (fichiers JSON individuels)
✅ **VPS = Backup seulement** (pas de dépendance)
✅ **Obsidian Semantic Search** (built-in, pas VPS)
✅ **Git Integration** (unified repo)
✅ **Portabilité** (format Mem0 standard)

## Migration Historique

**Date:** 2025-12-02
**Opération:** Migration VPS → Local complète

- 1,902 mémoires migrées
- 5 projets consolidés
- 785 duplicates supprimés
- Architecture Mem0 respectée

**Rapport:** `memories/final-merge-report.json`

## Références

- [[mem0-auto-sync-architecture]] - Ancien système (VPS primary)
- Script: `SecondBrain/scripts/sync-to-vps.sh`
- Migration report: `SecondBrain/memories/final-merge-report.json`
