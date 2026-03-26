#!/usr/bin/env python3
"""
FORGE Context Compiler v0.1
Deterministic compiler for .ctx.md context files.

Architecture: Two-layer design (Meeting 2 decision)
- This compiler is AGNOSTIC to file organization
- It receives a list of files and merge rules, produces one compiled output
- The Selector layer (in Orchestrator SKILL.md) decides WHICH files to compile

Usage:
    # Explicit files (manual selection):
    python compile_context.py master.ctx.md targets/veo3.ctx.md -o output.md

    # Auto-select by target (reads _index.md):
    python compile_context.py --target veo3 -o output.md

    # Auto-select by target with custom contexts dir:
    python compile_context.py --target veo3 --contexts-dir /path/to/contexts -o output.md

Design decisions (from Review Team Meetings):
    - Sections delimited by ## headings
    - Directives [OVERRIDE] and [EXTEND] in section headers
    - Default behavior: later file wins (child wins)
    - EXTEND: appends to existing section instead of replacing
    - Compiled output: generic → specific → CRITICAL (recency exploit)
    - Token estimation: word_count * 1.3
    - Hard limits: max 4 source files, warn at 2500 tokens
    - Fallback: no sections found → concatenate as single block
"""

import argparse
import os
import re
import sys
from datetime import datetime
from pathlib import Path


# ─── Constants ────────────────────────────────────────────────────────────────

MAX_SOURCE_FILES = 4
TOKEN_WARN_THRESHOLD = 2500
TOKEN_MULTIPLIER = 1.3  # words → approximate tokens


# ─── Parsing ──────────────────────────────────────────────────────────────────

def parse_meta(content: str) -> dict:
    """Extract @meta block from HTML comment at top of file."""
    meta = {}
    match = re.search(r'<!--\s*@meta\s*(.*?)\s*-->', content, re.DOTALL)
    if match:
        for line in match.group(1).strip().splitlines():
            line = line.strip()
            if ':' in line:
                key, val = line.split(':', 1)
                key = key.strip()
                val = val.strip()
                # Parse list values [tag1, tag2]
                if val.startswith('[') and val.endswith(']'):
                    val = [v.strip() for v in val[1:-1].split(',')]
                meta[key] = val
    return meta


def parse_sections(content: str) -> list:
    """
    Parse markdown into sections based on ## headings.
    Returns list of dicts: {name, directive, content, priority}

    Directives in headers: ## Section Name [OVERRIDE|EXTEND]
    No directive = default (child wins / replace)
    """
    # Remove @meta block before parsing sections
    content = re.sub(r'<!--\s*@meta\s*.*?\s*-->', '', content, flags=re.DOTALL).strip()

    sections = []
    # Split on ## headings (not ### or #)
    parts = re.split(r'^(##\s+.+)$', content, flags=re.MULTILINE)

    # Content before first ## heading → "preamble" section
    if parts[0].strip():
        sections.append({
            'name': '_preamble',
            'directive': None,
            'content': parts[0].strip(),
            'priority': 0,
            'is_critical': False,
        })

    # Process heading + content pairs
    for i in range(1, len(parts), 2):
        heading = parts[i].strip()
        body = parts[i + 1].strip() if i + 1 < len(parts) else ''

        # Parse directive from heading: ## Name [OVERRIDE|EXTEND]
        directive = None
        name = heading.lstrip('#').strip()

        directive_match = re.search(r'\[(OVERRIDE|EXTEND)\]\s*$', name)
        if directive_match:
            directive = directive_match.group(1)
            name = name[:directive_match.start()].strip()

        # Detect CRITICAL sections
        is_critical = 'CRITICAL' in name.upper()

        # Parse priority hint if present: ## Name (priority: 8)
        priority = 5  # default
        priority_match = re.search(r'\(priority:\s*(\d+)\)', name)
        if priority_match:
            priority = int(priority_match.group(1))
            name = name[:priority_match.start()].strip()

        if is_critical:
            priority = 10

        sections.append({
            'name': name,
            'directive': directive,
            'content': body,
            'priority': priority,
            'is_critical': is_critical,
        })

    return sections


