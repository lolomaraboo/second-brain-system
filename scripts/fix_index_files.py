#!/usr/bin/env python3
"""
Automatically fix empty and incomplete _INDEX.md files.

Generates proper content based on actual directory contents.
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# ANSI colors
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
BOLD = '\033[1m'
NC = '\033[0m'

VAULT_PATH = Path.home() / "Documents/APP_HOME/CascadeProjects/windsurf-project/Memories/vault"

def get_directory_contents(directory):
    """Get files and subdirectories."""
    try:
        items = os.listdir(directory)
        files = []
        dirs = []
        for item in items:
            if item.startswith('.') or item == '_INDEX.md':
                continue
            path = os.path.join(directory, item)
            if os.path.isdir(path):
                dirs.append(item)
            elif item.endswith('.md'):
                files.append(item)
        return sorted(dirs), sorted(files)
    except Exception as e:
        return [], []

def generate_index_content(directory, vault_path):
    """Generate _INDEX.md content based on directory contents."""
    rel_dir = os.path.relpath(directory, vault_path)
    dir_name = os.path.basename(directory)

    dirs, files = get_directory_contents(directory)

    # Build content
    lines = [f"# {dir_name.replace('-', ' ').title()}", ""]

    # Add description based on location
    if 'projects/dev' in rel_dir:
        lines.append(f"Documentation pour le projet {dir_name}.")
    elif 'projects/perso' in rel_dir:
        lines.append(f"Notes personnelles: {dir_name}.")
    elif 'projects/studio' in rel_dir:
        lines.append(f"Studio: {dir_name}.")
    elif 'wiki' in rel_dir:
        lines.append(f"Documentation: {dir_name}.")
    else:
        lines.append(f"Index du dossier {dir_name}.")

    lines.append("")

    # List subdirectories
    if dirs:
        lines.append("## Sous-dossiers")
        lines.append("")
        for d in dirs:
            # Check if subdirectory has _INDEX.md
            subindex_path = os.path.join(directory, d, '_INDEX.md')
            if os.path.exists(subindex_path):
                lines.append(f"- [[{d}/_INDEX|{d}]]")
            else:
                lines.append(f"- {d}/")
        lines.append("")

    # List files
    if files:
        lines.append("## Fichiers")
        lines.append("")
        for f in files:
            # Remove .md extension for link
            name = f[:-3] if f.endswith('.md') else f
            lines.append(f"- [[{name}]]")
        lines.append("")

    # Footer
    lines.append("---")
    lines.append(f"*Mis à jour automatiquement le {datetime.now().strftime('%Y-%m-%d')}*")

    return "\n".join(lines)

def is_index_empty_or_minimal(index_path):
    """Check if _INDEX.md is empty or has minimal content."""
    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if it's the auto-generated minimal version
        if "Créé automatiquement" in content:
            lines = [l.strip() for l in content.split('\n') if l.strip() and not l.strip().startswith('#')]
            if len(lines) <= 2:
                return True

        return False
    except:
        return False

def fix_vault_indexes(vault_path, dry_run=False):
    """Fix all _INDEX.md files in vault."""
    vault_path = Path(vault_path).resolve()

    print(f"{BLUE}{'='*70}{NC}")
    print(f"{BLUE}  _INDEX.md Automatic Repair{NC}")
    print(f"{BLUE}{'='*70}{NC}")
    print(f"Vault: {vault_path}")
    if dry_run:
        print(f"{YELLOW}DRY RUN MODE - No files will be modified{NC}")
    print()

    # Find all _INDEX.md files
    index_files = []
    for root, dirs, files in os.walk(vault_path):
        if '.obsidian' in root:
            continue
        if '_INDEX.md' in files:
            index_files.append(os.path.join(root, '_INDEX.md'))

    index_files.sort()

    fixed_count = 0
    skipped_count = 0

    for index_path in index_files:
        directory = os.path.dirname(index_path)
        rel_path = os.path.relpath(index_path, vault_path)

        # Check if needs fixing
        if not is_index_empty_or_minimal(index_path):
            print(f"{GREEN}✓{NC} {rel_path} - OK (has content)")
            skipped_count += 1
            continue

        # Generate new content
        new_content = generate_index_content(directory, vault_path)

        print(f"{YELLOW}→{NC} {rel_path} - FIXING")

        if not dry_run:
            try:
                with open(index_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"{GREEN}  ✅ Fixed{NC}")
                fixed_count += 1
            except Exception as e:
                print(f"{RED}  ❌ Error: {e}{NC}")
        else:
            print(f"{BLUE}  Would write:{NC}")
            print(f"{BLUE}{'-'*60}{NC}")
            lines = new_content.split('\n')
            for line in lines[:10]:
                print(f"{BLUE}  {line}{NC}")
            if len(lines) > 10:
                remaining = len(lines) - 10
                print(f"{BLUE}  ... ({remaining} more lines){NC}")
            print(f"{BLUE}{'-'*60}{NC}")
            fixed_count += 1

    print()
    print(f"{BOLD}{'='*70}{NC}")
    print(f"{BOLD}Summary{NC}")
    print(f"{BOLD}{'='*70}{NC}")
    print()
    print(f"{GREEN}✅ Fixed: {fixed_count}{NC}")
    print(f"{BLUE}⊘  Skipped (already OK): {skipped_count}{NC}")
    print()

    if dry_run:
        print(f"{YELLOW}DRY RUN - Run without --dry-run to apply changes{NC}")
    else:
        print(f"{GREEN}✅ All _INDEX.md files have been updated!{NC}")

    print(f"{BOLD}{'='*70}{NC}")

    return True

if __name__ == "__main__":
    dry_run = '--dry-run' in sys.argv
    success = fix_vault_indexes(VAULT_PATH, dry_run=dry_run)
    sys.exit(0 if success else 1)
