#!/usr/bin/env python3
"""
Check for broken Obsidian wiki links in markdown files.

Finds all [[wiki links]] and verifies that target files exist.
Outputs broken links with suggestions for fixes.
"""

import os
import re
import sys
from pathlib import Path
from collections import defaultdict

# ANSI colors
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
BOLD = '\033[1m'
NC = '\033[0m'

def find_wiki_links(content):
    """Extract all [[wiki links]] from content."""
    # Match [[link]] or [[link|alias]]
    pattern = r'\[\[([^\]|]+)(?:\|[^\]]*)?\]\]'
    return re.findall(pattern, content)

def find_all_markdown_files(vault_path):
    """Find all markdown files in vault."""
    md_files = {}
    for root, dirs, files in os.walk(vault_path):
        # Skip .obsidian directory
        if '.obsidian' in root:
            continue
        for file in files:
            if file.endswith('.md'):
                full_path = os.path.join(root, file)
                # Store both with and without .md extension
                name_without_ext = file[:-3]
                md_files[name_without_ext] = full_path
                md_files[file] = full_path
    return md_files

def check_links(vault_path):
    """Check all wiki links in vault for broken references."""
    vault_path = Path(vault_path).resolve()

    print(f"{BLUE}📊 Analyzing Obsidian Links{NC}")
    print(f"Vault: {vault_path}")
    print()

    # Find all markdown files
    md_files = find_all_markdown_files(vault_path)
    print(f"Found {len(md_files)} markdown files (with variants)")

    # Track statistics
    total_links = 0
    broken_links = []
    files_with_links = 0

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
                print(f"{RED}Error reading {file_path}: {e}{NC}")
                continue

            # Find all wiki links
            links = find_wiki_links(content)
            if not links:
                continue

            files_with_links += 1
            total_links += len(links)

            # Check each link
            for link in links:
                # Clean up the link (remove spaces, etc.)
                link_clean = link.strip()

                # Check if target exists
                # Try exact match first
                if link_clean not in md_files and f"{link_clean}.md" not in md_files:
                    broken_links.append({
                        'source': file_path,
                        'link': link,
                        'relative_source': os.path.relpath(file_path, vault_path)
                    })

    # Print results
    print()
    print(f"{BOLD}{'='*70}{NC}")
    print(f"{BOLD}Link Analysis Summary{NC}")
    print(f"{BOLD}{'='*70}{NC}")
    print()
    print(f"📄 Files analyzed: {len([f for f in md_files.values() if f.endswith('.md')])}")
    print(f"🔗 Files with links: {files_with_links}")
    print(f"🔗 Total wiki links: {total_links}")

    if broken_links:
        print(f"{RED}❌ Broken links: {len(broken_links)}{NC}")
        print()
        print(f"{BOLD}Broken Links:{NC}")
        print()

        for broken in broken_links:
            print(f"{RED}✗{NC} {broken['relative_source']}")
            print(f"  Link: {YELLOW}[[{broken['link']}]]{NC}")

            # Suggest similar files
            suggestions = []
            for name in md_files.keys():
                if broken['link'].lower() in name.lower() or name.lower() in broken['link'].lower():
                    suggestions.append(name)

            if suggestions:
                print(f"  Suggestions: {', '.join(suggestions[:3])}")
            print()
    else:
        print(f"{GREEN}✅ All links valid!{NC}")

    print(f"{BOLD}{'='*70}{NC}")

    return len(broken_links) == 0

if __name__ == "__main__":
    vault_path = sys.argv[1] if len(sys.argv) > 1 else "."

    if not os.path.exists(vault_path):
        print(f"{RED}Error: Vault path does not exist: {vault_path}{NC}")
        sys.exit(1)

    success = check_links(vault_path)
    sys.exit(0 if success else 1)
