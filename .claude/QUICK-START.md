# 🚀 Quick Start - Configuration Claude Code Synchronisée

## ✅ Sur cette machine (Studio Maraboo)

Tout est déjà installé et fonctionnel !

### Commandes disponibles

```bash
# Claude Code Monitor
ccm                    # Lance le monitor
ccm --version          # Vérifier version (3.1.0)

# Claude Code CLI
claude                 # Lance Claude Code

# Agents (dans Claude Code)
@session-closer        # Ferme session et commit Git
@brutal-critic         # Critique à 3 perspectives
@gemini-researcher     # Recherche générale
@perplexity-researcher # Recherche temps réel

# Output Styles (dans Claude Code)
/output-style research-mode
/output-style project-manager
/output-style general-assistant

# Utilitaires
sync-context           # Sync claude.md, gemini.md, etc.
ai "question"          # Routeur intelligent AI
ai-info                # Voir tous les alias
```

### Fichiers de configuration

Tous dans `~/Documents/APP_HOME/.claude/` (synchronisé) :
- **agents/** : 4 agents personnalisés
- **output-styles/** : 3 styles de sortie
- **hooks/** : pre-session-close.sh
- **shell-config/aliases.sh** : Tous les alias

## 📱 Sur une nouvelle machine (marabook_m1 ou autre)

### Installation en 3 étapes

```bash
# 1. Assure-toi que APP_HOME est synchronisé
ls ~/Documents/APP_HOME/.claude
# Devrait montrer: agents/, output-styles/, hooks/, shell-config/

# 2. Lance le script d'installation
cd ~/Documents/APP_HOME/.claude/shell-config
./setup.sh

# 3. Recharge ton shell
source ~/.zshrc  # ou ~/.bashrc
```

C'est tout ! Tous tes alias, agents, et configurations sont maintenant disponibles.

## 🔍 Vérification rapide

```bash
# Vérifie le symlink
ls -lh ~/.claude
# Devrait afficher: ~/.claude -> /Users/ton-user/Documents/APP_HOME/.claude

# Vérifie les agents
ls ~/.claude/agents/
# Devrait montrer: 4 fichiers .md

# Teste ccm
ccm --version
# Devrait afficher: claude-monitor 3.1.0
```

## ✏️ Modifier une configuration

```bash
# Modifier un agent (sera synchronisé automatiquement)
nano ~/Documents/APP_HOME/.claude/agents/session-closer.md

# Ajouter un alias (sera synchronisé automatiquement)
nano ~/Documents/APP_HOME/.claude/shell-config/aliases.sh

# Recharger
source ~/.zshrc
```

## 📚 Documentation complète

- **SYNC-GUIDE.md** : Guide détaillé avec troubleshooting
- **README.md** : Vue d'ensemble de la structure
- **session-summary-2025-11-03.md** : Détails de cette session

## 🐛 Problèmes ?

### ccm ne fonctionne pas

```bash
# Vérifie Python 3.9+
python3 --version

# Réinstalle si besoin
cd ~/Documents/APP_HOME/.claude/shell-config
./setup.sh
```

### Agents n'apparaissent pas

```bash
# Vérifie le symlink
ls -lh ~/.claude

# Si pas un symlink, relance setup
cd ~/Documents/APP_HOME/.claude/shell-config
./setup.sh
```

### "command not found"

```bash
# Recharge le shell
source ~/.zshrc

# Ou ouvre un nouveau terminal
```

## 🎯 Prochaines étapes

1. **Tester sur marabook_m1** : Lancer `./setup.sh`
2. **Commit dans Git** :
   ```bash
   cd ~/Documents/APP_HOME
   git add .claude/
   git commit -m "Add multi-machine sync system"
   git push
   ```
3. **Profiter** : Toutes tes configs suivent partout ! 🎉
