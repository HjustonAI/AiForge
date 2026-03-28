#!/usr/bin/env python3
"""
FORGE Context Validator v0.1
Structural validation for .ctx.md target context files.

Checks format, section completeness, token budget, and CRITICAL rule quality.
Does NOT assess content quality — that's the human's job (via test prompt proxy).

Usage:
    python validate_context.py forge/contexts/targets/gemini.ctx.md
    python validate_context.py forge/contexts/targets/gemini.ctx.md --strict
    python validate_context.py forge/contexts/targets/gemini.ctx.md --json

Exit codes:
    0 = all checks passed
    1 = warnings only (non-blocking)
    2 = errors found (blocking)

Design: Zero external dependencies. Uses word count * 1.3 for token estimation.
"""

import argparse
import json
import re
import sys
from pathlib import Path


# ─── Constants ────────────────────────────────────────────────────────────────

TOKEN_MULTIPLIER = 1.3
TOKEN_MIN = 800      # below this, context is suspiciously thin
TOKEN_TARGET_MAX = 2000  # ideal max for a target context
TOKEN_HARD_MAX = 2800    # above this, context is too bloated

REQUIRED_SECTIONS = [
    "Mental Model",
    "Prompt Architecture",
    "Leverage Points",
    "Failure Modes & Repair",
    "Calibration",
    "CRITICAL",
]

OPTIONAL_SECTIONS = [
    "Operating Environment",
]

CRITICAL_VERBS = [
    "ALWAYS", "NEVER", "PREFER", "INCLUDE", "AVOID",
    "REQUIRE", "ENSURE", "MATCH", "KEEP", "FRONT-LOAD",
]

VALID_CATEGORIES = ["generative", "analytical", "creative", "voice"]

# Section-level token ranges (word counts, not tokens)
SECTION_WORD_RANGES = {
    "Mental Model": (100, 250),
    "Prompt Architecture": (140, 350),
    "Leverage Points": (100, 250),
    "Failure Modes & Repair": (170, 400),
    "Calibration": (100, 250),
    "Operating Environment": (70, 300),
    "CRITICAL": (100, 250),
}


# ─── Parsing ──────────────────────────────────────────────────────────────────

def parse_meta(content: str) -> dict:
    """Extract @meta block from HTML comment."""
    meta = {}
    match = re.search(r'<!--\s*@meta\s*(.*?)\s*-->', content, re.DOTALL)
    if match:
        for line in match.group(1).strip().splitlines():
            line = line.strip()
            if ':' in line:
                key, val = line.split(':', 1)
                key = key.strip()
                val = val.strip()
                if val.startswith('[') and val.endswith(']'):
                    val = [v.strip() for v in val[1:-1].split(',')]
                meta[key] = val
    return meta


def parse_sections(content: str) -> dict:
    """Parse markdown into sections by ## headings. Returns {normalized_name: {raw_name, content, words}}."""
    # Remove meta block
    content = re.sub(r'<!--\s*@meta\s*.*?\s*-->', '', content, flags=re.DOTALL).strip()

    sections = {}
    parts = re.split(r'^(##\s+.+)$', content, flags=re.MULTILINE)

    for i in range(1, len(parts), 2):
        raw_name = parts[i].lstrip('#').strip()
        body = parts[i + 1].strip() if i + 1 < len(parts) else ''
        words = len(body.split())

        # Normalize: strip directives and target-specific suffixes for matching
        normalized = raw_name
        normalized = re.sub(r'\s*\[(OVERRIDE|EXTEND)\]\s*$', '', normalized)
        # "CRITICAL — Gemini Rules" → "CRITICAL"
        if 'CRITICAL' in normalized.upper():
            normalized = 'CRITICAL'

        sections[normalized] = {
            'raw_name': raw_name,
            'content': body,
            'words': words,
        }

    return sections


def estimate_tokens(text: str) -> int:
    """Estimate token count: words * 1.3"""
    return int(len(text.split()) * TOKEN_MULTIPLIER)


# ─── Checks ──────────────────────────────────────────────────────────────────

