#!/usr/bin/env python3

"""
extract-obsidian-docs.py
Extrait documentation depuis code comments avec tag OBSIDIAN_DOC

Usage:
    python3 extract-obsidian-docs.py <file>                 # Affiche tags trouvés
    python3 extract-obsidian-docs.py <file> --auto-update   # Met à jour docs automatiquement
    python3 extract-obsidian-docs.py <dir> --recursive      # Scan récursif

Format attendu dans code:
    def function():
        '''
        OBSIDIAN_DOC: doc-file.md#section

        Description de la fonction...
        '''
        pass
"""

import sys
import os
import re
import argparse
from pathlib import Path
from typing import List, Tuple, Optional

# Couleurs terminal
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color

# Regex pour détecter tag OBSIDIAN_DOC
OBSIDIAN_DOC_PATTERN = r'OBSIDIAN_DOC:\s*(.+?)#(.+)'

# Workspace path
WORKSPACE = Path.home() / "Documents/APP_HOME/CascadeProjects/windsurf-project"
DOC_BASE = WORKSPACE / "Memories/vault/wiki/tools"


class ObsidianDocTag:
    """Représente un tag OBSIDIAN_DOC trouvé dans le code"""

    def __init__(self, file_path: str, line_number: int, doc_file: str, section: str, content: str):
        self.file_path = file_path
        self.line_number = line_number
        self.doc_file = doc_file
        self.section = section
        self.content = content

    def __repr__(self):
        return f"ObsidianDocTag({self.file_path}:{self.line_number} -> {self.doc_file}#{self.section})"


def extract_docstring(lines: List[str], start_index: int) -> Tuple[Optional[str], int]:
    """
    Extrait docstring à partir de start_index
    Retourne (docstring, end_index) ou (None, start_index) si pas de docstring
    """
    # Chercher début docstring (""" ou ''')
    quote_type = None
    i = start_index

    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('"""'):
            quote_type = '"""'
            break
        elif line.startswith("'''"):
            quote_type = "'''"
            break
        elif line and not line.startswith('#'):
            # Ligne non-vide qui n'est pas un commentaire = pas de docstring
            return None, start_index
        i += 1

    if not quote_type:
        return None, start_index

    # Extraire docstring
    docstring_lines = []
    i += 1  # Skip opening quotes

    while i < len(lines):
        line = lines[i]
        if quote_type in line:
            # Fin de docstring
            # Ajouter ligne avant closing quotes
            before_close = line.split(quote_type)[0]
            if before_close.strip():
                docstring_lines.append(before_close)
            break
        docstring_lines.append(line)
        i += 1

    docstring = '\n'.join(docstring_lines).strip()
    return docstring, i


def find_obsidian_tags(file_path: str) -> List[ObsidianDocTag]:
    """
    Parse fichier Python et trouve tous les tags OBSIDIAN_DOC
    """
    tags = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"{RED}Error reading {file_path}: {e}{NC}", file=sys.stderr)
        return tags

    i = 0
    while i < len(lines):
        line = lines[i]

        # Chercher définition de fonction/classe
        if line.strip().startswith('def ') or line.strip().startswith('class '):
            # Extraire docstring
            docstring, end_index = extract_docstring(lines, i + 1)

            if docstring:
                # Chercher tag OBSIDIAN_DOC dans docstring
                match = re.search(OBSIDIAN_DOC_PATTERN, docstring)
                if match:
                    doc_file = match.group(1).strip()
                    section = match.group(2).strip()

                    # Extraire reste de la docstring (sans le tag)
                    content = re.sub(r'OBSIDIAN_DOC:.*?\n', '', docstring, flags=re.DOTALL).strip()

                    tag = ObsidianDocTag(
                        file_path=file_path,
                        line_number=i + 1,
                        doc_file=doc_file,
                        section=section,
                        content=content
                    )
                    tags.append(tag)

                i = end_index
            else:
                i += 1
        else:
            i += 1

    return tags


def display_tags(tags: List[ObsidianDocTag], verbose: bool = False):
    """
    Affiche les tags trouvés
    """
    if not tags:
        print(f"{YELLOW}No OBSIDIAN_DOC tags found{NC}")
        return

    print(f"{GREEN}Found {len(tags)} OBSIDIAN_DOC tag(s):{NC}\n")

    for tag in tags:
        print(f"{BLUE}File:{NC} {tag.file_path}:{tag.line_number}")
        print(f"{BLUE}Doc:{NC} {tag.doc_file}#{tag.section}")

        if verbose:
            print(f"{BLUE}Content:{NC}")
            # Indenter content
            for line in tag.content.split('\n'):
                print(f"  {line}")

        print()


