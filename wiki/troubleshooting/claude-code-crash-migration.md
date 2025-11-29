# Claude Code Crash lors migration ~/.claude

## Problème

**Date :** 2025-11-29
**Symptôme :** Claude Code crash avec erreur `ENOENT: no such file or directory, mkdir '/Users/marabook_m1/.claude/todos'`

## Cause

Tentative de migration de `~/.claude` vers `SecondBrain/.claude/` via symlink :
1. Suppression de `~/.claude` (dossier actif)
2. Création de `SecondBrain/.claude/`
3. Création symlink `~/.claude → SecondBrain/.claude/`
4. Claude Code essaie de créer dossiers runtime (todos/, debug/, projects/)
5. **CRASH** car structure incomplète

## Erreur fondamentale

⚠️ **NE JAMAIS supprimer/déplacer `~/.claude`** - c'est le dossier ACTIF de Claude Code qui a besoin de :
- Fichiers de config (CLAUDE.md, settings.json, agents/, commands/, hooks/)
- Dossiers runtime (todos/, debug/, projects/, plans/, file-history/, session-env/)

## Solution

**Architecture finale :**
```
~/.claude/                    ← MASTER (ne JAMAIS toucher)
  ├── Config files
  └── Runtime directories

SecondBrain/.claude/          ← BACKUP VERSIONNÉ (Git)
  ├── sync-config.sh
  ├── Config files only
  └── .gitignore (ignore runtime)
```

**Script de synchronisation :**
- `sync-config.sh` : Détection intelligente des changements
- Sync unidirectionnel : `~/.claude → SecondBrain/.claude/`
- Ignore les dossiers runtime (debug/, todos/, etc.)

## Leçon critique

**RÈGLE D'OR :** `~/.claude` reste l'emplacement actif. Pour versionner, créer un BACKUP séparé et synchroniser régulièrement, ne PAS utiliser de symlink.

## Résultat

- ✅ Claude Code fonctionne normalement
- ✅ Configuration versionnée dans Git (lolomaraboo/SecondBrain)
- ✅ Sync facile avec script automatique
- ✅ Historique des changements préservé

## Commits

- `763c722` - feat: Add Claude Code config versioning with smart sync script
- `7897377` - docs: Update README with sync-config.sh usage guide
