# APP_HOME Architecture Review

**Date:** 2025-12-01
**Status:** 💡 Idée / TODO
**Priority:** Moyenne

## Problème actuel

La configuration APP_HOME avec symlinks **n'est pas active** sur cette machine:

- ❌ `~/.claude` n'est PAS un symlink vers `APP_HOME/.claude/`
- ❌ `~/.claude` est un vrai répertoire (non synchronisé)
- ❌ Message au startup: "CONFIGURATION CLAUDE CODE NON SYNCHRONISÉE"
- ❌ Fichiers `~/scripts/` et `~/.claude/` sont locaux uniquement

## Architecture actuelle vs cible

### Actuel (NON synchronisé)
```
~/.claude/              # Vrai répertoire, local
  ├── commands/
  ├── hooks/
  └── ...

~/scripts/              # Pas de repo git
  ├── mem0_mcp_server.py
  ├── weekly-doc-audit.sh
  └── ...

~/Documents/APP_HOME/   # Existe mais pas utilisé pour .claude
  └── .claude/          # Non utilisé
```

### Cible (Architecture documentée)
```
~/.claude → symlink vers APP_HOME/.claude/

~/Documents/APP_HOME/.claude/    # Source synchronisée (Git)
  ├── commands/
  ├── hooks/
  ├── shell-config/
  └── .setup-status

Synchronisation: Git / iCloud / Dropbox
```

## Impact

**Fichiers créés/modifiés non synchronisés:**
- `~/.claude/hooks/pre-commit` (modifié - check #8 doc validation)
- `~/.claude/commands/end.md` (modifié - Documentation Review)
- `~/scripts/weekly-doc-audit.sh` (créé - monitoring)
- `~/scripts/extract-obsidian-docs.py` (créé - extraction docs)

**Conséquence:**
- Ces modifications sont locales uniquement
- Pas de backup automatique
- Pas de sync multi-machines
- Risque de perte si machine crashe

## Actions à faire

### 1. Décider architecture finale

**Option A: Activer APP_HOME symlink (recommandé)**
- Exécuter `~/Documents/APP_HOME/.claude/shell-config/setup.sh`
- Migrer `.claude` actuel vers `APP_HOME/.claude/`
- Créer symlink `~/.claude → APP_HOME/.claude/`
- Synchroniser via Git

**Option B: Garder séparé mais versionner**
- Créer repo git pour `~/.claude/`
- Créer repo git pour `~/scripts/`
- Synchroniser manuellement

**Option C: Intégrer dans windsurf-project**
- Copier scripts dans `windsurf-project/scripts/`
- Copier config dans `windsurf-project/.claude/`
- Tout dans un seul repo

### 2. Clarifier relation Windsurf Project

**Questions:**
- Windsurf Project contient déjà `ClaudeCodeChampion/.claude/`
- Quelle est la relation entre:
  - `~/.claude/` (config globale)
  - `APP_HOME/.claude/` (sync multi-machines)
  - `windsurf-project/ClaudeCodeChampion/.claude/` (config projet?)
- Doit-on avoir une config par projet ou une config globale?

### 3. Migrer fichiers créés

Une fois architecture décidée:
- [ ] Copier/migrer `weekly-doc-audit.sh`
- [ ] Copier/migrer `extract-obsidian-docs.py`
- [ ] Migrer modifications `pre-commit` hook
- [ ] Migrer modifications `end.md` command
- [ ] Mettre à jour CODE-DOC-MAP.md avec nouveaux chemins

## Risques

- **Perte de données** si migration mal faite
- **Conflits** si fichiers existent déjà dans APP_HOME
- **Symlinks cassés** si APP_HOME déplacé
- **Confusion** sur quel fichier est la source de vérité

## Références

- [[claude-code-sync]] - Architecture APP_HOME documentée
- [[CODE-DOC-MAP]] - Mapping code→doc (chemins actuels)
- Hook startup: "CONFIGURATION CLAUDE CODE NON SYNCHRONISÉE"
- Setup script: `~/Documents/APP_HOME/.claude/shell-config/setup.sh`

## Prochaine session

Quand on reprendra ce sujet:
1. Lire ce fichier
2. Décider quelle option (A/B/C)
3. Faire backup de `~/.claude/` et `~/scripts/` avant migration
4. Exécuter migration
5. Tester que tout fonctionne
6. Mettre à jour documentation