def parse_file(filepath: str) -> dict:
    """Parse a .ctx.md file into structured data."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"  WARN: File not found: {filepath} — skipping", file=sys.stderr)
        return None
    except Exception as e:
        print(f"  WARN: Error reading {filepath}: {e} — skipping", file=sys.stderr)
        return None

    meta = parse_meta(content)
    sections = parse_sections(content)

    return {
        'path': filepath,
        'name': meta.get('name', Path(filepath).stem),
        'meta': meta,
        'sections': sections,
    }


# ─── Merging ──────────────────────────────────────────────────────────────────

def merge_sections(file_data_list: list) -> list:
    """
    Merge sections from multiple files.
    Order: files are processed in order (generic → specific).
    Rules:
        - Same section name, no directive: child wins (replace)
        - Same section name, OVERRIDE: child wins (explicit)
        - Same section name, EXTEND: child content appended to parent
        - New section: added to output
        - _preamble sections: always concatenated
    """
    merged = {}  # name → section dict
    order = []   # track insertion order

    for file_data in file_data_list:
        if file_data is None:
            continue
        for section in file_data['sections']:
            name = section['name']

            # Preambles always concatenate
            if name == '_preamble':
                if '_preamble' in merged:
                    merged['_preamble']['content'] += '\n\n' + section['content']
                else:
                    merged['_preamble'] = dict(section)
                    order.append('_preamble')
                continue

            if name in merged:
                if section['directive'] == 'EXTEND':
                    # Append to existing
                    merged[name]['content'] += '\n\n' + section['content']
                    # Keep higher priority
                    merged[name]['priority'] = max(merged[name]['priority'], section['priority'])
                    merged[name]['is_critical'] = merged[name]['is_critical'] or section['is_critical']
                else:
                    # OVERRIDE or default: child wins
                    merged[name] = dict(section)
            else:
                merged[name] = dict(section)
                order.append(name)

    # Return in order: non-critical by priority, then CRITICAL at the end
    regular = []
    critical = []

    for name in order:
        section = merged[name]
        if section['is_critical']:
            critical.append(section)
        else:
            regular.append(section)

    # Sort regular by priority (ascending — lower priority first, important later)
    regular.sort(key=lambda s: s['priority'])
    # Critical always at the end (recency exploit)
    critical.sort(key=lambda s: s['priority'])

    return regular + critical


# ─── Output ───────────────────────────────────────────────────────────────────

def estimate_tokens(text: str) -> int:
    """Estimate token count: words * 1.3"""
    words = len(text.split())
    return int(words * TOKEN_MULTIPLIER)


def render_compiled(sections: list, sources: list, target: str = None) -> str:
    """
    Render merged sections into compiled output.
    Format (Meeting 2 decision):
        - Header with metadata
        - Sections generic → specific
        - CRITICAL sections at the end (recency exploit)
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    source_names = ' + '.join([Path(s).name for s in sources])
    target_label = target or 'general'

    lines = []
    lines.append(f'# Compiled Context: {target_label}')
    lines.append(f'<!-- sources: {source_names} | compiled: {timestamp} -->')
    lines.append('')

    for section in sections:
        name = section['name']
        if name == '_preamble':
            lines.append(section['content'])
            lines.append('')
        else:
            # Mark critical sections visibly
            if section['is_critical']:
                # Avoid "CRITICAL — CRITICAL — X" duplication
                if name.upper().startswith('CRITICAL'):
                    lines.append(f"## {name}")
                else:
                    lines.append(f"## CRITICAL — {name}")
            else:
                lines.append(f"## {name}")
            lines.append('')
            lines.append(section['content'])
            lines.append('')

    return '\n'.join(lines)


# ─── Auto-select (target → file list) ────────────────────────────────────────

