# Configuration Claude Code Versionnée

Ce dossier contient une **copie versionnée** de la configuration Claude Code, sauvegardée dans Git pour historique et backup.

## Architecture

```
~/.claude/                           # ← MASTER (utilisé par Claude Code)
├── CLAUDE.md                        #    Configuration active
├── settings.json                    #    Paramètres
├── agents/                          #    Agents personnalisés
├── commands/                        #    Slash commands
├── hooks/                           #    Hooks de session
├── todos/                           #    Runtime (non versionné)
├── debug/                           #    Runtime (non versionné)
└── projects/                        #    Runtime (non versionné)

SecondBrain/.claude/                 # ← BACKUP VERSIONNÉ (ce dossier)
├── sync-config.sh                   #    Script de synchronisation
├── .gitignore                       #    Ignore les dossiers runtime
├── CLAUDE.md                        #    Copie versionnée
├── settings.json                    #    Copie versionnée
├── agents/                          #    Copie versionnée
├── commands/                        #    Copie versionnée
└── hooks/                           #    Copie versionnée
```

**Principe :**
- `~/.claude` reste l'emplacement actif que Claude Code utilise
- `SecondBrain/.claude/` est une copie versionnée des fichiers de config uniquement
- Le script `sync-config.sh` synchronise `~/.claude → SecondBrain/.claude/`

## Utilisation du script de synchronisation

### Synchronisation manuelle

```bash
# Se placer dans le dossier
cd ~/Documents/APP_HOME/CascadeProjects/windsurf-project/SecondBrain/.claude

# Forcer un sync complet (copie tous les fichiers)
./sync-config.sh --force

# Sync automatique (copie seulement si fichiers essentiels modifiés)
./sync-config.sh
```

### Détection intelligente

Le script ne synchronise **que si** des fichiers essentiels ont été modifiés depuis le dernier sync :
- `CLAUDE.md`
- `settings.json`
- Fichiers dans `agents/`
- Fichiers dans `commands/`
- Fichiers dans `hooks/`

Si aucun changement détecté, le script affiche un message et ne fait rien.

### Workflow de modification

1. Modifier un fichier dans `~/.claude/` (ex: ajouter un agent)
   ```bash
   nano ~/.claude/agents/mon-nouvel-agent.md
   ```

2. Synchroniser vers le backup versionné
   ```bash
   cd ~/Documents/APP_HOME/CascadeProjects/windsurf-project/SecondBrain/.claude
   ./sync-config.sh
   ```

3. Commit dans Git si changement important
   ```bash
   cd ~/Documents/APP_HOME/CascadeProjects/windsurf-project/SecondBrain
   git add .claude/
   git commit -m "Add mon-nouvel-agent"
   git push
   ```

## Fichiers versionnés vs ignorés

### ✅ Versionnés (dans Git)
- Fichiers de configuration : `CLAUDE.md`, `settings.json`, etc.
- Agents personnalisés : `agents/*.md`
- Slash commands : `commands/*.md`
- Hooks de session : `hooks/*.sh`
- Output styles : `output-styles/*.md`
- Shell config : `shell-config/*.sh`

### ❌ Ignorés (dans .gitignore)
- Dossiers runtime : `debug/`, `todos/`, `projects/`, `plans/`
- Fichiers temporaires : `history.jsonl`, `.last-sync`, `.DS_Store`
- Settings locaux : `settings.local.json`

## Important

- ⚠️ **NE JAMAIS supprimer ou déplacer `~/.claude`** - c'est le dossier actif de Claude Code
- ✅ Modifier les fichiers dans `~/.claude` normalement via Claude Code
- ✅ Utiliser `sync-config.sh` pour sauvegarder les changements
- ✅ Commit régulièrement pour garder un historique des modifications

## Restauration depuis le backup

Si `~/.claude` est perdu ou corrompu :

```bash
# Copier depuis le backup versionné
rsync -av SecondBrain/.claude/ ~/.claude/

# Recréer les dossiers runtime manquants
mkdir -p ~/.claude/{todos,debug,projects,plans,file-history,session-env}
```
