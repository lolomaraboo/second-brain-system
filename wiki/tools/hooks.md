# Hooks Claude Code

**Statut:** ✅ PRODUCTION

## Vue d'ensemble

Les hooks sont des scripts shell exécutés automatiquement par Claude Code ou Git à des moments clés du workflow.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Session Claude Code                        │
├─────────────────────────────────────────────────────────┤
│  Démarrage  →  pre-session-start.sh                    │
│  Fermeture  →  pre-session-close.sh                    │
│  Compaction →  pre-compact.sh                          │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│              Git Workflow                               │
├─────────────────────────────────────────────────────────┤
│  git commit  →  pre-commit (anti-drift)                │
└─────────────────────────────────────────────────────────┘
```

## Hooks Claude Code (automatiques)

**Location:** `~/.claude/hooks/`

**Synchronisé:** ✅ Oui (via APP_HOME)

### pre-session-start.sh

**Trigger:** Démarrage de chaque session Claude Code

**Fichier:** `~/.claude/hooks/pre-session-start.sh` (202 lignes)

**Vérifications:**

1. **Setup multi-machines**
   - Vérifie que ~/.claude est un symlink vers APP_HOME
   - Vérifie que machine est enregistrée dans .setup-status
   - Si NON configuré → affiche message setup.sh

2. **Git Status**
   - Fichiers uncommitted
   - Fichiers untracked
   - Commits non pushés
   - ⚠️ Affiche warnings si problèmes

3. **Submodules Git**
   - Vérifie si submodules outdated
   - Affiche quels submodules doivent être mis à jour

4. **TodoWrite Sync**
   - Appelle `todo-manager/sync-session.sh` si existe
   - Synchronise TodoWrite → TODO.md (protocole 6)

5. **TODOs Loading**
   - Appelle `todo-manager/load-todos.sh` si existe
   - Ou affiche 5 premiers TODOs actifs de TODO.md

6. **Second Brain Reminder**
   - Affiche: "🧠 Second Brain disponible (Mem0 + Obsidian)"
   - Rappel: "Tape /start pour charger le contexte"

**Output exemple:**
```
🔍 Vérification de synchronisation...

✅ Configuration symlink OK
✅ Machine enregistrée
⚠️  2 fichier(s) modifié(s) non commité(s)
⚠️  1 commit(s) non pushé(s) sur GitHub

📋 Todos actifs:
  - [ ] Finaliser documentation hooks
  **Context:** SecondBrain/wiki/tools/

💡 Pensez à commiter/pusher vos changements avant de commencer

🧠 Second Brain disponible (Mem0 + Obsidian)
   Tape /start pour charger le contexte
```

**Code principal:**
```bash
# Vérif setup
check_setup() {
    if [ -L "$CLAUDE_HOME" ]; then
        TARGET=$(readlink "$CLAUDE_HOME")
        if [[ "$TARGET" == *"APP_HOME/.claude"* ]]; then
            return 0
        fi
    fi
    return 1
}

# Vérif Git
check_git_status() {
    UNCOMMITTED=$(git status --porcelain | grep -v "^??" | wc -l)
    UNPUSHED=$(git rev-list @{u}..HEAD | wc -l)
    # Affiche warnings...
}
```

### pre-session-close.sh

**Trigger:** Fermeture de session Claude Code

**Fichier:** `~/.claude/hooks/pre-session-close.sh` (1144 lignes)

**Actions:**

1. **Sync Contextes**
   - Synchronise les contextes actifs
   - Appelle @session-manager si configuré

2. **Git Auto-commit/push (optionnel)**
   - Commit changements si configuré
   - Push vers GitHub

**Usage:**
Automatique à la fermeture de session.

### pre-compact.sh

**Trigger:** Avant compaction de contexte

**Fichier:** `~/.claude/hooks/pre-compact.sh` (714 lignes)

**Actions:**

1. **Sauvegarde contexte**
   - Sauvegarde état avant compaction

2. **Nettoyage mémoire**
   - Libère ressources si besoin

**Usage:**
Automatique quand Claude Code compacte le contexte.

## Hooks Git (installation manuelle)

**Location:** `.git/hooks/` (installation)

**Source:** `~/.claude/hooks/` (templates)

### pre-commit - Anti-drift

**Trigger:** Avant chaque `git commit`

**Fichier source:** `~/.claude/hooks/pre-commit` (4974 lignes)

**But:** Vérifier cohérence du projet avant commit (anti-drift).

**Vérifications:**

1. **Agent count cohérent**
   ```bash
   # Vérifie que tous les fichiers mentionnent le même count
   - CLAUDE.md: "Agents actuels: 6/7"
   - PROJECT-INDEX.md: "6/7"
   - claude-code-agents/CLAUDE.md: "6/7"
   ```

2. **Core tools count**
   ```bash
   # Vérifie nombre de scripts dans core/bin/
   - core/bin/ contient 15 fichiers
   - PROJECT-INDEX.md mentionne "15 scripts"
   ```

3. **sync-context.sh obsolète**
   ```bash
   # Vérifie que le script est marqué obsolète
   - Recherche "OBSOLÈTE" dans la doc
   ```

4. **Symlinks existent**
   ```bash
   # Vérifie présence des symlinks
   - agents.md → CLAUDE.md
   - gemini.md → CLAUDE.md
   - bin/ → core/bin/
   ```

5. **PROJECT-INDEX.md valide**
   ```bash
   # Vérifie que le fichier existe et n'est pas vide
   ```

6. **CHANGELOG.md format**
   ```bash
   # Vérifie format Keep a Changelog
   - Sections: Added/Changed/Fixed/Removed
   ```

**Installation:**
```bash
# Automatique
cd ~/Documents/APP_HOME
./.claude/hooks/install-git-hooks.sh

