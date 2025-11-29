#!/bin/bash
# Synchronise les fichiers de config depuis ~/.claude vers SecondBrain/.claude/
# Usage: ./sync-config.sh [--force]

SOURCE="$HOME/.claude"
TARGET="$HOME/Documents/APP_HOME/CascadeProjects/windsurf-project/SecondBrain/.claude"

# Couleurs pour output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fichiers essentiels à surveiller
ESSENTIAL_FILES=(
  "CLAUDE.md"
  "settings.json"
  "agents/*.md"
  "commands/*.md"
  "hooks/*.sh"
)

# Vérifier si un fichier essentiel a changé (sauf si --force)
if [ "$1" != "--force" ]; then
  CHANGED=false

  # Vérifier les fichiers individuels
  for file in "CLAUDE.md" "settings.json"; do
    if [ -f "$SOURCE/$file" ] && [ "$SOURCE/$file" -nt "$TARGET/.last-sync" ]; then
      CHANGED=true
      break
    fi
  done

  # Vérifier les dossiers
  if [ "$CHANGED" = false ]; then
    for dir in agents commands hooks; do
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

echo "Synchronisation de ~/.claude vers SecondBrain/.claude/ ..."

# Synchroniser les fichiers de config
rsync -av --delete \
  --include='CLAUDE.md' \
  --include='settings.json' \
  --include='settings.local.json' \
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
  --exclude='*' \
  "$SOURCE/" "$TARGET/"

# Marquer le timestamp du dernier sync
touch "$TARGET/.last-sync"

echo -e "${GREEN}✓ Config synchronisée depuis ~/.claude vers SecondBrain/.claude/${NC}"
echo "Fichiers versionnés prêts pour commit Git"
