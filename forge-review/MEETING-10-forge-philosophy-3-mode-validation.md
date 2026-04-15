# Meeting Output: Forge Philosophy Validation and 3-Mode Architecture

**Date**: 2026-04-15
**Format**: Structured Workshop
**Team Charter**: FORGE Architecture Development Team v1.0
**Meeting ID**: M-010

---

## Meeting Goal

**As stated**: Forge should become a system that gets better and better at designing LLM patterns across models, skills, tools, MCPs, agents, workflows, prompts, metaprompts, and contexts. It should be fed by scraped internet guides, idea files, and patterns (autoresearch, wiki, etc.). It should have 3 modes only: Compose, Distill, Deploy. It must be Claude-native via CLAUDE.md, token-efficient, user friendly, and able to discover/study best prompting while remaining practical.

**As understood**: Validate Forge concept end-to-end and redesign architecture around a simple but powerful philosophy: 3 operating modes, compounding knowledge, optional advanced tooling, and software-engineering rigor without architectural bloat.

**Target outcome**: Decision-ready concept framework and implementation architecture for Forge v2.

---

## Context Summary

### What Is Known

- [FACT] Forge already has strong foundations: deterministic scripts, mode workflows, fallback behavior, and model-target contexts. Evidence: forge/README.md, FORGE-ARCHITECTURE.md.
- [FACT] Current system already supports prompt generation, context distillation, and idea-file deployment patterns. Evidence: forge/README.md.
- [FACT] Previous meetings identified concept-fragmentation risk and proposed mode simplification direction. Evidence: forge-review/MEETING-9-forge-concept-validation-karpathy-thinking.md.
- [FACT] Karpathy-style ingestion mechanics are useful for compounding knowledge assets, but direct architecture copy is not desired. Evidence: user directive + forge/seeds/llm-wiki.md.
- [INFERENCE] Forge can become a meta-designer platform if research-heavy operations are separated from token-light runtime usage.

### What Is Uncertain

- Unknown whether Study should remain a separate visible mode or become a sub-workflow of Distill.
- Unknown best artifact model for storing reusable metaprompts across projects and models.
- Unknown how much automation in model/tool selection users will trust before wanting manual override.
- Unknown practical thresholds for runtime token budgets as knowledge corpus scales.

### Constraints Applied

- Canonical modes must be exactly 3: Compose, Distill, Deploy.
- Claude-native operation with CLAUDE.md compatibility is mandatory.
- Runtime usage must remain token-efficient as corpus grows.
- UX must stay simple for normal users and controllable for power users.
- Concept should be inspired by Karpathy thinking principles, not transformed into wiki-clone architecture.

---

## Expert Participation

| Expert | Role | Participation Level | Primary Contribution Area |
|--------|------|-------------------|--------------------------|
| Nadia Petrov | Claude Runtime and Integration Architect | Primary | Mode architecture and Claude-native control plane |
| Rafael Kim | Anthropic Prompt and Context Intelligence Engineer | Primary | Prompt-study mechanics and metaprompt evolution |
| Emilia Torres | Agentic Workflow and Automation Engineer | Primary | Scriptability, ingestion mechanics, deployment feasibility |
| Dr. Ibrahim Halevi | Reliability, Risk, and Evaluation Lead | Primary | Quality governance, uncertainty controls, token-risk constraints |
| Mei Lin Carter | Agentic IDE Product and Adoption Strategist | Primary | User clarity, operational simplicity, adoption design |

---

## Discussion Summary

### Work Item 1: What is good in current Forge and must be preserved

- Deterministic safety primitives are strong and should remain core infrastructure.
- Distill capability is strategically correct: knowledge transformation is Forge's core edge.
- Deploy from idea files is a unique and expandable differentiator.
- Fallback behavior is excellent product quality and should not be weakened.

### Work Item 2: Concept reset to match requested philosophy

Team validated this concept statement:

