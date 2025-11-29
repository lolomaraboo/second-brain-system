# Claude Code Champion v4

Framework d'automatisation pour Claude Code.

## Composants

### CLI (26 commandes)
- `ccc index` - Indexation des projets
- `ccc classify` - Classification automatique
- `ccc verify` - Vérification pré-modification
- `ccc doc` - Documentation automatique
- `ccc protocols` - Gestion des protocols
- `ccc setup-project` - Initialisation projet

### 6 Protocols
1. **Classification** - Détection type de projet
2. **Vérification** - Fichiers critiques, backups
3. **Anti-duplication** - SQLite FTS5, 70% similarité
4. **Documentation** - CHANGELOG, session summaries
5. **Adaptatif** - Patterns multi-fenêtres
6. **Setup** - Initialisation projets

### Agents
- `brutal-critic.md` - 4 critiques (technique, UX, stratégie, performance)
- `session-manager.md` - Gestion sessions
- `protocol-guardian.md` - Validation protocols
- `systems-checker.md` - Vérification système

### Hooks
- `SessionStart.sh` / `SessionEnd.sh`
- `pre-file-modify.sh` - Sécurité fichiers
- `checkpoint-context.sh` - Sauvegarde contexte

## Stats

- 451 fichiers
- 129k lignes de code
- Architecture: Event Bus + DI Container

## Fichiers

- Aucune décision documentée pour l'instant

## Liens

- Repo: [lolomaraboo/claude-code-champion-v4](https://github.com/lolomaraboo/claude-code-champion-v4)
- Chemin: `~/Documents/APP_HOME/CascadeProjects/windsurf-project/ClaudeCodeChampion`
