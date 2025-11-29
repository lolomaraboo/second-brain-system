# Configuration Claude Code Active

Configuration actuelle de Claude Code avec agents, hooks et slash commands.

## Agents (1)

### brutal-critic
Critique impitoyable avec 3 perspectives :
- **Technical Expert** : Structure, logique, précision
- **Audience Advocate** : UX, valeur, utilité
- **Strategic Thinker** : Big picture, ROI, alignement

**Score** : 1-10 (7+ = exceptionnel)
**Usage** : `@brutal-critic`

## Slash Commands (3)

| Commande | Description |
|----------|-------------|
| `/start` | Charge contexte Second Brain (Mem0 + Obsidian) |
| `/end` | Sauvegarde contexte session (Mem0 + Obsidian) |
| `/wiki [note]` | Ajoute une note au wiki Obsidian |

## Hooks (3)

### pre-compact.sh (TEST)
Exécuté avant compaction du contexte (quand contexte bas).

**Actions** :
- Affiche rappel de sauvegarder avec /end
- Log la date/heure de déclenchement

**Statut** : En test - à valider quand ça se déclenche exactement.

### pre-session-start.sh
Exécuté au démarrage de chaque session.

**Actions** :
1. Vérifie symlink ~/.claude → APP_HOME
2. Vérifie machine enregistrée
3. Check Git status (uncommited, unpushed)
4. Check submodules
5. Sync TodoWrite → TODO.md
6. Affiche todos actifs
7. Rappel `/start` pour Second Brain

### pre-session-close.sh
Exécuté à la fin de session.

**Actions** :
- Rappel de sauvegarder le contexte `/end`

## Settings

### settings.json (hooks)
```json
{
  "hooks": {
    "SessionStart": ["pre-session-start.sh"],
    "SessionEnd": ["pre-session-close.sh"]
  },
  "alwaysThinkingEnabled": true
}
```

## Emplacement des fichiers

| Type | Chemin |
|------|--------|
| Agents | `~/.claude/agents/*.md` |
| Hooks | `~/.claude/hooks/*.sh` |
| Commands | `~/.claude/commands/*.md` |
| Settings | `~/.claude/settings.json` |
| Permissions | `~/.claude/settings.local.json` |
| Global instructions | `~/.claude/CLAUDE.md` |

## Agents disponibles dans ClaudeCodeChampion (à tester)

Ces agents sont archivés dans ClaudeCodeChampion et peuvent être réintégrés si besoin :
- gemini-researcher
- perplexity-researcher
- session-manager
- setup-assistant
- systems-checker
- protocol-guardian (v2)

## Liens

- [[claude-code-tools]] : Outils MCP disponibles
- [[second-brain]] : Système Mem0 + Obsidian