Forge is a Claude-native Meta-Designer for AI Systems that:
- composes high-quality prompts and system instructions,
- distills external intelligence into compact operational patterns,
- deploys idea-file-based environments for specific outcomes,
- and continuously improves through validated metaprompt assets.

Karpathy influence is principle-level only:
- compounding assets,
- simple primitives,
- optional smart tooling,
- human-guided control.

### Work Item 3: 3-mode architecture definition

#### Mode 1: Compose

Purpose:
- produce best-fit prompt/system artifact for a concrete user goal.

Default flow:
1. classify request intent and required outcome.
2. select model and pattern sources from distilled knowledge cards.
3. generate test prompt.
4. if accepted, generate production-grade metaprompt variant.
5. optionally save reusable metaprompt/playbook.

Output classes (v1 scope):
- prompt (primary)

Ambition path (future, same mode):
- system prompt, skill skeleton, tool spec, workflow script.

#### Mode 2: Distill

Purpose:
- ingest raw scraped guides, idea files, skills/tools docs, and benchmark examples into browseable, LLM-useful knowledge assets.

Critical adaptation from Karpathy-style ingestion:
- not a general wiki for everything,
- a prompt-pattern intelligence base optimized for model usage.

Distill artifacts:
- model prompting cards
- capability matrices
- failure/repair patterns
- reusable metaprompt blueprints
- benchmark snippets with confidence labels

Study capability decision:
- Study is implemented as a Distill sub-workflow (not a fourth public mode).
- Distill includes analysis pipelines for best-prompt discovery.

#### Mode 3: Deploy

Purpose:
- instantiate working environments from idea-file concepts, mixing seed pattern + Forge context + CLAUDE.md-native controls.

Examples:
- autoresearch workspace
- llm wiki workspace
- custom research/production system from idea file

Deployment rules:
- always plan first, ask approval, then write.
- include reproducible setup docs and first-run guidance.

### Work Item 4: Token-efficiency architecture

Team designed a two-tier cost model:

- expensive phase (Distill): ingest and compress knowledge once.
- cheap phase (Compose/Deploy runtime): load compact cards and targeted patterns only.

Runtime token controls:
- per-request budget caps by mode.
- top-k card retrieval instead of broad context loads.
- compact runtime cards for model-specific operations.
- strict separation between raw corpus and runtime pack.

### Work Item 5: User-friendliness and control design

- User-facing simplicity: three plain commands and predictable outcomes.
- Progressive disclosure: advanced diagnostics only when requested.
- Explicit acceptance checkpoints for saving metaprompts and deploying environments.
- Keep smart automation, but always provide manual override for model/tool choice.

### Work Item 6: Use-case validation against requested examples

- Geometry graphics style consistency:
  - Compose can perform model selection + style lock metaprompt generation + consistency package.
- Claude Cowork teaching environment prompt:
  - Compose uses model card + capability card + optional skill recommendations and constraints.
- Gemini deep research prompting:
  - Compose uses deep research card and can produce reusable research metaprompts.
- Cross-project metaprompt reuse:
  - Distill stores reusable blueprints with adaptation notes and confidence level.

### Expert Perspectives

#### Nadia Petrov — Claude Runtime and Integration Architect

- [FACT] Three public modes reduce conceptual overhead and align control plane boundaries.
- [INFERENCE] Study as Distill sub-workflow keeps architecture simple while preserving ambition.
- [RECOMMENDATION] Formalize mode contracts and CLAUDE.md integration boundaries before adding new features.

#### Rafael Kim — Anthropic Prompt and Context Intelligence Engineer

- [FACT] Best prompting quality emerges from iterative analysis and pattern extraction.
- [INFERENCE] Metaprompt assets should be first-class outputs, not byproducts.
- [RECOMMENDATION] Add metaprompt blueprint registry in Distill and automatic suggestion in Compose after successful prompt outcomes.

#### Emilia Torres — Agentic Workflow and Automation Engineer