def update_documentation(tags: List[ObsidianDocTag], dry_run: bool = False) -> int:
    """
    Met à jour automatiquement les fichiers documentation
    Retourne nombre de fichiers modifiés
    """
    updated_count = 0

    # Grouper tags par fichier doc
    doc_updates = {}
    for tag in tags:
        if tag.doc_file not in doc_updates:
            doc_updates[tag.doc_file] = []
        doc_updates[tag.doc_file].append(tag)

    # Pour chaque fichier doc
    for doc_file, file_tags in doc_updates.items():
        doc_path = DOC_BASE / doc_file

        if not doc_path.exists():
            print(f"{RED}Warning: Doc file not found: {doc_path}{NC}")
            continue

        print(f"{BLUE}Processing {doc_file}...{NC}")

        # Lire fichier doc
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                doc_content = f.read()
        except Exception as e:
            print(f"{RED}Error reading {doc_path}: {e}{NC}")
            continue

        # Pour chaque tag, mettre à jour section
        modified = False
        for tag in file_tags:
            # Chercher section dans doc
            section_pattern = rf'(##\s+{re.escape(tag.section)}.*?)(?=\n##|\Z)'
            match = re.search(section_pattern, doc_content, re.DOTALL)

            if match:
                print(f"  {GREEN}✓{NC} Found section '{tag.section}'")

                if dry_run:
                    print(f"    {YELLOW}(dry-run: would update with content from {tag.file_path}:{tag.line_number}){NC}")
                else:
                    # TODO: Implémenter logique update intelligente
                    # Pour l'instant, juste afficher
                    print(f"    {YELLOW}(auto-update not yet implemented - manual update required){NC}")
            else:
                print(f"  {RED}✗{NC} Section '{tag.section}' not found in {doc_file}")

        if modified:
            updated_count += 1

    return updated_count


def scan_directory(directory: str, recursive: bool = False) -> List[ObsidianDocTag]:
    """
    Scan directory pour fichiers Python
    """
    all_tags = []
    dir_path = Path(directory)

    pattern = "**/*.py" if recursive else "*.py"

    for py_file in dir_path.glob(pattern):
        if py_file.is_file():
            tags = find_obsidian_tags(str(py_file))
            all_tags.extend(tags)

    return all_tags


def main():
    parser = argparse.ArgumentParser(
        description="Extract OBSIDIAN_DOC tags from Python files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s ~/scripts/mem0_mcp_server.py
  %(prog)s ~/scripts/mem0_mcp_server.py --verbose
  %(prog)s ~/scripts/mem0_mcp_server.py --auto-update
  %(prog)s ~/scripts --recursive
        """
    )

    parser.add_argument('path', help='Python file or directory to scan')
    parser.add_argument('--auto-update', action='store_true',
                        help='Automatically update documentation files')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be updated without modifying files')
    parser.add_argument('--recursive', action='store_true',
                        help='Recursively scan directory')
    parser.add_argument('--verbose', action='store_true',
                        help='Show extracted content')

    args = parser.parse_args()

    # Expand ~ to home directory
    path = os.path.expanduser(args.path)

    # Vérifier path existe
    if not os.path.exists(path):
        print(f"{RED}Error: Path not found: {path}{NC}", file=sys.stderr)
        sys.exit(1)

    # Scan file ou directory
    if os.path.isfile(path):
        tags = find_obsidian_tags(path)
    elif os.path.isdir(path):
        tags = scan_directory(path, recursive=args.recursive)
    else:
        print(f"{RED}Error: Path is neither file nor directory: {path}{NC}", file=sys.stderr)
        sys.exit(1)

    # Afficher résultats
    display_tags(tags, verbose=args.verbose)

    # Auto-update si demandé
    if args.auto_update and tags:
        print(f"\n{BLUE}Auto-updating documentation...{NC}\n")
        updated = update_documentation(tags, dry_run=args.dry_run)
        print(f"\n{GREEN}Updated {updated} documentation file(s){NC}")

    # Exit code
    sys.exit(0 if tags else 1)


if __name__ == '__main__':
    main()
