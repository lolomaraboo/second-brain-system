# Second Brain

Personal knowledge base for Claude Code sessions, combining Mem0 (working memory) and Obsidian (permanent wiki).

## Structure

```
SecondBrain/
├── projects/          # Notes par projet
├── wiki/
│   ├── patterns/      # Best practices
│   ├── tools/         # Documentation outils
│   ├── secrets/       # Annuaire secrets (PAS les valeurs!)
│   └── troubleshooting/
├── ideas/             # Brainstorming
├── daily/             # Notes quotidiennes
└── templates/         # Templates pour nouvelles notes
```

## Usage

| Commande | Action |
|----------|--------|
| `/start` | Charge le contexte (Mem0 + Obsidian) |
| `/end` | Sauvegarde le contexte |
| `/wiki [note]` | Ajoute une note au wiki |

## Rules

1. **Mem0** = automatique, sans confirmation
2. **Obsidian** = avec confirmation
3. **Secrets** = JAMAIS dans Obsidian, toujours dans .env
4. **Fichiers** = atomiques, max 50-100 lignes
5. **Index** = maintenu automatiquement par Claude

## Infrastructure

- Mem0 API: `http://31.220.104.244:8081`
- MCP Server: `~/scripts/mem0_mcp_server.py`
