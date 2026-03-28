#!/usr/bin/env python3
"""
FORGE Arsenal & Context Sync v0.1
Validates that _index.md entries match actual files on disk.
Can auto-repair by removing ghost entries.

Usage:
    python arsenal-sync.py forge --check     # Report only (default)
    python arsenal-sync.py forge --fix       # Remove ghost entries from indexes

Design: Zero external dependencies. Reads markdown tables, checks file existence.
"""
import argparse
import os
import re
import sys


def parse_index_table(index_path):
    """
    Parse markdown table from _index.md.
    Returns list of dicts with 'name', 'path', 'line' (original line text).
    Handles variable column counts by looking for path-like values.
    """
    entries = []
    if not os.path.exists(index_path):
        return entries

    with open(index_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    header_found = False
    path_col_idx = None

    for line in lines:
        stripped = line.strip()
        if not stripped.startswith('|'):
            continue

        cells = [c.strip() for c in stripped.split('|')]
        # Remove empty strings from leading/trailing |
        cells = [c for c in cells if c != '']

        if not cells:
            continue

        # Skip separator rows
        if all(re.match(r'^-+$', c) for c in cells):
            continue

        # Detect header row — find which column has "Path"
        if not header_found:
            for idx, cell in enumerate(cells):
                if cell.lower() == 'path':
                    path_col_idx = idx
                    break
            header_found = True
            continue

        # Data row
        if len(cells) < 2:
            continue

        name = cells[0]

        # Use detected path column, or try to find a path-like value
        path = ''
        if path_col_idx is not None and path_col_idx < len(cells):
            path = cells[path_col_idx]
        else:
            # Fallback: look for cell containing / or .md or .ctx.md
            for cell in cells[1:]:
                if '/' in cell or cell.endswith('.md'):
                    path = cell
                    break

        if path:
            entries.append({
                'name': name,
                'path': path,
                'line': stripped,
            })

    return entries


def check_sync(forge_dir, index_type):
    """
    Check index vs files.
    Returns (ok_entries, ghost_entries).
    """
    if index_type == 'arsenal':
        index_path = os.path.join(forge_dir, 'arsenal', '_index.md')
        base_dir = os.path.join(forge_dir, 'arsenal')
    elif index_type == 'contexts':
        index_path = os.path.join(forge_dir, 'contexts', '_index.md')
        base_dir = os.path.join(forge_dir, 'contexts')
    else:
        return [], []

    entries = parse_index_table(index_path)
    ok = []
    ghosts = []

    for entry in entries:
        full_path = os.path.join(base_dir, entry['path'])
        if os.path.exists(full_path):
            ok.append(entry)
        else:
            ghosts.append(entry)

    return ok, ghosts


def fix_index(forge_dir, index_type):
    """Remove ghost entries from _index.md by filtering out their lines."""
    if index_type == 'arsenal':
        index_path = os.path.join(forge_dir, 'arsenal', '_index.md')
    elif index_type == 'contexts':
        index_path = os.path.join(forge_dir, 'contexts', '_index.md')
    else:
        return

    _, ghosts = check_sync(forge_dir, index_type)
    if not ghosts:
        print(f"  {index_type}: No ghost entries to fix.")
        return

    ghost_lines = {g['line'] for g in ghosts}

    with open(index_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = [l for l in lines if l.strip() not in ghost_lines]

    with open(index_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

    for g in ghosts:
        print(f"  REMOVED from {index_type}: {g['name']} (missing: {g['path']})")


def main():
    parser = argparse.ArgumentParser(
        description='FORGE Arsenal & Context Sync — validate index/file consistency',
        epilog='Examples:\n'
               '  python arsenal-sync.py forge --check\n'
               '  python arsenal-sync.py forge --fix',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('forge_dir', help='Path to forge directory')
    parser.add_argument('--check', action='store_true', default=True,
                        help='Check sync only (default)')
    parser.add_argument('--fix', action='store_true',
                        help='Fix by removing ghost entries from indexes')
    args = parser.parse_args()

    total_ghosts = 0

    for idx_type in ['arsenal', 'contexts']:
        ok, ghosts = check_sync(args.forge_dir, idx_type)
        status = "OK" if not ghosts else "GHOSTS FOUND"
        print(f"  {idx_type}: {len(ok)} valid, {len(ghosts)} ghost(s) [{status}]")

        for g in ghosts:
            print(f"    GHOST: '{g['name']}' -> {g['path']}")
            total_ghosts += 1

        if args.fix and ghosts:
            fix_index(args.forge_dir, idx_type)

    if total_ghosts == 0:
        print("\n  All indexes are in sync.")
    elif not args.fix:
        print(f"\n  Found {total_ghosts} ghost(s). Run with --fix to remove them.")

    sys.exit(0 if total_ghosts == 0 else 1)


if __name__ == '__main__':
    main()