# Manuel
cp ~/.claude/hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

**Output exemple (succès):**
```
🔍 Vérification anti-drift...
   Checking agent count... ✓
   Checking core tools count... ✓
   Checking sync-context.sh obsolete... ✓
   Checking symlinks... ✓
   Checking PROJECT-INDEX.md... ✓
   Checking CHANGELOG.md format... ✓
✅ All drift checks passed
```

**Output exemple (échec):**
```
🔍 Vérification anti-drift...
   Checking agent count... ✗
   ERROR: Agent count drift detected!
   Expected: 6/7 in all files
   Found in CLAUDE.md: 0 occurrences
   Found in PROJECT-INDEX.md: 1 occurrences

   Please update agent count in all files to match.

❌ Drift check failed - commit aborted
```

**Bypass (déconseillé):**
```bash
git commit --no-verify -m "urgent fix"
```

## Créer un hook custom

### Hook Claude Code

**Étape 1:** Créer le script
```bash
nano ~/.claude/hooks/my-custom-hook.sh
```

**Étape 2:** Rendre exécutable
```bash
chmod +x ~/.claude/hooks/my-custom-hook.sh
```

**Étape 3:** Configurer dans Claude Code settings
```json
{
  "hooks": {
    "pre-session-start": "~/.claude/hooks/my-custom-hook.sh"
  }
}
```

**Exemple - Vérification Python venv:**
```bash
#!/bin/bash
# Check if in venv before starting session

if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  No Python venv active"
    echo "   Activate with: source venv/bin/activate"
fi

exit 0  # Always return 0 to not block Claude Code
```

### Hook Git

**Étape 1:** Créer dans .git/hooks/
```bash
nano .git/hooks/pre-push
```

**Étape 2:** Rendre exécutable
```bash
chmod +x .git/hooks/pre-push
```

**Exemple - Vérification tests avant push:**
```bash
#!/bin/bash
# Run tests before push

echo "🧪 Running tests before push..."

if ! pytest; then
    echo "❌ Tests failed - push aborted"
    exit 1
fi

echo "✅ Tests passed"
exit 0
```

## Variables d'environnement disponibles

Dans les hooks Claude Code:

- `$CLAUDE_HOME` - Chemin vers ~/.claude
- `$PWD` - Répertoire courant
- `$USER` - Utilisateur actuel
- `$HOSTNAME` - Nom de la machine

Dans les hooks Git:

- `$GIT_DIR` - Répertoire .git
- `$GIT_INDEX_FILE` - Fichier index
- Variables Git standard

## Troubleshooting

### Hook ne s'exécute pas

**Symptôme:** Hook ignoré par Claude Code

**Diagnostic:**
```bash
ls -la ~/.claude/hooks/pre-session-start.sh
# Doit être: -rwx--x--x (exécutable)
```

**Solution:**
```bash
chmod +x ~/.claude/hooks/pre-session-start.sh
```

### Hook bloque démarrage

**Symptôme:** Session Claude Code ne démarre pas

**Cause:** Hook retourne exit code != 0

**Solution temporaire:**
```bash
# Désactiver le hook
chmod -x ~/.claude/hooks/pre-session-start.sh

# Debug
bash -x ~/.claude/hooks/pre-session-start.sh
```

**Solution permanente:**
- Toujours retourner `exit 0` à la fin du hook
- Gérer les erreurs sans bloquer

### Git hook ne fonctionne pas

**Symptôme:** `git commit` n'exécute pas pre-commit

**Diagnostic:**
```bash
ls -la .git/hooks/pre-commit
# Doit exister et être exécutable
```

**Solution:**
```bash
# Réinstaller
~/.claude/hooks/install-git-hooks.sh
```

## Best Practices

✅ **DO:**
- Toujours retourner `exit 0` pour hooks Claude Code (ne pas bloquer)
- Rendre scripts exécutables (`chmod +x`)
- Tester hooks avant de commiter
- Ajouter messages clairs d'erreur
- Documenter dans Obsidian

❌ **DON'T:**
- Ne pas bloquer le démarrage de session
- Ne pas exécuter commandes longues (> 5s)
- Ne pas modifier fichiers sans user input
- Ne pas oublier de synchroniser (APP_HOME)

## Références

- [[claude-code-sync]] - Synchronisation multi-machines
- [[slash-commands]] - Slash commands (/start, /end)
- Location: `~/.claude/hooks/`
- Git hooks doc: https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks
- Claude Code hooks: (voir settings.json)
