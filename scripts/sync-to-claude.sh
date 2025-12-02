#!/bin/bash
# sync-to-claude.sh
# Synchronise SecondBrain/ (Git source) vers ~/.claude/ (runtime)
#
# Usage: ./sync-to-claude.sh [--dry-run]

set -euo pipefail

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Chemins
SECONDBRAIN_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLAUDE_ROOT="$HOME/.claude"

DRY_RUN=false
if [[ "${1:-}" == "--dry-run" ]]; then
    DRY_RUN=true
    echo -e "${YELLOW}🔍 Mode dry-run activé (aucune modification)${NC}\n"
fi

echo -e "${BLUE}🔄 Synchronisation SecondBrain → ~/.claude/${NC}"
echo -e "   Source: ${SECONDBRAIN_ROOT}"
echo -e "   Dest:   ${CLAUDE_ROOT}\n"

# Fonction pour synchroniser un dossier
sync_dir() {
    local src="$1"
    local dest="$2"
    local name="$3"

    if [[ ! -d "$src" ]]; then
        echo -e "${YELLOW}⚠️  $name: source inexistante ($src)${NC}"
        return
    fi

    if $DRY_RUN; then
        echo -e "${BLUE}📂 $name:${NC}"
        rsync -avn --delete "$src/" "$dest/" | grep -v "^sending\|^sent\|^total" || true
    else
        echo -e "${GREEN}✓ $name synced${NC}"
        mkdir -p "$dest"
        rsync -a --delete "$src/" "$dest/"
    fi
}

# Fonction pour créer un symlink
create_symlink() {
    local target="$1"
    local link="$2"
    local name="$3"

    if $DRY_RUN; then
        if [[ -L "$link" ]]; then
            echo -e "${BLUE}🔗 $name: symlink existe déjà → $(readlink "$link")${NC}"
        else
            echo -e "${BLUE}🔗 $name: créerait symlink $link → $target${NC}"
        fi
        return
    fi

    # Supprimer ancien lien/dossier si nécessaire
    if [[ -L "$link" ]]; then
        current_target=$(readlink "$link")
        if [[ "$current_target" == "$target" ]]; then
            echo -e "${GREEN}✓ $name: symlink déjà correct${NC}"
            return
        else
            rm "$link"
        fi
    elif [[ -d "$link" ]]; then
        echo -e "${YELLOW}⚠️  $name: dossier existant, renommage en ${link}.backup${NC}"
        mv "$link" "${link}.backup.$(date +%Y%m%d-%H%M%S)"
    fi

    mkdir -p "$(dirname "$link")"
    ln -s "$target" "$link"
    echo -e "${GREEN}✓ $name: symlink créé${NC}"
}

# Synchroniser commands/
sync_dir "$SECONDBRAIN_ROOT/commands" "$CLAUDE_ROOT/commands" "commands"

# Synchroniser hooks/
sync_dir "$SECONDBRAIN_ROOT/hooks" "$CLAUDE_ROOT/hooks" "hooks"

# Symlink pour memories/ (partage des données)
create_symlink "$SECONDBRAIN_ROOT/memories" "$CLAUDE_ROOT/memories" "memories"

# Log
if ! $DRY_RUN; then
    echo -e "\n${GREEN}✓ Synchronisation terminée${NC}"
    date > "$SECONDBRAIN_ROOT/.last-sync"
fi
