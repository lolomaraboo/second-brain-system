# Second Brain

Système de mémoire persistante pour Claude Code combinant Mem0 et Obsidian.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Second Brain                       │
├──────────────────────┬──────────────────────────────┤
│        Mem0          │         Obsidian             │
│  (Mémoire de travail)│    (Wiki permanent)          │
├──────────────────────┼──────────────────────────────┤
│ - Contexte rapide    │ - Documentation structurée   │
│ - Décisions récentes │ - Patterns réutilisables     │
│ - Bugs en cours      │ - Guides détaillés           │
│ - État du projet     │ - Décisions architecturales  │
└──────────────────────┴──────────────────────────────┘
```

## Composants

### Mem0 (MCP Server)
- API de mémoire sémantique
- Stockage par project_id
- Recherche intelligente
- Outils: `mem0_recall`, `mem0_save`, `mem0_search`

### Obsidian Vault
- Chemin: `~/Documents/APP_HOME/CascadeProjects/windsurf-project/SecondBrain/`
- Fichiers Markdown atomiques
- Liens entre notes `[[note]]`
- Chaque dossier a un `_INDEX.md`

## Décisions

- [[decisions/2025-12-01-start-command-memory-fix]] - Fix /start : Relecture CLAUDE.md obligatoire pour mémorisation auto (2025-12-01)
- [[decisions/2025-12-01-start-intelligent]] - /start intelligent avec mode rapide par défaut (2025-12-01)

## Améliorations

- [[../../wiki/improvements/2025-12-02-claude-md-consultation-priority|CLAUDE.md - Renforcement Règle de Consultation]] - Checklist critique + warnings (2025-12-02)

## Fichiers
- Voir [[second-brain|wiki/tools/second-brain]] pour le guide d'utilisation

## Liens
- Vault: ~/Documents/APP_HOME/CascadeProjects/windsurf-project/SecondBrain/
- Config Mem0: `<workspace>/.mcp.json` (dans le répertoire du projet)