- [FACT] Existing scripts can support this redesign with incremental changes rather than rewrite.
- [INFERENCE] Distill pipeline should generate compact runtime cards automatically to protect token efficiency.
- [RECOMMENDATION] Implement card-generation and indexing scripts as highest-priority technical path.

#### Dr. Ibrahim Halevi — Reliability, Risk, and Evaluation Lead

- [FACT] Compounding systems degrade without confidence and freshness governance.
- [INFERENCE] Token efficiency and quality must be measured together, not separately.
- [RECOMMENDATION] Introduce mode-level scorecards and hard guardrails for runtime token budget and confidence thresholds.

#### Mei Lin Carter — Agentic IDE Product and Adoption Strategist

- [FACT] User trust increases when system behavior is simple and predictable.
- [INFERENCE] Compose must feel immediate while Distill and Deploy remain powerful but non-intrusive.
- [RECOMMENDATION] Keep default UX minimal: Compose first, Distill and Deploy opt-in with clear prompts and confirmations.

---

## Disagreements

### Disagreement: Should Study be a visible fourth mode?

- **Parties**: Rafael Kim vs Nadia Petrov, Mei Lin Carter
- **Type**: Values
- **Position A**: Study deserves explicit visibility to emphasize strategic value.
- **Position B**: Visible fourth mode increases conceptual complexity and breaks requested 3-mode philosophy.
- **What would change minds**: User research showing whether hidden Study in Distill reduces discoverability too much.
- **Resolution**: Resolved. Study becomes a named Distill workflow, not separate mode.

### Disagreement: Automation-first model selection vs user-first selection

- **Parties**: Nadia Petrov vs Mei Lin Carter
- **Type**: Predictive
- **Position A**: Automation-first improves performance and consistency.
- **Position B**: User-first transparency improves trust and control.
- **What would change minds**: Pilot results on acceptance rate and override frequency.
- **Resolution**: Partially resolved. Automation suggests default model; user can override with one step.

### Disagreement: How strict should runtime token caps be?

- **Parties**: Dr. Ibrahim Halevi vs Rafael Kim
- **Type**: Factual
- **Position A**: Strict caps protect scalability and cost predictability.
- **Position B**: Too strict caps may underfeed high-complexity compose tasks.
- **What would change minds**: Benchmark of quality vs token budget by task class.
- **Resolution**: Unresolved. Open as optimization question with benchmark action.

---

## Convergence

### Synthesis

The team validated Forge’s core potential and converged on a cleaner concept: Forge should be a 3-mode Claude-native meta-designer system where Compose delivers immediate value, Distill performs heavy knowledge learning (including Study workflows), and Deploy instantiates idea-driven environments. Karpathy’s influence is retained as engineering philosophy: compounding assets, simple primitives, optional tooling, and elegant flow. The architecture remains sophisticated under the hood but intentionally simple on the surface.

### Decision Records

| Field | Content |
|-------|---------|
| **ID** | D-023 |
| **Decision** | Adopt canonical Forge philosophy: 3 modes only (Compose, Distill, Deploy). |
| **Rationale** | Aligns product clarity with user directive and lowers conceptual overhead. |
| **Dissent** | None. |
| **Confidence** | High - unanimous alignment. |
| **Revisit if** | User outcomes show critical discoverability loss for analysis workflows. |

| Field | Content |
|-------|---------|
| **ID** | D-024 |
| **Decision** | Implement Study as a Distill sub-workflow, not a standalone public mode. |
| **Rationale** | Preserves advanced prompt-discovery capability while keeping 3-mode simplicity. |
| **Dissent** | Rafael preferred standalone visibility. |
| **Confidence** | Medium-High. |
| **Revisit if** | Distill adoption shows poor study workflow discoverability. |

| Field | Content |
|-------|---------|
| **ID** | D-025 |
| **Decision** | Distill outputs must include compact runtime cards for token-efficient Compose usage. |
| **Rationale** | Ensures ingest cost is paid once while runtime remains efficient at scale. |
| **Dissent** | None. |
| **Confidence** | High. |
| **Revisit if** | Runtime quality degrades due to over-compression. |

