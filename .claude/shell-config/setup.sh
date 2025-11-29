#!/bin/bash
# Script d'installation et synchronisation Claude Code - Version améliorée
# ~/Documents/APP_HOME/.claude/shell-config/setup.sh
# Vérifie et installe automatiquement tous les outils essentiels

set -e  # Exit on error

APP_HOME="$HOME/Documents/APP_HOME"
CLAUDE_SYNC="$APP_HOME/.claude"
CLAUDE_HOME="$HOME/.claude"

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "🚀 Configuration Claude Code - Synchronisation Multi-Machines"
echo "=============================================================="
echo ""

# ============================================
# 0. Vérifier et installer les outils essentiels
# ============================================
echo "🔍 Vérification des outils essentiels..."
echo ""

MISSING_TOOLS=()
INSTALL_NEEDED=false

# Fonction pour vérifier un outil
check_tool() {
    local tool=$1
    local name=$2
    local install_cmd=$3

    if command -v $tool &> /dev/null; then
        echo "   ✅ $name installé"
        return 0
    else
        echo "   ❌ $name manquant"
        MISSING_TOOLS+=("$name:$install_cmd")
        INSTALL_NEEDED=true
        return 1
    fi
}

# Vérifier Homebrew (requis pour installer les autres outils)
if ! command -v brew &> /dev/null; then
    echo "   ❌ Homebrew non installé"
    echo ""
    echo "⚠️  Homebrew est requis pour installer les outils manquants."
    echo "   Installer avec:"
    echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    echo ""
    read -p "Voulez-vous que je continue sans installer les outils manquants ? (o/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Oo]$ ]]; then
        exit 1
    fi
    BREW_AVAILABLE=false
else
    echo "   ✅ Homebrew installé"
    BREW_AVAILABLE=true
fi

# Vérifier Git
check_tool "git" "Git" "brew install git"

