#!/bin/bash
# Hook de fin de session Claude Code
# Propose de sauvegarder le contexte Second Brain

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Sync existant si disponible
if [ -f ~/sync-context.sh ]; then
    ~/sync-context.sh
fi

echo ""
echo -e "${BLUE}══════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}💾 Fin de session - Pense à sauvegarder le contexte !${NC}"
echo -e "${BLUE}══════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "Si tu n'as pas encore sauvegardé, tape ${GREEN}/end${NC}"
echo -e "ou dis à Claude: ${GREEN}\"Sauvegarde le contexte\"${NC}"
echo ""

exit 0
