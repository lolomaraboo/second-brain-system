# Pre-Tool Validation Hook

**Statut:** 💡 IDÉE (pas encore implémenté)
**Date:** 2025-12-02
**Priorité:** Basse (à implémenter si problème persiste)

## Problème

Claude n'applique pas toujours systématiquement la règle de consulter Mem0/Obsidian AVANT d'utiliser Bash/Read/Write pour explorer le système.

## Solutions déjà implémentées

1. ✅ **Checklist critique** au début de `~/.claude/CLAUDE.md`
2. ✅ **Warnings renforcés** dans section "Consultation automatique"

## Idée: Hook pre-tool

Un hook qui s'exécute AVANT chaque appel à certains outils critiques (Bash, Read pour exploration) et qui:

1. **Détecte l'intention:**
   - Si Bash/Read semble être une recherche/exploration (pas exécution)
   - Exemples: `ls`, `find`, `grep`, `cat` pour découverte

2. **Vérifie historique récent:**
   - A-t-on appelé `mem0_search` dans les N derniers tours?
   - A-t-on lu un fichier Obsidian `_INDEX.md` récemment?

3. **Action si violation:**
   - Bloquer l'outil? (trop strict)
   - Afficher warning? (mieux)
   - Logger pour audit? (utile)

## Implémentation possible

**Fichier:** `~/.claude/hooks/pre-tool-use.sh`

```bash
#!/bin/bash
# Hook appelé avant chaque utilisation d'outil

TOOL_NAME="$1"
TOOL_ARGS="$2"

# Liste des outils à monitorer
case "$TOOL_NAME" in
  "Bash")
    # Détecter commandes d'exploration
    if echo "$TOOL_ARGS" | grep -qE "^(ls|find|grep|cat|head|tail)"; then
      # Vérifier si mem0_search appelé récemment
      if ! grep -q "mem0_search" ~/.claude/session-history-recent.log; then
        echo "⚠️ WARNING: Utilisation de $TOOL_ARGS sans mem0_search préalable"
        echo "💡 Considère d'abord: mem0_search pour chercher dans la mémoire"
      fi
    fi
    ;;
  "Read")
    # Si lecture dans /Users/... (filesystem exploration)
    if echo "$TOOL_ARGS" | grep -qE "^/Users/.*/(scripts|\.claude)"; then
      echo "💡 Rappel: Cherche d'abord dans Obsidian/Mem0 avant de lire des fichiers"
    fi
    ;;
esac
```

## Considérations

**Avantages:**
- Rappel automatique de la règle
- Audit des violations
- Éducatif pour renforcer le comportement

**Inconvénients:**
- Complexité technique
- Faux positifs possibles (lectures légitimes)
- Peut ralentir l'exécution

## Décision

**Status:** IDÉE EN ATTENTE

Attendre 2-3 semaines après implémentation des améliorations CLAUDE.md (checklist + warnings).

Si problème persiste → implémenter ce hook
Si problème résolu → garder comme référence future

## Références

- [[claude-code-hooks]] - Système de hooks existant
- `~/.claude/CLAUDE.md` - Instructions améliorées (2025-12-02)
- Discussion: session 2025-12-02 10:50-11:00

## Alternative: System Reminder

Claude Code peut aussi supporter des system-reminders injectés dans le contexte.
Pourrait être une alternative plus simple que le hook shell.

---

**Tags:** #improvement #hooks #second-brain #automation