| Field | Content |
|-------|---------|
| **ID** | D-026 |
| **Decision** | Compose should auto-suggest metaprompt/playbook creation after successful outcomes. |
| **Rationale** | Converts one-off successes into reusable, compounding assets. |
| **Dissent** | None. |
| **Confidence** | High. |
| **Revisit if** | Suggestion prompts create measurable UX friction. |

| Field | Content |
|-------|---------|
| **ID** | D-027 |
| **Decision** | Deploy remains idea-file driven and CLAUDE.md-native, with mandatory plan-then-approval execution. |
| **Rationale** | Keeps deployment powerful, reproducible, and safe. |
| **Dissent** | None. |
| **Confidence** | High. |
| **Revisit if** | Deployment friction blocks practical usage. |

| Field | Content |
|-------|---------|
| **ID** | D-028 |
| **Decision** | Introduce mode-level scorecards for quality, token cost, speed, and user friction. |
| **Rationale** | Enables evidence-based concept evolution and prevents complexity drift. |
| **Dissent** | None. |
| **Confidence** | High. |
| **Revisit if** | Metrics fail to correlate with user-perceived value. |

### Trade-Off Map

- **Choosing strict 3-mode simplicity**: Gains user clarity and operational ease. Costs reduced explicit visibility for specialized study workflows. Favored by Mei Lin and Nadia.
- **Choosing separate Study mode**: Gains conceptual visibility for prompt research. Costs mode bloat and higher onboarding friction. Favored by Rafael.
- **Choosing aggressive card compression**: Gains token efficiency and scalability. Costs potential quality loss in edge cases. Favored by Ibrahim and Emilia.
- **Choosing richer runtime context loads**: Gains potential quality headroom for complex tasks. Costs higher token burn and slower response. Favored by Rafael for advanced cases.

---

## Uncertainty Register

| ID | Unknown | Impact if Wrong | Resolvable? | Proposed Action | Owner (if applicable) |
|----|---------|----------------|-------------|-----------------|----------------------|
| U-022 | Will Distill-embedded Study workflow be discoverable enough without separate mode branding? | High | Yes | Run discoverability tests on Distill UX variants | Mei Lin Carter |
| U-023 | What compression threshold keeps runtime cards both cheap and high quality? | High | Yes | Benchmark quality vs token budget per model family | Rafael Kim |
| U-024 | How often will users accept metaprompt suggestions in Compose? | Medium | Yes | Track suggestion acceptance rate and friction signals | Dr. Ibrahim Halevi |
| U-025 | Does optional Obsidian sidecar improve outcomes enough to justify support cost? | Medium | Partially | Pilot with and without sidecar integration | Emilia Torres |
| U-026 | Which tasks require override of auto-selected model/tool decisions most often? | Medium-High | Yes | Log override frequency by use case category | Nadia Petrov |

---

## Open Questions

1. Should runtime cards be one per model or one per model x task archetype? — Matters because retrieval precision and maintenance cost trade off. Best answered by benchmark. Current assumption: start with model-level card plus optional task overlays.
2. Should metaprompt assets be project-scoped first or global by default? — Matters because reuse and contamination risk trade off. Best answered by pilot. Current assumption: project-scoped first, promote globally on validation.
3. How should Distill ingest scraped internet sources safely and reproducibly? — Matters because source quality/noise can degrade intelligence. Best answered by ingestion quality rubric. Current assumption: curated source whitelist plus confidence labels.
4. Should Deploy support partial setup profiles (lite/full) per idea file? — Matters because UX and setup time vary by user maturity. Best answered by user trials. Current assumption: yes, lite default.
5. What is the one-line Forge product promise for onboarding? — Matters because adoption depends on immediate understanding. Best answered by message testing. Current assumption: Forge designs, learns, and deploys AI prompt systems that improve over time.

---

## Next Work Package

