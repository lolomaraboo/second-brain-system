#!/bin/bash

# Monitor Obsidian vault health (broken links, orphan files, etc.)

VAULT_PATH="${1:-$HOME/Documents/APP_HOME/CascadeProjects/windsurf-project/Memories/vault}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🔍 Monitoring Obsidian Vault Health"
echo "Vault: $VAULT_PATH"
echo ""

# Run link checker
python3 "$SCRIPT_DIR/check_obsidian_links.py" "$VAULT_PATH"
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "✅ Vault healthy - no broken links!"
else
    echo ""
    echo "⚠️  Vault has broken links - see details above"
fi

exit $EXIT_CODE
