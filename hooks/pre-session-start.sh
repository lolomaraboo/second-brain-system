#!/bin/bash
# Hook de vérification automatique du setup Claude Code
# Exécuté au démarrage de chaque session Claude Code
# ~/Documents/APP_HOME/.claude/hooks/pre-session-start.sh

APP_HOME="$HOME/Documents/APP_HOME"
CLAUDE_HOME="$HOME/.claude"
SETUP_STATUS="$APP_HOME/.claude/.setup-status"
HOSTNAME=$(hostname)
USERNAME=$(whoami)

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Flags pour tracking des warnings
HAS_WARNINGS=false

# Fonction pour vérifier si le setup est fait
check_setup() {
    # Vérifier si ~/.claude est un symlink vers APP_HOME
    if [ -L "$CLAUDE_HOME" ]; then
        TARGET=$(readlink "$CLAUDE_HOME")
        if [[ "$TARGET" == *"APP_HOME/.claude"* ]]; then
            return 0  # Setup OK
        fi
    fi
    return 1  # Setup pas fait
}

# Fonction pour vérifier si cette machine est enregistrée
is_registered() {
    if [ -f "$SETUP_STATUS" ]; then
        grep -q "$HOSTNAME|$USERNAME" "$SETUP_STATUS" 2>/dev/null
        return $?
    fi
    return 1
}

# Fonction pour vérifier l'état Git du repo principal
check_git_status() {
    cd "$APP_HOME" 2>/dev/null || return 1

    # Vérifier si on est dans un repo git
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        return 1
    fi

    # Fichiers non commités
    UNCOMMITTED=$(git status --porcelain 2>/dev/null | grep -v "^??" | wc -l | tr -d ' ')
    UNTRACKED=$(git status --porcelain 2>/dev/null | grep "^??" | wc -l | tr -d ' ')

    # Commits non pushés
    BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
    UNPUSHED=0
    if [ -n "$BRANCH" ]; then
        git rev-parse @{u} > /dev/null 2>&1 && \
        UNPUSHED=$(git rev-list @{u}..HEAD 2>/dev/null | wc -l | tr -d ' ')
    fi

    # Afficher les warnings si nécessaire
    if [ "$UNCOMMITTED" -gt 0 ]; then
        echo -e "${YELLOW}⚠️  $UNCOMMITTED fichier(s) modifié(s) non commité(s)${NC}"
        HAS_WARNINGS=true
    fi

    if [ "$UNTRACKED" -gt 0 ]; then
        echo -e "${BLUE}ℹ️  $UNTRACKED fichier(s) non tracké(s)${NC}"
    fi

    if [ "$UNPUSHED" -gt 0 ]; then
        echo -e "${YELLOW}⚠️  $UNPUSHED commit(s) non pushé(s) sur GitHub${NC}"
        HAS_WARNINGS=true
    fi
}

# Fonction pour vérifier l'état des submodules
check_submodules() {
    cd "$APP_HOME" 2>/dev/null || return 1

    # Vérifier si on a des submodules
    if [ ! -f .gitmodules ]; then
        return 0
    fi

    # Récupérer l'état des submodules
    SUBMODULE_STATUS=$(git submodule status 2>/dev/null)

    # Compter les submodules pas à jour (commencent par + ou -)
    OUTDATED=$(echo "$SUBMODULE_STATUS" | grep -E "^[+-]" | wc -l | tr -d ' ')

    if [ "$OUTDATED" -gt 0 ]; then
        echo -e "${YELLOW}⚠️  $OUTDATED submodule(s) pas à jour${NC}"
        echo "$SUBMODULE_STATUS" | grep -E "^[+-]" | while read -r line; do
            NAME=$(echo "$line" | awk '{print $2}')
            echo -e "${YELLOW}   → $NAME${NC}"
        done
        HAS_WARNINGS=true
    fi
}

# Vérification principale
echo ""
echo -e "${BLUE}🔍 Vérification de synchronisation...${NC}"
echo ""

if ! check_setup; then
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo "⚠️  CONFIGURATION CLAUDE CODE NON SYNCHRONISÉE"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    echo "Cette machine n'est pas encore configurée pour utiliser"
    echo "la synchronisation multi-machines."
    echo ""
    echo "🔧 Pour configurer cette machine, exécutez:"
    echo ""
    echo "   cd ~/Documents/APP_HOME/.claude/shell-config"
    echo "   ./setup.sh"
    echo ""
    echo "Ou utilisez l'agent assistant:"
    echo ""
    echo "   @setup-assistant"
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo ""
elif ! is_registered; then
    # Setup fait mais pas enregistré - on l'enregistre
    echo "$HOSTNAME|$USERNAME|$(date +%Y-%m-%d)|1.0" >> "$SETUP_STATUS"
    echo -e "${GREEN}✅ Machine enregistrée dans le setup-status${NC}"
fi

# Vérifications supplémentaires si setup OK
if check_setup; then
    echo -e "${GREEN}✅ Configuration symlink OK${NC}"
    echo -e "${GREEN}✅ Machine enregistrée${NC}"

    # Vérifier Git
    check_git_status

    # Vérifier submodules
    check_submodules

    # Sync TodoWrite → TODO.md si session précédente non-syncée (PROTOCOLE 6)
    if [ -f "$APP_HOME/projects/todo-manager/sync-session.sh" ]; then
        "$APP_HOME/projects/todo-manager/sync-session.sh"
    fi

    # Générer instruction TodoWrite depuis TODO.md
    if [ -f "$APP_HOME/projects/todo-manager/load-todos.sh" ]; then
        "$APP_HOME/projects/todo-manager/load-todos.sh"
    else
        # Fallback: Afficher TODOs actifs (ancien comportement)
        echo ""
        echo -e "${BLUE}📋 Todos actifs:${NC}"
        if [ -f "$APP_HOME/TODO.md" ]; then
            # Extraire les 5 premiers todos actifs (ceux avec [ ])
            TODOS=$(grep -A 1 "^- \[ \]" "$APP_HOME/TODO.md" | grep -v "^--$" | head -10)
            if [ -n "$TODOS" ]; then
                echo "$TODOS" | while IFS= read -r line; do
                    if [[ $line == "- [ ]"* ]]; then
                        # Todo item
                        echo -e "${YELLOW}  $line${NC}"
                    elif [[ $line == "**"* ]]; then
                        # Context line
                        echo -e "${BLUE}    $line${NC}"
                    fi
                done
                echo ""
                echo -e "${BLUE}📄 Voir tous les todos: cat ~/Documents/APP_HOME/TODO.md${NC}"
            else
                echo -e "${GREEN}  ✅ Aucun todo actif${NC}"
            fi
        else
            echo -e "${YELLOW}  ⚠️  Fichier TODO.md non trouvé${NC}"
        fi
    fi

    # Message final
    echo ""
    if [ "$HAS_WARNINGS" = true ]; then
        echo -e "${YELLOW}💡 Pensez à commiter/pusher vos changements avant de commencer${NC}"
    else
        echo -e "${GREEN}✅ Tout est synchronisé !${NC}"
    fi
fi

echo ""

# ══════════════════════════════════════════════════════════════
# SECOND BRAIN - Rappel de charger le contexte
# ══════════════════════════════════════════════════════════════
echo -e "${BLUE}🧠 Second Brain disponible (Mem0 + Obsidian)${NC}"
echo -e "   Tape ${YELLOW}/start${NC} pour charger le contexte"
echo ""

# Le hook retourne toujours 0 pour ne pas bloquer Claude Code
exit 0
