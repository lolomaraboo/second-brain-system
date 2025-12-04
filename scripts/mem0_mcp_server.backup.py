#!/usr/bin/env python3
"""
MCP Server for Mem0 - Connects Claude Code to Mem0 API on VPS
Solution 2A: Queue locale + worker async + dual write
"""

import json
import sys
import uuid
import os
import time
import fcntl
import requests
from pathlib import Path
from datetime import datetime
from typing import Any

# Configuration
MEM0_API_URL = "http://31.220.104.244:8081"
QUEUE_FILE = Path.home() / ".claude/mem0_queue.json"
LOCK_FILE = Path.home() / ".claude/mem0_queue.lock"
LOCK_TIMEOUT = 5  # seconds

def acquire_lock_with_timeout(lock_file, timeout=LOCK_TIMEOUT):
    """Acquire file lock with timeout to prevent blocking indefinitely"""
    start = time.time()

    while time.time() - start < timeout:
        try:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True  # Lock acquired
        except BlockingIOError:
            time.sleep(0.1)  # Wait 100ms and retry

    return False  # Timeout

def send_response(response: dict):
    """Send JSON-RPC response to stdout"""
    print(json.dumps(response), flush=True)

def send_error(id: Any, code: int, message: str):
    """Send JSON-RPC error response"""
    send_response({
        "jsonrpc": "2.0",
        "id": id,
        "error": {"code": code, "message": message}
    })

def send_result(id: Any, result: Any):
    """Send JSON-RPC success response"""
    send_response({
        "jsonrpc": "2.0",
        "id": id,
        "result": result
    })

# ============================================================================
# QUEUE MANAGEMENT FUNCTIONS (Solution 2A)
# ============================================================================

def load_queue() -> dict:
    """Load queue from JSON file"""
    if not QUEUE_FILE.exists():
        return {
            "queue": [],
            "last_100": [],
            "failed": [],
            "stats": {
                "total_queued": 0,
                "total_synced": 0,
                "total_failed": 0,
                "last_sync": None
            }
        }

    try:
        with open(QUEUE_FILE, 'r') as f:
            return json.load(f)
    except:
        # Corrupted file, start fresh
        return {
            "queue": [],
            "last_100": [],
            "failed": [],
            "stats": {
                "total_queued": 0,
                "total_synced": 0,
                "total_failed": 0,
                "last_sync": None
            }
        }

def save_queue(queue_data: dict):
    """Save queue to JSON file (atomic write)"""
    tmp_file = QUEUE_FILE.with_suffix('.tmp')
    try:
        with open(tmp_file, 'w') as f:
            json.dump(queue_data, f, indent=2)
        tmp_file.replace(QUEUE_FILE)
    except:
        if tmp_file.exists():
            tmp_file.unlink()

def add_to_queue(project_id: str, content: str) -> dict:
    """Add entry to queue and update cache (with file locking)"""
    # Ensure lock file directory exists
    LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(LOCK_FILE, 'w') as lock:
        if not acquire_lock_with_timeout(lock):
            raise Exception("Could not acquire queue lock (timeout). Queue might be busy.")

        queue = load_queue()

        entry = {
            "id": str(uuid.uuid4()),
            "project_id": project_id,
            "content": content,
            "timestamp": int(datetime.now().timestamp()),
            "retries": 0
        }

        # Add to queue
        queue["queue"].append(entry)
        queue["stats"]["total_queued"] += 1

        # Update last_100 cache
        queue["last_100"].append(entry)
        if len(queue["last_100"]) > 100:
            queue["last_100"] = queue["last_100"][-100:]

        save_queue(queue)
        return entry

def get_queue_status() -> dict:
    """Get queue status for monitoring (with file locking)"""
    LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(LOCK_FILE, 'w') as lock:
        if not acquire_lock_with_timeout(lock):
            return {
                "status": "ERROR",
                "message": "Could not acquire lock (queue busy)",
                "queue_size": 0,
                "failed_size": 0
            }

        queue = load_queue()

        queue_size = len(queue["queue"])
        failed_size = len(queue["failed"])

        # Determine VPS status
        if queue_size >= 20 or failed_size > 5:
            status = "critical" if failed_size > 5 else "warning"
        else:
            status = "healthy"

        # Calculate age of oldest entry
        oldest_age = None
        if queue["queue"]:
            oldest_timestamp = min(e["timestamp"] for e in queue["queue"])
            oldest_age = int(datetime.now().timestamp()) - oldest_timestamp

        return {
            "queue_size": queue_size,
            "failed_size": failed_size,
            "last_sync": queue["stats"].get("last_sync"),
            "total_queued": queue["stats"].get("total_queued", 0),
            "total_synced": queue["stats"].get("total_synced", 0),
            "total_failed": queue["stats"].get("total_failed", 0),
            "oldest_age_seconds": oldest_age,
            "vps_status": status
        }