def check_meta(meta: dict) -> list:
    """Validate meta header. Returns list of (level, message)."""
    results = []

    if not meta:
        results.append(('ERROR', 'Missing @meta block in HTML comment'))
        return results

    # Required fields
    for field in ['name', 'tags', 'priority']:
        if field not in meta:
            results.append(('ERROR', f'Missing required meta field: {field}'))

    # Category
    category = meta.get('category', '')
    if not category:
        results.append(('WARN', 'Missing meta field: category (generative|analytical|creative|voice)'))
    elif category not in VALID_CATEGORIES:
        results.append(('WARN', f'Unknown category: "{category}". Expected: {", ".join(VALID_CATEGORIES)}'))

    # Tags should be a list with 3+ entries
    tags = meta.get('tags', [])
    if isinstance(tags, list) and len(tags) < 3:
        results.append(('WARN', f'Only {len(tags)} tags — recommend 3-5 for auto-selection'))

    # Name should be lowercase, no spaces
    name = meta.get('name', '')
    if name and (name != name.lower() or ' ' in name):
        results.append(('WARN', f'Meta name "{name}" should be lowercase with no spaces (e.g., "gemini-deep-research")'))

    return results


def check_sections(sections: dict) -> list:
    """Validate required sections are present."""
    results = []
    found = set(sections.keys())

    for req in REQUIRED_SECTIONS:
        if req not in found:
            results.append(('ERROR', f'Missing required section: ## {req}'))

    # Check Prompt Architecture has [OVERRIDE]
    pa = sections.get('Prompt Architecture')
    if pa and '[OVERRIDE]' not in pa['raw_name']:
        results.append(('WARN', 'Prompt Architecture section should have [OVERRIDE] directive'))

    # Check for unexpected sections (not required, not optional, not CRITICAL variant)
    expected = set(REQUIRED_SECTIONS + OPTIONAL_SECTIONS)
    for name in found:
        if name not in expected:
            results.append(('INFO', f'Non-standard section found: ## {sections[name]["raw_name"]}'))

    return results


def check_section_sizes(sections: dict) -> list:
    """Check section word counts against expected ranges."""
    results = []

    for name, (min_words, max_words) in SECTION_WORD_RANGES.items():
        if name not in sections:
            continue
        words = sections[name]['words']
        if words < min_words * 0.5:  # 50% of minimum = definitely too short
            results.append(('WARN', f'{name}: {words} words — very thin (expected {min_words}-{max_words})'))
        elif words < min_words:
            results.append(('INFO', f'{name}: {words} words — slightly below target ({min_words}-{max_words})'))
        elif words > max_words * 1.3:  # 130% of max = definitely too long
            results.append(('WARN', f'{name}: {words} words — overweight (expected {min_words}-{max_words})'))

    return results


def check_tokens(content: str) -> list:
    """Check overall token budget."""
    results = []
    tokens = estimate_tokens(content)

    if tokens < TOKEN_MIN:
        results.append(('WARN', f'Total: ~{tokens} tokens — suspiciously thin (target: {TOKEN_MIN}-{TOKEN_TARGET_MAX})'))
    elif tokens > TOKEN_HARD_MAX:
        results.append(('WARN', f'Total: ~{tokens} tokens — exceeds budget (target: {TOKEN_MIN}-{TOKEN_TARGET_MAX}, hard max: {TOKEN_HARD_MAX})'))
    elif tokens > TOKEN_TARGET_MAX:
        results.append(('INFO', f'Total: ~{tokens} tokens — above target but within budget (target max: {TOKEN_TARGET_MAX})'))
    else:
        results.append(('OK', f'Total: ~{tokens} tokens (within {TOKEN_MIN}-{TOKEN_TARGET_MAX} budget)'))

    return results


def check_critical_rules(sections: dict) -> list:
    """Validate CRITICAL rules section quality."""
    results = []

    critical = sections.get('CRITICAL')
    if not critical:
        return results

    content = critical['content']

    # Count rules (numbered lines starting with digit)
    rules = re.findall(r'^\d+\.\s+(.+)$', content, re.MULTILINE)

    if len(rules) < 5:
        results.append(('WARN', f'CRITICAL section has {len(rules)} rules — recommend 7-12'))
    elif len(rules) > 14:
        results.append(('WARN', f'CRITICAL section has {len(rules)} rules — too many, recommend 7-12 (dilution risk)'))
    else:
        results.append(('OK', f'CRITICAL section: {len(rules)} rules'))

    # Check rules start with approved verbs
    for i, rule in enumerate(rules, 1):
        first_word = rule.split()[0].upper().rstrip(',.:') if rule.split() else ''
        if first_word not in CRITICAL_VERBS:
            results.append(('WARN', f'CRITICAL rule {i} starts with "{first_word}" — expected verb like {", ".join(CRITICAL_VERBS[:5])}'))

    # Check for generic filler
    filler_phrases = ['be specific', 'high quality', 'best results', 'good output', 'try to']
    for phrase in filler_phrases:
        if phrase.lower() in content.lower():
            results.append(('WARN', f'CRITICAL section contains generic phrase "{phrase}" — rules should be operationally specific'))

    return results


