#!/bin/bash
# FORGE Session Init — Warm Start Script v0.1
# Generates a quick snapshot of FORGE state for session context.
# Called by Orchestrator at session start.
#
# Usage: bash forge/core/forge-init.sh [forge-root-dir]

FORGE_DIR="${1:-forge}"

echo "=== FORGE Session Snapshot ==="

# Context files count
CTX_COUNT=$(find "$FORGE_DIR/contexts" -name '*.ctx.md' 2>/dev/null | grep -v _template | wc -l)
echo "Contexts: ${CTX_COUNT} files"

# List available targets
TARGETS=$(find "$FORGE_DIR/contexts/targets" -name '*.ctx.md' 2>/dev/null | xargs -I{} basename {} .ctx.md | tr '\n' ', ' | sed 's/,$//')
if [ -n "$TARGETS" ]; then
    echo "Targets: ${TARGETS}"
fi

# Arsenal count
ARSENAL_COUNT=$(find "$FORGE_DIR/arsenal/prompts" -name '*.md' 2>/dev/null | wc -l)
echo "Arsenal: ${ARSENAL_COUNT} prompts"

# Top-rated arsenal items (if any exist)
if [ "$ARSENAL_COUNT" -gt 0 ]; then
    echo ""
    echo "=== Recent Arsenal ==="
    ls -t "$FORGE_DIR/arsenal/prompts/" 2>/dev/null | head -5

    # Show top-rated if we can parse quality from files
    echo ""
    echo "=== Top Rated ==="
    for f in "$FORGE_DIR/arsenal/prompts/"*.md; do
        [ -f "$f" ] || continue
        quality=$(grep -m1 'quality:' "$f" 2>/dev/null | grep -oP '\d+' | head -1)
        name=$(basename "$f" .md)
        if [ -n "$quality" ]; then
            echo "  ${name}: ${quality}/10"
        fi
    done | sort -t: -k2 -rn | head -5
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
