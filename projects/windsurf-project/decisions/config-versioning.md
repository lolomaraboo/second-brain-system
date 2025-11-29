# Décision : Versionnement de la configuration Claude Code

## Contexte

**Date :** 2025-11-29
**Problème :** Configuration Claude Code (~/.claude/) non versionnée, risque de perte en cas de crash système

## Décision

Créer un système de backup versionné pour la configuration Claude Code dans le repo SecondBrain.

## Architecture retenue

```
~/.claude/                           ← SOURCE (Master)
├── CLAUDE.md
├── settings.json
├── agents/
├── commands/
├── hooks/
├── todos/                          (runtime - ignoré)
├── debug/                          (runtime - ignoré)
└── projects/                       (runtime - ignoré)

SecondBrain/.claude/                 ← BACKUP (Git)
├── sync-config.sh                  (script de sync)
├── .gitignore                      (ignore runtime)
├── CLAUDE.md                       (copie versionnée)
├── settings.json
├── agents/
├── commands/
└── hooks/
```

## Principe

- `~/.claude` reste l'emplacement actif (Claude Code l'utilise)
- `SecondBrain/.claude/` est une copie versionnée
- Sync unidirectionnel : `~/.claude → SecondBrain/.claude/`
- Script intelligent détecte changements avant de synchroniser

## Script sync-config.sh

**Fonctionnalités :**
- Détection changements : vérifie si fichiers essentiels modifiés depuis dernier sync
- Fichiers surveillés : CLAUDE.md, settings.json, agents/*.md, commands/*.md, hooks/*.sh
- Mode force : `--force` pour forcer sync complet
- Rsync avec filtres : copie seulement les fichiers de config, ignore runtime

**Usage :**
```bash
cd ~/Documents/APP_HOME/CascadeProjects/windsurf-project/SecondBrain/.claude
./sync-config.sh         # Auto (si changements détectés)
./sync-config.sh --force # Force sync complet
```

## Alternatives rejetées

### Option A : Symlink ~/.claude → SecondBrain/.claude/
**Rejetée** car :
- Nécessite que SecondBrain/.claude/ contienne TOUS les dossiers (y compris runtime)
- Risque de crash si structure incomplète
- Mélange config versionnée et données runtime

### Option B : Repo dédié claude-config
**Rejetée** car :
- Un repo supplémentaire à gérer
- Documentation séparée de la config
- SecondBrain est le bon endroit (système de mémoire)

## Avantages

- ✅ Historique Git complet des changements de config
- ✅ Backup automatique sur GitHub
- ✅ Aucun risque pour ~/.claude (reste intact)
- ✅ Sync manuel ou automatisable (hooks)

## Inconvénients

- ⚠️ Nécessite exécution manuelle du script (ou hook)
- ⚠️ Possible divergence si sync oublié
- ⚠️ Source of truth : ~/.claude (mais Git fait référence)

## Résultat

- 23 fichiers de config versionnés
- Repo GitHub : lolomaraboo/SecondBrain
- Commits : `763c722` (config) + `7897377` (docs)

## Statut

✅ **Implémenté et testé** - 2025-11-29
