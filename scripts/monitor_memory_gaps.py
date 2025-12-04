#!/usr/bin/env python3
"""
Memory Gap Monitor - Detects divergence between JSON files and Qdrant vectors

Purpose:
- Prevents the "326 missing memories" problem from happening again
- Runs periodically (cron/launchd) to detect JSON vs Qdrant gaps
- Alerts when divergence exceeds threshold (default 5%)

Usage:
- monitor_memory_gaps.py                    # Check all projects
- monitor_memory_gaps.py --project foo      # Check specific project
- monitor_memory_gaps.py --threshold 10     # Custom threshold (%)
- monitor_memory_gaps.py --alert-only       # Only output if gaps found
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
import requests
from typing import Dict, List, Tuple

# Configuration
MEMORIES_DIR = Path.home() / "Documents/APP_HOME/CascadeProjects/windsurf-project/Memories/memories"
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
DEFAULT_THRESHOLD = 5.0  # Alert if divergence > 5%

# ANSI Colors for output
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
RESET = "\033[0m"


def get_json_count(project_name: str) -> int:
    """Count JSON files for a project"""
    project_dir = MEMORIES_DIR / project_name

    if not project_dir.exists():
        return 0

    json_files = list(project_dir.glob("*.json"))
    return len(json_files)


def get_qdrant_count(project_name: str) -> int:
    """Count vectors in Qdrant for a project"""
    try:
        offset = None
        total = 0

        while True:
            payload = {
                "filter": {
                    "must": [
                        {"key": "user_id", "match": {"value": project_name}}
                    ]
                },
                "limit": 100,
                "with_payload": False,
                "with_vector": False
            }

            if offset:
                payload["offset"] = offset

            response = requests.post(
                f"http://{QDRANT_HOST}:{QDRANT_PORT}/collections/mem0/points/scroll",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=5
            )

            if response.status_code != 200:
                print(f"{YELLOW}⚠️  Qdrant query failed for {project_name}: {response.status_code}{RESET}", file=sys.stderr)
                return -1

            data = response.json()
            points = data.get('result', {}).get('points', [])

            if not points:
                break

            total += len(points)
            offset = data.get('result', {}).get('next_page_offset')

            if not offset:
                break

        return total

    except requests.exceptions.RequestException as e:
        print(f"{YELLOW}⚠️  Qdrant connection failed: {e}{RESET}", file=sys.stderr)
        return -1
    except Exception as e:
        print(f"{RED}❌ Error querying Qdrant for {project_name}: {e}{RESET}", file=sys.stderr)
        return -1


def calculate_divergence(json_count: int, qdrant_count: int) -> float:
    """Calculate percentage divergence"""
    if json_count == 0:
        return 0.0

    divergence = abs(json_count - qdrant_count) / json_count * 100
    return divergence


def check_project(project_name: str, threshold: float = DEFAULT_THRESHOLD) -> Dict:
    """Check a single project for gaps"""
    json_count = get_json_count(project_name)
    qdrant_count = get_qdrant_count(project_name)

    if qdrant_count == -1:
        # Qdrant query failed
        return {
            "project": project_name,
            "json_count": json_count,
            "qdrant_count": None,
            "divergence": None,
            "status": "error",
            "message": "Qdrant query failed"
        }

    divergence = calculate_divergence(json_count, qdrant_count)
    missing = json_count - qdrant_count

    # Determine status
    if divergence > threshold:
        status = "alert"
        message = f"⚠️  {missing:+d} vectors ({divergence:.1f}% divergence)"
    elif divergence > 0:
        status = "warning"
        message = f"{missing:+d} vectors ({divergence:.1f}% divergence)"
    else:
        status = "ok"
        message = "✅ In sync"

    return {
        "project": project_name,
        "json_count": json_count,
        "qdrant_count": qdrant_count,
        "missing": missing,
        "divergence": divergence,
        "status": status,
        "message": message
    }


def discover_projects() -> List[str]:
    """Find all projects with JSON files"""
    if not MEMORIES_DIR.exists():
        return []

    projects = []
    for item in MEMORIES_DIR.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            # Check if has JSON files
            json_files = list(item.glob("*.json"))
            if json_files:
                projects.append(item.name)

    return sorted(projects)


def print_report(results: List[Dict], alert_only: bool = False):
    """Print monitoring report"""

    # Filter if alert_only
    if alert_only:
        results = [r for r in results if r["status"] in ["alert", "error"]]
        if not results:
            # Silent success
            return

    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}  Memory Gap Monitor Report{RESET}")
    print(f"{BLUE}{'='*70}{RESET}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Qdrant: {QDRANT_HOST}:{QDRANT_PORT}")
    print(f"{BLUE}{'='*70}{RESET}\n")

    # Summary counts
    alerts = sum(1 for r in results if r["status"] == "alert")
    warnings = sum(1 for r in results if r["status"] == "warning")
    errors = sum(1 for r in results if r["status"] == "error")
    ok = sum(1 for r in results if r["status"] == "ok")

    if alerts > 0:
        print(f"{RED}🚨 ALERTS: {alerts}{RESET}")
    if errors > 0:
        print(f"{RED}❌ ERRORS: {errors}{RESET}")
    if warnings > 0:
        print(f"{YELLOW}⚠️  WARNINGS: {warnings}{RESET}")
    if ok > 0:
        print(f"{GREEN}✅ OK: {ok}{RESET}")

    print()

    # Detailed results
    print(f"{'Project':<30} {'JSON':<8} {'Qdrant':<8} {'Status':<20}")
    print(f"{'-'*70}")

    for result in results:
        project = result["project"]
        json_count = result["json_count"]
        qdrant_count = result["qdrant_count"]
        status = result["status"]
        message = result["message"]

        # Color based on status
        if status == "alert":
            color = RED
        elif status == "error":
            color = RED
        elif status == "warning":
            color = YELLOW
        else:
            color = GREEN

        qdrant_str = str(qdrant_count) if qdrant_count is not None else "N/A"

        print(f"{project:<30} {json_count:<8} {qdrant_str:<8} {color}{message}{RESET}")

    print(f"\n{BLUE}{'='*70}{RESET}\n")

    # Exit code
    if alerts > 0 or errors > 0:
        sys.exit(1)


def main():
    """Main monitoring function"""
    import argparse

    parser = argparse.ArgumentParser(description='Monitor memory gaps between JSON and Qdrant')
    parser.add_argument('--project', help='Check specific project only')
    parser.add_argument('--threshold', type=float, default=DEFAULT_THRESHOLD,
                       help=f'Alert threshold in percent (default: {DEFAULT_THRESHOLD}%)')
    parser.add_argument('--alert-only', action='store_true',
                       help='Only output if gaps found (for cron)')
    args = parser.parse_args()

    # Discover or use specified project
    if args.project:
        projects = [args.project]
    else:
        projects = discover_projects()

    if not projects:
        print(f"{RED}❌ No projects found in {MEMORIES_DIR}{RESET}")
        sys.exit(1)

    # Check each project
    results = []
    for project in projects:
        result = check_project(project, threshold=args.threshold)
        results.append(result)

    # Print report
    print_report(results, alert_only=args.alert_only)


if __name__ == "__main__":
    main()
