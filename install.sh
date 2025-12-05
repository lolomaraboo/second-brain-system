#!/bin/bash

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

# Configuration
QDRANT_CONTAINER="qdrant-secondbrain"
QDRANT_PORT=6333
CLAUDE_DIR="$HOME/.claude"
SCRIPTS_DIR="$HOME/scripts"
DEFAULT_MEMORIES_DIR="$HOME/Memories/memories"

# Functions
print_header() {
    echo ""
    echo -e "${BOLD}${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}${BLUE}  $1${NC}"
    echo -e "${BOLD}${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${BLUE}→${NC} $1"
}

check_prereq() {
    local cmd=$1
    local name=$2
    local install_url=$3

    if command -v "$cmd" &> /dev/null; then
        return 0
    else
        print_error "$name is not installed"
        echo "  Install from: $install_url"
        return 1
    fi
}

# ============================================================================
# WELCOME
# ============================================================================

clear
cat << "EOF"
   ____                      _   ____            _
  / ___|  ___  ___ ___ _ __ __| | | __ ) _ __ __ _(_)_ __
  \___ \ / _ \/ __/ _ \ '_ / _` | |  _ \| '__/ _` | | '_ \
   ___) |  __/ (_| (_) | | (_| | | |_) | | | (_| | | | | |
  |____/ \___|\___\___/|_|\__,_| |____/|_|  \__,_|_|_| |_|

EOF

echo -e "${BOLD}Automatic Installation Script${NC}"
echo ""
echo "This script will automatically install and configure Second Brain."
echo "You'll only need to provide your OpenAI API key."
echo ""
print_info "Installation takes ~2-3 minutes"
echo ""

read -p "Press ENTER to start..."

# ============================================================================
# STEP 1: Check Prerequisites
# ============================================================================

print_header "Step 1/7: Checking Prerequisites"

PREREQ_OK=true

if ! check_prereq python3 "Python 3.9+" "https://www.python.org/downloads/"; then
    PREREQ_OK=false
fi

if ! check_prereq docker "Docker" "https://docs.docker.com/get-docker/"; then
    PREREQ_OK=false
else
    if ! docker ps &> /dev/null; then
        print_error "Docker is installed but not running. Please start Docker."
        PREREQ_OK=false
    else
        print_success "Docker is running"
    fi
fi

if ! check_prereq git "Git" "https://git-scm.com/downloads"; then
    PREREQ_OK=false
fi

if [ "$PREREQ_OK" = false ]; then
    echo ""
    print_error "Please install missing dependencies and run again."
    exit 1
fi

print_success "All prerequisites satisfied"

# ============================================================================
# STEP 2: Clean Previous Installation (Auto)
# ============================================================================

print_header "Step 2/7: Cleaning Previous Memories"

CLEANED=false

if [ -d "qdrant_storage" ] && [ "$(ls -A qdrant_storage 2>/dev/null)" ]; then
    print_warning "Found existing Qdrant storage (previous user's memories)"
    print_info "Cleaning automatically (you'll create your own)..."
    rm -rf qdrant_storage/*
    CLEANED=true
fi

# Stop and remove existing container if present
if docker ps -a --format '{{.Names}}' | grep -q "^${QDRANT_CONTAINER}$"; then
    print_info "Removing existing Qdrant container..."
    docker stop "$QDRANT_CONTAINER" >/dev/null 2>&1 || true
    docker rm "$QDRANT_CONTAINER" >/dev/null 2>&1 || true
    CLEANED=true
fi

if [ "$CLEANED" = true ]; then
    print_success "Clean installation ready"
else
    print_success "No cleanup needed"
fi

# ============================================================================
# STEP 3: Install Qdrant (Auto)
# ============================================================================

print_header "Step 3/7: Installing Qdrant Vector Store"

print_info "Starting Qdrant container on port $QDRANT_PORT..."

docker run -d \
    --name "$QDRANT_CONTAINER" \
    -p "$QDRANT_PORT:6333" \
    -v "$(pwd)/qdrant_storage:/qdrant/storage" \
    --restart unless-stopped \
    qdrant/qdrant:latest >/dev/null

sleep 3

if curl -s "http://localhost:$QDRANT_PORT" > /dev/null; then
    print_success "Qdrant running on http://localhost:$QDRANT_PORT"
else
    print_error "Qdrant failed to start"
    exit 1
fi

# ============================================================================
# STEP 4: Configure OpenAI API (Interactive)
# ============================================================================

print_header "Step 4/7: Configure OpenAI API Key"

mkdir -p "$CLAUDE_DIR"

NEED_API_KEY=true

if [ -f "$CLAUDE_DIR/.env" ] && grep -q "OPENAI_API_KEY=sk-" "$CLAUDE_DIR/.env"; then
    EXISTING_KEY=$(grep "OPENAI_API_KEY=" "$CLAUDE_DIR/.env" | cut -d'=' -f2 | cut -c1-10)
    print_success "Found existing API key: ${EXISTING_KEY}..."
    NEED_API_KEY=false
fi

if [ "$NEED_API_KEY" = true ]; then
    echo ""
    echo "You need an OpenAI API key for text embeddings."
    echo "Get one at: ${BLUE}https://platform.openai.com/api-keys${NC}"
    echo ""

    while true; do
        read -p "Enter your OpenAI API key: " -s OPENAI_KEY
        echo ""

        if [[ $OPENAI_KEY == sk-* ]]; then
            # Remove old key if exists
            if [ -f "$CLAUDE_DIR/.env" ]; then
                sed -i.bak '/OPENAI_API_KEY=/d' "$CLAUDE_DIR/.env"
            fi
            echo "OPENAI_API_KEY=$OPENAI_KEY" >> "$CLAUDE_DIR/.env"
            print_success "API key saved to $CLAUDE_DIR/.env"
            break
        else
            print_error "Invalid API key format (should start with 'sk-')"
        fi
    done
fi

# ============================================================================
# STEP 5: Install Python Packages (Auto)
# ============================================================================

print_header "Step 5/7: Installing Python Packages"

print_info "Installing mem0ai, requests, openai, watchdog..."
pip3 install -q --upgrade mem0ai requests openai watchdog 2>&1 | grep -v "already satisfied" || true

if python3 -c "import mem0, requests, openai, watchdog" 2>/dev/null; then
    MEM0_VERSION=$(python3 -c "import mem0; print(mem0.__version__)" 2>/dev/null)
    print_success "Python packages installed (mem0 v$MEM0_VERSION)"
else
    print_error "Package installation failed"
    exit 1
fi

# ============================================================================
# STEP 6: Configure MCP & Claude (Auto)
# ============================================================================

print_header "Step 6/7: Configuring Claude Code Integration"

# 1. Copy MCP server
mkdir -p "$SCRIPTS_DIR"
if [ -f "scripts/mem0_mcp_server_local.py" ]; then
    cp scripts/mem0_mcp_server_local.py "$SCRIPTS_DIR/"
    chmod +x "$SCRIPTS_DIR/mem0_mcp_server_local.py"
    print_success "MCP server installed to $SCRIPTS_DIR/"
fi

# 2. Configure MCP automatically
MCP_CONFIG="$CLAUDE_DIR/mcp.json"
mkdir -p "$CLAUDE_DIR"

if [ ! -f "$MCP_CONFIG" ]; then
    # Create new config
    cat > "$MCP_CONFIG" << EOF
{
  "mcpServers": {
    "mem0": {
      "command": "/usr/bin/python3",
      "args": ["$SCRIPTS_DIR/mem0_mcp_server_local.py"]
    }
  }
}
EOF
    print_success "MCP configuration created"
else
    # Update existing config if mem0 not present
    if ! grep -q '"mem0"' "$MCP_CONFIG"; then
        print_info "Adding mem0 to existing MCP config..."
        # Simple append (assumes valid JSON structure)
        python3 << EOF
import json
with open('$MCP_CONFIG', 'r') as f:
    config = json.load(f)
if 'mcpServers' not in config:
    config['mcpServers'] = {}
config['mcpServers']['mem0'] = {
    'command': '/usr/bin/python3',
    'args': ['$SCRIPTS_DIR/mem0_mcp_server_local.py']
}
with open('$MCP_CONFIG', 'w') as f:
    json.dump(config, f, indent=2)
EOF
        print_success "MCP configuration updated"
    else
        print_success "MCP already configured"
    fi
fi

# 3. Copy Claude commands and hooks
print_info "Installing slash commands and hooks..."

mkdir -p "$CLAUDE_DIR/commands" "$CLAUDE_DIR/hooks"

if [ -d "claude-config/commands" ]; then
    cp -f claude-config/commands/*.md "$CLAUDE_DIR/commands/" 2>/dev/null || true
fi

if [ -d "claude-config/hooks" ]; then
    cp -f claude-config/hooks/*.md "$CLAUDE_DIR/hooks/" 2>/dev/null || true
fi

if [ -f "claude-config/CLAUDE.md" ]; then
    cp -f claude-config/CLAUDE.md "$CLAUDE_DIR/"
fi

print_success "Claude Code integration complete"

# ============================================================================
# STEP 7: Install Filesystem Watcher (Auto) - Phase 2
# ============================================================================

print_header "Step 7/8: Installing Phase 2 - Obsidian Filesystem Watcher"

# Get project root (where Memories/ vault is located)
if [ -z "$PROJECT_ROOT" ]; then
    # Try to detect project root from current directory
    if [ -d "$(pwd)/Memories/vault" ]; then
        PROJECT_ROOT="$(pwd)"
    elif [ -d "$HOME/Documents/APP_HOME/CascadeProjects/windsurf-project/Memories/vault" ]; then
        PROJECT_ROOT="$HOME/Documents/APP_HOME/CascadeProjects/windsurf-project"
    else
        print_warning "Cannot find Memories/vault directory"
        read -p "Enter path to project root (where Memories/ is located): " PROJECT_ROOT
    fi
fi

print_info "Project root: $PROJECT_ROOT"

# Create logs directory
mkdir -p "$PROJECT_ROOT/SecondBrain/logs"
print_success "Created logs directory"

# Copy filesystem watcher script
if [ -f "scripts/obsidian_vault_watcher.py" ]; then
    cp scripts/obsidian_vault_watcher.py "$PROJECT_ROOT/SecondBrain/scripts/"
    chmod +x "$PROJECT_ROOT/SecondBrain/scripts/obsidian_vault_watcher.py"
    print_success "Filesystem watcher installed"
else
    print_warning "obsidian_vault_watcher.py not found (skip watcher)"
fi

# Install LaunchAgent for 24/7 watcher
if [ -f "$PROJECT_ROOT/SecondBrain/scripts/obsidian_vault_watcher.py" ]; then
    PLIST_PATH="$HOME/Library/LaunchAgents/com.secondbrain.obsidian-watcher.plist"

    cat > "$PLIST_PATH" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.secondbrain.obsidian-watcher</string>

    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>$PROJECT_ROOT/SecondBrain/scripts/obsidian_vault_watcher.py</string>
    </array>

    <key>RunAtLoad</key>
    <true/>

    <key>KeepAlive</key>
    <true/>

    <key>StandardOutPath</key>
    <string>$PROJECT_ROOT/SecondBrain/logs/obsidian-watcher.log</string>

    <key>StandardErrorPath</key>
    <string>$PROJECT_ROOT/SecondBrain/logs/obsidian-watcher.error.log</string>

    <key>WorkingDirectory</key>
    <string>$PROJECT_ROOT</string>

    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    </dict>
</dict>
</plist>
EOF

    # Load LaunchAgent
    launchctl unload "$PLIST_PATH" 2>/dev/null || true
    launchctl load "$PLIST_PATH" 2>/dev/null

    sleep 2

    # Check if running
    if launchctl list | grep -q "com.secondbrain.obsidian-watcher"; then
        print_success "Filesystem watcher service running (24/7)"
    else
        print_warning "Watcher installed but not running (check logs)"
    fi
else
    print_info "Skipping LaunchAgent (watcher script not found)"
fi

# ============================================================================
# STEP 8: Create Project Structure (Auto)
# ============================================================================

print_header "Step 8/8: Setting Up Project Structure"

MEMORIES_DIR="$DEFAULT_MEMORIES_DIR"

if [ ! -d "$MEMORIES_DIR" ]; then
    mkdir -p "$MEMORIES_DIR"
    print_success "Created memories directory: $MEMORIES_DIR"
else
    print_success "Memories directory exists: $MEMORIES_DIR"
fi

# Create test project
TEST_PROJECT="$MEMORIES_DIR/test-project"
mkdir -p "$TEST_PROJECT"
print_info "Created test project: test-project"

# ============================================================================
# INSTALLATION COMPLETE
# ============================================================================

print_header "✨ Installation Complete!"

echo ""
echo -e "${GREEN}${BOLD}Your Second Brain is ready!${NC}"
echo ""
echo -e "${BOLD}Quick Start:${NC}"
echo "  1. Open Claude Code in any project directory"
echo "  2. Type: ${YELLOW}/start${NC}"
echo "  3. Claude will automatically remember your context"
echo ""
echo -e "${BOLD}Test Installation:${NC}"
echo "  cd $TEST_PROJECT"
echo "  claude-code"
echo "  > /start test-project"
echo ""
echo -e "${BOLD}Available Commands:${NC}"
echo "  ${YELLOW}/start${NC}              Load project context (Mem0 + Obsidian)"
echo "  ${YELLOW}/end${NC}                Save context at session end"
echo "  ${YELLOW}/wiki [note]${NC}        Add note to wiki"
echo ""
echo -e "${BOLD}What's Running:${NC}"
echo "  • Qdrant: ${BLUE}http://localhost:$QDRANT_PORT${NC}"
echo "  • Memories: ${BLUE}$MEMORIES_DIR${NC}"
echo "  • Config: ${BLUE}$CLAUDE_DIR${NC}"
echo "  • Watcher: ${BLUE}Obsidian filesystem watcher (24/7)${NC}"
echo ""
echo -e "${BOLD}Phase 2 Features (Auto-Documentation):${NC}"
echo "  • GPT-4o-mini analyzes mem0_save for documentable patterns"
echo "  • Automatic suggestions with pre-generated drafts"
echo "  • Filesystem watcher re-indexes Obsidian vault on .md changes"
echo "  • Patterns: Bug, Decision, Config, Tool, Pattern, Migration"
echo ""
echo -e "${BOLD}Documentation:${NC}"
echo "  • Complete guide: ${BLUE}docs/INSTALL.md${NC}"
echo "  • Architecture: ${BLUE}README.md${NC}"
echo "  • Phase 2 details: ${BLUE}Memories/vault/ideas/auto-doc-phase2.md${NC}"
echo ""
echo -e "${BOLD}Cost:${NC}"
echo "  • Embeddings: ~\$0.002 per 1000 memories"
echo "  • Phase 2: ~\$0.58/month (100 mem0_save/day)"
echo "  • Total: ~\$1/month for active usage"
echo ""

# Optional: Install monitoring
echo -e "${BOLD}Optional: Install Monitoring${NC}"
echo "  Run daily checks for memory sync gaps"
echo ""
read -p "Install monitoring? (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -f "scripts/com.mem0.gap-monitor.plist" ]; then
        USERNAME=$(whoami)
        sed "s/marabook_m1/$USERNAME/g" scripts/com.mem0.gap-monitor.plist > /tmp/com.mem0.gap-monitor.plist
        cp /tmp/com.mem0.gap-monitor.plist ~/Library/LaunchAgents/
        launchctl load ~/Library/LaunchAgents/com.mem0.gap-monitor.plist 2>/dev/null || true
        print_success "Monitoring installed (check logs: /tmp/mem0-gap-monitor.log)"
    fi
else
    print_info "Skipped monitoring (install later: docs/scripts/MONITORING.md)"
fi

echo ""
print_success "Happy coding with your Second Brain! 🧠"
echo ""
