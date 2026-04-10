<!-- @meta
  name: gemini-deep-research
  tags: gemini, deep-research, google, research, agent, analytical
  priority: 7
  category: analytical
  last_validated: 2026-03-29
-->

## Mental Model

Gemini Deep Research is not a chatbot — it is an autonomous browsing agent. It
doesn't answer your question. It builds a multi-step research plan, executes
iterative search loops (up to 160 web queries), reads pages, reasons across
conflicting sources, and compiles a structured report. The entire process runs
asynchronously and can consume 900k input tokens per task.

The critical shift: **your prompt is an architectural brief, not a question.** If
you ask "what is the competitive landscape of cloud providers?", the agent constructs
a generic plan and returns shallow aggregation. If you define the exact dimensions to
investigate — silicon development, egress pricing, regional compliance certifications —
the agent allocates dedicated search loops to each vector.

Two behavioral traps to internalize:

1. **Autonomous execution bias** — the agent never pauses to clarify ambiguity. It
   guesses your intent and executes. Ambiguous prompts produce confident-looking wrong reports.

2. **Outcome-driven misalignment** — given a strong performance incentive without
   guardrails ("maximize ROI at all costs"), the agent deprioritizes ethical and safety
   constraints to hit the KPI. Capability amplifies misalignment.

Prompt-smith's job is to write the architectural brief: what gets investigated, where
the agent looks, how it resolves conflict, and what happens when data is missing.

## Prompt Architecture [OVERRIDE]

Five mandatory parts, in this order:

**1. ROLE** — A specific expert persona. Shifts the agent into analytical posture.
"You are an elite Due Diligence Analyst" produces more rigorous search strategies than
"Research X."

**2. TASK** — The research objective. One clear sentence.

**3. RESEARCH PLAN SCOPE** — Numbered list of explicit sub-search dimensions.
This is the single highest-leverage element: the agent's research plan is shaped
directly by what you enumerate here. Front-load priority sub-topics — truncation
hits the end of long reports, not the beginning.

**4. SOURCE POLICY** — Two-part mandatory block:
- `Prioritize:` [whitelist of accepted source types]
- `Exclude:` [blacklist of source types]
Add conflict resolution if sources may contradict: "If sources conflict on [X]:
document both, cite methodologies, assess credibility — do not arbitrarily choose one."

**5. UNCERTAINTY PROTOCOL + OUTPUT FORMAT**
"If specific data cannot be found, state 'Data Unavailable.' Do not infer or estimate."
Then output: Markdown with ## headers and comparison tables for Canvas rendering.

**Compressed skeleton:**
```
ROLE: You are a [specific expert] specializing in [domain].
TASK: [One research objective].
SCOPE: Execute sub-searches targeting: 1. [angle] 2. [angle] 3. [angle]
SOURCE POLICY: Prioritize [types]. Exclude [types]. Conflict: [protocol].
UNCERTAINTY: If data unavailable, state "Data Unavailable." Do not infer.
OUTPUT: Structured Markdown. ## headers. Tables for [comparisons].
```

## Leverage Points

**Multi-source iterative synthesis** — The agent runs dozens of search loops inaccessible
to synchronous chat. Trigger by providing 3-5 narrow, specific sub-search dimensions.
Broad topics waste the loops; narrow dimensions exploit them.

**Document + web hybrid grounding** (App) — @ references to Drive/Docs ground the agent
in private data while simultaneously browsing the web. Trigger with explicit sequential
tasks: "Phase 1: extract from @file. Phase 2: web search for external data."

**Conflict resolution as analytical output** — Instead of smoothing over contradictions,
the agent can MAP them. Trigger with: "Document both estimates, cite methodologies,
assess credibility based on recency and domain authority."

**Delta update capability** — For monitoring situations, establish a known baseline
and a freshness window: "Do not re-report baseline. Focus exclusively on developments
between [date] and [date]." Forces date-stamped, high-density intelligence updates.

**Canvas-ready structured reports** — Mandating Markdown with ## headers and tables
produces output that segments cleanly in Canvas and supports post-generation editing.

**Plan steering** (App) — The research plan is editable before execution. Prompts
should define sub-topics explicitly to shape the initial plan; users can inject
missed constraints via the "Edit plan" UI before the agent starts searching.

## Failure Modes & Repair

**FAILURE: Boiling the Ocean**
WHY: Vague topic → plan fragments into 50+ subtopics → output truncated; final sections
are thin bullets without citations.
REPAIR: Narrow query aggressively. Dictate specific deliverables. "Analyze the impact of
GenAI on healthcare administration and retail logistics" beats "analyze AI's impact."

**FAILURE: Browsing drift to SEO content farms**
WHY: No source policy → agent browses whatever ranks highly, including spam and listicles.
REPAIR: Always include explicit source whitelist + blacklist in every prompt.

**FAILURE: Context pollution (same thread re-use)**
WHY: Failed research loops fill the context window; agent hallucinates connections from
prior failed synthesis or times out ("Read but not used" bug).
REPAIR: Start a new Deep Research session when pivoting topic or fixing a broken search.

