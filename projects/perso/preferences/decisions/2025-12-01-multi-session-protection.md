# Protection Multi-Sessions Claude Code

**Date :** 2025-12-01
**Statut :** Implémenté ✅
**Impact :** Architecture système

## Contexte

Besoin de travailler avec plusieurs sessions Claude en parallèle :
- Git worktrees (plusieurs branches)
- Projets différents simultanément
- Éviter conflits Git dans SecondBrain/

## Décision

Implémentation d'un système de protection à deux niveaux :

### 1. Session Tracking
- Fichier : `~/.claude/obsidian_sessions.json`
- Script : `~/scripts/obsidian_session_manager.py`
- File locking avec `fcntl` (timeout 5s)
- Auto-cleanup des sessions mortes
- Détection de conflits (même projet vs projets différents)

### 2. Lock /end
- Fichier : `~/.claude/end.lock`
- Timeout : 30 secondes
- Empêche sauvegardes simultanées
- Cleanup automatique des locks orphelins

## Composants créés

**Scripts :**
- `~/scripts/obsidian_session_manager.py` (gestion sessions)
- `~/.claude/shell-config/obsidian-session-helpers.sh` (helpers Bash)
- `~/.claude/shell-config/end-lock-helpers.sh` (lock /end)

**Modifications :**
- `.claude/commands/start.md` (enregistrement session)
- `.claude/commands/end.md` (lock + cleanup)

**Documentation :**
- `~/.claude/MULTI-SESSION-PROTECTION.md`

## Tests

✅ Lock concurrent : PROCESS 2 attend PROCESS 1
✅ Session tracking avec file locking
✅ Cleanup automatique
✅ Synchronisation SecondBrain

## Scénarios protégés

| Scénario | Protection |
|----------|------------|
| Projets différents | ✅ Info sessions actives |
| Git worktrees | ✅ Lock /end + warning |
| Même worktree | ⚠️ Déconseillé mais protégé |

## Références

- Doc complète : `~/.claude/MULTI-SESSION-PROTECTION.md`
- Tests : `/tmp/test-concurrent-sessions.sh`
- Mem0 : Sauvegardé dans windsurf-project