def check_failure_modes(sections: dict) -> list:
    """Check Failure Modes section has proper FAILURE → WHY → REPAIR structure."""
    results = []

    fm = sections.get('Failure Modes & Repair')
    if not fm:
        return results

    content = fm['content'].upper()

    # Look for structural markers
    has_failure = 'FAILURE' in content or 'FAIL' in content
    has_why = 'WHY' in content or 'BECAUSE' in content or 'CAUSE' in content
    has_repair = 'REPAIR' in content or 'INSTEAD' in content or 'FIX' in content or 'SOLUTION' in content

    if not has_failure:
        results.append(('INFO', 'Failure Modes: consider labeling failure patterns explicitly (FAILURE: ...)'))
    if not has_repair:
        results.append(('WARN', 'Failure Modes: missing repair strategies — each failure should have a fix'))

    return results


# ─── Main ─────────────────────────────────────────────────────────────────────

def validate(filepath: str, strict: bool = False) -> dict:
    """Run all checks. Returns {status, errors, warnings, info, ok, results}."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        return {'status': 'ERROR', 'errors': 1, 'warnings': 0, 'info': 0, 'ok': 0,
                'results': [('ERROR', f'File not found: {filepath}')]}

    meta = parse_meta(content)
    sections = parse_sections(content)

    all_results = []
    all_results.extend(check_meta(meta))
    all_results.extend(check_sections(sections))
    all_results.extend(check_section_sizes(sections))
    all_results.extend(check_tokens(content))
    all_results.extend(check_critical_rules(sections))
    all_results.extend(check_failure_modes(sections))

    errors = sum(1 for level, _ in all_results if level == 'ERROR')
    warnings = sum(1 for level, _ in all_results if level == 'WARN')
    info = sum(1 for level, _ in all_results if level == 'INFO')
    ok = sum(1 for level, _ in all_results if level == 'OK')

    if errors > 0:
        status = 'FAIL'
    elif warnings > 0 and strict:
        status = 'FAIL'
    elif warnings > 0:
        status = 'WARN'
    else:
        status = 'PASS'

    return {
        'status': status,
        'file': filepath,
        'name': meta.get('name', Path(filepath).stem),
        'category': meta.get('category', 'unknown'),
        'tokens': estimate_tokens(content),
        'errors': errors,
        'warnings': warnings,
        'info': info,
        'ok': ok,
        'results': all_results,
    }


def main():
    parser = argparse.ArgumentParser(
        description='FORGE Context Validator — structural checks for .ctx.md files',
        epilog='Example: python validate_context.py forge/contexts/targets/gemini.ctx.md'
    )
    parser.add_argument('file', help='Path to .ctx.md file to validate')
    parser.add_argument('--strict', action='store_true', help='Treat warnings as errors')
    parser.add_argument('--json', action='store_true', help='Output results as JSON')
    parser.add_argument('--quiet', '-q', action='store_true', help='Only show errors and warnings')

    args = parser.parse_args()
    result = validate(args.file, strict=args.strict)

    if args.json:
        # Convert results tuples to dicts for JSON
        result['results'] = [{'level': level, 'message': msg} for level, msg in result['results']]
        print(json.dumps(result, indent=2))
    else:
        # Pretty print
        filename = Path(args.file).name
        print(f"\n  FORGE Context Validator — {filename}")
        print(f"  {'─' * 50}")

        for level, msg in result['results']:
            if args.quiet and level in ('INFO', 'OK'):
                continue
            icon = {'ERROR': '✗', 'WARN': '⚠', 'INFO': '·', 'OK': '✓'}[level]
            print(f"  {icon} [{level}] {msg}")

        print(f"  {'─' * 50}")
        status_icon = {'PASS': '✓', 'WARN': '⚠', 'FAIL': '✗'}[result['status']]
        print(f"  {status_icon} Status: {result['status']} | "
              f"~{result['tokens']} tokens | "
              f"{result['errors']} errors, {result['warnings']} warnings")
        print()

    sys.exit(0 if result['status'] in ('PASS', 'WARN') else 2)


if __name__ == '__main__':
    main()
