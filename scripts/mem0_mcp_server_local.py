#!/usr/bin/env python3
"""
MCP Server for Mem0 - LOCAL Architecture (Qdrant + OpenAI)
Replaces VPS-based architecture with local Qdrant vector store
"""

import json
import sys
import uuid
import os
from pathlib import Path
from datetime import datetime
from typing import Any
from mem0 import Memory
from openai import OpenAI
from qdrant_client import QdrantClient

# Configuration
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
MEMORIES_BACKUP_DIR = Path.home() / "Documents/APP_HOME/CascadeProjects/windsurf-project/Memories/memories"
OBSIDIAN_COLLECTION = "obsidian_vault"
EMBEDDING_MODEL = "text-embedding-3-small"

# OpenAI API Key (from environment or .env file)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
if not OPENAI_API_KEY:
    # Try to load from .env file
    env_file = Path.home() / ".claude" / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if line.startswith('OPENAI_API_KEY='):
                OPENAI_API_KEY = line.split('=', 1)[1].strip()
                break

# Initialize Mem0 with local Qdrant
config = {
    'llm': {
        'provider': 'openai',
        'config': {
            'model': 'gpt-4o-mini',
            'temperature': 0.1,
            'max_tokens': 2000,
            'api_key': OPENAI_API_KEY
        }
    },
    'vector_store': {
        'provider': 'qdrant',
        'config': {
            'host': QDRANT_HOST,
            'port': QDRANT_PORT,
        }
    },
    'embedder': {
        'provider': 'openai',
        'config': {
            'model': 'text-embedding-3-small',
            'api_key': OPENAI_API_KEY
        }
    }
}

try:
    memory = Memory.from_config(config)
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
    qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    print(f"✅ Mem0 initialized (Qdrant: {QDRANT_HOST}:{QDRANT_PORT})", file=sys.stderr)
except Exception as e:
    print(f"❌ Failed to initialize Mem0: {e}", file=sys.stderr)
    memory = None
    openai_client = None
    qdrant_client = None

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

def backup_memory_to_json(project_id: str, memory_data: dict):
    """Backup memory to JSON file for Git versioning"""
    project_dir = MEMORIES_BACKUP_DIR / project_id
    project_dir.mkdir(parents=True, exist_ok=True)

    memory_id = memory_data.get('id', str(uuid.uuid4()))
    json_file = project_dir / f"{memory_id}.json"

    with open(json_file, 'w') as f:
        json.dump(memory_data, f, indent=2)

def analyze_for_documentation(content: str, project_id: str) -> dict:
    """
    Analyze memory content to detect if it should be documented in Obsidian.
    Uses GPT-4o-mini for intelligent pattern detection.

    Returns:
        dict with 'suggestion' key if documentable (confidence > 0.7), else None
    """
    if not openai_client:
        return None

    prompt = f"""Analyze this memory content and determine if it should be documented in Obsidian.

Memory content:
{content}

Project: {project_id}

Patterns to detect:
1. Bug resolved (symptom + root cause + solution)
2. Technical decision (choice + reasoning)
3. Config/Secret (new ENV variable, API key setup - DO NOT include values)
4. New tool (script/helper created)
5. Reusable pattern (workaround, best practice, convention)
6. Migration/Refactoring (architecture change, breaking change)

If a pattern is detected and truly worth documenting (confidence > 0.7), return JSON:
{{
  "type": "bug|decision|config|tool|pattern|migration",
  "confidence": 0.0-1.0,
  "title": "Short descriptive title",
  "suggested_path": "wiki/section/filename.md",
  "draft_content": "# Title\\n\\n## Context\\n\\n[content based on memory]\\n\\n## Solution/Details\\n\\n[details]"
}}

If no significant pattern or confidence < 0.7, return null.

Be strict: only suggest documentation for genuinely useful, reusable knowledge."""

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=800,
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)

        # Validate response
        if result and isinstance(result, dict):
            confidence = result.get("confidence", 0)
            if confidence > 0.7:
                return result

        return None

    except Exception as e:
        print(f"⚠️  Documentation analysis error: {e}", file=sys.stderr)
        return None

def handle_initialize(id: Any, params: dict):
    """Handle initialize request"""
    send_result(id, {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "tools": {}
        },
        "serverInfo": {
            "name": "mem0-local-server",
            "version": "2.0.0"
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
            "description": "Check if Mem0 LOCAL system is healthy and accessible.",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "obsidian_search",
            "description": "Search in Obsidian vault documentation. Use to find documentation, guides, architecture, patterns. ALWAYS use AFTER mem0_search to get complete context.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (semantic search in Obsidian markdown files)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum results (default: 5)",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        }
    ]
    send_result(id, {"tools": tools})