| Priority | Action | Rationale | Depends On |
|----------|--------|-----------|------------|
| High | Draft Forge Philosophy v2 document anchored on 3 modes and compounding principles | Establishes concept source of truth | D-023, D-024 |
| High | Define Distill output schema for runtime cards, metaprompt blueprints, and confidence metadata | Enables token-efficient downstream Compose | D-025 |
| High | Add Compose post-success suggestion flow for metaprompt/playbook capture | Activates compounding loop in daily use | D-026 |
| Medium | Define Deploy contract: idea-file merge rules + CLAUDE.md generation + approval gates | Ensures safe, reproducible environment setup | D-027 |
| Medium | Implement mode-level scorecard instrumentation and dashboards | Enables evidence-led iteration | D-028 |
| Medium | Define optional Obsidian sidecar spec (plugin/script packs) as non-core extension | Supports smart tooling without core dependency | U-025 |
| Low | Run model selection override analytics pilot | Calibrates automation trust balance | U-026 |

---

## Artifacts to Update

| Artifact | Action | Specific Change | Triggered By |
|----------|--------|----------------|-------------|
| FORGE-ARCHITECTURE.md | Update | Replace loop taxonomy with canonical 3-mode philosophy and Distill-embedded Study workflow | D-023, D-024 |
| forge/README.md | Update | Reframe product narrative and use-case messaging around Compose/Distill/Deploy | D-023 |
| .claude/skills/forge/SKILL.md | Update | Align mode detection and flow logic to 3-mode contract and metaprompt suggestions | D-024, D-026 |
| forge/contexts/_template.ctx.md | Update | Include runtime-card generation fields and confidence metadata guidance | D-025 |
| forge-review/SYNTHESIS-all-decisions.md | Update | Record D-023 to D-028 and related uncertainty set | Convergence outcomes |
| New Distill schema spec | Create | Define artifacts: cards, blueprints, matrices, confidence tags | D-025 |
| New scorecard spec | Create | Define metrics for quality, token cost, speed, and friction | D-028 |

---

## Meeting Metadata

- **Format used**: Structured Workshop
- **Experts activated**: 5 of 5
- **Decisions made**: 6
- **Uncertainties logged**: 5
- **Open questions**: 5
- **Estimated confidence in primary recommendation**: High

---

# Artifact Updates from Meeting M-010

**Meeting**: Forge Philosophy Validation and 3-Mode Architecture
**Date**: 2026-04-15
**Generated by**: Expert Meeting Facilitator

---

## Decision Log Updates

| Decision ID | Decision | Confidence | Action | Notes |
|------------|----------|------------|--------|-------|
| D-023 | Canonical Forge philosophy uses 3 modes only: Compose, Distill, Deploy | High | Add to decision log | Foundational concept decision |
| D-024 | Study capability is implemented inside Distill, not as public fourth mode | Med-High | Add to decision log | Preserves simplicity while keeping ambition |
| D-025 | Distill must produce compact runtime cards for token-efficient Compose | High | Add to decision log | Cost-control core mechanism |
| D-026 | Compose must suggest metaprompt/playbook capture on successful outcomes | High | Add to decision log | Compounding asset loop |
| D-027 | Deploy remains idea-file and CLAUDE.md native with plan/approval gate | High | Add to decision log | Safety and reproducibility |
| D-028 | Mode-level scorecards are mandatory for evolution governance | High | Add to decision log | Prevent complexity drift |

---

## Risk & Uncertainty Updates

| ID | Type | Description | Severity | Action | Notes |
|----|------|------------|----------|--------|-------|
| U-022 | New risk | Distill-embedded Study may be under-discoverable | High | Add | UX discoverability test required |
| U-023 | New risk | Over-compressed runtime cards may reduce quality | High | Add | Quality/token benchmarks required |
| U-024 | New risk | Metaprompt suggestions may add interaction friction | Medium | Add | Acceptance-rate monitoring required |
| U-025 | New risk | Optional Obsidian support may create maintenance overhead | Medium | Add | Sidecar pilot before broad support |
| U-026 | New risk | Auto model/tool selection may be overridden frequently | Med-High | Add | Override analytics required |