# Vérifier Python 3.9+
PYTHON_CMD=""
PYTHON_OK=false
for py in python3.13 python3.12 python3.11 python3.10 python3.9; do
    if command -v $py &> /dev/null; then
        PY_VERSION=$($py -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        if awk "BEGIN {exit !($PY_VERSION >= 3.9)}"; then
            echo "   ✅ Python $PY_VERSION installé ($py)"
            PYTHON_CMD=$py
            PYTHON_OK=true
            break
        fi
    fi
done

if [ "$PYTHON_OK" = false ]; then
    echo "   ❌ Python 3.9+ manquant"
    MISSING_TOOLS+=("Python 3.9+:brew install python@3.13")
    INSTALL_NEEDED=true
fi

# Vérifier Node.js (pour Claude Code CLI)
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "   ✅ Node.js installé ($NODE_VERSION)"
else
    echo "   ❌ Node.js manquant"
    MISSING_TOOLS+=("Node.js:brew install node@18")
    INSTALL_NEEDED=true
fi

# Vérifier npm
check_tool "npm" "npm" "brew install node@18"

# Vérifier gh (GitHub CLI) - optionnel mais recommandé
if command -v gh &> /dev/null; then
    echo "   ✅ GitHub CLI (gh) installé"
    GH_AVAILABLE=true
else
    echo "   ⚠️  GitHub CLI (gh) manquant (optionnel)"
    echo "      Utile pour: pousser vers GitHub facilement"
    MISSING_TOOLS+=("GitHub CLI (optionnel):brew install gh")
    GH_AVAILABLE=false
fi

# Proposer d'installer les outils manquants
if [ "$INSTALL_NEEDED" = true ] && [ "$BREW_AVAILABLE" = true ]; then
    echo ""
    echo "=============================================================="
    echo "⚠️  Outils manquants détectés"
    echo "=============================================================="
    echo ""
    for tool_info in "${MISSING_TOOLS[@]}"; do
        IFS=':' read -r tool_name install_cmd <<< "$tool_info"
        echo "   📦 $tool_name"
        echo "      → $install_cmd"
    done
    echo ""
    read -p "Voulez-vous installer les outils manquants automatiquement ? (O/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Oo]$ ]] || [[ -z $REPLY ]]; then
        echo ""
        echo "📥 Installation des outils manquants..."
        echo ""

        # Installer Python si manquant
        if [ "$PYTHON_OK" = false ]; then
            echo "   🐍 Installation de Python 3.13..."
            brew install python@3.13
            PYTHON_CMD=python3.13
        fi

        # Installer Node.js si manquant
        if ! command -v node &> /dev/null; then
            echo "   📦 Installation de Node.js..."
            brew install node@18
        fi

        # Installer Git si manquant
        if ! command -v git &> /dev/null; then
            echo "   🔧 Installation de Git..."
            brew install git
        fi

        # Installer gh si souhaité
        if [ "$GH_AVAILABLE" = false ]; then
            echo ""
            read -p "Installer GitHub CLI (gh) ? (recommandé) (O/n) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Oo]$ ]] || [[ -z $REPLY ]]; then
                echo "   🐙 Installation de GitHub CLI..."
                brew install gh 2>/dev/null || echo "   ⚠️  Installation de gh échouée (peut nécessiter macOS plus récent)"
            fi
        fi

        echo ""
        echo "✅ Installation des outils terminée"
    else
        echo ""
        echo "⚠️  Certaines fonctionnalités peuvent ne pas fonctionner sans ces outils."
    fi
fi

echo ""
echo "=============================================================="

# ============================================
# 1. Vérifier que APP_HOME existe
# ============================================
echo ""
if [ ! -d "$APP_HOME" ]; then
    echo "❌ Erreur: $APP_HOME n'existe pas"
    echo "💡 Créer ce dossier et le synchroniser entre vos machines"
    exit 1
fi

echo "✅ APP_HOME trouvé: $APP_HOME"

# ============================================
# 1.1 Détecter le système de synchronisation
# ============================================
echo ""
echo "🔍 Détection du système de synchronisation..."

SYNC_SYSTEM="inconnu"
if [ -d "$APP_HOME/.git" ]; then
    SYNC_SYSTEM="Git"
    echo "   ✅ Synchronisation via Git détectée"
elif find "$APP_HOME" -name "*.icloud" 2>/dev/null | grep -q .; then
    SYNC_SYSTEM="iCloud"
    echo "   ✅ Synchronisation via iCloud détectée"
elif [ -d "$APP_HOME/.dropbox" ] || [ -f "$APP_HOME/.dropbox.attr" ]; then
    SYNC_SYSTEM="Dropbox"
    echo "   ✅ Synchronisation via Dropbox détectée"
elif [ -d "$APP_HOME/.stfolder" ]; then
    SYNC_SYSTEM="Syncthing"
    echo "   ✅ Synchronisation via Syncthing détectée"
else
    echo "   ⚠️  Aucun système de synchronisation détecté"
    echo "   💡 Pour synchroniser entre machines, utilisez:"
    echo "      - Git (recommandé): git init && git remote add origin ..."
    echo "      - iCloud Drive: déplacez APP_HOME dans ~/Library/Mobile Documents/"
    echo "      - Dropbox/Syncthing/autre solution"
fi

# ============================================
# 1.2 Vérifier les fichiers essentiels
# ============================================
echo ""
echo "📋 Vérification des fichiers essentiels..."

REQUIRED_FILES=(
    ".claude/shell-config/aliases.sh"
    ".claude/shell-config/setup.sh"
)

REQUIRED_DIRS=(
    ".claude/agents"
    ".claude/output-styles"
    ".claude/hooks"
)

MISSING_FILES=()
MISSING_DIRS=()

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$APP_HOME/$file" ]; then
        MISSING_FILES+=("$file")
    fi
done

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ ! -d "$APP_HOME/$dir" ]; then
        MISSING_DIRS+=("$dir")
    fi
done