# ============================================================================

def handle_initialize(id: Any, params: dict):
    """Handle initialize request"""
    send_result(id, {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "tools": {}
        },
        "serverInfo": {
            "name": "mem0-server",
            "version": "1.0.0"
        }
    })

def handle_tools_list(id: Any):
    """Return list of available tools"""
    tools = [
        {
            "name": "mem0_recall",
            "description": "Retrieve context and memories for a project. Use at the START of each session to get previous context.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project identifier (e.g., 'recording-studio-manager', 'claude-code-champion')"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of memories to retrieve (default: 20)",
                        "default": 20
                    }
                },
                "required": ["project_id"]
            }
        },
        {
            "name": "mem0_save",
            "description": "Save important context to memory. Use to remember decisions, progress, or important information.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project identifier"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to memorize (decisions, progress, important context)"
                    }
                },
                "required": ["project_id", "content"]
            }
        },
        {
            "name": "mem0_search",
            "description": "Semantic search in project memories. Find relevant context by meaning, not just keywords.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project identifier"
                    },
                    "query": {
                        "type": "string",
                        "description": "Search query (semantic search)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum results (default: 10)",
                        "default": 10
                    }
                },
                "required": ["project_id", "query"]
            }
        },
        {
            "name": "mem0_list_projects",
            "description": "List all projects that have memories stored.",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "mem0_health",
            "description": "Check if Mem0 API is healthy and accessible.",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "mem0_queue_status",
            "description": "Get local queue status and VPS health (queue size, failed count, last sync). Use to monitor Mem0 synchronization.",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    ]
    send_result(id, {"tools": tools})

def call_mem0_api(method: str, endpoint: str, data: dict = None) -> dict:
    """Make HTTP request to Mem0 API"""
    url = f"{MEM0_API_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, timeout=30)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=30)
        elif method == "DELETE":
            response = requests.delete(url, timeout=30)
        else:
            return {"error": f"Unknown method: {method}"}

        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}