---

## Requirements Updates

| Requirement | Change Type | Description | Triggered By |
|------------|------------|-------------|-------------|
| REQ-3mode-canonical | New | Forge must expose exactly 3 public modes: Compose, Distill, Deploy | D-023 |
| REQ-distill-study-embedded | New | Study workflows must be part of Distill pipeline | D-024 |
| REQ-runtime-cards | New | Distill outputs must include token-efficient runtime cards | D-025 |
| REQ-metaprompt-capture | New | Compose must support post-success metaprompt/playbook capture suggestions | D-026 |
| REQ-deploy-claude-native | New | Deploy must generate CLAUDE.md-native environments with plan approval | D-027 |
| REQ-mode-scorecards | New | All three modes must be tracked via shared scorecard framework | D-028 |

---

## Design & Architecture Updates

| Artifact | Section/Component | Change | Triggered By |
|----------|------------------|--------|-------------|
| FORGE-ARCHITECTURE.md | Vision and mode model | Replace prior taxonomy with 3-mode canonical architecture | D-023, D-024 |
| forge/README.md | Product framing and examples | Align with user-friendly 3-mode philosophy and use-case narrative | D-023 |
| .claude/skills/forge/SKILL.md | Mode routing logic | Update detection rules and flow steps for 3-mode operation | D-023, D-026 |
| forge/contexts/_template.ctx.md | Distill output contracts | Add fields needed for runtime-card extraction and confidence tagging | D-025 |

---

## Action Items

| Priority | Action | Owner/Assignee | Depends On | Deadline (if known) |
|----------|--------|---------------|------------|-------------------|
| High | Write Forge Philosophy v2 and mode contracts document | Nadia Petrov + Mei Lin Carter | D-023 | TBD |
| High | Define Distill artifact schema and card generator requirements | Rafael Kim + Emilia Torres | D-025 | TBD |
| High | Implement Compose metaprompt suggestion and capture flow spec | Rafael Kim | D-026 | TBD |
| Medium | Define Deploy CLAUDE.md merge and approval protocol | Nadia Petrov + Emilia Torres | D-027 | TBD |
| Medium | Define and instrument mode-level scorecards | Dr. Ibrahim Halevi | D-028 | TBD |
| Medium | Design optional Obsidian sidecar support boundary | Emilia Torres + Mei Lin Carter | U-025 | TBD |

---

## Assumption Log Updates

| Assumption ID | Assumption | Status Change | Evidence/Reasoning | Impact |
|--------------|-----------|--------------|-------------------|--------|
| A-016 | 3-mode public contract improves user comprehension versus broader mode sets | New | User explicitly requested fixed 3-mode design | High onboarding impact |
| A-017 | Distill can safely absorb Study workflows without losing power | New | Expert compromise and architecture discussion | Preserves simplicity and ambition |
| A-018 | Runtime-card strategy is key to token-efficient scale | New | Cross-expert agreement on cost dynamics | Core efficiency mechanism |

---

## Team Charter Updates

| Change | Reason | Priority |
|--------|--------|----------|
| No mandatory charter revision identified | Existing team coverage remained sufficient for philosophy and architecture validation | Low |

---

## Prior Meeting Output Updates

| Prior Meeting | Prior Decision/Finding | Change | Reason |
|--------------|----------------------|--------|--------|
| M-009 | D-019 (Compose, Study, Distill, Deploy as canonical loops) | Modified | Public mode set is now constrained to 3 modes; Study moved under Distill |
| M-009 | D-020 (Study mode pilot) | Modified | Study pilot remains, but as Distill sub-workflow pilot |
| M-008 | Runtime simplification direction | Upheld with conditions | Simplicity retained and now explicitly tied to 3-mode philosophy |

---

## Summary

- **Artifacts to create**: 2
- **Artifacts to update**: 7
- **Artifacts to review**: 2
- **High-priority actions**: 3
- **Charter revision needed**: No
