# Prompt Intelligence Layer Blueprint

Status: Draft for implementation planning
Date: 2026-04-13
Scope: Wave A foundation (from M-007 decisions D-007 to D-011)

## 1. What this layer is

The Prompt Intelligence Layer is the missing middle tier between:
- raw source material (research, transcripts, prompt experiments)
- production assets (contexts and arsenal prompts used at generation time)

Its job is to make Forge compounding, not one-shot.

In plain terms:
- today: generate prompt -> maybe save prompt
- target: generate prompt -> extract reusable intelligence -> validate -> feed back into contexts and arsenal decisions

## 2. Design goals and non-goals

### Goals
- Preserve deterministic pipeline spine (compiler, validators, indexes).
- Add persistent intelligence artifacts that improve future outputs.
- Keep user friction low (approval gates, no silent automation).
- Make uncertainty explicit (confidence, freshness, evidence source).
- Keep everything markdown and file-system first.

### Non-goals (Wave A)
- No mandatory vector database.
- No mandatory MCP retrieval dependency.
- No autonomous self-editing of production contexts without approval.
- No large schema rewrite of existing contexts and arsenal.

## 3. New architecture model

Current model:
- sources -> contexts + arsenal -> generation

Target model:
- sources -> intelligence -> contexts + arsenal -> generation
- generation -> intelligence (session trace, extracted patterns)

So contexts and arsenal become production views over intelligence, not isolated stores.

## 4. Directory schema (exact)

## Proposed tree

```text
forge/
  intelligence/
    README.md
    _index.md
    log.md
    _templates/
      artifact.template.md
      contradiction.template.md
      pattern-candidate.template.md
      session-trace.template.md
    shared/
      taxonomy.md
      confidence-scale.md
      lint-policy.md
      filing-policy.md
    targets/
      <target>/
        _index.md
        facts.md
        patterns.md
        contradictions.md
        failures.md
        proposals.md
        trails.md
        sessions/
          2026-04-13-<slug>.md
        candidates/
          pattern-<id>.md
          context-patch-<id>.md
```

## Why this shape

- _index.md and log.md mirror Karpathy mechanics (navigation + chronology).
- shared contains global governance and scoring policy.
- targets/<target>/ holds bounded intelligence to prevent cross-target noise.
- sessions gives an auditable trail without polluting core files.
- candidates enforces approval-gated evolution.

## 5. File contracts (what each file means)

## forge/intelligence/_index.md

Purpose: content-oriented catalog of all intelligence assets.

Must contain table columns:
- id
- target
- kind (fact, pattern, contradiction, failure, proposal, session)
- confidence (high, medium, low)
- freshness_date
- status (draft, candidate, approved, archived)
- path

Update rule:
- deterministic script updates this after any create/update/archive operation.

## forge/intelligence/log.md

Purpose: append-only timeline of intelligence events.

Entry format:
- ## [YYYY-MM-DD] event_type | target | short_title
- sources:
- files_created:
- files_updated:
- decision_ref:
- notes:

Event types:
- ingest
- extract
- lint
- contradiction
- approval
- reject
- promote
- archive

## forge/intelligence/targets/<target>/facts.md

Purpose: stable factual observations extracted from sources.

Rules:
- every fact must cite source refs.
- uncertain facts are marked with low confidence.
- no recommendations in this file.

## forge/intelligence/targets/<target>/patterns.md

Purpose: reusable prompt/context tactics that proved useful.

Each pattern block includes:
- id
- pattern statement
- when to use
- when not to use
- supporting evidence refs
- quality signal (from arsenal ratings or test outputs)
- confidence

## forge/intelligence/targets/<target>/contradictions.md

Purpose: resolved and unresolved conflicts between sources, contexts, and high-quality prompts.

Each contradiction block includes:
- id
- conflict statement
- conflicting artifacts
- severity
- current judgment
- confidence
- action (investigate, patch candidate, defer)

## forge/intelligence/targets/<target>/failures.md

Purpose: failure atlas for this target.

Each failure entry includes:
- trigger pattern
- observed failure
- likely cause
- repair pattern
- confidence
- last_seen date

## forge/intelligence/targets/<target>/proposals.md

Purpose: candidate changes suggested by intelligence but not yet applied to production contexts.

Each proposal includes:
- proposal id
- intended production target file
- change summary
- expected upside
- risk
- evidence refs
- approval status

## forge/intelligence/targets/<target>/trails.md

Purpose: human-readable evolution trail.

Trail entry includes:
- what changed
- why it changed
- what evidence triggered change
- who approved
- downstream impact

## forge/intelligence/targets/<target>/sessions/*.md

Purpose: per-session trace snapshot for audit and learning loops.

Contains:
- session intent
- target
- artifacts touched
- extracted insights count
- filed suggestions
- accepted/rejected changes
- session gain summary

