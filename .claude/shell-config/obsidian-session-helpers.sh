#!/usr/bin/env bash
# Obsidian Session Helpers - Protection multi-sessions
# Source ce fichier dans ton shell ou slash commands

SESSION_MANAGER="$HOME/scripts/obsidian_session_manager.py"

# Enregistre la session courante
obsidian_session_register() {
    local project_id="$1"
    local cwd="${2:-$PWD}"

    if [[ -z "$project_id" ]]; then
        echo "❌ project_id requis" >&2
        return 1
    fi

    python3 "$SESSION_MANAGER" register "$project_id" "$cwd"
}

# Supprime la session courante
obsidian_session_unregister() {
    python3 "$SESSION_MANAGER" unregister
}

# Vérifie les sessions actives et affiche un warning si nécessaire
obsidian_session_check() {
    local project_id="$1"
    local result

    result=$(python3 "$SESSION_MANAGER" check "$project_id")
    local status=$(echo "$result" | jq -r '.status')
    local message=$(echo "$result" | jq -r '.message')

    if [[ "$status" == "warning" ]]; then
        echo ""
        echo "════════════════════════════════════════════════════════════"
        echo "$message"
        echo "════════════════════════════════════════════════════════════"
        echo ""
        echo "⚠️  ATTENTION: Risque de conflit lors de modifications Obsidian"
        echo ""
        echo "Recommandations:"
        echo "  • Coordonner avec l'autre session avant /end"
        echo "  • Ou attendre que l'autre session se termine"
        echo ""
        return 2
    elif [[ "$status" == "info" ]]; then
        echo ""
        echo "$message"
        echo ""
        return 0
    fi

    # status == "ok"
    return 0
}

# Liste toutes les sessions actives
obsidian_session_list() {
    local sessions
    sessions=$(python3 "$SESSION_MANAGER" list)

    if [[ $(echo "$sessions" | jq '. | length') -eq 0 ]]; then
        echo "Aucune session active"
        return 0
    fi

    echo "Sessions actives:"
    echo "$sessions" | jq -r '.[] | "  • PID \(.pid) - \(.project_id) (\(.cwd))"'
}

# Vérifie si on peut écrire dans Obsidian (pour utilisation avant modifications)
obsidian_check_before_write() {
    local project_id="$1"
    local result

    result=$(python3 "$SESSION_MANAGER" check "$project_id")
    local status=$(echo "$result" | jq -r '.status')

    if [[ "$status" == "warning" ]]; then
        echo ""
        echo "⚠️  Autre session active sur le même projet!"
        echo ""
        echo "Continuer quand même? (risque de conflit Git)"
        read -p "[y/N] " -n 1 -r
        echo

        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "✗ Modification annulée"
            return 1
        fi

        echo "⚠️  Continuer à vos risques et périls..."
        return 0
    fi

    return 0
}

# Export des fonctions
export -f obsidian_session_register
export -f obsidian_session_unregister
export -f obsidian_session_check
export -f obsidian_session_list
export -f obsidian_check_before_write
