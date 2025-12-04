#!/usr/bin/env python3
"""
Check coherence between _INDEX.md files and actual directory contents.

Verifies that each _INDEX.md accurately reflects the files and subdirectories
in its parent directory.
"""

import os
import sys
from pathlib import Path
import re

# ANSI colors
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
BOLD = '\033[1m'
NC = '\033[0m'

def find_all_index_files(vault_path):
    """Find all _INDEX.md files in vault."""
    index_files = []
    for root, dirs, files in os.walk(vault_path):
        if '.obsidian' in root:
            continue
        if '_INDEX.md' in files:
            index_files.append(os.path.join(root, '_INDEX.md'))
    return sorted(index_files)

def get_directory_contents(directory):
    """Get actual files and subdirectories in a directory."""
    try:
        items = os.listdir(directory)
        # Filter out hidden files, _INDEX.md itself
        filtered = []
        for item in items:
            if item.startswith('.'):
                continue
            if item == '_INDEX.md':
                continue
            filtered.append(item)
        return sorted(filtered)
    except Exception as e:
        print(f"{RED}Error reading directory {directory}: {e}{NC}")
        return []

def extract_referenced_items(index_content, directory):
    """
    Extract items referenced in _INDEX.md content.
    Looks for:
    - [[item/_INDEX|item]] or [[item]]
    - Links to .md files
    - Listed subdirectories
    """
    referenced = set()

    # Pattern 1: [[path/_INDEX|name]] or [[path|name]]
    wiki_links = re.findall(r'\[\[([^\]|]+)(?:\|[^\]]*)?\]\]', index_content)
    for link in wiki_links:
        # Extract just the directory/file name
        parts = link.split('/')
        if parts:
            item = parts[0]
            # Remove .md extension if present
            if item.endswith('.md'):
                referenced.add(item)
                referenced.add(item[:-3])  # Also add without .md
            else:
                referenced.add(item)

    # Pattern 2: Markdown lists with directory/file names
    # Looking for lines like "- patterns/" or "- tools/"
    list_items = re.findall(r'^[\s-]*([a-zA-Z0-9_-]+)/?\s*:', index_content, re.MULTILINE)
    referenced.update(list_items)

    return referenced

def check_index_file(index_path, vault_path):
    """Check one _INDEX.md file for coherence."""
    directory = os.path.dirname(index_path)
    rel_dir = os.path.relpath(directory, vault_path)

    # Get actual contents
    actual_items = get_directory_contents(directory)

    # Read _INDEX.md
    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            index_content = f.read()
    except Exception as e:
        return {
            'path': rel_dir,
            'error': f"Cannot read _INDEX.md: {e}",
            'status': 'error'
        }

    # Check if index is empty/minimal
    lines = [l.strip() for l in index_content.split('\n') if l.strip() and not l.strip().startswith('#')]
    if len(lines) <= 2:  # Very minimal content
        if actual_items:  # But directory has items
            return {
                'path': rel_dir,
                'status': 'empty',
                'actual_items': actual_items,
                'referenced_items': [],
                'missing': actual_items,
                'extra': []
            }

    # Extract referenced items
    referenced_items = extract_referenced_items(index_content, directory)

    # Compare
    actual_set = set(actual_items)

    # Items in directory but NOT in _INDEX.md
    missing = actual_set - referenced_items

    # Items in _INDEX.md but NOT in directory
    extra = referenced_items - actual_set

    status = 'ok' if not missing and not extra else 'mismatch'

    return {
        'path': rel_dir,
        'status': status,
        'actual_items': sorted(actual_items),
        'referenced_items': sorted(referenced_items),
        'missing': sorted(missing),
        'extra': sorted(extra)
    }

def check_vault_coherence(vault_path):
    """Check all _INDEX.md files in vault."""
    vault_path = Path(vault_path).resolve()

    print(f"{BLUE}{'='*70}{NC}")
    print(f"{BLUE}  Obsidian _INDEX.md Coherence Check{NC}")
    print(f"{BLUE}{'='*70}{NC}")
    print(f"Vault: {vault_path}")
    print()

    # Find all _INDEX.md files
    index_files = find_all_index_files(vault_path)
    print(f"Found {len(index_files)} _INDEX.md files")
    print()

    # Check each one
    results = []
    for index_file in index_files:
        result = check_index_file(index_file, vault_path)
        results.append(result)

    # Categorize results
    ok_count = sum(1 for r in results if r['status'] == 'ok')
    empty_count = sum(1 for r in results if r['status'] == 'empty')
    mismatch_count = sum(1 for r in results if r['status'] == 'mismatch')
    error_count = sum(1 for r in results if r['status'] == 'error')

    # Print summary
    print(f"{BOLD}{'='*70}{NC}")
    print(f"{BOLD}Summary{NC}")
    print(f"{BOLD}{'='*70}{NC}")
    print()
    print(f"{GREEN}✅ OK: {ok_count}{NC}")
    print(f"{RED}❌ Empty/Minimal: {empty_count}{NC}")
    print(f"{YELLOW}⚠️  Mismatch: {mismatch_count}{NC}")
    print(f"{RED}🚨 Errors: {error_count}{NC}")
    print()

    # Print details for problematic ones
    if empty_count > 0:
        print(f"{BOLD}{RED}Empty/Minimal _INDEX.md files:{NC}")
        print()
        for r in results:
            if r['status'] == 'empty':
                print(f"{RED}📁 {r['path']}/{NC}")
                print(f"   _INDEX.md is empty but directory contains:")
                for item in r['actual_items']:
                    print(f"   - {item}")
                print()

    if mismatch_count > 0:
        print(f"{BOLD}{YELLOW}Mismatched _INDEX.md files:{NC}")
        print()
        for r in results:
            if r['status'] == 'mismatch':
                print(f"{YELLOW}📁 {r['path']}/{NC}")
                if r['missing']:
                    print(f"   Missing from _INDEX.md:")
                    for item in r['missing']:
                        print(f"   {RED}- {item}{NC}")
                if r['extra']:
                    print(f"   Referenced but not in directory:")
                    for item in r['extra']:
                        print(f"   {YELLOW}+ {item}{NC}")
                print()

    if error_count > 0:
        print(f"{BOLD}{RED}Errors:{NC}")
        print()
        for r in results:
            if r['status'] == 'error':
                print(f"{RED}📁 {r['path']}/{NC}")
                print(f"   {r['error']}")
                print()

    print(f"{BOLD}{'='*70}{NC}")

    return ok_count == len(results)

if __name__ == "__main__":
    vault_path = sys.argv[1] if len(sys.argv) > 1 else "."

    if not os.path.exists(vault_path):
        print(f"{RED}Error: Vault path does not exist: {vault_path}{NC}")
        sys.exit(1)

    success = check_vault_coherence(vault_path)
    sys.exit(0 if success else 1)
