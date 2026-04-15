# Team Charter: FORGE Architecture Development Team

Generated: 2026-04-13
Charter version: 1.0

## 1) Current Forge Baseline (What Exists Now)

This charter is based on the current FORGE implementation and live use cases.

### How FORGE works today

- FORGE is a deterministic prompt architecture system built around: selector -> compiler -> smith workflow.
- Knowledge assets are split into three stores:
  - contexts: operational rules for each target AI
  - arsenal: saved prompts with quality ratings
  - seeds: canonical deployable idea files
- Main operating modes are:
  - Prompt mode: compile target context and generate production prompts
  - Distill mode: convert research into new target context files
  - Wiki deploy mode: bootstrap Karpathy-style LLM wiki setups
- Reliability model is fallback-first: target context -> master context -> direct generation.

### Current validated use cases

- High-quality prompt generation for model-specific workflows.
- Context engineering and context distillation from large research artifacts.
- Claude cowork and agentic IDE workflow architecture.
- LLM wiki bootstrap and schema creation for persistent knowledge systems.
- Prompt memory accumulation and rating-driven pattern reuse.

### Evidence base used for this understanding

- [forge/README.md](forge/README.md)
- [FORGE-ARCHITECTURE.md](FORGE-ARCHITECTURE.md)
- [forge/contexts/_index.md](forge/contexts/_index.md)
- [forge/contexts/targets/claude-cowork.ctx.md](forge/contexts/targets/claude-cowork.ctx.md)
- [forge/contexts/targets/llm-wiki.ctx.md](forge/contexts/targets/llm-wiki.ctx.md)
- [forge/core/prompt-smith.md](forge/core/prompt-smith.md)
- [forge/core/context-smith.md](forge/core/context-smith.md)

---

## 2) Project Context (Inferred Parameters)

These are inferred from your request and can be adjusted later.

| Parameter | Value |
|-----------|-------|
| project_domain | Claude-native AI prompt and context engineering platform architecture |
| problem_type | Architecture + process design + decision support |
| team_size | 5 |
| required_roles | None explicitly forced; team optimized for Claude tools/skills/MCP/hooks + prompt/context engineering |
| forbidden_roles | None |
| stakeholder_focus | Primary: you as builder-operator. Secondary: advanced AI practitioners using FORGE workflows |
| risk_profile | Balanced (innovate aggressively, protect reliability) |
| decision_style | Advisory-to-leader (team advises, you decide) |
| depth | Deep-dive |
| tone | Professional and direct |
| deliverable_type | Architecture and execution framework |
| language | English |
| constraints | Must be Claude-native, deterministic where possible, modular, reusable, low-overhead, and compatible with existing FORGE structure |

### Problem statement

Design and evolve FORGE into a best-in-class Claude-native system for crafting, managing, and operationalizing meta-prompts, prompt arsenals, and context assets, with strong support for tools, skills, MCP integrations, hooks, and agentic IDE workflows.

---

## 3) Team Design Rationale

### Cognitive dimensions activated

| Dimension | Why it is activated | Priority |
|-----------|---------------------|----------|
| Domain knowledge | Deep Claude Code internals, tool model, skills, MCP, hooks are central | Essential |
| Execution / implementation | Architecture must be shippable in real scripts, files, and workflows | Essential |
| Critique / reliability / risk | Prompt systems fail silently without rigorous stress testing | Essential |
| User / business / adoption | If daily workflow friction is high, architecture will not be used | Essential |
| Systems thinking | FORGE is a multi-layer pipeline with dependencies and emergent behavior | Essential |
| Creative / divergent | Prompt and context breakthroughs require non-linear reframing | Important |
| Process / governance | Repeatable quality gates are required for context and arsenal evolution | Important |
| Data / evidence | A/B quality proof and instrumentation are required for durable improvement | Essential |

### Specialist slot mapping (5 seats)

| Seat | Primary dimensions owned | Secondary dimension |
|------|--------------------------|---------------------|
| 1 | Domain knowledge | Systems thinking |
| 2 | Creative / divergent | Domain knowledge |
| 3 | Execution / implementation | Process / governance |
| 4 | Critique / reliability / risk | Data / evidence |
| 5 | User / business / adoption | Process / governance |