def auto_select(target: str, contexts_dir: str) -> list:
    """
    Read _index.md and find files matching target.
    Returns list of file paths (always includes master.ctx.md first).
    """
    index_path = os.path.join(contexts_dir, '_index.md')

    if not os.path.exists(index_path):
        print(f"  WARN: _index.md not found at {index_path}", file=sys.stderr)
        # Fallback: try to find master + targets/{target}.ctx.md
        files = []
        master = os.path.join(contexts_dir, 'master.ctx.md')
        if os.path.exists(master):
            files.append(master)
        target_file = os.path.join(contexts_dir, 'targets', f'{target}.ctx.md')
        if os.path.exists(target_file):
            files.append(target_file)
        return files

    # Parse _index.md — look for table rows matching target in tags
    files = []
    master = os.path.join(contexts_dir, 'master.ctx.md')
    if os.path.exists(master):
        files.append(master)

    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            index_content = f.read()

        # Parse markdown table rows: | name | path | tags | ...
        target_lower = target.lower()
        for line in index_content.splitlines():
            line = line.strip()
            if not line.startswith('|') or '---' in line:
                continue
            cells = [c.strip() for c in line.split('|')[1:-1]]
            if len(cells) >= 3:
                path = cells[1].strip()
                tags = cells[2].lower()
                if target_lower in tags and path != 'master.ctx.md':
                    full_path = os.path.join(contexts_dir, path)
                    if os.path.exists(full_path):
                        files.append(full_path)
    except Exception as e:
        print(f"  WARN: Error reading _index.md: {e}", file=sys.stderr)

    return files


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='FORGE Context Compiler — deterministic .ctx.md merger',
        epilog='Examples:\n'
               '  python compile_context.py master.ctx.md veo3.ctx.md -o compiled.md\n'
               '  python compile_context.py --target veo3 -o compiled.md',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('files', nargs='*', help='Context files to compile (in order: generic → specific)')
    parser.add_argument('-o', '--output', default='-', help='Output file (default: stdout)')
    parser.add_argument('--target', help='Auto-select files by target name (reads _index.md)')
    parser.add_argument('--contexts-dir', default=None, help='Path to contexts directory')
    parser.add_argument('--quiet', '-q', action='store_true', help='Suppress warnings')

    args = parser.parse_args()

    # Determine contexts directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    forge_dir = os.path.dirname(script_dir)  # forge/core/ → forge/
    contexts_dir = args.contexts_dir or os.path.join(forge_dir, 'contexts')

    # Resolve file list
    if args.target:
        files = auto_select(args.target, contexts_dir)
        if not files:
            print(f"  WARN: No context files found for target '{args.target}'", file=sys.stderr)
            sys.exit(0)
    elif args.files:
        # Resolve relative paths against contexts_dir
        files = []
        for f in args.files:
            if os.path.isabs(f):
                files.append(f)
            elif os.path.exists(f):
                files.append(f)
            elif os.path.exists(os.path.join(contexts_dir, f)):
                files.append(os.path.join(contexts_dir, f))
            else:
                print(f"  WARN: Cannot find file: {f}", file=sys.stderr)
    else:
        parser.print_help()
        sys.exit(1)

    # Enforce max source files limit
    if len(files) > MAX_SOURCE_FILES:
        print(f"  WARN: {len(files)} files exceed max {MAX_SOURCE_FILES}. Using first {MAX_SOURCE_FILES}.", file=sys.stderr)
        files = files[:MAX_SOURCE_FILES]

    if not args.quiet:
        print(f"  Compiling {len(files)} files: {', '.join(Path(f).name for f in files)}", file=sys.stderr)

    # Parse all files
    file_data_list = []
    for filepath in files:
        data = parse_file(filepath)
        if data:
            file_data_list.append(data)

    if not file_data_list:
        print("  WARN: No valid files to compile. Empty output.", file=sys.stderr)
        sys.exit(0)

    # Merge sections
    merged_sections = merge_sections(file_data_list)

    # Render output
    target_name = args.target or file_data_list[-1]['name']
    output = render_compiled(merged_sections, files, target=target_name)

    # Token estimation
    tokens = estimate_tokens(output)
    if not args.quiet:
        print(f"  Tokens (estimated): {tokens}", file=sys.stderr)
        if tokens > TOKEN_WARN_THRESHOLD:
            print(f"  WARN: Compiled output exceeds {TOKEN_WARN_THRESHOLD} token threshold!", file=sys.stderr)

    # Write output
    if args.output == '-':
        print(output)
    else:
        # Create parent directories if needed
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        if not args.quiet:
            print(f"  Output written to: {args.output}", file=sys.stderr)


if __name__ == '__main__':
    main()
