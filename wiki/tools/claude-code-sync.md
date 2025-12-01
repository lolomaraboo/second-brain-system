# Claude Code - Synchronisation Multi-Machines

**Statut:** ✅ PRODUCTION

## Vue d'ensemble

Système de synchronisation de configuration Claude Code entre plusieurs machines via APP_HOME.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Machine 1                            │
│  ~/.claude (symlink) → APP_HOME/.claude                │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │      APP_HOME        │ ← Synchronisé (Git/iCloud/Dropbox)
        │  .claude/            │
        │    agents/           │
        │    commands/         │
        │    hooks/            │
        │    shell-config/     │
        └──────────┬───────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│                    Machine 2                            │
│  ~/.claude (symlink) → APP_HOME/.claude                │
└─────────────────────────────────────────────────────────┘
```

## Composants

### APP_HOME

**Location:** `~/Documents/APP_HOME/`

**Rôle:** Dossier synchronisé entre machines contenant la configuration Claude Code.

**Synchronisation supportée:**
- Git (recommandé)
- iCloud Drive
- Dropbox
- Syncthing

### Structure APP_HOME/.claude/

```
APP_HOME/.claude/
├── agents/              # Agents personnalisés
├── commands/            # Slash commands (/start, /end, /wiki)
├── hooks/               # Hooks système (pre-session-start, etc.)
├── shell-config/        # Configuration shell
│   ├── setup.sh         # Script installation multi-machines
│   └── aliases.sh       # Alias shell
├── output-styles/       # Styles de sortie
├── .setup-status        # Registre machines configurées
└── CLAUDE.md            # Instructions globales
```

### Symlink ~/.claude

**Rôle:** Lien symbolique de `~/.claude` vers `APP_HOME/.claude`

**Bénéfice:**
- Claude Code lit toujours `~/.claude/`
- Mais le contenu vient de `APP_HOME/.claude/` synchronisé
- Configuration identique sur toutes les machines

### .setup-status

**Location:** `APP_HOME/.claude/.setup-status`

**Rôle:** Registre des machines configurées avec ce système.

**Format:**
```
# Claude Code Setup Status
# Format: hostname|username|date|version

# Machines configurées:
MacBook-Pro.local|user|2025-11-28|1.0
iMac.local|user|2025-11-29|1.0
```

**Usage:**
- Créé/mis à jour par `setup.sh`
- Vérifié par `pre-session-start.sh` hook
- Permet de tracker quelle machine a quel setup

## Installation sur nouvelle machine

### Méthode automatique

```bash
cd ~/Documents/APP_HOME/.claude/shell-config
./setup.sh
```

Le script `setup.sh` :
1. Vérifie et installe outils essentiels (Git, Python, Node.js)
2. Détecte le système de synchronisation (Git/iCloud/Dropbox)
3. Vérifie présence fichiers essentiels
4. Synchronise avec Git si configuré
5. Sauvegarde ~/.claude existant (backup)
6. Crée symlink ~/.claude → APP_HOME/.claude
7. Configure shell (.zshrc/.bashrc)
8. Installe Claude Code Monitor (optionnel)
9. Enregistre machine dans .setup-status

### Méthode manuelle

```bash
# 1. Créer symlink
mv ~/.claude ~/.claude.backup  # Si existe déjà
ln -s ~/Documents/APP_HOME/.claude ~/.claude

# 2. Configurer shell
echo 'source ~/Documents/APP_HOME/.claude/shell-config/aliases.sh' >> ~/.zshrc

# 3. Enregistrer machine
echo "$(hostname)|$(whoami)|$(date +%Y-%m-%d)|1.0" >> ~/Documents/APP_HOME/.claude/.setup-status

# 4. Recharger shell
source ~/.zshrc
```

## Hook de vérification

**Fichier:** `~/.claude/hooks/pre-session-start.sh`

**Exécuté:** À chaque démarrage de session Claude Code

**Vérifications:**
- ✅ ~/.claude est un symlink vers APP_HOME
- ✅ Machine enregistrée dans .setup-status
- ⚠️ Git status (uncommitted, unpushed)
- ⚠️ Submodules status
- 🧠 Rappel Second Brain (/start)

**Message si non configuré:**
```
⚠️  CONFIGURATION CLAUDE CODE NON SYNCHRONISÉE
Cette machine n'est pas encore configurée pour utiliser
la synchronisation multi-machines.

🔧 Pour configurer cette machine, exécutez:
   cd ~/Documents/APP_HOME/.claude/shell-config
   ./setup.sh
```

## Workflow de synchronisation

### Avec Git (recommandé)

```bash
# Machine 1: Modifier config
cd ~/Documents/APP_HOME
git add .claude/
git commit -m "feat: add new agent"
git push

# Machine 2: Récupérer changements
cd ~/Documents/APP_HOME
git pull

# Hook pre-session-start détecte automatiquement si git pull nécessaire
```

### Avec iCloud/Dropbox

Synchronisation automatique en arrière-plan.

**Vérification:**
```bash
# Vérifier que APP_HOME est dans le dossier synchronisé
ls -la ~/Documents/APP_HOME/.claude/
```

## Fichiers synchronisés vs locaux

### Synchronisés (dans APP_HOME/.claude/)

- `agents/` - Agents personnalisés
- `commands/` - Slash commands
- `hooks/` - Hooks système
- `shell-config/` - Config shell
- `output-styles/` - Styles
- `CLAUDE.md` - Instructions
- `.setup-status` - Registre machines

### Locaux (dans ~/.claude/)

Ces fichiers sont **locaux** à chaque machine et **ne sont pas synchronisés** :

- `history.jsonl` - Historique sessions
- `session-env/` - Environnement sessions
- `todos/` - TodoWrite state
- `plans/` - Plans en cours
- `file-history/` - Historique fichiers
- `settings.json` / `settings.local.json` - Settings
- `mem0_*.json` - Fichiers Mem0 queue
- `logs/` - Logs

**Raison:** Ces fichiers contiennent l'état local de la machine et ne doivent pas être synchronisés.

## Troubleshooting

### Symlink cassé

**Symptôme:** `~/.claude` pointe vers un dossier qui n'existe pas

**Solution:**
```bash
rm ~/.claude
ln -s ~/Documents/APP_HOME/.claude ~/.claude
```

### APP_HOME pas synchronisé

**Symptôme:** Changements sur Machine 1 n'apparaissent pas sur Machine 2

**Diagnostic:**
```bash
# Vérifier système sync
cd ~/Documents/APP_HOME
git status  # Si Git

# Vérifier iCloud
find ~/Documents/APP_HOME -name "*.icloud"  # Si iCloud
```

**Solution:**
```bash
# Git
cd ~/Documents/APP_HOME && git pull

# iCloud: attendre sync ou forcer download
# Dropbox: vérifier status icône
```

### Hook non exécuté

**Symptôme:** Hook pre-session-start.sh ne s'exécute pas

**Diagnostic:**
```bash
# Vérifier permissions
ls -la ~/.claude/hooks/pre-session-start.sh

# Doit être exécutable
-rwx--x--x  1 user  staff  7113 Nov 29 00:40 pre-session-start.sh
```

**Solution:**
```bash
chmod +x ~/.claude/hooks/pre-session-start.sh
```

## Références

- [[hooks]] - Documentation hooks système
- [[slash-commands]] - Documentation slash commands
- Code: `~/Documents/APP_HOME/.claude/shell-config/setup.sh`
- Hook: `~/.claude/hooks/pre-session-start.sh`