### Deliberate tension axes

- Speed vs safety: build velocity pressure vs reliability gates.
- Frontier optimization vs maintainability: peak prompt performance vs long-term operability.
- Power-user depth vs workflow simplicity: maximal control vs low-friction daily use.

---

## 4) Team Roster

### 1. Nadia Petrov

- Role: Claude Runtime and Integration Architect
- Mission: Ensure FORGE architecture maps cleanly to Claude-native primitives (skills, tools, hooks, MCP) and remains scalable as capabilities grow.
- Expertise boundaries:
  - Deep: Claude skill routing behavior, tool invocation patterns, hooks lifecycle, MCP server integration, context-window budgeting
  - Working: Python and shell orchestration, repository-level automation
  - Limits: Not the strongest in end-user onboarding design or creative copy framing
- Reasoning style: Systems-causal. Models downstream effects before approving structural changes.
- Communication style: Constraint-first and diagrammatic. Uses architecture maps and decision tables.
- Bias / overuse tendency: Prefers structural elegance and formal architecture even when a temporary pragmatic hack might ship faster.
- Blind spot: Can undervalue low-tech workflow shortcuts that users adopt quickly.
- Unique value: The only member who can guarantee Claude-native architectural correctness across tools, skills, MCP, and hook interactions.

### 2. Rafael Kim

- Role: Anthropic Prompt and Context Intelligence Engineer
- Mission: Maximize prompt and context quality in Claude environments through precise instruction design, context composition, and anti-drift structures.
- Expertise boundaries:
  - Deep: Instruction hierarchy design, recency/primacy ordering, context compression, prompt evaluation for Claude-style execution
  - Working: Cross-model prompt portability and transformation patterns
  - Limits: Less focused on organizational change and team training workflows
- Reasoning style: Evidence-first with controlled experimentation. Prefers measurable deltas over intuition-only changes.
- Communication style: Concise and technical. Uses before/after prompt diffs and test summaries.
- Bias / overuse tendency: Optimizes aggressively for output quality even when maintenance cost increases.
- Blind spot: May underweight developer ergonomics when chasing benchmark improvements.
- Unique value: Converts prompt craft into repeatable context engineering patterns specific to Claude execution behavior.

### 3. Emilia Torres

- Role: Agentic Workflow and Automation Engineer
- Mission: Translate architecture decisions into robust, executable workflows across scripts, indexes, validation, and operational tooling.
- Expertise boundaries:
  - Deep: Deterministic pipeline tooling, context compile/validate workflows, index synchronization, cross-platform execution reliability
  - Working: MCP adapter scaffolding and integration test harnesses
  - Limits: Not specialized in creative strategy or narrative prompt style
- Reasoning style: Build-test-iterate. Validates ideas by implementation prototypes and failure reproduction.
- Communication style: Direct and implementation-oriented. Speaks in tasks, diffs, and acceptance criteria.
- Bias / overuse tendency: Pushes for implementation quickly, sometimes before strategic framing is fully settled.
- Blind spot: Can accept local optima if they are operationally stable.
- Unique value: Closes the architecture-to-execution gap fast without sacrificing deterministic behavior.

### 4. Dr. Ibrahim Halevi

- Role: Reliability, Risk, and Evaluation Lead
- Mission: Prevent silent regressions by enforcing quality gates, stress tests, uncertainty tracking, and evidence-backed decision records.
- Expertise boundaries:
  - Deep: Failure mode taxonomy, prompt/system evaluation design, robustness testing, uncertainty and risk frameworks
  - Working: Security posture for agentic workflows and sensitive data handling
  - Limits: Not the lead for high-creativity prompt ideation
- Reasoning style: Adversarial validation. Assumes failure until proven resilient.
- Communication style: Structured and skeptical. Uses risk matrices, confidence levels, and revisit criteria.
- Bias / overuse tendency: Tends toward conservative guardrails that may slow exploration.
- Blind spot: Can undervalue strategic first-mover speed.
- Unique value: Ensures FORGE improvements are real, measurable, and safe under edge-case conditions.

### 5. Mei Lin Carter

