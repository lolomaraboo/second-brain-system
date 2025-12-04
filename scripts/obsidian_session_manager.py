#!/usr/bin/env python3
"""
Obsidian Session Manager - Protection multi-sessions Claude Code

Gère le tracking des sessions actives pour éviter les conflits
lors de modifications concurrentes dans Obsidian.
"""

import json
import os
import sys
import time
import fcntl
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

SESSION_FILE = Path.home() / ".claude" / "obsidian_sessions.json"
LOCK_FILE = Path.home() / ".claude" / "obsidian_sessions.lock"

def acquire_lock(lock_file: Path, timeout: int = 5) -> Optional[int]:
    """Acquiert un lock fichier avec timeout."""
    fd = os.open(lock_file, os.O_CREAT | os.O_RDWR)
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return fd
        except BlockingIOError:
            time.sleep(0.1)

    os.close(fd)
    return None

def release_lock(fd: int):
    """Relâche un lock fichier."""
    fcntl.flock(fd, fcntl.LOCK_UN)
    os.close(fd)

def is_process_alive(pid: int) -> bool:
    """Vérifie si un processus existe."""
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False

def load_sessions() -> Dict:
    """Charge les sessions existantes."""
    if not SESSION_FILE.exists():
        return {"sessions": []}

    with open(SESSION_FILE, 'r') as f:
        return json.load(f)

def save_sessions(data: Dict):
    """Sauvegarde les sessions."""
    SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SESSION_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def cleanup_dead_sessions(sessions: List[Dict]) -> List[Dict]:
    """Supprime les sessions dont le processus n'existe plus."""
    return [s for s in sessions if is_process_alive(s['pid'])]

def register_session(project_id: str, cwd: str) -> Dict:
    """Enregistre une nouvelle session."""
    lock_fd = acquire_lock(LOCK_FILE)
    if lock_fd is None:
        print("❌ Timeout: impossible d'acquérir le lock", file=sys.stderr)
        sys.exit(1)

    try:
        data = load_sessions()
        data['sessions'] = cleanup_dead_sessions(data['sessions'])

        # Utiliser le PID du shell courant (via env var PPID si disponible)
        # En CLI, os.getpid() est le PID du script Python, on veut le shell parent
        shell_pid = int(os.environ.get('PPID', os.getppid()))

        # Créer nouvelle session
        session = {
            "pid": shell_pid,
            "project_id": project_id,
            "cwd": cwd,
            "started": datetime.now().isoformat(),
            "last_active": datetime.now().isoformat()
        }

        # Vérifier si session existe déjà (même PID)
        data['sessions'] = [s for s in data['sessions'] if s['pid'] != session['pid']]
        data['sessions'].append(session)

        save_sessions(data)
        return session
    finally:
        release_lock(lock_fd)

def unregister_session(pid: Optional[int] = None) -> bool:
    """Supprime une session."""
    if pid is None:
        pid = int(os.environ.get('PPID', os.getppid()))

    lock_fd = acquire_lock(LOCK_FILE)
    if lock_fd is None:
        return False

    try:
        data = load_sessions()
        data['sessions'] = [s for s in data['sessions'] if s['pid'] != pid]
        save_sessions(data)
        return True
    finally:
        release_lock(lock_fd)

def check_active_sessions(project_id: Optional[str] = None) -> Dict:
    """Vérifie les sessions actives et retourne un rapport."""
    lock_fd = acquire_lock(LOCK_FILE)
    if lock_fd is None:
        return {"error": "Timeout acquiring lock"}

    try:
        data = load_sessions()
        data['sessions'] = cleanup_dead_sessions(data['sessions'])
        save_sessions(data)

        current_pid = int(os.environ.get('PPID', os.getppid()))
        active_sessions = [s for s in data['sessions'] if s['pid'] != current_pid]

        if not active_sessions:
            return {
                "status": "ok",
                "message": "Aucune autre session active",
                "sessions": []
            }

        # HIERARCHICAL-AWARE: Filtrer par projet si spécifié
        if project_id:
            def is_related_project(project_a: str, project_b: str) -> bool:
                """Vérifie si les projets sont liés (même ou parent/enfant)."""
                if project_a == project_b:
                    return True
                # Parent/enfant: dev vs dev/recording-studio-manager
                if project_a.startswith(project_b + '/') or project_b.startswith(project_a + '/'):
                    return True
                return False

            related_sessions = [s for s in active_sessions
                              if is_related_project(s['project_id'], project_id)]
            if related_sessions:
                return {
                    "status": "warning",
                    "message": f"⚠️  Autre session active sur projet lié: {project_id}",
                    "sessions": related_sessions,
                    "risk": "high"
                }

        return {
            "status": "info",
            "message": f"ℹ️  {len(active_sessions)} autre(s) session(s) active(s) sur des projets différents",
            "sessions": active_sessions,
            "risk": "low"
        }
    finally:
        release_lock(lock_fd)

def list_sessions() -> List[Dict]:
    """Liste toutes les sessions actives."""
    lock_fd = acquire_lock(LOCK_FILE)
    if lock_fd is None:
        return []

    try:
        data = load_sessions()
        data['sessions'] = cleanup_dead_sessions(data['sessions'])
        save_sessions(data)
        return data['sessions']
    finally:
        release_lock(lock_fd)

def main():
    """CLI pour gérer les sessions."""
    if len(sys.argv) < 2:
        print("Usage: obsidian_session_manager.py [register|unregister|check|list]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "register":
        if len(sys.argv) < 4:
            print("Usage: obsidian_session_manager.py register <project_id> <cwd>")
            sys.exit(1)
        session = register_session(sys.argv[2], sys.argv[3])
        print(json.dumps(session, indent=2))

    elif command == "unregister":
        pid = int(sys.argv[2]) if len(sys.argv) > 2 else None
        success = unregister_session(pid)
        print("✓ Session supprimée" if success else "✗ Échec")

    elif command == "check":
        project_id = sys.argv[2] if len(sys.argv) > 2 else None
        result = check_active_sessions(project_id)
        print(json.dumps(result, indent=2))

    elif command == "list":
        sessions = list_sessions()
        print(json.dumps(sessions, indent=2))

    else:
        print(f"❌ Commande inconnue: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