if [ ${#MISSING_FILES[@]} -gt 0 ] || [ ${#MISSING_DIRS[@]} -gt 0 ]; then
    echo "   ❌ APP_HOME semble incomplet ou non synchronisé"
    echo ""
    if [ ${#MISSING_FILES[@]} -gt 0 ]; then
        echo "   Fichiers manquants:"
        for file in "${MISSING_FILES[@]}"; do
            echo "      - $file"
        done
    fi
    if [ ${#MISSING_DIRS[@]} -gt 0 ]; then
        echo "   Dossiers manquants:"
        for dir in "${MISSING_DIRS[@]}"; do
            echo "      - $dir"
        done
    fi
    echo ""
    echo "   💡 Solutions:"
    if [ "$SYNC_SYSTEM" = "Git" ]; then
        echo "      - Vérifier: cd $APP_HOME && git pull"
        echo "      - Ou cloner: git clone <url> $APP_HOME"
    else
        echo "      - Vérifier que la synchronisation est complète"
        echo "      - Attendre la fin de la synchronisation"
        echo "      - Ou cloner depuis: https://github.com/lolomaraboo/claude-code-setup"
    fi
    echo ""
    read -p "   Continuer malgré les fichiers manquants ? (o/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Oo]$ ]]; then
        exit 1
    fi
else
    echo "   ✅ Tous les fichiers essentiels sont présents"
fi

# ============================================
# 1.3 Vérifier et synchroniser avec Git
# ============================================
if [ "$SYNC_SYSTEM" = "Git" ] && [ -d "$APP_HOME/.git" ]; then
    echo ""
    echo "🔄 Vérification de la synchronisation Git..."

    # Vérifier s'il y a un remote configuré
    if git -C "$APP_HOME" remote get-url origin &> /dev/null; then
        # Fetch les dernières modifications
        echo "   📥 Récupération des mises à jour..."
        git -C "$APP_HOME" fetch origin 2>/dev/null || echo "   ⚠️  Impossible de fetch (connexion réseau?)"

        # Vérifier si on est à jour
        LOCAL=$(git -C "$APP_HOME" rev-parse @ 2>/dev/null)
        REMOTE=$(git -C "$APP_HOME" rev-parse @{u} 2>/dev/null)
        BASE=$(git -C "$APP_HOME" merge-base @ @{u} 2>/dev/null)

        if [ "$LOCAL" = "$REMOTE" ]; then
            echo "   ✅ APP_HOME est à jour avec le remote"
        elif [ "$LOCAL" = "$BASE" ]; then
            echo "   ⚠️  Des mises à jour sont disponibles sur le remote"
            echo ""
            COMMITS_BEHIND=$(git -C "$APP_HOME" rev-list HEAD..@{u} --count 2>/dev/null)
            echo "   📊 $COMMITS_BEHIND commit(s) en retard"
            echo ""
            read -p "   Voulez-vous mettre à jour maintenant (git pull) ? (O/n) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Oo]$ ]] || [[ -z $REPLY ]]; then
                echo "   📥 Mise à jour en cours..."
                if git -C "$APP_HOME" pull; then
                    echo "   ✅ APP_HOME mis à jour avec succès"
                else
                    echo "   ❌ Erreur lors du git pull"
                    echo "   💡 Résoudre manuellement: cd $APP_HOME && git pull"
                    exit 1
                fi
            else
                echo "   ⚠️  Continuant avec la version locale (potentiellement obsolète)"
            fi
        elif [ "$REMOTE" = "$BASE" ]; then
            echo "   ⚠️  Vous avez des commits locaux non poussés"
            COMMITS_AHEAD=$(git -C "$APP_HOME" rev-list @{u}..HEAD --count 2>/dev/null)
            echo "   📊 $COMMITS_AHEAD commit(s) en avance"
            echo "   💡 Pensez à pousser: cd $APP_HOME && git push"
        else
            echo "   ⚠️  Les branches ont divergé (conflits possibles)"
            echo "   💡 Résoudre manuellement: cd $APP_HOME && git status"
        fi
    else
        echo "   ℹ️  Pas de remote Git configuré"
    fi
fi

# ============================================
# 2. Configurer Git si nécessaire
# ============================================
if command -v git &> /dev/null; then
    echo ""
    echo "🔧 Configuration Git..."

    GIT_NAME=$(git config --global user.name 2>/dev/null || echo "")
    GIT_EMAIL=$(git config --global user.email 2>/dev/null || echo "")

    if [ -z "$GIT_NAME" ] || [ -z "$GIT_EMAIL" ]; then
        echo "   ⚠️  Git n'est pas configuré"
        echo ""
        read -p "   Nom complet (pour Git): " git_name
        read -p "   Email (pour Git): " git_email

        git config --global user.name "$git_name"
        git config --global user.email "$git_email"
        echo "   ✅ Git configuré avec: $git_name <$git_email>"
    else
        echo "   ✅ Git déjà configuré: $GIT_NAME <$GIT_EMAIL>"
    fi

    # Vérifier si APP_HOME est un repo Git
    if [ -d "$APP_HOME/.git" ]; then
        echo "   ✅ APP_HOME est un repository Git"

        # Vérifier remote GitHub
        if git -C "$APP_HOME" remote get-url origin &> /dev/null; then
            REMOTE_URL=$(git -C "$APP_HOME" remote get-url origin)
            echo "   ✅ Remote configuré: $REMOTE_URL"
        else
            echo "   ⚠️  Aucun remote GitHub configuré"
            echo "   💡 Vous pouvez configurer un remote avec:"
            echo "      cd $APP_HOME"
            echo "      git remote add origin https://github.com/utilisateur/repo.git"
        fi
    else
        echo "   ℹ️  APP_HOME n'est pas un repository Git"
        echo "   💡 Pour versionner votre configuration:"
        echo "      cd $APP_HOME && git init && git add . && git commit -m 'Initial commit'"
    fi
fi

# ============================================
# 3. Créer la structure de dossiers
# ============================================
echo ""
echo "📁 Création de la structure de dossiers..."

mkdir -p "$CLAUDE_SYNC/agents"
mkdir -p "$CLAUDE_SYNC/output-styles"
mkdir -p "$CLAUDE_SYNC/hooks"
mkdir -p "$CLAUDE_SYNC/shell-config"

echo "✅ Structure créée dans $CLAUDE_SYNC"

# ============================================
# 4. Sauvegarder ~/.claude existant
# ============================================
if [ -d "$CLAUDE_HOME" ] && [ ! -L "$CLAUDE_HOME" ]; then
    echo ""
    echo "⚠️  ~/.claude existe déjà (pas un symlink)"
    echo "📦 Sauvegarde en cours..."

    BACKUP_DIR="$CLAUDE_HOME.backup-$(date +%Y%m%d-%H%M%S)"
    mv "$CLAUDE_HOME" "$BACKUP_DIR"
    echo "✅ Sauvegardé dans: $BACKUP_DIR"

    # Copier les fichiers importants vers APP_HOME
    if [ -d "$BACKUP_DIR/agents" ]; then
        echo "   → Copie agents..."
        cp -r "$BACKUP_DIR/agents/"* "$CLAUDE_SYNC/agents/" 2>/dev/null || true
    fi
    if [ -d "$BACKUP_DIR/output-styles" ]; then
        echo "   → Copie output-styles..."
        cp -r "$BACKUP_DIR/output-styles/"* "$CLAUDE_SYNC/output-styles/" 2>/dev/null || true
    fi
    if [ -d "$BACKUP_DIR/hooks" ]; then
        echo "   → Copie hooks..."
        cp -r "$BACKUP_DIR/hooks/"* "$CLAUDE_SYNC/hooks/" 2>/dev/null || true
    fi
fi

# ============================================
# 5. Créer symlink ~/.claude → APP_HOME/.claude
# ============================================
echo ""
echo "🔗 Création du symlink ~/.claude → $CLAUDE_SYNC"

if [ -L "$CLAUDE_HOME" ]; then
    echo "   ℹ️  Symlink existe déjà, suppression..."
    rm "$CLAUDE_HOME"
fi

ln -s "$CLAUDE_SYNC" "$CLAUDE_HOME"
echo "✅ Symlink créé"

# ============================================
# 6. Ajouter les alias au shell
# ============================================
echo ""
echo "🐚 Configuration du shell..."

# Détecter le shell
SHELL_RC=""
if [ -n "$ZSH_VERSION" ] || [ -f "$HOME/.zshrc" ]; then
    SHELL_RC="$HOME/.zshrc"
    SHELL_NAME="zsh"
elif [ -f "$HOME/.bashrc" ]; then
    SHELL_RC="$HOME/.bashrc"
    SHELL_NAME="bash"
else
    SHELL_RC="$HOME/.bash_profile"
    SHELL_NAME="bash"
fi

echo "   📝 Shell détecté: $SHELL_NAME ($SHELL_RC)"

# Vérifier si déjà configuré
if grep -q "APP_HOME/.claude/shell-config/aliases.sh" "$SHELL_RC" 2>/dev/null; then
    echo "   ✅ Alias déjà configurés dans $SHELL_RC"
else
    echo "   ➕ Ajout des alias dans $SHELL_RC"

    cat >> "$SHELL_RC" << 'EOF'

# ============================================
# Claude Code - Configuration synchronisée
# Source: APP_HOME/.claude/shell-config/aliases.sh
# ============================================
if [ -f "$HOME/Documents/APP_HOME/.claude/shell-config/aliases.sh" ]; then
    source "$HOME/Documents/APP_HOME/.claude/shell-config/aliases.sh"
fi
EOF

    echo "   ✅ Alias ajoutés"
fi

# ============================================
# 7. Installer Claude Code Monitor
# ============================================
echo ""
echo "📊 Installation Claude Code Monitor..."

CCM_DIR="$APP_HOME/Claude-Code-Usage-Monitor"

if [ ! -d "$CCM_DIR" ]; then
    echo "   ⚠️  Claude-Code-Usage-Monitor introuvable dans APP_HOME"
    echo ""
    read -p "   Voulez-vous cloner Claude-Code-Usage-Monitor ? (O/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Oo]$ ]] || [[ -z $REPLY ]]; then
        if command -v git &> /dev/null; then
            echo "   📥 Clonage de Claude-Code-Usage-Monitor..."
            git clone https://github.com/Maciek-roboblog/Claude-Code-Usage-Monitor.git "$CCM_DIR"
        else
            echo "   ❌ Git n'est pas installé, impossible de cloner"
            echo "   💡 Cloner manuellement depuis: https://github.com/Maciek-roboblog/Claude-Code-Usage-Monitor"
        fi
    fi
fi

if [ -d "$CCM_DIR" ] && [ -n "$PYTHON_CMD" ]; then
    # Créer venv si nécessaire
    if [ ! -d "$CCM_DIR/venv" ]; then
        echo "   📦 Création du virtual environment..."
        (cd "$CCM_DIR" && $PYTHON_CMD -m venv venv)
        echo "   📥 Installation des dépendances..."
        (cd "$CCM_DIR" && venv/bin/pip install --quiet --upgrade pip)
        (cd "$CCM_DIR" && venv/bin/pip install --quiet pytz rich pydantic pydantic-settings numpy pyyaml)
        echo "   ✅ Claude Code Monitor installé"
    else
        echo "   ✅ Virtual environment existe déjà"
    fi
elif [ -d "$CCM_DIR" ]; then
    echo "   ⚠️  Python 3.9+ requis mais non installé"
    echo "   💡 Installer Python avec: brew install python@3.13"
fi

# ============================================
# 8. Installer Claude Code CLI si nécessaire
# ============================================
if command -v npm &> /dev/null; then
    echo ""
    echo "💻 Vérification de Claude Code CLI..."

    if command -v claude &> /dev/null; then
        echo "   ✅ Claude Code CLI déjà installé"
    else
        echo "   ⚠️  Claude Code CLI non installé"
        read -p "   Voulez-vous installer Claude Code CLI ? (O/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Oo]$ ]] || [[ -z $REPLY ]]; then
            echo "   📥 Installation de Claude Code CLI..."
            npm install -g @anthropic-ai/claude-code
            echo "   ✅ Claude Code CLI installé"
        fi
    fi
fi

# ============================================
# 9. Résumé final
# ============================================
echo ""
echo "=============================================================="
echo "✨ Installation terminée !"
echo "=============================================================="
echo ""
echo "📂 Fichiers synchronisés:"
echo "   ~/.claude → $CLAUDE_SYNC"
echo ""
echo "🔧 Configuration disponible:"
echo "   - Agents: ~/.claude/agents/"
echo "   - Output styles: ~/.claude/output-styles/"
echo "   - Hooks: ~/.claude/hooks/"
echo ""
echo "💡 Commandes disponibles (après relance du shell):"
echo "   ccm                  # Claude Code Monitor"
echo "   claude               # Claude Code CLI"
echo "   ai-info              # Voir tous les alias"
echo "   sync-context         # Sync claude.md, gemini.md, etc."
echo ""
echo "🛠️  Outils installés:"
if command -v git &> /dev/null; then
    echo "   ✅ Git $(git --version | cut -d' ' -f3)"
fi
if [ -n "$PYTHON_CMD" ]; then
    PY_VER=$($PYTHON_CMD --version | cut -d' ' -f2)
    echo "   ✅ Python $PY_VER"
fi
if command -v node &> /dev/null; then
    echo "   ✅ Node.js $(node --version)"
fi
if command -v gh &> /dev/null; then
    echo "   ✅ GitHub CLI $(gh --version | head -1 | cut -d' ' -f3)"
fi
echo ""
echo "🔄 Pour activer les alias maintenant:"
echo "   source $SHELL_RC"
echo ""
echo "🚀 Prêt à l'emploi sur toutes vos machines synchronisées !"
echo ""

# ============================================
# Enregistrer cette machine dans .setup-status
# ============================================
HOSTNAME=$(hostname)
USERNAME=$(whoami)
SETUP_STATUS="$APP_HOME/.claude/.setup-status"

# Créer le fichier s'il n'existe pas
if [ ! -f "$SETUP_STATUS" ]; then
    cat > "$SETUP_STATUS" << 'EOF'
# Claude Code Setup Status
# Ce fichier mémorise l'état du setup sur chaque machine
# Format: hostname|username|date|version

# Machines configurées:
EOF
fi

# Ajouter cette machine si elle n'est pas déjà enregistrée
if ! grep -q "$HOSTNAME|$USERNAME" "$SETUP_STATUS" 2>/dev/null; then
    echo "$HOSTNAME|$USERNAME|$(date +%Y-%m-%d)|1.0" >> "$SETUP_STATUS"
    echo "📝 Machine enregistrée dans .setup-status"
    echo ""
fi
