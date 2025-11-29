# Guide de Synchronisation Claude Code Multi-Machines

## 🎯 Objectif

Synchroniser automatiquement toutes les configurations Claude Code entre toutes vos machines via `APP_HOME` (~/Documents/APP_HOME).

## 📁 Architecture

```
~/Documents/APP_HOME/
├── .claude/                          # ← Configuration Claude Code synchronisée
│   ├── agents/                       # Agents personnalisés
│   │   ├── session-closer.md
│   │   ├── brutal-critic.md
│   │   ├── gemini-researcher.md
│   │   └── perplexity-researcher.md
│   ├── output-styles/                # Styles de sortie
│   │   ├── general-assistant.md
│   │   ├── research-mode.md
│   │   └── project-manager.md
│   ├── hooks/                        # Hooks Git
│   │   └── pre-session-close.sh
│   ├── shell-config/                 # Configurations shell
│   │   ├── aliases.sh               # ← Tous les alias ici
│   │   └── setup.sh                 # Script d'installation
│   ├── settings.local.json           # Settings Claude Code
│   ├── README.md                     # Documentation
│   └── SYNC-GUIDE.md                # Ce fichier
│
├── Claude-Code-Usage-Monitor/        # Outil de monitoring
│   ├── venv/                         # Virtual environment Python
│   └── src/
│
├── bin/                              # Scripts utilitaires
│   ├── ai                           # Routeur intelligent AI
│   ├── comet.sh                     # Comet automation
│   └── perplexity.sh                # Perplexity CLI
│
└── CLAUDE.md                         # Documentation projet

~/.claude → ~/Documents/APP_HOME/.claude  # ← Symlink automatique
```

## 🚀 Installation sur une nouvelle machine

### Prérequis

1. **APP_HOME synchronisé** sur la machine
   - Via iCloud, Dropbox, Syncthing, Git, etc.
   - Doit être dans `~/Documents/APP_HOME`

2. **Python 3.9+** installé
   ```bash
   # macOS avec Homebrew
   brew install python@3.13
   ```

3. **Node.js 18+** (pour Claude Code CLI)
   ```bash
   brew install node@18
   ```

### Étapes d'installation

```bash
# 1. Aller dans APP_HOME
cd ~/Documents/APP_HOME/.claude/shell-config

# 2. Lancer le script d'installation
./setup.sh
```

Le script va :
- ✅ Créer la structure de dossiers
- ✅ Sauvegarder votre `~/.claude` existant (si présent)
- ✅ Créer un symlink `~/.claude → APP_HOME/.claude`
- ✅ Ajouter les alias dans `.zshrc` ou `.bashrc`
- ✅ Installer Claude Code Monitor (si Python 3.9+ disponible)

### Activer la configuration

```bash
# Relancer le shell ou sourcer
source ~/.zshrc  # ou ~/.bashrc
```

## 🔧 Utilisation quotidienne

### Commandes disponibles

```bash
# Claude Code CLI
claude                    # Lance Claude Code

# Claude Code Monitor
ccm                       # Lance le monitor
ccmonitor                 # Alias alternatif
claude-monitor            # Nom complet

# Outils AI
ai "votre question"       # Routeur intelligent (Grok/Claude/Comet)
sync-context              # Sync claude.md, gemini.md, etc.

# Info
ai-info                   # Voir tous les alias disponibles
```

### Agents Claude Code

Dans Claude Code, utilisez :

```
@session-closer           # Ferme session et commit Git
@brutal-critic            # Critique à 3 perspectives
@gemini-researcher        # Recherche générale gratuite
@perplexity-researcher    # Recherche temps réel avec citations
```

### Output Styles

```
/output-style research-mode
/output-style project-manager
/output-style general-assistant
```

## 📝 Ajouter un nouvel alias

### Méthode 1 : Modifier aliases.sh (Recommandé)

```bash
# Éditer le fichier centralisé
nano ~/Documents/APP_HOME/.claude/shell-config/aliases.sh

# Ajouter votre alias
alias mon-alias='ma-commande'

# Recharger
source ~/.zshrc
```

### Méthode 2 : Modifier directement .zshrc (Non recommandé)

⚠️ **Attention** : Les changements dans `.zshrc` ne seront pas synchronisés entre machines.

## 🔄 Ajouter un nouvel agent

