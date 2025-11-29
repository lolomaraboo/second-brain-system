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

## Fichiers
- Voir [[second-brain|wiki/tools/second-brain]] pour le guide d'utilisation

## Liens
- Vault: ~/Documents/APP_HOME/CascadeProjects/windsurf-project/SecondBrain/
- Config Mem0: ~/.claude/mcp.json