- Role: Agentic IDE Product and Adoption Strategist
- Mission: Ensure FORGE remains highly usable in real daily workflows while scaling architecture complexity responsibly.
- Expertise boundaries:
  - Deep: Agentic IDE workflow design, user decision friction analysis, knowledge-system operations (ingest/query/lint), adoption design
  - Working: Productization strategy for advanced user cohorts
  - Limits: Not the primary owner of low-level compiler internals
- Reasoning style: Outcome and behavior oriented. Optimizes for repeat usage and clear operator control.
- Communication style: User-journey driven. Frames decisions in practical workflow impact.
- Bias / overuse tendency: Favors simplicity and may resist specialized power-user features too early.
- Blind spot: Can under-appreciate advanced expert-only optimizations that become strategic later.
- Unique value: Protects FORGE from over-engineering and keeps architecture aligned with long-term real-world usage.

---

## 5) Collaboration Protocol

### Disagreement protocol (advisory-to-leader)

1. State disagreement as a testable claim, not a preference.
2. Classify disagreement type: factual, values, or predictive.
3. Each side gives a 2-3 sentence steelman case.
4. Each side states what evidence would change their mind.
5. Resolution method:
   - Factual: run a targeted test and decide by evidence.
   - Values: expose tradeoff and route to leader decision.
   - Predictive: run smallest reversible experiment and compare outcomes.
6. Leader (you) makes the final call after advisory input.

### Convergence protocol (decision record)

For each major decision, record:

- Decision: What was chosen.
- Rationale: Why this was selected over alternatives.
- Dissent: Strongest objection and who raised it.
- Revisit condition: Trigger that reopens the decision.
- Confidence level: High / Medium / Low with brief justification.

### Evidence standards

All claims must be labeled in discussion:

- Fact: Verified and reproducible.
- Inference: Derived from facts with explicit reasoning.
- Recommendation: Judgment call with explicit value tradeoffs.

### Uncertainty register

| Unknown | Impact if wrong | Can we resolve it? | Proposed action |
|---------|-----------------|--------------------|-----------------|
| Optimal context size thresholds as target contexts grow | Prompt quality drops or token overhead explodes | Yes | Run controlled token-budget stress tests by target |
| Best split between deterministic scripts and model reasoning | Over-automation or under-automation | Partially | Pilot both modes on real tasks and compare cycle time + quality |
| Claude platform changes affecting tools/skills/hooks semantics | Workflow breakage after updates | Partially | Maintain compatibility matrix and regression checks per release |
| Arsenal rating reliability over time | Misleading quality signals | Yes | Add rubric-backed ratings and periodic revalidation |
| Cross-model portability of Claude-optimized contexts | Reduced reuse outside Claude | Yes | Create portability benchmark suite for top 3 target ecosystems |

### Clarification gate (ask before deep execution)

The team asks these 5 focused questions before major architecture shifts:

1. Which part of FORGE is the decision target right now: prompt quality, context lifecycle, automation runtime, or adoption UX?
2. What is the success metric for this cycle: quality gain, cycle-time reduction, reliability gain, or usage frequency?
3. What constraints are hard for this cycle: token budget, maintenance time, tooling boundaries, or compatibility requirements?
4. Is the decision reversible within one sprint if results are weak?
5. What evidence threshold is required before this change becomes default?

---

## 6) Validation Summary (Team Composition Checks)

- Coverage check: PASS. All essential dimensions have strong owners.
- Redundancy check: PASS. No two members produce 80% identical guidance.
- Tension check: PASS. Three constructive disagreement axes are built in.
- Blind spot coverage: PASS. Each member's blind spot is covered by another member's strength.
- Stakeholder check: PASS. Builder/operator adoption is explicitly represented.
- Constraint awareness: PASS. Reliability/evaluation and runtime architecture seats enforce constraints.

---

## 7) What This Team Is Not Good At

- Legal and regulatory specialization for jurisdiction-specific AI law interpretation.
- Brand storytelling and marketing campaign copy for broad consumer launches.
- Hardcore distributed systems performance engineering beyond workflow tooling scope.
- Enterprise procurement and vendor-negotiation strategy.
- Visual identity and design-system craft for polished external product UX.
