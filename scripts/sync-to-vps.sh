#!/bin/bash
#
# Sync Local Memories → VPS (Backup)
# Architecture: LOCAL = Source of Truth, VPS = Backup Only
#
# Usage:
#   ./sync-to-vps.sh [--dry-run] [--project PROJECT_NAME]
#

set -euo pipefail

# Configuration
VPS_URL="http://31.220.104.244:8081"
MEMORIES_DIR="$HOME/Documents/APP_HOME/CascadeProjects/windsurf-project/SecondBrain/memories"
LOG_FILE="/tmp/sync-to-vps.log"
DRY_RUN=false
SPECIFIC_PROJECT=""

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --project)
            SPECIFIC_PROJECT="$2"
            shift 2
            ;;
        *)
            echo "Usage: $0 [--dry-run] [--project PROJECT_NAME]"
            exit 1
            ;;
    esac
done

# Logging
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1" | tee -a "$LOG_FILE"
}

log_warn() {
    echo -e "${YELLOW}⚠${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}✗${NC} $1" | tee -a "$LOG_FILE"
}

# VPS Health Check
check_vps_health() {
    log "Checking VPS health..."

    if ! curl -s --max-time 5 "${VPS_URL}/health" > /dev/null 2>&1; then
        log_error "VPS is unreachable at ${VPS_URL}"
        return 1
    fi

    log_success "VPS is healthy"
    return 0
}

# Sync single memory to VPS
sync_memory() {
    local project_id="$1"
    local memory_file="$2"
    local memory_id=$(basename "$memory_file" .json)

    # Read memory content and prepare payload
    local content=$(cat "$memory_file" | python3 -c "
import json, sys
mem = json.load(sys.stdin)
# Format: {\"content\": \"...\", \"user_id\": \"project_id\"}
payload = {
    'content': mem.get('content', ''),
    'user_id': '${project_id}'
}
print(json.dumps(payload))
")

    if [ "$DRY_RUN" = true ]; then
        log "  [DRY-RUN] Would sync: ${project_id}/${memory_id}"
        return 0
    fi

    # POST to VPS Mem0 (correct endpoint: /memory not /memory/{project_id})
    response=$(curl -s -w "\n%{http_code}" -X POST \
        "${VPS_URL}/memory" \
        -H "Content-Type: application/json" \
        -d "$content")

    http_code=$(echo "$response" | tail -1)

    if [[ "$http_code" =~ ^2 ]]; then
        return 0
    else
        log_warn "  Failed to sync ${memory_id}: HTTP ${http_code}"
        return 1
    fi
}

# Sync project to VPS
sync_project() {
    local project_id="$1"
    local project_dir="${MEMORIES_DIR}/${project_id}"

    if [ ! -d "$project_dir" ]; then
        log_warn "Project directory not found: ${project_dir}"
        return 1
    fi

    log "Syncing project: ${project_id}"

    # Count memories
    local total_files=$(find "$project_dir" -type f -name "*.json" | wc -l | tr -d ' ')

    if [ "$total_files" -eq 0 ]; then
        log_warn "  No memories found in ${project_id}"
        return 0
    fi

    log "  Found ${total_files} memories"

    # Sync each memory
    local synced=0
    local failed=0

    for memory_file in "$project_dir"/*.json; do
        if [ -f "$memory_file" ]; then
            if sync_memory "$project_id" "$memory_file"; then
                ((synced++))
            else
                ((failed++))
            fi
        fi
    done

    if [ "$DRY_RUN" = true ]; then
        log_success "  [DRY-RUN] ${synced} memories would be synced"
    else
        log_success "  Synced: ${synced}/${total_files} memories"

        if [ $failed -gt 0 ]; then
            log_warn "  Failed: ${failed} memories"
        fi
    fi
}

# Main sync
main() {
    echo ""
    log "=== Mem0 Sync: Local → VPS (Backup) ==="
    echo ""

    if [ "$DRY_RUN" = true ]; then
        log_warn "DRY-RUN MODE: No changes will be made"
        echo ""
    fi

    # Health check
    if ! check_vps_health; then
        log_error "Aborting sync - VPS unavailable"
        exit 1
    fi

    echo ""

    # Determine projects to sync
    if [ -n "$SPECIFIC_PROJECT" ]; then
        # Sync specific project
        sync_project "$SPECIFIC_PROJECT"
    else
        # Sync all projects
        log "Discovering projects in ${MEMORIES_DIR}..."

        local projects=()
        for dir in "$MEMORIES_DIR"/*/; do
            if [ -d "$dir" ]; then
                project_name=$(basename "$dir")

                # Skip hidden and backup directories
                if [[ ! "$project_name" =~ ^\. ]] && [ "$project_name" != ".backup" ]; then
                    projects+=("$project_name")
                fi
            fi
        done

        if [ ${#projects[@]} -eq 0 ]; then
            log_warn "No projects found in ${MEMORIES_DIR}"
            exit 0
        fi

        log_success "Found ${#projects[@]} projects: ${projects[*]}"
        echo ""

        # Sync each project
        for project in "${projects[@]}"; do
            sync_project "$project"
            echo ""
        done
    fi

    echo ""
    log_success "Sync complete!"
    log "Full logs: ${LOG_FILE}"
}

# Run
main