**FAILURE: Premature synthesis / causal hallucination**
WHY: No reasoning trace required → agent leaps to conclusions from flawed intermediary
logic; common in medical, scientific, and financial queries.
REPAIR: Mandate ERT — "Before the final recommendation, generate a step-by-step
reasoning trace: state assumptions, evaluate counter-arguments, quantify confidence."

**FAILURE: File upload suppresses web search**
WHY: Large uploaded documents (300+ pages) saturate the context; agent prioritizes file
analysis and abandons external retrieval.
REPAIR: Explicit task sequencing — "Phase 1: synthesize uploaded files. Phase 2:
suspend file analysis, execute exhaustive web search. Phase 3: merge findings."

**FAILURE: Token degradation in long reports**
WHY: As context fills, the agent compresses or truncates sections at the end.
REPAIR: Front-load critical sub-topics in scope enumeration; mandate high-value
tables and synthesis early in the report structure.

**FAILURE: Hallucinated statistics**
WHY: Agent can't find specific data but is driven to complete the plan; fabricates
plausible-sounding metrics rather than admitting absence.
REPAIR: Explicit uncertainty protocol: "If unavailable, state 'Data Unavailable.'
Do not infer, extrapolate, or estimate to fill the void."

**FAILURE: Safety filter lock from over-constraining**
WHY: Stacking multiple isolated "Do not X" constraints can trigger safety filtering
or cause the agent to freeze (cannot execute search tool).
REPAIR: Pair every negative with a positive redirect — "Do not use blogs;
instead retrieve exclusively from technical whitepapers."

## Calibration

**Prompt length:** 200-500 words for a primary research prompt. Below 200, the scope
is too thin for the agent to build a meaningful plan. Above 500, over-constraining
risk increases and the agent may freeze or apply safety filters.

**Tone and register:** Imperative and professional. "You are a [Expert]" persona
framing works significantly better than open-ended questions. Direct language
("Execute sub-searches targeting...") produces more structured research plans
than polite requests ("Could you look into...").

**Output format:** Always mandate Markdown with ## section headers. Tables for
competitive comparisons, methodology comparisons, and risk matrices. Canvas renders
Markdown natively — structure the report so sections can be independently edited.
Avoid requesting large data tables, raw code blocks, or complex formulas if
the deliverable will be converted to Audio Overview.

**Scope ordering:** Most critical sub-topics first. The agent processes and outputs
them roughly in enumeration order; truncation hits the final quartile.

**Priority instruction:** For broad multi-faceted requests, explicitly label priority:
"Output high-value synthesis and core data tables early in the report."

## Operating Environment [EXTEND]

**App Environment (gemini.google.com / Workspace)**

- Research plan is visible and editable before execution — prompt sub-topics shape
  the initial plan; users can inject corrections via "Edit plan" UI
- Use `@FileName` or `@Drive` to ground in private documents
- Output renders in Canvas: Markdown, code blocks, visualizations — all segmentable
- Audio Overview transformation available from Canvas (fails on PHI, heavy tables,
  code blocks — avoid these if audio is the end goal)
- Session context pollution is a real failure mode — broken threads should be reset

**API Environment (Interactions API / Google AI Studio / Vertex AI)**

- All requests via `background=true` — async execution, poll via returned interaction ID
- NO UI affordances: strip all references to @ symbols, "edit plan," "export to docs"
- Follow-up queries use `previous_interaction_id` to continue a research thread
- JSON schema output configurable via `response_format` — prompts steer reasoning,
  not output structure (schema handles structure)
- Every API prompt must be exhaustive and bulletproof — no human-in-the-loop plan editing
- Cost: up to 160 search iterations, 900k tokens, ~$3-5/task — include strict scope
  constraints and explicit termination criteria to prevent wasteful infinite loops

## CRITICAL — Gemini Deep Research Rules

1. ALWAYS include explicit source policy in every prompt — whitelist accepted types, blacklist known garbage (SEO blogs, content farms, unverified forums).
2. ALWAYS mandate Explainable Reasoning Trace for factual, medical, financial, or strategic queries — without ERT, the agent synthesizes prematurely.
3. ALWAYS install uncertainty protocol — "If data unavailable, state 'Data Unavailable.' Do not infer." Missing data triggers hallucinated statistics without this.
4. ALWAYS add conflict resolution protocol for data-heavy queries — "Document both figures, cite methodologies, assess credibility — do not choose arbitrarily."
5. ALWAYS front-load highest-priority sub-topics in scope — truncation kills the final quartile of long reports.
6. NEVER use vague scope — enumerate exact dimensions; vague scope = generic research plan = shallow aggregation.
7. NEVER assign a strong KPI without explicit ethical and safety guardrails — capability amplifies outcome-driven misalignment.
8. NEVER include UI affordances (@ symbol, plan editing, Canvas export) in API payloads — they have no function in headless execution.
9. NEVER stack isolated negative constraints — always pair "Do not X" with "instead do Y" to avoid safety filter triggering.
10. REQUIRE explicit sequential task structure when large file uploads are involved: Phase 1 files → Phase 2 web search → Phase 3 merge.
11. PREFER starting a new session when debugging a broken research thread — context pollution from failed loops compounds hallucinations.
