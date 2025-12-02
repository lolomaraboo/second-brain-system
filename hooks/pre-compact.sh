#!/bin/bash
# Hook déclenché avant compaction du contexte
# Test pour voir quand il se déclenche

echo ""
echo "══════════════════════════════════════════════════════════════"
echo "⚠️  CONTEXTE BAS - Compaction imminente !"
echo "══════════════════════════════════════════════════════════════"
echo ""
echo "💾 Pense à sauvegarder avec /end ou dis 'sauvegarde le contexte'"
echo ""
echo "📅 Déclenché à: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

exit 0
