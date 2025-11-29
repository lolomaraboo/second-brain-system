# Sync avec Backup Automatique

Pattern pour synchroniser des fichiers avec backup avant `rsync --delete`.

## Problème

`rsync --delete` supprime les fichiers qui n'existent pas dans la source :

```bash
rsync -av --delete source/ target/
# ⚠️ Fichiers dans target/ mais pas dans source/ = SUPPRIMÉS
```

Sans backup, impossible de récupérer en cas d'erreur.

## Solution : Backup + Lock + Dry-run

```bash
#!/bin/bash

SOURCE="~/config"
TARGET="~/backup/config"
BACKUP_DIR="$TARGET/.backups"
LOCK_FILE="$TARGET/.sync.lock"

# 1. Lock anti-concurrence
if [ -f "$LOCK_FILE" ]; then
  LOCK_PID=$(cat "$LOCK_FILE")
  if ps -p "$LOCK_PID" > /dev/null; then
    echo "Sync already running (PID: $LOCK_PID)"
    exit 1
  fi
fi
echo $$ > "$LOCK_FILE"
trap "rm -f $LOCK_FILE" EXIT

# 2. Backup avant sync
BACKUP_PATH="$BACKUP_DIR/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_PATH"
rsync -a --exclude='.backups' --exclude='.sync.lock' \
  "$TARGET/" "$BACKUP_PATH/"

# 3. Sync avec option dry-run
if [ "$1" = "--dry-run" ]; then
  rsync -av --delete --dry-run "$SOURCE/" "$TARGET/"
  echo "Dry-run complete (no changes made)"
  exit 0
fi

# 4. Sync réel
rsync -av --delete "$SOURCE/" "$TARGET/"

# 5. Nettoyer vieux backups (garder 10 derniers)
cd "$BACKUP_DIR" && ls -t | tail -n +11 | xargs rm -rf

# 6. Lock automatiquement libéré par trap EXIT
```

## Fonctionnalités

### Dry-run
```bash
./sync.sh --dry-run  # Simulation
./sync.sh            # Sync réel
```

### Lock anti-concurrence
```bash
# Terminal 1
./sync.sh  # Démarre

# Terminal 2
./sync.sh  # Bloqué : "Sync already running"
```

### Backup avec rotation
```
.backups/
├── 20251129_140530/  ← Plus récent
├── 20251129_120015/
├── ...
└── 20251128_093045/  ← 10ème (limite)
# Plus anciens supprimés automatiquement
```

### Restauration
```bash
# Lister les backups
ls -la .backups/

# Restaurer un backup
cp -r .backups/20251129_140530/* ./

# Ou restaurer fichier spécifique
cp .backups/20251129_140530/settings.json ./
```

## Options avancées

### Exclusions rsync
```bash
rsync -av --delete \
  --exclude='.git/' \
  --exclude='node_modules/' \
  --exclude='*.log' \
  "$SOURCE/" "$TARGET/"
```

### Inclusions sélectives
```bash
rsync -av --delete \
  --include='config/' \
  --include='config/***' \
  --include='settings.json' \
  --exclude='*' \
  "$SOURCE/" "$TARGET/"
```

### Notification erreurs
```bash
if ! rsync -av --delete "$SOURCE/" "$TARGET/"; then
  echo "Sync failed! Backup preserved in $BACKUP_PATH"
  exit 1
fi
```

## Cas d'usage

✅ **Bon pour :**
- Config synchronisée entre machines
- Backup de code versionné
- Sync de documentation
- Réplication de fichiers critiques

⚠️ **Attention :**
- `--delete` supprime VRAIMENT les fichiers
- Tester avec `--dry-run` d'abord
- Vérifier les exclusions avant sync

## Voir aussi

- [[file-locking-fcntl]] - Lock fichier avec fcntl
- Projet : [[windsurf-project/_INDEX]] - sync-config.sh utilise ce pattern
