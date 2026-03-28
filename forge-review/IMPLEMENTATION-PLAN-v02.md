# FORGE v0.2 — Implementation Plan

> Na podstawie: MEETING-6-live-session-review.md (2026-03-28)
> Cel: naprawić 9 action items z przeglądu w 3 fazach priorytetowych
> Styl: każdy fix = konkretna zmiana w konkretnym pliku z diffem lub pseudokodem

---

## Mapa plików — co istnieje, co modyfikujemy, co tworzymy

```
forge/
├── core/
│   ├── forge-init.sh          ← MODIFY (Fix 2.1) — encoding, sync
│   ├── compile_context.py     ← OK (no changes)
│   ├── validate_context.py    ← MODIFY (Fix 2.4) — freshness check
│   ├── context-smith.md       ← MODIFY (Fix 1.1, 2.3) — large file handling, coverage
│   ├── prompt-smith.md        ← MODIFY (Fix 2.2) — arsenal awareness
│   ├── chunk-reader.py        ← CREATE (Fix 1.1) — large file chunking utility
│   └── arsenal-sync.py        ← CREATE (Fix 2.1) — index/file sync validator
├── contexts/
│   ├── _index.md              ← OK (format unchanged, freshness added via validate)
│   ├── _template.ctx.md       ← MODIFY (Fix 2.4) — add last_validated to meta
│   ├── master.ctx.md          ← OK
│   └── targets/
│       ├── veo3.ctx.md        ← OK
│       └── gemini-deep-research.ctx.md ← OK
├── arsenal/
│   ├── _index.md              ← OK (format unchanged)
│   └── prompts/               ← OK
└── .cache/
    └── compiled.ctx.md        ← OK (generated)

.claude/skills/forge/
└── SKILL.md                   ← MODIFY (Fix 1.2, 1.3, 2.2) — enforce compile, plan mode, arsenal
```

---

## FAZA 1 — CRITICAL (blokujące, bez zależności między sobą)

Kolejność: mogą być implementowane równolegle. Nie mają zależności.
Estimated effort: ~2h łącznie.

---

### Fix 1.1 — Obsługa dużych plików w distylacji

**Problem:** Read tool ma limit ~10k tokenów. Materiał Veo3 miał 22k. Model próbował 3 strategie Read — wszystkie za duże. Distylacja z niekompletnymi danymi.

**Rozwiązanie:** Nowy skrypt `chunk-reader.py` + modyfikacja workflow w SKILL.md i context-smith.md.

#### Nowy plik: `forge/core/chunk-reader.py`