## forge/intelligence/targets/<target>/candidates/*.md

Purpose: isolated candidate artifacts awaiting approval.

Status transitions:
- draft -> candidate -> approved -> promoted
- draft -> candidate -> rejected -> archived

## 6. Standard frontmatter for intelligence artifacts

Use this frontmatter for any new artifact file in intelligence:

```yaml
---
id: INT-<target>-<YYYYMMDD>-<seq>
target: <target>
kind: fact | pattern | contradiction | failure | proposal | session
status: draft | candidate | approved | archived
confidence: high | medium | low
freshness_date: YYYY-MM-DD
sources:
  - <path>
derived_from:
  - <path>
quality_signal:
  score: <0-10 or null>
  basis: arsenal-rating | test-run | manual-review
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

## 7. Operational lifecycle (how it works)

## A. Ingest intelligence lifecycle

1. Input arrives (research file, prompt output, user answer worth preserving).
2. Extract step creates or updates fact/pattern/failure entries.
3. Deterministic index updater refreshes local and global indexes.
4. Log event appended.
5. If extraction implies production change, create proposal in candidates.

## B. Query-to-artifact lifecycle (approval-gated)

1. User asks question.
2. Forge answers using contexts plus relevant intelligence pages.
3. System suggests filing if answer passes threshold.
4. On approval:
   - create artifact in candidates or target files
   - update index
   - append log
5. On rejection:
   - append log with reason
   - no persistent artifact created

## C. Contradiction lint lifecycle

1. Lint scans:
   - contexts/targets/<target>.ctx.md
   - high-rated arsenal prompts for same target
   - intelligence facts/patterns
2. Lint writes contradiction entries with severity and confidence.
3. If severity high and confidence medium/high, create proposal candidate.
4. Human approval required before production patch.

## D. Promotion to production lifecycle

1. Candidate proposal reviewed.
2. If approved:
   - apply patch to context/production file
   - mark candidate approved/promoted
   - add trail entry
   - append log
3. If rejected:
   - mark candidate archived/rejected with reason
   - append log

## 8. Deterministic vs model-led responsibilities

## Deterministic scripts must do
- file creation path rules
- id generation
- index sync
- log append structure
- status transition validation
- lint structural checks

## Model-led synthesis can do
- extract candidate patterns
- infer likely contradictions
- draft proposals
- summarize session gains

Hard rule:
- model can propose; deterministic flow and user approval decide persistence and promotion.

## 9. Approval gates and state machine

Allowed states:
- draft
- candidate
- approved
- archived

Transition matrix:
- draft -> candidate (automatic after extraction quality threshold)
- candidate -> approved (manual)
- candidate -> archived (manual reject)
- approved -> archived (manual rollback)

No direct transitions:
- draft -> approved
- archived -> approved

## 10. How this changes daily Forge usage

User-visible behavior changes should be minimal.

### Prompt mode
- before: generate prompt and optional save to arsenal
- after: same behavior plus optional insight filing suggestion and session gain summary

### Distill mode
- before: produce target context
- after: also stores evidence-backed intelligence artifacts used to justify context sections

### Lint mode
- before: structural checks and freshness
- after: also contradiction intelligence and targeted proposals

## 11. Concrete example (single target)

Scenario: target is midjourney.

1. User generates 5 prompts, rates 2 of them 9/10.
2. Pattern Distiller drafts 3 candidate patterns in:
   - intelligence/targets/midjourney/candidates/pattern-*.md
3. Contradiction Lint finds one conflict between ctx rule and top prompt behavior.
4. Proposal file is created in candidates.
5. User approves one proposal.
6. Context patch is applied.
7. trails.md and log.md record why and when it happened.
8. Next generation benefits from updated context.

This is compounding in practice.

## 12. Required scripts for Wave A

Add these scripts in forge/core:
- intelligence-index-sync.py
  - rebuilds global and target indexes from file metadata
- intelligence-log.py
  - appends standardized log entries
- intelligence-file.py
  - creates artifact files from templates and validates frontmatter
- intelligence-session-summary.py
  - creates session gain summary from current session trace

Optional in Wave A, required in Wave B:
- contradiction-lint.py
- pattern-distiller.py

## 13. Metrics (to prove value)

Track weekly:
- generation quality trend (average rating for target)
- acceptance rate of filed suggestions
- contradiction count by severity
- time-to-good-prompt (session turns until rated >= 8)
- user friction proxy (abandon rate after suggestion prompts)

Wave A success criteria:
- >= 10% improvement in time-to-good-prompt OR
- >= 0.5 increase in mean quality for active targets
- no more than 15% session-time regression

## 14. Risks and controls

Risk: artifact sprawl
- control: strict target-bounded directories, monthly archive pass

Risk: noisy auto-capture
- control: approval-gated filing and candidate state

Risk: contradiction false positives
- control: confidence labels and severity thresholds

Risk: added UX friction
- control: suggestion prompts only when value threshold met

## 15. Rollout plan

## Wave A (2 weeks)
- create intelligence directory and templates
- implement index/log/file/session scripts
- enable approval-gated query-to-artifact flow
- enable session gain summary

## Wave B (2 to 4 weeks)
- implement contradiction-lint
- implement pattern-distiller draft mode
- start confidence/freshness metadata enforcement

## Wave C (conditional)
- add retrieval bridge (MCP or local search) only if index miss-rate trigger is met
- explore adaptive selection using intelligence metrics

## 16. Day-1 bootstrap checklist

1. Create forge/intelligence tree from section 4.
2. Create shared policy files.
3. Add templates.
4. Add first target intelligence files for one active target (recommend midjourney or gemini-deep-research).
5. Integrate index/log update hooks into existing save and distill flows.
6. Run first session and verify session gain summary.
7. Review artifact count and friction after 1 week.

## 17. Quick FAQ

Q: Is this replacing contexts and arsenal?
A: No. It feeds them and makes them evolve with evidence.

Q: Do I need vector search now?
A: No. Not in Wave A. Index plus log first.

Q: Can this run entirely as markdown plus Python scripts?
A: Yes. That is the default design.

Q: What is the single biggest benefit?
A: Prompt quality improvements become persistent system knowledge instead of staying trapped in chat history.

## 18. Integration map (current Forge -> new layer)

| Current component | Keep or change | New behavior after integration |
|-------------------|----------------|-------------------------------|
| forge/core/compile_context.py | Keep | No behavior change. Consumes production contexts as today. |
| forge/core/validate_context.py | Keep + extend later | Optional check for intelligence-linked metadata in Wave B. |
| forge/core/prompt-smith.md | Keep + small update | Adds suggestion step: file high-value output into intelligence candidates. |
| forge/core/context-smith.md | Keep + small update | Writes extraction evidence into target intelligence facts and patterns. |
| forge/contexts/targets/*.ctx.md | Keep | Still source of truth for generation at runtime. |
| forge/arsenal/prompts/*.md | Keep | Still stores rated prompts; now also acts as signal source for pattern extraction. |
| forge/arsenal/_index.md | Keep | No schema break; optional derived refs to intelligence artifacts can be added later. |
| .claude/skills/forge/SKILL.md | Update | Adds approval-gated query-to-artifact flow and session gain summary output. |
| forge/.cache/compiled.ctx.md | Keep | Unchanged deterministic runtime artifact. |

## 19. End-to-end trace (realistic sequence)

This trace shows what happens in one normal day after Wave A is installed.

1. User asks for a complex midjourney prompt.
2. Forge compiles context and generates prompt exactly as now.
3. User rates result 9/10 and saves to arsenal.
4. Forge asks: "This output contains reusable pattern candidates. File to intelligence?"
5. If user says yes:
  - create candidate file under intelligence/targets/midjourney/candidates/
  - append event to intelligence/log.md
  - update intelligence/_index.md and intelligence/targets/midjourney/_index.md
6. End of session: Forge prints Session Gain Summary:
  - new intelligence artifacts created
  - candidates pending review
  - expected impact on next runs
7. Later, contradiction-lint (Wave B) detects conflict between a context rule and repeated high-rated prompts.
8. Forge drafts context patch candidate and asks for approval.
9. On approval, context is updated and trails.md records why.

## 20. Minimal API contract for helper scripts

You can keep script interfaces very small and stable.

### intelligence-file.py

Inputs:
- --target
- --kind
- --title
- --source (repeatable)
- --confidence
- --status

Outputs:
- created file path
- artifact id
- metadata summary

### intelligence-index-sync.py

Inputs:
- --root forge/intelligence
- --target optional

Outputs:
- updated global index path
- updated target index path(s)
- counts by kind/status/confidence

### intelligence-log.py

Inputs:
- --event
- --target
- --title
- --created (repeatable)
- --updated (repeatable)
- --note optional

Outputs:
- appended log entry id

### intelligence-session-summary.py

Inputs:
- --target
- --session-id

Outputs:
- summary markdown block to display in closeout

## 21. How to know it is working (operator checklist)

After first week, answer these checks:

1. Can you trace why a context change happened from trails.md without reading chat logs?
2. Can you find newly learned patterns from one index file quickly?
3. Are suggestion prompts helpful, not noisy (acceptance rate >= 30%)?
4. Did prompt quality improve for at least one active target?
5. Did workflow friction stay acceptable (no major slowdowns)?

If 1 to 4 are yes and 5 is yes, Wave A is successful and ready for Wave B.
