#!/bin/bash
# Alias Claude Code et outils AI - Synchronisé entre toutes les machines
# Source: ~/Documents/APP_HOME/.claude/shell-config/aliases.sh

# ============================================
# Claude Code CLI
# ============================================
export NODE_TLS_REJECT_UNAUTHORIZED=0

# Détection automatique du chemin Claude selon l'architecture
if [ -f "/usr/local/opt/node@18/bin/claude" ]; then
    # Intel Mac (Studio Maraboo)
    alias claude="NODE_TLS_REJECT_UNAUTHORIZED=0 /usr/local/opt/node@18/bin/claude"
elif [ -f "/opt/homebrew/Caskroom/claude-code/2.0.1/claude" ]; then
    # ARM Mac M1 (marabook_m1)
    alias claude="NODE_TLS_REJECT_UNAUTHORIZED=0 /opt/homebrew/Caskroom/claude-code/2.0.1/claude"
else
    # Fallback: chercher dans PATH
    alias claude="NODE_TLS_REJECT_UNAUTHORIZED=0 claude"
fi

# ============================================
# Claude Code Usage Monitor (ccm)
# ============================================
# Installé via UV (cross-platform: ARM64 + x86_64)

_ccm_run() {
    local UV_CCM="$HOME/.local/bin/ccm"
    if [ -f "$UV_CCM" ]; then
        "$UV_CCM" "$@"
    else
        echo "❌ Error: claude-monitor not installed with UV"
        echo "Run: cd $APP_HOME/projects/claude-code-monitor && ./install-ccm.sh"
        return 1
    fi
}

alias ccm='_ccm_run'
alias ccmonitor='_ccm_run'
alias claude-monitor='_ccm_run'

# ============================================
# OpenCode AI
# ============================================
# Installé via: npm install -g opencode-ai@latest
# Usage: opencode ou opencode run "prompt"

# ============================================
# Routeur Intelligent AI (bin/ai)
# ============================================
export PATH="$HOME/Documents/APP_HOME/bin:$PATH"

# ============================================
# APP_HOME
# ============================================
export APP_HOME="$HOME/Documents/APP_HOME"

# ============================================
# Project Management
# ============================================
new-project() {
    "$APP_HOME/core/bin/setup-new-project.sh" "$@"
}

mkproject() {
    "$APP_HOME/core/bin/setup-new-project.sh" "$@"
}

classify-project() {
    "$APP_HOME/core/bin/classify-project.sh" "$@"
}

# ============================================
# Sync Context Files
# ============================================
alias sync-context='$APP_HOME/core/bin/sync-context.sh'

# ============================================
# Agents Claude Code
# ============================================
# Disponibles:
# - @session-closer    : Ferme session et commit Git
# - @brutal-critic     : Critique à 3 perspectives
# - @gemini-researcher : Recherche gratuite via Gemini
# - @perplexity-researcher : Recherche temps réel avec citations

# ============================================
# VPS Management (si vps-infrastructure existe)
# ============================================
if [ -f "$APP_HOME/projects/vps-infrastructure/scripts/vps-aliases.sh" ]; then
    source "$APP_HOME/projects/vps-infrastructure/scripts/vps-aliases.sh"
fi

# ============================================
# TODO Manager (si todo-manager existe)
# ============================================
if [ -f "$APP_HOME/projects/todo-manager/todo" ]; then
    alias todo="$APP_HOME/projects/todo-manager/todo"
fi

# ============================================
# Informations
# ============================================
alias ai-info='cat $APP_HOME/.claude/shell-config/aliases.sh'