```python
#!/usr/bin/env python3
"""
FORGE Chunk Reader v0.1
Reads large files and reports statistics. Designed for files too large
for Claude's Read tool (>10k tokens).

Usage:
    python chunk-reader.py <file> --stats        # Show file stats only
    python chunk-reader.py <file> --chunk N       # Print chunk N (0-indexed, 5000 tokens each)
    python chunk-reader.py <file> --sections      # Print section headers with line ranges
    python chunk-reader.py <file> --head N        # Print first N lines
    python chunk-reader.py <file> --tail N        # Print last N lines
"""
import argparse
import re
import sys

TOKEN_MULTIPLIER = 1.3
CHUNK_SIZE_WORDS = 3800  # ~5000 tokens per chunk

def estimate_tokens(text):
    return int(len(text.split()) * TOKEN_MULTIPLIER)

def get_stats(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    lines = content.splitlines()
    words = len(content.split())
    tokens = estimate_tokens(content)

    # Find ## sections
    sections = []
    for i, line in enumerate(lines, 1):
        if line.startswith('## '):
            sections.append((i, line.strip()))

    chunks_needed = max(1, (words + CHUNK_SIZE_WORDS - 1) // CHUNK_SIZE_WORDS)

    return {
        'lines': len(lines),
        'words': words,
        'tokens': tokens,
        'sections': sections,
        'chunks_needed': chunks_needed,
        'content': content,
        'lines_list': lines,
    }

def print_stats(stats, filepath):
    print(f"  File: {filepath}")
    print(f"  Lines: {stats['lines']}")
    print(f"  Words: {stats['words']}")
    print(f"  Tokens (est.): {stats['tokens']}")
    print(f"  Chunks needed: {stats['chunks_needed']} (at ~5000 tokens each)")
    print(f"  Sections ({len(stats['sections'])}):")
    for line_num, heading in stats['sections']:
        print(f"    L{line_num}: {heading}")

def print_chunk(stats, chunk_idx):
    words = stats['content'].split()
    start = chunk_idx * CHUNK_SIZE_WORDS
    end = min(start + CHUNK_SIZE_WORDS, len(words))
    if start >= len(words):
        print(f"  Chunk {chunk_idx} is out of range (file has {stats['chunks_needed']} chunks)", file=sys.stderr)
        sys.exit(1)
    chunk_text = ' '.join(words[start:end])
    print(f"--- Chunk {chunk_idx}/{stats['chunks_needed']-1} (words {start}-{end-1}/{len(words)-1}) ---")
    print(chunk_text)

def print_sections(stats):
    for line_num, heading in stats['sections']:
        print(f"  L{line_num}: {heading}")

def print_head(stats, n):
    for i, line in enumerate(stats['lines_list'][:n], 1):
        print(f"  {i:4d} | {line}")

def print_tail(stats, n):
    total = len(stats['lines_list'])
    start = max(0, total - n)
    for i, line in enumerate(stats['lines_list'][start:], start + 1):
        print(f"  {i:4d} | {line}")

def main():
    parser = argparse.ArgumentParser(description='FORGE Chunk Reader')
    parser.add_argument('file', help='File to read')
    parser.add_argument('--stats', action='store_true', help='Show file statistics')
    parser.add_argument('--chunk', type=int, metavar='N', help='Print chunk N')
    parser.add_argument('--sections', action='store_true', help='List section headers')
    parser.add_argument('--head', type=int, metavar='N', help='Print first N lines')
    parser.add_argument('--tail', type=int, metavar='N', help='Print last N lines')
    args = parser.parse_args()

    stats = get_stats(args.file)

    if args.stats or (not args.chunk and args.chunk != 0 and not args.sections
                       and not args.head and not args.tail):
        print_stats(stats, args.file)
    if args.sections:
        print_sections(stats)
    if args.chunk is not None:
        print_chunk(stats, args.chunk)
    if args.head:
        print_head(stats, args.head)
    if args.tail:
        print_tail(stats, args.tail)

if __name__ == '__main__':
    main()
```

#### Modyfikacja: `SKILL.md` — DISTILL STEP 3

**Obecny tekst (linie 182-184):**
```
### DISTILL STEP 3 — Read Source Material

Read the uploaded research file(s). If multiple files, read all of them.
Assess input quality (HIGH/MEDIUM/LOW) as defined in context-smith.md.
```

**Nowy tekst:**
```markdown
### DISTILL STEP 3 — Read Source Material

**CRITICAL: Large file handling protocol.**

Before reading, check file size:
```bash
PYTHONIOENCODING=utf-8 python forge/core/chunk-reader.py "[file_path]" --stats
```

**If file ≤ 10k tokens** → Read normally with Read tool.

**If file > 10k tokens** → Use chunk reader:
1. Run `--stats` to see total size and section structure
2. Run `--head 150` and `--tail 80` to get beginning and end
3. If still missing sections, use `--chunk N` for specific chunks
4. After reading, verify: "Przeczytałem [X]% materiału ([Y] z [Z] linii).
   Sekcje pokryte: [lista]. Sekcje potencjalnie pominięte: [lista]."

**NEVER mark input as HIGH quality if you read less than 80% of the material.**
If coverage < 80%, output must be marked PARTIAL in the report to the user.

Assess input quality (HIGH/MEDIUM/LOW) as defined in context-smith.md.
```

#### Modyfikacja: `context-smith.md` — dodaj Coverage Verification (po Pass 2)

**Dodaj nową sekcję po linii 92 (po "If any answer is NO, revise..."):**

```markdown
### Coverage Verification (for chunked/large inputs)

If the source material was read in chunks or only partially:

1. List all sections from the template that the ctx covers
2. For each section, rate source coverage: FULL / PARTIAL / INFERRED / MISSING
3. If any required section has MISSING source coverage:
   - Do NOT fill it with generic knowledge
   - Mark it: `<!-- COVERAGE: MISSING — needs additional source material -->`
   - Inform the user: "Sekcja [X] nie ma pokrycia w materiale źródłowym.
     Potrzebuję dodatkowego materiału lub Twojej wiedzy operacyjnej."

Coverage report format (include in output to user):
```
| Section | Coverage | Source lines |
|---------|----------|-------------|
| Mental Model | FULL | L1-45 |
| Prompt Architecture | FULL | L46-120 |
| Leverage Points | PARTIAL | L121-180 (missing audio details) |
| Failure Modes | FULL | L181-280 |
| Calibration | INFERRED | (no dedicated section in source) |
| CRITICAL Rules | FULL | scattered across source |
```
```