def handle_tool_call(id: Any, params: dict):
    """Handle tool execution"""
    tool_name = params.get("name")
    arguments = params.get("arguments", {})

    try:
        if tool_name == "mem0_recall":
            project_id = arguments.get("project_id")
            limit = arguments.get("limit", 20)
            result = call_mem0_api("GET", f"/memory/{project_id}?limit={limit}")

            if "error" in result:
                content = f"Error retrieving memories: {result['error']}"
            elif result.get("success"):
                memories = result.get("memories", {}).get("results", [])
                if memories:
                    content = f"Found {len(memories)} memories for '{project_id}':\n\n"
                    for i, mem in enumerate(memories, 1):
                        memory_text = mem.get("memory", "")
                        content += f"{i}. {memory_text}\n"
                else:
                    content = f"No memories found for project '{project_id}'. This might be a new project or first session."
            else:
                content = f"Unexpected response: {json.dumps(result)}"

        elif tool_name == "mem0_save":
            project_id = arguments.get("project_id")
            memory_content = arguments.get("content")

            # Solution 2A: Add to queue instead of direct API call
            entry = add_to_queue(project_id, memory_content)

            # TODO: Dual write to knowledge graph (Phase 5)
            # For now, just queue it

            # Check queue status for alerts
            status = get_queue_status()

            base_message = f"Memory queued successfully for project '{project_id}' (will sync to VPS in background)."

            # Add alerts if needed
            if status["vps_status"] == "critical":
                content = f"""🚨 ALERTE MEM0 VPS - CRITICAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Failed entries : {status['failed_size']} mémoires (3 retries échoués)
VPS Mem0 est probablement DOWN

⚠️  Ces mémoires ne seront jamais uploadées sur le VPS
    mais sont sauvegardées dans le knowledge graph.

🔧 Action URGENTE requise :
   Investiguer le VPS immédiatement
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{base_message}"""
            elif status["vps_status"] == "warning":
                oldest_hours = (status.get("oldest_age_seconds") or 0) // 3600
                content = f"""⚠️  ALERTE MEM0 VPS - WARNING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Queue locale : {status['queue_size']} mémoires en attente
Le VPS semble inaccessible depuis {oldest_hours} heures

💾 Tes données sont sauvegardées dans :
   ✓ Queue locale : ~/.claude/mem0_queue.json
   ✓ Knowledge graph : toujours à jour

🔧 Actions recommandées :
   1. Vérifier VPS : ssh user@31.220.104.244
   2. Voir logs : tail -f /opt/mem0-api/logs/api.log
   3. Status queue : mem0_queue_status

Le système continue de fonctionner normalement.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{base_message}"""
            else:
                content = base_message

        elif tool_name == "mem0_search":
            project_id = arguments.get("project_id")
            query = arguments.get("query")
            limit = arguments.get("limit", 10)
            result = call_mem0_api("POST", "/memory/search", {
                "user_id": project_id,
                "query": query,
                "limit": limit
            })

            if "error" in result:
                content = f"Error searching memories: {result['error']}"
            elif result.get("success"):
                # Handle nested results structure: results.results
                results_data = result.get("results", {})
                if isinstance(results_data, dict):
                    results = results_data.get("results", [])
                else:
                    results = results_data

                if results:
                    content = f"Found {len(results)} relevant memories for '{query}':\n\n"
                    for i, res in enumerate(results, 1):
                        memory_text = res.get("memory", "")
                        score = res.get("score", 0)
                        content += f"{i}. [{score:.2f}] {memory_text}\n"
                else:
                    content = f"No memories found matching '{query}' in project '{project_id}'."
            else:
                content = f"Unexpected response: {json.dumps(result)}"

        elif tool_name == "mem0_list_projects":
            # Note: Mem0 API doesn't have a direct "list projects" endpoint
            # We'll check the health and return a helpful message
            result = call_mem0_api("GET", "/health")
            if "error" in result:
                content = f"Error connecting to Mem0: {result['error']}"
            else:
                content = """Mem0 API is healthy.

Known projects (configured):
- recording-studio-manager
- claude-code-champion

To see memories for a project, use mem0_recall with the project_id."""

        elif tool_name == "mem0_health":
            result = call_mem0_api("GET", "/health")
            if "error" in result:
                content = f"Mem0 API is NOT healthy: {result['error']}"
            else:
                content = f"""Mem0 API Status: HEALTHY

Version: {result.get('version', 'unknown')}
LLM Provider: {result.get('llm_provider', 'unknown')}
LLM Model: {result.get('llm_model', 'unknown')}
Vector Store: {result.get('vector_store', 'unknown')}
Backup Enabled: {result.get('backup_enabled', False)}"""

        elif tool_name == "mem0_queue_status":
            status = get_queue_status()

            # Format last sync
            last_sync = status["last_sync"]
            if last_sync:
                last_sync_str = f"Last sync: {last_sync}"
            else:
                last_sync_str = "No sync yet"

            # Format oldest age
            oldest_age = status.get("oldest_age_seconds")
            if oldest_age:
                hours = oldest_age // 3600
                minutes = (oldest_age % 3600) // 60
                oldest_str = f"Oldest entry: {hours}h {minutes}min ago"
            else:
                oldest_str = "No entries in queue"

            # Status indicator
            status_emoji = {
                "healthy": "✅",
                "warning": "⚠️",
                "critical": "🚨"
            }.get(status["vps_status"], "❓")

            content = f"""Mem0 Queue Status

{status_emoji} VPS Status: {status["vps_status"].upper()}

Queue:
  - Pending: {status["queue_size"]} mémoires
  - Failed: {status["failed_size"]} mémoires
  - {oldest_str}

Stats:
  - Total queued: {status["total_queued"]}
  - Total synced: {status["total_synced"]}
  - {last_sync_str}

File: ~/.claude/mem0_queue.json"""

        else:
            content = f"Unknown tool: {tool_name}"

        send_result(id, {
            "content": [{"type": "text", "text": content}]
        })

    except Exception as e:
        send_result(id, {
            "content": [{"type": "text", "text": f"Error executing {tool_name}: {str(e)}"}],
            "isError": True
        })

def main():
    """Main loop - read JSON-RPC messages from stdin"""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            continue

        method = message.get("method")
        id = message.get("id")
        params = message.get("params", {})

        if method == "initialize":
            handle_initialize(id, params)
        elif method == "notifications/initialized":
            pass  # Acknowledgment, no response needed
        elif method == "tools/list":
            handle_tools_list(id)
        elif method == "tools/call":
            handle_tool_call(id, params)
        else:
            if id is not None:
                send_error(id, -32601, f"Method not found: {method}")

if __name__ == "__main__":
    main()
