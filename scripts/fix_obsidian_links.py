#!/usr/bin/env python3
"""
Fix broken Obsidian links by creating missing files with minimal content.
"""

import os
import sys
import re
from pathlib import Path
from datetime import datetime

# ANSI colors
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
BOLD = '\033[1m'
NC = '\033[0m'

def find_wiki_links(content):
    """Extract all [[wiki links]] from content."""
    pattern = r'\[\[([^\]|]+)(?:\|[^\]]*)?\]\]'
    return re.findall(pattern, content)

def find_all_markdown_files(vault_path):
    """Find all markdown files in vault."""
    md_files = {}
    for root, dirs, files in os.walk(vault_path):
        if '.obsidian' in root:
            continue
        for file in files:
            if file.endswith('.md'):
                full_path = os.path.join(root, file)
                name_without_ext = file[:-3]
                md_files[name_without_ext] = full_path
                md_files[file] = full_path
    return md_files

def create_missing_file(file_path, link_name, source_file):
    """Create a missing file with minimal content."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Determine content based on filename
    if file_path.endswith('_INDEX.md'):
        content = f"""# Index\n\nCréé automatiquement le {datetime.now().strftime('%Y-%m-%d')}\n\nRéférencé par: [[{os.path.basename(source_file)[:-3]}]]\n"""
    elif 'decision' in file_path.lower():
        content = f"""# Décision: {link_name}\n\nDate: {datetime.now().strftime('%Y-%m-%d')}\n\n## Contexte\n\n## Décision\n\n## Conséquences\n"""
    elif 'architecture' in file_path.lower():
        content = f"""# Architecture: {link_name}\n\nDate: {datetime.now().strftime('%Y-%m-%d')}\n\n## Vue d'ensemble\n\n## Composants\n\n## Intégrations\n"""
    else:
        content = f"""# {link_name}\n\nCréé automatiquement le {datetime.now().strftime('%Y-%m-%d')}\n\nRéférencé par: [[{os.path.basename(source_file)[:-3]}]]\n"""

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return True

def fix_links(vault_path, dry_run=False):
    """Fix broken links in vault."""
    vault_path = Path(vault_path).resolve()

    print(f"{BLUE}🔧 Fixing Obsidian Links{NC}")
    print(f"Vault: {vault_path}")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print()

    # Find all markdown files
    md_files = find_all_markdown_files(vault_path)

    created_files = []
    skipped_links = []

    # Check each markdown file
    for root, dirs, files in os.walk(vault_path):
        if '.obsidian' in root:
            continue

        for file in files:
            if not file.endswith('.md'):
                continue

            file_path = os.path.join(root, file)

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                print(f"{YELLOW}⚠ Error reading {file_path}: {e}{NC}")
                continue

            # Find all wiki links
            links = find_wiki_links(content)

            for link in links:
                link_clean = link.strip()

                # Skip if already exists
                if link_clean in md_files or f"{link_clean}.md" in md_files:
                    continue

                # Skip bash code patterns
                if link_clean.startswith('$') or '==' in link_clean or link_clean.startswith('"'):
                    skipped_links.append(link_clean)
                    continue

                # Determine target path
                file_dir = os.path.dirname(file_path)

                # Handle relative paths
                if '/' in link_clean:
                    if link_clean.startswith('../'):
                        # Relative path
                        target_path = os.path.normpath(os.path.join(file_dir, f"{link_clean}.md"))
                    else:
                        # Absolute from vault root
                        target_path = os.path.join(vault_path, f"{link_clean}.md")
                else:
                    # Same directory or vault root
                    target_path = os.path.join(file_dir, f"{link_clean}.md")

                # Check if file exists
                if os.path.exists(target_path):
                    continue

                # Create missing file
                if dry_run:
                    print(f"{YELLOW}[DRY RUN]{NC} Would create: {os.path.relpath(target_path, vault_path)}")
                    print(f"  Referenced by: {os.path.relpath(file_path, vault_path)}")
                else:
                    try:
                        create_missing_file(target_path, link_clean, file_path)
                        created_files.append(os.path.relpath(target_path, vault_path))
                        print(f"{GREEN}✓{NC} Created: {os.path.relpath(target_path, vault_path)}")
                    except Exception as e:
                        print(f"{YELLOW}⚠{NC} Failed to create {target_path}: {e}")

    # Summary
    print()
    print(f"{BOLD}{'='*70}{NC}")
    print(f"{BOLD}Summary{NC}")
    print(f"{BOLD}{'='*70}{NC}")
    print(f"Files created: {len(created_files)}")
    print(f"Skipped links (code): {len(skipped_links)}")

    if created_files:
        print()
        print(f"{GREEN}Created files:{NC}")
        for f in created_files[:10]:  # Show first 10
            print(f"  - {f}")
        if len(created_files) > 10:
            print(f"  ... and {len(created_files) - 10} more")

    return len(created_files) > 0

if __name__ == "__main__":
    vault_path = sys.argv[1] if len(sys.argv) > 1 else "."
    dry_run = "--dry-run" in sys.argv

    if not os.path.exists(vault_path):
        print(f"Error: Vault path does not exist: {vault_path}")
        sys.exit(1)

    fixed = fix_links(vault_path, dry_run)
    sys.exit(0)
