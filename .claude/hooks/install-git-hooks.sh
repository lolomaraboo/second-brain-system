#!/bin/bash

# Install Git hooks from .claude/hooks/ to .git/hooks/
# Usage: ./install-git-hooks.sh

set -e

APP_HOME="$(git rev-parse --show-toplevel)"
HOOKS_SRC="$APP_HOME/.claude/hooks"
HOOKS_DEST="$APP_HOME/.git/hooks"

echo "📦 Installing Git hooks..."

# Check if .git directory exists
if [ ! -d "$APP_HOME/.git" ]; then
    echo "❌ ERROR: Not a git repository"
    exit 1
fi

# Install pre-commit hook
if [ -f "$HOOKS_SRC/pre-commit" ]; then
    echo "   Installing pre-commit hook..."
    cp "$HOOKS_SRC/pre-commit" "$HOOKS_DEST/pre-commit"
    chmod +x "$HOOKS_DEST/pre-commit"
    echo "   ✅ pre-commit hook installed"
else
    echo "   ⚠️  pre-commit hook not found in $HOOKS_SRC"
fi

echo ""
echo "✅ Git hooks installation complete!"
echo ""
echo "To test the pre-commit hook:"
echo "  git commit (will run automatically)"
echo ""
echo "To bypass the hook (not recommended):"
echo "  git commit --no-verify"