```bash
# 1. Créer le fichier dans APP_HOME (sera synchronisé)
nano ~/Documents/APP_HOME/.claude/agents/mon-agent.md

# 2. Le fichier sera automatiquement disponible dans Claude Code
#    via le symlink ~/.claude → APP_HOME/.claude

# 3. Utiliser dans Claude Code
@mon-agent votre requête
```

## 🎨 Ajouter un output style

```bash
# 1. Créer dans APP_HOME
nano ~/Documents/APP_HOME/.claude/output-styles/mon-style.md

# 2. Utiliser dans Claude Code
/output-style mon-style
```

## 🪝 Ajouter un hook

```bash
# 1. Créer dans APP_HOME
nano ~/Documents/APP_HOME/.claude/hooks/pre-commit.sh

# 2. Rendre exécutable
chmod +x ~/Documents/APP_HOME/.claude/hooks/pre-commit.sh

# 3. Le hook sera automatiquement utilisé par Claude Code
```

## 🔍 Vérifier la synchronisation

```bash
# Vérifier que le symlink existe
ls -lh ~/.claude
# Devrait afficher: ~/.claude -> ~/Documents/APP_HOME/.claude

# Vérifier les agents
ls ~/.claude/agents/

# Vérifier les alias
ai-info

# Tester ccm
ccm --version
```

## ⚙️ Configuration avancée

### Différences entre machines

Si une machine nécessite une configuration spécifique (ex: path Python différent), vous pouvez créer :

```bash
# Fichier local non synchronisé
nano ~/.zshrc.local

# Ajouter vos overrides
export PYTHON_CMD=/custom/path/python3.11

# Source dans .zshrc (après aliases.sh)
if [ -f ~/.zshrc.local ]; then
    source ~/.zshrc.local
fi
```

### Désinstallation

```bash
# 1. Supprimer le symlink
rm ~/.claude

# 2. Restaurer l'ancienne config (si backup existe)
mv ~/.claude.backup-YYYYMMDD-HHMMSS ~/.claude

# 3. Retirer les lignes de .zshrc
# (Supprimer la section "Claude Code - Configuration synchronisée")
```

## 🐛 Troubleshooting

### "ccm: command not found"

```bash
# 1. Vérifier que aliases.sh est sourcé
grep "aliases.sh" ~/.zshrc

# 2. Recharger le shell
source ~/.zshrc

# 3. Vérifier que le venv existe
ls ~/Documents/APP_HOME/Claude-Code-Usage-Monitor/venv
```

### "Python 3.9+ requis"

```bash
# Installer Python via Homebrew
brew install python@3.13

# Relancer setup.sh
~/Documents/APP_HOME/.claude/shell-config/setup.sh
```

### "~/.claude n'est pas un symlink"

```bash
# Le script setup.sh sauvegarde automatiquement
# Mais si problème, faire manuellement :

# 1. Sauvegarder
mv ~/.claude ~/.claude.backup-manual

# 2. Relancer setup
~/Documents/APP_HOME/.claude/shell-config/setup.sh
```

### Les agents n'apparaissent pas dans Claude Code

```bash
# 1. Vérifier le symlink
ls -lh ~/.claude

# 2. Vérifier que les fichiers existent
ls ~/.claude/agents/

# 3. Relancer Claude Code
```

## 📚 Documentation supplémentaire

- **README.md** : Vue d'ensemble de la structure
- **CLAUDE.md** : Documentation complète du projet
- **aliases.sh** : Liste de tous les alias (commenter avec `ai-info`)

## 🎯 Best Practices

1. **Toujours modifier APP_HOME/.claude**, jamais ~/.claude directement
2. **Commiter les changements** dans Git (si APP_HOME est versionné)
3. **Documenter les nouveaux alias** dans aliases.sh avec des commentaires
4. **Tester sur une machine** avant de synchroniser partout
5. **Garder setup.sh à jour** quand vous ajoutez des dépendances

## 🔄 Workflow de modification

```bash
# 1. Modifier la config
nano ~/Documents/APP_HOME/.claude/agents/mon-agent.md

# 2. Tester localement
@mon-agent test

# 3. Si APP_HOME est sous Git, commit
cd ~/Documents/APP_HOME
git add .claude/agents/mon-agent.md
git commit -m "Add mon-agent"
git push

# 4. Sur les autres machines
cd ~/Documents/APP_HOME
git pull
# Les changements sont immédiatement disponibles via le symlink !
```

---

**Dernière mise à jour** : 2025-11-03
**Version** : 1.0
