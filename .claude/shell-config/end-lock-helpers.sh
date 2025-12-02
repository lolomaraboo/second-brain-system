#!/usr/bin/env bash
# /end Lock Helpers - Protection sauvegarde simultanée
# Empêche 2 sessions de faire /end en même temps

END_LOCK_FILE="$HOME/.claude/end.lock"
END_LOCK_TIMEOUT=30  # 30 secondes max

# Acquiert le lock /end avec timeout
end_lock_acquire() {
    local start_time=$(date +%s)
    local waited=0

    while [ -f "$END_LOCK_FILE" ]; do
        local current_time=$(date +%s)
        local elapsed=$((current_time - start_time))

        if [ $elapsed -ge $END_LOCK_TIMEOUT ]; then
            echo ""
            echo "❌ Timeout: Impossible d'acquérir le lock après ${END_LOCK_TIMEOUT}s"
            echo ""
            echo "Possible causes:"
            echo "  • Autre session Claude en cours de sauvegarde (bloquée?)"
            echo "  • Lock orphelin (process mort)"
            echo ""
            echo "Solutions:"
            echo "  1. Attendre que l'autre session termine"
            echo "  2. Forcer suppression du lock: rm ~/.claude/end.lock"
            echo ""
            return 1
        fi

        if [ $waited -eq 0 ]; then
            echo ""
            echo "⏳ Autre session en cours de sauvegarde..."
            echo "   Attente (max ${END_LOCK_TIMEOUT}s)..."
            echo ""
        fi

        waited=1
        sleep 1
    done

    # Créer le lock avec PID pour debug
    echo "$$" > "$END_LOCK_FILE"

    if [ $waited -eq 1 ]; then
        echo "✓ Lock acquis, reprise de la sauvegarde..."
        echo ""
    fi

    return 0
}

# Relâche le lock /end
end_lock_release() {
    if [ -f "$END_LOCK_FILE" ]; then
        local lock_pid=$(cat "$END_LOCK_FILE" 2>/dev/null)
        if [ "$lock_pid" = "$$" ]; then
            rm -f "$END_LOCK_FILE"
        fi
    fi
}

# Cleanup du lock au cas où le process meurt
end_lock_cleanup() {
    if [ -f "$END_LOCK_FILE" ]; then
        local lock_pid=$(cat "$END_LOCK_FILE" 2>/dev/null)

        # Vérifier si le process existe encore
        if ! ps -p "$lock_pid" > /dev/null 2>&1; then
            echo "⚠️  Lock orphelin détecté (PID $lock_pid mort), nettoyage..."
            rm -f "$END_LOCK_FILE"
        fi
    fi
}

# Wrapper pour exécuter /end avec lock
end_with_lock() {
    # Cleanup des locks orphelins
    end_lock_cleanup

    # Acquérir le lock
    if ! end_lock_acquire; then
        return 1
    fi

    # Trap pour cleanup en cas d'erreur
    trap 'end_lock_release' EXIT INT TERM

    echo "🔒 Lock /end acquis - sauvegarde protégée"
    echo ""

    # La vraie sauvegarde sera faite par Claude dans /end.md
    # Ce script fournit juste le mécanisme de lock

    return 0
}

# Export des fonctions
export -f end_lock_acquire
export -f end_lock_release
export -f end_lock_cleanup
export -f end_with_lock
