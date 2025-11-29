# Hooks APP_HOME

Ce répertoire contient les hooks pour Claude Code et Git.

## 📋 Hooks Disponibles

### Claude Code Hooks (automatiques)

Ces hooks sont exécutés automatiquement par Claude Code:

- **`pre-session-start.sh`** - Exécuté au démarrage de chaque session Claude Code
  - Vérifie git status
  - Affiche les todos actifs
  - Vérifie la synchronisation des contextes

- **`pre-session-close.sh`** - Exécuté à la fermeture de session
  - Synchronise les contextes
  - Commit et push automatique (via @session-manager)

### Git Hooks (installation manuelle)

Ces hooks doivent être installés manuellement dans `.git/hooks/`:

- **`pre-commit`** - Hook anti-drift pour vérifier la cohérence avant commit
  - Vérifie agent count (6/7) cohérent dans tous les fichiers
  - Vérifie core tools count (15)
  - Vérifie que sync-context.sh est marqué obsolète
  - Vérifie que les symlinks existent
  - Vérifie que PROJECT-INDEX.md existe
  - Vérifie le format CHANGELOG.md

## 🔧 Installation des Hooks Git

```bash
# Depuis la racine de APP_HOME
./.claude/hooks/install-git-hooks.sh
```

Ou manuellement:
```bash
cp .claude/hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

## ✅ Test du Hook Pre-Commit

```bash
# Le hook s'exécute automatiquement à chaque commit
git commit -m "test"

# Pour bypass (NON RECOMMANDÉ)
git commit --no-verify -m "test"
```

## 🔍 Que Vérifie le Hook Pre-Commit?

1. **Agent count cohérent**
   - CLAUDE.md: "Agents actuels: 6/7"
   - PROJECT-INDEX.md: "6/7"
   - claude-code-agents/CLAUDE.md: "6/7"

2. **Core tools count**
   - core/bin/ contient 15 fichiers
   - PROJECT-INDEX.md mentionne "15 scripts"

3. **sync-context.sh obsolète**
   - Marqué comme obsolète dans la documentation

4. **Symlinks existent**
   - agents.md → CLAUDE.md
   - gemini.md → CLAUDE.md
   - opencode.md → CLAUDE.md
   - bin/ → core/bin/

5. **PROJECT-INDEX.md valide**
   - Fichier existe et n'est pas vide

6. **CHANGELOG.md format**
   - Suit le format Keep a Changelog (Added/Changed/Fixed/Removed)

## 🚨 Si le Hook Échoue

Le hook affichera exactement quelle vérification a échoué:

```
🔍 Vérification anti-drift...
   Checking agent count... ✗
   ERROR: Agent count drift detected!
   Expected: 6/7 in all files
   Found in CLAUDE.md: 0 occurrences
   ...
```

**Actions à prendre:**
1. Lire le message d'erreur
2. Corriger le drift détecté
3. Re-tenter le commit

**En cas d'urgence (déconseillé):**
```bash
git commit --no-verify -m "urgent fix"
```

## 📚 Documentation

- Claude Code hooks: https://docs.claude.com
- Git hooks: https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks
