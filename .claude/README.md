# Configuration Claude Code Synchronisée

Ce dossier contient toutes les configurations Claude Code synchronisées entre machines via APP_HOME.

## Structure

```
.claude/
├── agents/              # Agents personnalisés (@session-closer, @brutal-critic, etc.)
├── output-styles/       # Styles de sortie (research-mode, project-manager, etc.)
├── hooks/               # Hooks Git (pre-session-close.sh, etc.)
├── settings.local.json  # Paramètres locaux Claude Code
└── shell-config/        # Alias shell et configurations
    ├── aliases.sh       # Alias communs (ccm, claude-monitor, etc.)
    └── setup.sh         # Script d'installation automatique
```

## Utilisation

### Installation initiale sur une nouvelle machine

```bash
cd ~/Documents/APP_HOME/.claude
./shell-config/setup.sh
```

Ce script va :
1. Créer des symlinks de `~/.claude` vers `APP_HOME/.claude`
2. Ajouter les alias dans votre `.zshrc` ou `.bashrc`
3. Installer Claude Code Monitor si nécessaire

### Synchronisation

Tous les fichiers sont automatiquement synchronisés via votre système de sync de dossiers.

## Important

- **Ne pas modifier** `~/.claude` directement - modifier `APP_HOME/.claude` à la place
- Les symlinks pointent vers APP_HOME pour synchronisation automatique
- Relancer `./shell-config/setup.sh` après ajout d'alias ou de configs
