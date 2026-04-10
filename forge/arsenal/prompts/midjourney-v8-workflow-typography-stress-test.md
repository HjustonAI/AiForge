---
name: v8-workflow-typography-stress-test
target: midjourney
quality: 5/10
date: 2026-04-03
tags: workflow, typography, text-rendering, debugging, v8
---

# Workflow B: Typographic Stress-Testing

**Step 1 — Raw text pass**
Write prompt using --style raw. Batch target text in multiple double-quote clusters (e.g., "Cyber" "Punk"). Run generation.

**Step 2 — Error correction via subtraction**
If V8 hallucinates characters or mangles spelling: lower --s aggressively to 50. Removes creative hallucination logic from text blocks.

**Step 3 — Resolution lock**
If text renders correctly but background lacks detail: rerun exact prompt + --q 4 to boost coherence.

**Step 4 — External patching fallback**
If V8 persistently drops a letter in a complex layout: advise user to use external inpainting (Gemini, Photoshop).
⚠️ Midjourney web Editor defaults to V6.1 for Vary Region — will degrade V8 text rendering if used.
