#!/bin/bash
# FORGE Session Init — Warm Start Script v0.2
# Generates a quick snapshot of FORGE state for session context.
# Called by Orchestrator at session start.
#
# Usage: bash forge/core/forge-init.sh [forge-root-dir]
#
# Changes in v0.2:
#   - Replaced grep -P with POSIX-compatible grep -E
#   - Added index/file sync validation (ghost entry detection)
#   - Added UTF-8 locale hint
#   - Improved Top Rated parsing for cross-platform compatibility

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

# Top-rated arsenal items (if any exist)
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
    while IFS= read -r line; do
        # Skip non-table lines
        echo "$line" | grep -qE '^\|.*\|.*\|' || continue
        # Skip header and separator
        echo "$line" | grep -qE '^\| *Name|^\| *-' && continue

        # Extract path field (last data column before final |)
        path=$(echo "$line" | awk -F'|' '{print $(NF-1)}' | xargs 2>/dev/null)
        name=$(echo "$line" | awk -F'|' '{print $2}' | xargs 2>/dev/null)

        [ -z "$path" ] && continue
        full_path="$FORGE_DIR/arsenal/$path"
        if [ ! -f "$full_path" ]; then
            echo "  GHOST: Arsenal index has '$name' but file missing: $path"
            SYNC_OK=false
        fi
    done < "$FORGE_DIR/arsenal/_index.md"
fi

# Check contexts: index entries vs actual files
if [ -f "$FORGE_DIR/contexts/_index.md" ]; then
    while IFS= read -r line; do
        echo "$line" | grep -qE '^\|.*\|.*\|' || continue
        echo "$line" | grep -qE '^\| *Name|^\| *-' && continue

        path=$(echo "$line" | awk -F'|' '{print $3}' | xargs 2>/dev/null)
        name=$(echo "$line" | awk -F'|' '{print $2}' | xargs 2>/dev/null)

        [ -z "$path" ] && continue
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
