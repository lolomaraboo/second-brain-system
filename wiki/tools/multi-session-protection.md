# Protection Multi-Sessions Claude Code

**Statut :** ✅ Production
**Date :** 2025-12-01
**Version :** 1.0

## Vue d'ensemble

Système de protection contre les conflits lors de l'utilisation de plusieurs sessions Claude en parallèle (git worktrees, terminaux multiples).

**Guide complet :** `~/.claude/MULTI-SESSION-PROTECTION.md`

## Architecture

### 1. Session Tracking
**Script :** `~/scripts/obsidian_session_manager.py`

- Enregistre sessions actives dans `~/.claude/obsidian_sessions.json`
- File locking avec `fcntl` (timeout 5s)
- Auto-cleanup des sessions mortes
- Détecte conflits (même projet vs projets différents)

**Commandes :**
```bash
# Enregistrer session
python3 ~/scripts/obsidian_session_manager.py register <project> <cwd>

# Lister sessions actives
python3 ~/scripts/obsidian_session_manager.py list

# Vérifier conflits
python3 ~/scripts/obsidian_session_manager.py check <project>

# Supprimer session
python3 ~/scripts/obsidian_session_manager.py unregister [pid]
```

### 2. Lock /end
**Script :** `~/.claude/shell-config/end-lock-helpers.sh`

- Lock file : `~/.claude/end.lock`
- Timeout : 30 secondes
- Empêche sauvegardes simultanées
- Cleanup automatique locks orphelins

**Fonctions Bash :**
```bash
source ~/.claude/shell-config/end-lock-helpers.sh

end_lock_acquire    # Acquérir lock
end_lock_release    # Relâcher lock
end_lock_cleanup    # Nettoyer locks orphelins
end_with_lock       # Wrapper complet
```

### 3. Helpers Obsidian
**Script :** `~/.claude/shell-config/obsidian-session-helpers.sh`

**Fonctions Bash :**
```bash
source ~/.claude/shell-config/obsidian-session-helpers.sh

obsidian_session_register <project> <cwd>
obsidian_session_unregister
obsidian_session_check <project>
obsidian_session_list
obsidian_check_before_write <project>
```

## Intégration

### Dans /start
```markdown
1. Enregistrer la session
2. Vérifier les sessions actives
3. Afficher warning si conflit
```

### Dans /end
```markdown
1. Acquérir lock /end
2. Sauvegarder (Mem0 + Obsidian + Resume)
3. Relâcher lock + cleanup session
```

## Scénarios

| Scénario | Protection |
|----------|------------|
| Projets différents | ✅ Info sessions actives |
| Git worktrees (même projet) | ✅ Lock /end + warning |
| Même worktree | ⚠️ Déconseillé mais protégé |

## Tests

**Tests effectués :**
- ✅ Lock concurrent (PROCESS 2 attend PROCESS 1)
- ✅ Session tracking avec file locking
- ✅ Cleanup automatique
- ✅ Intégration /start et /end

**Scripts de test :**
- `/tmp/test-multi-sessions.sh`
- `/tmp/test-concurrent-sessions.sh`

## Troubleshooting

**Lock /end bloqué :**
```bash
# Vérifier PID du lock
cat ~/.claude/end.lock

# Vérifier si process existe
ps -p $(cat ~/.claude/end.lock)

# Forcer suppression si process mort
rm ~/.claude/end.lock
```

**Session orpheline :**
```bash
# Lister sessions
python3 ~/scripts/obsidian_session_manager.py list

# Supprimer manuellement
python3 ~/scripts/obsidian_session_manager.py unregister <pid>
```

## Références

- Guide complet : `~/.claude/MULTI-SESSION-PROTECTION.md`
- Décision : [[../projects/windsurf-project/decisions/2025-12-01-multi-session-protection|2025-12-01-multi-session-protection]]
- Mem0 : Sauvegardé dans `windsurf-project`