def handle_tool_call(id: Any, params: dict):
    """Handle tool execution"""
    if memory is None:
        send_error(id, -32000, "Mem0 not initialized - check OPENAI_API_KEY and Qdrant")
        return

    tool_name = params.get("name")
    arguments = params.get("arguments", {})

    try:
        if tool_name == "mem0_recall":
            project_id = arguments.get("project_id")
            limit = arguments.get("limit", 20)

            # Get all memories for user
            recall_response = memory.get_all(user_id=project_id, limit=limit)

            # Extract results from response dict (same fix as mem0_search)
            memories = recall_response.get("results", []) if isinstance(recall_response, dict) else recall_response

            if memories and len(memories) > 0:
                content = f"Found {len(memories)} memories for '{project_id}':\n\n"
                for i, mem in enumerate(memories, 1):
                    # Handle both dict and object formats
                    if isinstance(mem, dict):
                        memory_text = mem.get("memory", "")
                    else:
                        memory_text = str(mem)
                    content += f"{i}. {memory_text}\n"
            else:
                content = f"No memories found for project '{project_id}'. This might be a new project or first session."

        elif tool_name == "mem0_save":
            project_id = arguments.get("project_id")
            memory_content = arguments.get("content")

            # Save to Qdrant via Mem0
            result = memory.add(memory_content, user_id=project_id)

            # Backup to JSON for Git
            if result:
                backup_memory_to_json(project_id, {
                    "id": result.get('id', str(uuid.uuid4())),
                    "memory": memory_content,
                    "created_at": datetime.now().isoformat(),
                    "user_id": project_id
                })

            # Analyze for documentation (Phase 2)
            doc_suggestion = analyze_for_documentation(memory_content, project_id)

            # Base response
            content = f"Memory saved locally for project '{project_id}' ✅"

            # Add suggestion if found
            if doc_suggestion:
                content += f"\n\n💡 Documentation suggestion detected:\n"
                content += f"   Type: {doc_suggestion.get('type', 'unknown')}\n"
                content += f"   Confidence: {doc_suggestion.get('confidence', 0):.0%}\n"
                content += f"   Title: {doc_suggestion.get('title', 'N/A')}\n"
                content += f"   Path: {doc_suggestion.get('suggested_path', 'N/A')}\n"
                content += f"\n   [Draft ready - Claude Code will propose creation]"

        elif tool_name == "mem0_search":
            project_id = arguments.get("project_id")
            query = arguments.get("query")
            limit = arguments.get("limit", 10)

            # Semantic search via Mem0
            search_response = memory.search(query, user_id=project_id, limit=limit)

            # Extract results from response dict
            results = search_response.get("results", []) if isinstance(search_response, dict) else search_response

            if results and len(results) > 0:
                content = f"Found {len(results)} relevant memories for '{query}':\n\n"
                for i, result in enumerate(results, 1):
                    # Handle both dict and object formats
                    if isinstance(result, dict):
                        memory_text = result.get("memory", "")
                        score = result.get("score", 0)
                    else:
                        memory_text = str(result)
                        score = 0
                    content += f"{i}. [{score:.2f}] {memory_text}\n"
            else:
                content = f"No relevant memories found for query '{query}'"

        elif tool_name == "mem0_list_projects":
            # Scan backup directory for projects
            if MEMORIES_BACKUP_DIR.exists():
                projects = [d.name for d in MEMORIES_BACKUP_DIR.iterdir() if d.is_dir() and not d.name.startswith('.')]
                content = f"Found {len(projects)} projects with memories:\n\n"
                for proj in sorted(projects):
                    count = len(list((MEMORIES_BACKUP_DIR / proj).glob("*.json")))
                    content += f"- {proj}: {count} memories\n"
            else:
                content = "No projects found yet."

        elif tool_name == "mem0_health":
            # Check Qdrant connection
            try:
                from qdrant_client import QdrantClient
                client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
                collections = client.get_collections()
                content = f"✅ Mem0 LOCAL healthy\n"
                content += f"Qdrant: {QDRANT_HOST}:{QDRANT_PORT}\n"
                content += f"Collections: {len(collections.collections)}\n"
                content += f"OpenAI: Configured\n"
            except Exception as e:
                content = f"❌ Health check failed: {e}"

        elif tool_name == "obsidian_search":
            query = arguments.get("query")
            limit = arguments.get("limit", 5)

            if not openai_client or not qdrant_client:
                content = "❌ Obsidian search not available (OpenAI/Qdrant not initialized)"
            else:
                try:
                    # Create embedding for query
                    embedding_response = openai_client.embeddings.create(
                        model=EMBEDDING_MODEL,
                        input=query
                    )
                    query_vector = embedding_response.data[0].embedding

                    # Search in obsidian_vault collection
                    search_results = qdrant_client.query_points(
                        collection_name=OBSIDIAN_COLLECTION,
                        query=query_vector,
                        limit=limit
                    ).points

                    if search_results:
                        content = f"Found {len(search_results)} Obsidian documents for '{query}':\n\n"
                        for i, hit in enumerate(search_results, 1):
                            payload = hit.payload
                            file_path = payload.get('file_path', 'unknown')
                            file_type = payload.get('file_type', 'DOC')
                            project = payload.get('project_id', 'N/A')
                            preview = payload.get('content_preview', '')[:150]

                            content += f"{i}. [{hit.score:.2f}] {file_path}\n"
                            content += f"   Type: {file_type} | Project: {project}\n"
                            content += f"   Preview: {preview}...\n\n"
                    else:
                        content = f"No Obsidian documentation found for query '{query}'"

                except Exception as e:
                    content = f"❌ Obsidian search error: {e}"

        else:
            send_error(id, -32601, f"Unknown tool: {tool_name}")
            return

        send_result(id, {
            "content": [
                {
                    "type": "text",
                    "text": content
                }
            ]
        })

    except Exception as e:
        send_error(id, -32000, f"Tool execution failed: {str(e)}")

def main():
    """Main MCP server loop"""
    print("🚀 Mem0 LOCAL MCP Server starting...", file=sys.stderr)

    for line in sys.stdin:
        try:
            request = json.loads(line)
            method = request.get("method")
            id = request.get("id")
            params = request.get("params", {})

            if method == "initialize":
                handle_initialize(id, params)
            elif method == "tools/list":
                handle_tools_list(id)
            elif method == "tools/call":
                handle_tool_call(id, params)
            else:
                send_error(id, -32601, f"Unknown method: {method}")

        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON: {e}", file=sys.stderr)
        except Exception as e:
            print(f"❌ Error: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
