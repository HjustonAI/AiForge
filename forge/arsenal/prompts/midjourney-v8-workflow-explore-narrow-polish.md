---
name: v8-workflow-explore-narrow-polish
target: midjourney
quality: 5/10
date: 2026-04-03
tags: workflow, iteration, pipeline, ideation, v8
---

# Workflow A: Explore → Narrow → Polish

**Step 1 — Explore (low cost, high variance)**
Generate 4-5 baseline variations focused on subject + explicit lighting only. Standard V8 settings (no --hd, no --q 4). Add --chaos 20 to force divergent compositions.

**Step 2 — Narrow (style injection)**
Identify strongest composition. Extract aesthetic from a reference image via --sref. Start at --sw 100, scale up to --sw 300 if style isn't adhering. Dial --s to balance text prompt vs. reference influence.

**Step 3 — Polish (high-fidelity execution)**
Isolate the winning seed or re-run exact prompt. Append --hd for native 2K. Append --q 4 for micro-detail coherence. Keep --ar at 4:1 or below.

⚠️ Final step costs 16x normal GPU compute and forces Fast Mode. Warn user before executing.