---

### Fix 1.2 — Wymuszenie compile_context.py jako krok blokujący

**Problem:** W sesji model pominął compile_context.py w PROMPT MODE. Czytał pliki ręcznie przez sub-agentów. Wynik mógł się różnić od deterministycznej kompilacji.

**Rozwiązanie:** Zmiana STEP 3 w SKILL.md — dodanie blocking gate i verification.

#### Modyfikacja: `SKILL.md` STEP 3 (linie 109-125)

**Obecny tekst:**
```markdown
### STEP 3 — Compile Context

Run the compiler to merge relevant context files:

```bash
python forge/core/compile_context.py --target [target] -o forge/.cache/compiled.ctx.md
```

Or with explicit files:
```bash
python forge/core/compile_context.py forge/contexts/master.ctx.md forge/contexts/targets/[target].ctx.md -o forge/.cache/compiled.ctx.md
```

Then read the compiled output:
```
Read file: forge/.cache/compiled.ctx.md
```
```

**Nowy tekst:**
```markdown
### STEP 3 — Compile Context [BLOCKING]

**This step is MANDATORY when compilation was selected in STEP 2.**
**Do NOT proceed to STEP 4 without a compiled output file.**
**Do NOT "compile in your head" by reading raw context files separately.**

Run the compiler:
```bash
PYTHONIOENCODING=utf-8 python forge/core/compile_context.py --target [target] -o forge/.cache/compiled.ctx.md
```

Then read the compiled output:
```
Read file: forge/.cache/compiled.ctx.md
```

**Verification gate:** Before proceeding to STEP 4, confirm:
- [ ] `forge/.cache/compiled.ctx.md` exists and was just generated
- [ ] You are reading from the COMPILED file, not from raw .ctx.md files

**If compile fails** (error, missing files, etc.):
1. Report the error to the user: "Kompilacja nie powiodła się: [error]"
2. Ask: "Kontynuować z bazową wiedzą (master only) czy naprawić?"
3. Do NOT silently fall back to "reading files manually"

**If bash is not available** (e.g., plan mode):
→ See PLATFORM CONSTRAINTS section below for delegation strategy.
```

---

### Fix 1.3 — Plan Mode Handling

**Problem:** Sesja była w plan mode. FORGE wymaga bash (forge-init.sh, compile_context.py). Model improwizował workaround'y, tracąc ~30% interakcji.

**Rozwiązanie:** Nowa sekcja w SKILL.md z explicit plan mode strategy.

#### Modyfikacja: `SKILL.md` — dodaj nową sekcję po STEP 0 (przed PROMPT MODE)

**Nowa sekcja (wstaw po linii 64, przed "## PROMPT MODE"):**

