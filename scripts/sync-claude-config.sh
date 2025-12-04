#!/bin/bash
# Script de synchronisation ~/.claude <-> SecondBrain/claude-config/
# Source de vérité : ~/.claude/
# Backup versionné : SecondBrain/claude-config/

set -e

CLAUDE_HOME="$HOME/.claude"
SECONDBRAIN_DIR="$HOME/Documents/APP_HOME/CascadeProjects/windsurf-project/SecondBrain"
BACKUP_DIR="$SECONDBRAIN_DIR/claude-config"

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# Vérifier que les dossiers existent
if [ ! -d "$CLAUDE_HOME" ]; then
    echo -e "${RED}❌ Erreur: $CLAUDE_HOME n'existe pas${NC}"
    exit 1
fi

if [ ! -d "$SECONDBRAIN_DIR" ]; then
    echo -e "${RED}❌ Erreur: $SECONDBRAIN_DIR n'existe pas${NC}"
    exit 1
fi

# Créer claude-config/ si nécessaire
mkdir -p "$BACKUP_DIR"

# Fonction: Sync FROM ~/.claude TO SecondBrain/claude-config/
sync_to_backup() {
    print_header "📤 SYNC: ~/.claude → SecondBrain/claude-config/"

    echo -e "${YELLOW}🔄 Synchronisation en cours...${NC}"

    rsync -av --delete \
        --exclude '.DS_Store' \
        --exclude 'projects/' \
        --exclude 'file-history/' \
        --exclude 'debug/' \
        --exclude 'shell-snapshots/' \
        --exclude 'todos/' \
        --exclude 'plans/' \
        --exclude 'logs/' \
        --exclude '*.log' \
        --exclude 'history.jsonl' \
        --exclude 'mem0_metrics.json' \
        --exclude 'mem0_queue.json' \
        --exclude 'mem0-backup-*.json' \
        --exclude 'session-env/' \
        --exclude 'sessions/*/project.txt' \
        --exclude 'statsig/' \
        --exclude 'archive/' \
        --exclude '.env' \
        "$CLAUDE_HOME/" "$BACKUP_DIR/" | tail -10

    echo -e "${GREEN}✅ Sync terminé: SecondBrain/claude-config/ est à jour${NC}"
    echo -e "${BLUE}💡 N'oubliez pas de commit dans SecondBrain/ pour versionner${NC}"
}

# Fonction: Sync FROM SecondBrain/claude-config/ TO ~/.claude
sync_from_backup() {
    print_header "📥 RESTORE: SecondBrain/claude-config/ → ~/.claude"

    echo -e "${YELLOW}⚠️  Attention: Ceci va écraser des fichiers dans ~/.claude/${NC}"
    read -p "Continuer? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}ℹ️  Restore annulé${NC}"
        exit 0
    fi

    echo -e "${YELLOW}🔄 Restauration en cours...${NC}"

    rsync -av \
        --exclude '.gitignore' \
        --exclude 'projects/' \
        --exclude 'file-history/' \
        --exclude 'debug/' \
        "$BACKUP_DIR/" "$CLAUDE_HOME/" | tail -10

    echo -e "${GREEN}✅ Restore terminé: ~/.claude/ restauré depuis le backup${NC}"
}

# Fonction: Afficher les différences
show_diff() {
    print_header "🔍 DIFF: ~/.claude ↔ SecondBrain/claude-config/"

    echo -e "${YELLOW}📊 Fichiers différents:${NC}\n"

    rsync -avn --delete \
        --exclude '.DS_Store' \
        --exclude 'projects/' \
        --exclude 'file-history/' \
        --exclude 'debug/' \
        --exclude 'shell-snapshots/' \
        --exclude 'todos/' \
        --exclude 'plans/' \
        --exclude 'logs/' \
        --exclude '*.log' \
        --exclude 'history.jsonl' \
        --exclude 'mem0_metrics.json' \
        --exclude 'mem0_queue.json' \
        --exclude 'mem0-backup-*.json' \
        --exclude 'session-env/' \
        --exclude 'sessions/*/project.txt' \
        --exclude 'statsig/' \
        --exclude 'archive/' \
        --exclude '.env' \
        "$CLAUDE_HOME/" "$BACKUP_DIR/" | grep -E "^(<|>|deleting)"

    echo -e "\n${BLUE}💡 Légende: > = nouveau/modifié, deleting = à supprimer${NC}"
}

# Menu principal
case "${1:-}" in
    to-backup|push)
        sync_to_backup
        ;;
    from-backup|restore|pull)
        sync_from_backup
        ;;
    diff|status)
        show_diff
        ;;
    *)
        echo "Usage: $0 {to-backup|from-backup|diff}"
        echo ""
        echo "Commands:"
        echo "  to-backup    (push)    Sync ~/.claude → SecondBrain/claude-config/"
        echo "  from-backup  (restore) Restore SecondBrain/claude-config/ → ~/.claude"
        echo "  diff         (status)  Show differences"
        echo ""
        echo "Exemples:"
        echo "  $0 to-backup     # Backup quotidien"
        echo "  $0 diff          # Voir les changements"
        echo "  $0 from-backup   # Restaurer depuis le backup"
        exit 1
        ;;
esac
