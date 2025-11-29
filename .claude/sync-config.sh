#!/bin/bash
# Synchronise les fichiers de config depuis ~/.claude vers SecondBrain/.claude/
# Usage: ./sync-config.sh [--force] [--dry-run] [--no-backup]

SOURCE="$HOME/.claude"
TARGET="$HOME/Documents/APP_HOME/CascadeProjects/windsurf-project/SecondBrain/.claude"
LOCK_FILE="$TARGET/.sync.lock"
BACKUP_DIR="$TARGET/.backups"

# Couleurs pour output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Options
DRY_RUN=false
NO_BACKUP=false

# Fichiers essentiels à surveiller
ESSENTIAL_FILES=(
  "CLAUDE.md"
  "settings.json"
  ".setup-status"
  ".todowrite-init"
  "agents/*.md"
  "commands/*.md"
  "hooks/*.sh"
)

# Parse arguments
FORCE=false
for arg in "$@"; do
  case $arg in
    --force)
      FORCE=true
      ;;
    --dry-run)
      DRY_RUN=true
      ;;
    --no-backup)
      NO_BACKUP=true
      ;;
    --help)
      echo "Usage: $0 [--force] [--dry-run] [--no-backup]"
      echo "  --force      Force sync même si aucun fichier essentiel n'a changé"
      echo "  --dry-run    Affiche ce qui serait synchronisé sans rien modifier"
      echo "  --no-backup  Ne pas créer de backup avant la synchronisation"
      exit 0
      ;;
    *)
      echo -e "${RED}Option inconnue: $arg${NC}"
      exit 1
      ;;
  esac
done

# Fonction de nettoyage
cleanup() {
  rm -f "$LOCK_FILE"
}

# Configurer trap pour nettoyage
trap cleanup EXIT INT TERM

# Vérifier et créer le lock
if [ -f "$LOCK_FILE" ]; then
  LOCK_PID=$(cat "$LOCK_FILE")
  if ps -p "$LOCK_PID" > /dev/null 2>&1; then
    echo -e "${RED}✗ Synchronisation déjà en cours (PID: $LOCK_PID)${NC}"
    exit 1
  else
    echo -e "${YELLOW}⚠ Lock file obsolète détecté, nettoyage...${NC}"
    rm -f "$LOCK_FILE"
  fi
fi

# Créer le lock
echo $$ > "$LOCK_FILE"

# Vérifier si un fichier essentiel a changé (sauf si --force)
if [ "$FORCE" = false ]; then
  CHANGED=false

  # Vérifier les fichiers individuels
  for file in "CLAUDE.md" "settings.json" ".setup-status" ".todowrite-init"; do
    if [ -f "$SOURCE/$file" ] && [ "$SOURCE/$file" -nt "$TARGET/.last-sync" ]; then
      CHANGED=true
      break
    fi
  done

  # Vérifier les dossiers
  if [ "$CHANGED" = false ]; then
    for dir in agents commands hooks config output-styles shell-config metrics; do
      if [ -n "$(find "$SOURCE/$dir" -type f -newer "$TARGET/.last-sync" 2>/dev/null)" ]; then
        CHANGED=true
        break
      fi
    done
  fi

  if [ "$CHANGED" = false ]; then
    echo -e "${YELLOW}Aucun fichier essentiel modifié. Utilise --force pour forcer le sync.${NC}"
    exit 0
  fi
fi

# Afficher le mode
if [ "$DRY_RUN" = true ]; then
  echo -e "${BLUE}🔍 Mode DRY-RUN: Simulation sans modification${NC}"
fi

echo "Synchronisation de ~/.claude vers SecondBrain/.claude/ ..."

# Créer un backup avant rsync --delete (sauf si --no-backup ou --dry-run)
if [ "$NO_BACKUP" = false ] && [ "$DRY_RUN" = false ]; then
  BACKUP_TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
  BACKUP_PATH="$BACKUP_DIR/$BACKUP_TIMESTAMP"

  echo -e "${BLUE}📦 Création du backup dans $BACKUP_PATH${NC}"
  mkdir -p "$BACKUP_PATH"

  # Copier seulement les fichiers qui seront affectés par rsync --delete
  if [ -d "$TARGET" ]; then
    rsync -a --exclude='.backups' --exclude='.sync.lock' "$TARGET/" "$BACKUP_PATH/" 2>/dev/null || true
  fi

  # Garder seulement les 10 derniers backups
  cd "$BACKUP_DIR" 2>/dev/null && ls -t | tail -n +11 | xargs rm -rf 2>/dev/null || true

  echo -e "${GREEN}✓ Backup créé${NC}"
fi

# Préparer les options rsync
RSYNC_OPTS="-av --delete"
if [ "$DRY_RUN" = true ]; then
  RSYNC_OPTS="$RSYNC_OPTS --dry-run"
fi

# Synchroniser les fichiers de config
rsync $RSYNC_OPTS \
  --include='CLAUDE.md' \
  --include='settings.json' \
  --include='settings.local.json' \
  --include='.setup-status' \
  --include='.todowrite-init' \
  --include='QUICK-START.md' \
  --include='README.md' \
  --include='SYNC-GUIDE.md' \
  --include='agents/' \
  --include='agents/***' \
  --include='commands/' \
  --include='commands/***' \
  --include='hooks/' \
  --include='hooks/***' \
  --include='config/' \
  --include='config/***' \
  --include='output-styles/' \
  --include='output-styles/***' \
  --include='shell-config/' \
  --include='shell-config/***' \
  --include='metrics/' \
  --include='metrics/README.md' \
  --include='metrics/INTEGRATION-EXAMPLES.md' \
  --exclude='metrics/*' \
  --exclude='*' \
  "$SOURCE/" "$TARGET/"

if [ $? -eq 0 ]; then
  if [ "$DRY_RUN" = false ]; then
    # Marquer le timestamp du dernier sync
    touch "$TARGET/.last-sync"
    echo -e "${GREEN}✓ Config synchronisée depuis ~/.claude vers SecondBrain/.claude/${NC}"
    echo "Fichiers versionnés prêts pour commit Git"
  else
    echo -e "${BLUE}✓ Simulation terminée (aucune modification effectuée)${NC}"
  fi
else
  echo -e "${RED}✗ Erreur lors de la synchronisation${NC}"
  exit 1
fi