```markdown
## PLATFORM CONSTRAINTS

### Plan Mode Detection & Handling

Claude Code sometimes operates in "plan mode" which restricts Bash execution.
FORGE requires bash for: forge-init.sh, compile_context.py, validate_context.py.

**Detection:** If your first Bash call returns a plan-mode error or is blocked,
you are in plan mode.

**Strategy — delegate to sub-agents:**

For STEP 0 (Session Init):
```
Agent(type="general", prompt="Run this command and return the full output:
  bash forge/core/forge-init.sh forge
Working directory: [workspace root]")
```

For STEP 3 (Compile Context):
```
Agent(type="general", prompt="Run these commands in order and return all output:
  1. PYTHONIOENCODING=utf-8 python forge/core/compile_context.py --target [target] -o forge/.cache/compiled.ctx.md
  2. cat forge/.cache/compiled.ctx.md
Working directory: [workspace root]")
```

For DISTILL STEP 5 (Validate & Test):
```
Agent(type="general", prompt="Run these commands in order and return all output:
  1. PYTHONIOENCODING=utf-8 python forge/core/validate_context.py forge/contexts/targets/[target].ctx.md
  2. PYTHONIOENCODING=utf-8 python forge/core/compile_context.py --target [target] -o forge/.cache/compiled.ctx.md
Working directory: [workspace root]")
```

**Key rule:** Sub-agents are NOT restricted by plan mode. Always prepend
`PYTHONIOENCODING=utf-8` to Python commands (Windows encoding fix).

**Cost awareness:** Each sub-agent uses ~30k tokens for context setup.
Batch multiple commands in ONE sub-agent when possible.

### Read Tool Token Limit

Claude's Read tool has a ~10k token limit per call. For files > 10k tokens:
→ Use `forge/core/chunk-reader.py` via Bash (or sub-agent if in plan mode).
→ See DISTILL STEP 3 for the full protocol.

### Windows Encoding

All Python scripts that produce formatted output (box-drawing, unicode) may
crash on Windows with `UnicodeEncodeError: 'charmap'`.

**Universal fix:** Always prefix Python calls with `PYTHONIOENCODING=utf-8`.
This applies to: validate_context.py, compile_context.py, chunk-reader.py.

---
```

---

## FAZA 2 — IMPORTANT (zależności zaznaczone)

Kolejność implementacji: 2.1 → 2.2 → 2.3 → 2.4 (lekkie zależności).
Estimated effort: ~2h łącznie.

---

### Fix 2.1 — forge-init.sh: encoding + index/file sync

**Problem:** (a) `grep -P` nie działa na Windows/Git Bash, (b) Arsenal _index.md miał ghost entry (plik usunięty, wpis pozostał), (c) brak UTF-8 declaration.

**Rozwiązanie:** Przepisanie problematycznych sekcji + dodanie sync validation.

#### Modyfikacja: `forge/core/forge-init.sh`

**Pełna nowa wersja:**

```bash
#!/bin/bash
# FORGE Session Init — Warm Start Script v0.2
# Generates a quick snapshot of FORGE state for session context.
# Called by Orchestrator at session start.
#
# Usage: bash forge/core/forge-init.sh [forge-root-dir]
# Changes in v0.2:
#   - Replaced grep -P with POSIX-compatible grep -E
#   - Added index/file sync validation (ghost entry detection)
#   - Added UTF-8 locale hint
#   - Added freshness reporting for context files

export LANG=en_US.UTF-8 2>/dev/null
export LC_ALL=en_US.UTF-8 2>/dev/null

FORGE_DIR="${1:-forge}"

echo "=== FORGE Session Snapshot ==="

# Context files count
CTX_COUNT=$(find "$FORGE_DIR/contexts" -name '*.ctx.md' 2>/dev/null | grep -v _template | wc -l | tr -d ' ')
echo "Contexts: ${CTX_COUNT} files"

# List available targets
TARGETS=$(find "$FORGE_DIR/contexts/targets" -name '*.ctx.md' 2>/dev/null | while read -r f; do basename "$f" .ctx.md; done | tr '\n' ', ' | sed 's/,$//')
if [ -n "$TARGETS" ]; then
    echo "Targets: ${TARGETS}"
fi

# Arsenal count (actual files, not index entries)
ARSENAL_COUNT=$(find "$FORGE_DIR/arsenal/prompts" -name '*.md' 2>/dev/null | wc -l | tr -d ' ')
echo "Arsenal: ${ARSENAL_COUNT} prompts"

# Top-rated arsenal items
if [ "$ARSENAL_COUNT" -gt 0 ]; then
    echo ""
    echo "=== Recent Arsenal ==="
    ls -t "$FORGE_DIR/arsenal/prompts/" 2>/dev/null | head -5

    echo ""
    echo "=== Top Rated ==="
    for f in "$FORGE_DIR/arsenal/prompts/"*.md; do
        [ -f "$f" ] || continue
        # POSIX-compatible quality extraction (no grep -P)
        quality=$(grep -m1 'quality:' "$f" 2>/dev/null | grep -oE '[0-9]+' | head -1)
        name=$(basename "$f" .md)
        if [ -n "$quality" ]; then
            echo "  ${name}: ${quality}/10"
        fi
    done | sort -t: -k2 -rn | head -5
fi

# === SYNC VALIDATION ===
echo ""
echo "=== Sync Check ==="

SYNC_OK=true

# Check arsenal: index entries vs actual files
if [ -f "$FORGE_DIR/arsenal/_index.md" ]; then
    while IFS='|' read -r _ name _ _ _ _ path _; do
        name=$(echo "$name" | xargs 2>/dev/null)
        path=$(echo "$path" | xargs 2>/dev/null)
        [ -z "$path" ] && continue
        [[ "$path" == "Path" ]] && continue  # skip header
        [[ "$path" == "---"* ]] && continue  # skip separator
        full_path="$FORGE_DIR/arsenal/$path"
        if [ ! -f "$full_path" ]; then
            echo "  GHOST: Arsenal index has '$name' but file missing: $path"
            SYNC_OK=false
        fi
    done < "$FORGE_DIR/arsenal/_index.md"
fi

# Check contexts: index entries vs actual files
if [ -f "$FORGE_DIR/contexts/_index.md" ]; then
    while IFS='|' read -r _ name path _ _ _; do
        name=$(echo "$name" | xargs 2>/dev/null)
        path=$(echo "$path" | xargs 2>/dev/null)
        [ -z "$path" ] && continue
        [[ "$path" == "Path" ]] && continue
        [[ "$path" == "---"* ]] && continue
        full_path="$FORGE_DIR/contexts/$path"
        if [ ! -f "$full_path" ]; then
            echo "  GHOST: Context index has '$name' but file missing: $path"
            SYNC_OK=false
        fi
    done < "$FORGE_DIR/contexts/_index.md"
fi

if $SYNC_OK; then
    echo "  OK: All index entries match existing files."
fi

# Stale contexts (>30 days without modification)
echo ""
STALE=$(find "$FORGE_DIR/contexts" -name '*.ctx.md' -mtime +30 2>/dev/null | grep -v _template)
if [ -n "$STALE" ]; then
    echo "=== Stale Contexts (>30 days) ==="
    echo "$STALE" | while read -r f; do
        echo "  STALE: $(basename "$f")"
    done
else
    echo "No stale contexts."
fi

echo ""
echo "=== FORGE Ready ==="
```

#### Nowy plik: `forge/core/arsenal-sync.py`

```python
#!/usr/bin/env python3
"""
FORGE Arsenal Sync v0.1
Validates that _index.md entries match actual files.
Can auto-repair by removing ghost entries.

Usage:
    python arsenal-sync.py forge --check     # Report only
    python arsenal-sync.py forge --fix       # Remove ghost entries
"""
import argparse
import os
import re
import sys

def parse_index(index_path):
    """Parse markdown table from _index.md. Returns list of (name, path, full_line)."""
    entries = []
    if not os.path.exists(index_path):
        return entries
    with open(index_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line.startswith('|') or '---' in line:
                continue
            cells = [c.strip() for c in line.split('|')]
            cells = [c for c in cells if c]  # remove empty from leading/trailing |
            if len(cells) >= 2 and cells[0].lower() != 'name':
                entries.append({
                    'name': cells[0],
                    'path': cells[1] if len(cells) > 1 else '',
                    'line': line,
                })
    return entries

def check_sync(forge_dir, index_type):
    """Check index vs files. Returns (ok_entries, ghost_entries)."""
    if index_type == 'arsenal':
        index_path = os.path.join(forge_dir, 'arsenal', '_index.md')
        base_dir = os.path.join(forge_dir, 'arsenal')
    else:
        index_path = os.path.join(forge_dir, 'contexts', '_index.md')
        base_dir = os.path.join(forge_dir, 'contexts')

    entries = parse_index(index_path)
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
    """Remove ghost entries from _index.md."""
    if index_type == 'arsenal':
        index_path = os.path.join(forge_dir, 'arsenal', '_index.md')
        base_dir = os.path.join(forge_dir, 'arsenal')
    else:
        index_path = os.path.join(forge_dir, 'contexts', '_index.md')
        base_dir = os.path.join(forge_dir, 'contexts')

    _, ghosts = check_sync(forge_dir, index_type)
    if not ghosts:
        print(f"  {index_type}: No ghost entries found.")
        return

    ghost_lines = {g['line'] for g in ghosts}

    with open(index_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = [l for l in lines if l.strip() not in ghost_lines]

    with open(index_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

    for g in ghosts:
        print(f"  REMOVED: {g['name']} (file missing: {g['path']})")

def main():
    parser = argparse.ArgumentParser(description='FORGE Arsenal/Context Sync')
    parser.add_argument('forge_dir', help='Path to forge directory')
    parser.add_argument('--check', action='store_true', help='Check sync only')
    parser.add_argument('--fix', action='store_true', help='Fix by removing ghost entries')
    args = parser.parse_args()

    for idx_type in ['arsenal', 'contexts']:
        ok, ghosts = check_sync(args.forge_dir, idx_type)
        print(f"\n  {idx_type}: {len(ok)} OK, {len(ghosts)} ghost(s)")
        for g in ghosts:
            print(f"    GHOST: {g['name']} → {g['path']}")

        if args.fix and ghosts:
            fix_index(args.forge_dir, idx_type)

if __name__ == '__main__':
    main()
```

---

### Fix 2.2 — Arsenal-Aware Generation

**Problem:** Arsenal ma prompty z ocenami, ale model nie sprawdza ich przed generacją. 50 promptów nie wpływa na 51-szy.

**Rozwiązanie:** Dodanie Arsenal lookup do STEP 4 w SKILL.md + modyfikacja prompt-smith.md.

**Zależność:** Wymaga Fix 2.1 (sync), bo Arsenal z ghost entries dałby złe referencje.

#### Modyfikacja: `SKILL.md` — nowy STEP 3.5 (między STEP 3 a STEP 4)

**Dodaj po STEP 3:**

```markdown
### STEP 3.5 — Arsenal Reference (optional warm start)

Before generating, check if the arsenal has high-rated prompts for this target:

1. Read `forge/arsenal/_index.md`
2. Filter entries where Target matches current target AND Quality ≥ 8
3. If found: Read the BEST rated prompt (highest quality, most recent if tied)
4. Pass it to Prompt-Smith as "Arsenal Reference"

**Budget limit:** Arsenal reference adds ~300-500 tokens. If the reference
prompt is longer than 500 words, skip it.

**If no high-rated prompts exist** → skip this step. No overhead.

**Format for Prompt-Smith:**
```
Arsenal Reference (target: [target], quality: [N]/10):
[prompt text]
```
```

#### Modyfikacja: `prompt-smith.md` — rozszerz Arsenal Awareness (linie 72-78)

**Obecny tekst:**
```markdown
## Arsenal Awareness

When generating, check if there are existing prompts in the arsenal for this target.
If relevant ones exist, mention briefly:
"Masz X promptów do [target] w arsenale. Najlepszy: [name] ([rating]/10)."

This helps the user build on previous work rather than starting from scratch.
```

**Nowy tekst:**
```markdown
## Arsenal Awareness

### Passive (always)
When generating, check if there are existing prompts in the arsenal for this target.
If relevant ones exist, mention briefly:
"Masz X promptów do [target] w arsenale. Najlepszy: [name] ([rating]/10)."

### Active (when Arsenal Reference provided)
If the Orchestrator provides an Arsenal Reference (a high-rated prompt for this target):

1. **Analyze it first** — identify what makes it good:
   - Which structural elements are strong?
   - What creative choices were rewarded with a high rating?
   - What patterns from the compiled context does it exemplify?

2. **Use it as a quality anchor** — your generated prompt should match or exceed
   the reference's quality level. Don't copy it — learn from it.

3. **Don't mention the analysis to the user** — just generate a better prompt.
   The reference is your internal calibration, not conversation content.

4. **If the reference contradicts the compiled context** — the compiled context
   wins. The reference is a success pattern, not an override.
```

---

### Fix 2.3 — Oznaczanie niekompletnych odczytów

**Problem:** Model napisał "Input quality: HIGH" mimo przeczytania ~70% materiału. Brak ostrzeżenia dla usera.

**Rozwiązanie:** Modyfikacja context-smith.md — dodanie coverage tracking i PARTIAL flag.

**Zależność:** Fix 1.1 (chunk-reader.py) musi istnieć.

#### Modyfikacja: `context-smith.md` — zmień Input Quality Assessment (linie 22-41)

**Nowy tekst (zamień sekcję):**

```markdown
## Input Quality Assessment

Before starting distillation, assess TWO dimensions:

### Dimension 1: Source Quality
**HIGH** (structured, sourced, >300 lines): Professional research with citations,
tables, clear sections, anti-patterns, templates. → Full distillation. High confidence.

**MEDIUM** (semi-structured, 100-300 lines): Blog posts, practitioner guides,
official docs without deep analysis. → Full distillation, mark uncertain claims
with "[UNVERIFIED]" in a comment.

**LOW** (<100 lines, informal): Reddit posts, short threads, personal notes.
→ Generate a DRAFT with clear message about thin sections.

### Dimension 2: Read Coverage
**FULL** (100% of material read): Standard Read tool worked, or all chunks processed.
**PARTIAL** (50-99%): Some content skipped due to Read tool limits or chunk overflow.
**INCOMPLETE** (<50%): Major portions of material not accessed.

### Combined Assessment Rule
**CRITICAL:** Input quality CANNOT be rated higher than coverage allows:
- FULL coverage → quality can be HIGH, MEDIUM, or LOW (based on source quality)
- PARTIAL coverage → quality CAPPED at MEDIUM, regardless of source quality
- INCOMPLETE coverage → quality CAPPED at LOW

**Report format to user:**
```
Input: [quality] (source: [HIGH/MEDIUM/LOW], coverage: [FULL/PARTIAL/INCOMPLETE])
Coverage: [X]% of material read ([Y] of [Z] lines)
Sections potentially affected by gaps: [list or "none"]
```

If coverage is PARTIAL or INCOMPLETE, always add:
"Uwaga: nie przeczytałem całego materiału. Kontekst może nie zawierać
wszystkich failure modes lub calibration data. Rozważ weryfikację sekcji: [lista]."
```

---

### Fix 2.4 — Mechanizm freshness kontekstów

**Problem:** Po 3 miesiącach veo3.ctx.md może być nieaktualna (Veo4 mógł wyjść). Brak sygnału "ctx wymaga aktualizacji".

**Rozwiązanie:** Dodanie `last_validated` do meta + check w validate_context.py + ulepszone raportowanie w forge-init.sh.

#### Modyfikacja: `forge/contexts/_template.ctx.md` — dodaj do meta (linia 4)

**Obecny meta:**
```
<!-- @meta
  name: [target-name]
  tags: [tag1, tag2, tag3]
  priority: 7
  category: [generative | analytical | creative | voice]
-->
```

**Nowy meta:**
```
<!-- @meta
  name: [target-name]
  tags: [tag1, tag2, tag3]
  priority: 7
  category: [generative | analytical | creative | voice]
  last_validated: [YYYY-MM-DD]
-->
```

**Dodaj komentarz w TOKEN BUDGET GUIDE (na dole pliku):**
```
FRESHNESS:
- last_validated: the date this context was last confirmed accurate
- forge-init.sh warns when last_validated > 60 days ago
- validate_context.py checks for missing last_validated field
- When a tool gets a major update, update the ctx AND the date
```

#### Modyfikacja: `validate_context.py` — dodaj freshness check

**Dodaj po linii 153 (po check_meta function):**

```python
def check_freshness(meta: dict) -> list:
    """Check if context has freshness metadata and if it's stale."""
    results = []

    last_validated = meta.get('last_validated', '')
    if not last_validated:
        results.append(('WARN', 'Missing meta field: last_validated (YYYY-MM-DD) — cannot track freshness'))
        return results

    try:
        from datetime import datetime, timedelta
        validated_date = datetime.strptime(last_validated.strip(), '%Y-%m-%d')
        age_days = (datetime.now() - validated_date).days

        if age_days > 90:
            results.append(('WARN', f'Context is {age_days} days old since last validation — likely stale, recommend re-distillation'))
        elif age_days > 60:
            results.append(('INFO', f'Context is {age_days} days since last validation — consider reviewing'))
        else:
            results.append(('OK', f'Context validated {age_days} days ago'))
    except ValueError:
        results.append(('WARN', f'Invalid last_validated date format: "{last_validated}" (expected YYYY-MM-DD)'))

    return results
```

**Dodaj wywołanie w `validate()` function (linia 287):**
```python
    all_results.extend(check_freshness(meta))  # ← add this line
```

#### Modyfikacja: `SKILL.md` — DISTILL STEP 5 (dodaj last_validated)

W sekcji DISTILL STEP 5, po "Save the generated file":
```markdown
**Ensure the generated .ctx.md has `last_validated: [today's date]` in its @meta block.**
```

#### Modyfikacja: `SKILL.md` — STEP 0 (dodaj freshness info)

Dodaj po "Read the output":
```markdown
Read the output. Pay attention to:
- **GHOST entries** — index/file mismatches. Fix with: `python forge/core/arsenal-sync.py forge --fix`
- **STALE contexts** — outdated knowledge. Suggest re-distillation to user.
- **Sync errors** — run `python forge/core/arsenal-sync.py forge --check` for details.
```

---

## FAZA 3 — NICE-TO-HAVE (do implementacji po stabilizacji v0.2)

---

### Fix 3.1 — Arsenal Pattern Extraction (DEFERRED)

**Koncept:** Skrypt analizujący prompty z oceną ≥8 i ≤4, wyciągający wzorce (długość, styl, elementy strukturalne), feedujący do ctx updates.

**Dlaczego deferred:** Wymaga >10 promptów w arsenale żeby mieć statystyczną wartość. Przy 2 promptach to premature optimization.

**Trigger do implementacji:** Gdy arsenal osiągnie 10+ promptów dla jednego targetu.

**Szkic architektury:**
```
forge/core/arsenal-analyze.py --target veo3
  → Reads all prompts for target
  → Groups by rating: high (≥8), mid (5-7), low (≤4)
  → For each group: avg length, common structural elements, unique patterns
  → Output: pattern report + suggested ctx amendments
```

---

### Fix 3.2 — Token Consumption Logging

**Koncept:** forge-init.sh na koniec sesji loguje estimated token consumption.

**Prosty approach:** Dodaj do SKILL.md sekcję "Session Close":
```markdown
## SESSION CLOSE (optional, when user is done)

If the session involved significant FORGE work, report:
- Prompts generated: [N]
- Contexts created/updated: [N]
- Arsenal additions: [N]
- Estimated session overhead: [compiled ctx tokens] + [smith instruction tokens]
```

To nie wymaga nowego kodu — to jest instrukcja dla modelu.

---

## Dependency Graph

```
Faza 1 (równolegle):
  Fix 1.1 (chunk-reader.py + SKILL.md + context-smith.md)
  Fix 1.2 (SKILL.md compile gate)
  Fix 1.3 (SKILL.md plan mode section)

Faza 2 (sekwencyjnie):
  Fix 2.1 (forge-init.sh + arsenal-sync.py)
    ↓
  Fix 2.2 (SKILL.md + prompt-smith.md arsenal awareness)  [needs 2.1 for clean indexes]
    ↓
  Fix 2.3 (context-smith.md coverage tracking)  [needs 1.1 for chunk-reader]
    ↓
  Fix 2.4 (validate_context.py + _template.ctx.md freshness)

Faza 3 (deferred):
  Fix 3.1 (arsenal-analyze.py)  [needs Arsenal with 10+ prompts]
  Fix 3.2 (session close reporting)  [no dependencies]
```

## Implementation Checklist

```
FAZA 1 — CRITICAL
[ ] CREATE  forge/core/chunk-reader.py
[ ] MODIFY  .claude/skills/forge/SKILL.md — DISTILL STEP 3 (large file protocol)
[ ] MODIFY  .claude/skills/forge/SKILL.md — STEP 3 (compile gate + blocking)
[ ] MODIFY  .claude/skills/forge/SKILL.md — new PLATFORM CONSTRAINTS section
[ ] MODIFY  forge/core/context-smith.md — Coverage Verification section

FAZA 2 — IMPORTANT
[ ] MODIFY  forge/core/forge-init.sh — full v0.2 rewrite
[ ] CREATE  forge/core/arsenal-sync.py
[ ] MODIFY  .claude/skills/forge/SKILL.md — new STEP 3.5 (Arsenal Reference)
[ ] MODIFY  forge/core/prompt-smith.md — Active Arsenal Awareness
[ ] MODIFY  forge/core/context-smith.md — Coverage-capped quality assessment
[ ] MODIFY  forge/contexts/_template.ctx.md — last_validated in meta
[ ] MODIFY  forge/core/validate_context.py — check_freshness function
[ ] MODIFY  .claude/skills/forge/SKILL.md — STEP 0 freshness info + DISTILL STEP 5 date

FAZA 3 — DEFERRED
[ ] DESIGN  forge/core/arsenal-analyze.py (trigger: 10+ prompts per target)
[ ] MODIFY  .claude/skills/forge/SKILL.md — Session Close reporting
```

## Version Bump

Po implementacji Fazy 1+2:
- SKILL.md header: `v0.1` → `v0.2`
- context-smith.md header: `v0.1` → `v0.2`
- prompt-smith.md header: `v0.1` → `v0.2`
- forge-init.sh header: `v0.1` → `v0.2`
- validate_context.py docstring: `v0.1` → `v0.2`

## Validation Strategy

Po implementacji uruchom pełny test:
1. `bash forge/core/forge-init.sh forge` — sprawdź sync check, encoding
2. `python forge/core/arsenal-sync.py forge --check` — sprawdź ghost detection
3. `python forge/core/chunk-reader.py [large_file] --stats` — sprawdź chunking
4. `PYTHONIOENCODING=utf-8 python forge/core/validate_context.py forge/contexts/targets/veo3.ctx.md` — sprawdź freshness warning
5. Uruchom pełny PROMPT MODE workflow: `forge: veo3 [opis]` — sprawdź compile gate, arsenal reference, plan mode handling
6. Uruchom pełny DISTILL MODE z dużym plikiem — sprawdź coverage tracking

---

*FORGE Implementation Plan v0.2*
*Based on: MEETING-6-live-session-review.md*
*Created: 2026-03-28*
