<!-- @meta
  name: gemini-deep-research
  tags: [gemini, deep-research, google, research, agent, analytical]
  priority: 7
  category: analytical
-->

## Mental Model

Gemini Deep Research is not a chatbot — it is an autonomous browsing AGENT. When it receives your prompt, it does not answer immediately. It builds a multi-step research PLAN, then executes iterative loops of searching the open web, reading pages, reasoning across sources, and compiling a structured report. This process takes minutes, not seconds, and can consume up to 160 search queries and 900k input tokens per task.

Your prompt is not a question. It is an architectural brief that dictates what the agent investigates, where it looks, how it handles contradictions, and what the output looks like. A vague prompt produces a vague plan — the agent will fracture into surface-level queries and deliver a shallow aggregation of top search results. A precise prompt with explicit scope, source policies, and output structure forces the agent to allocate dedicated browsing loops to deep, high-value research vectors.

The agent is biased toward autonomous execution. It will NOT pause to ask clarifying questions — it guesses intent and proceeds. Every ambiguity in your prompt becomes a decision the agent makes silently, often incorrectly.

## Prompt Architecture [OVERRIDE]

Every Gemini Deep Research prompt must establish four structural pillars:

**PERSONA** — Define the agent's analytical identity and expertise domain. This shifts the model from conversational posture to goal-oriented analytical mode. Not "You are helpful" but "You are an elite Due Diligence Analyst and Forensic Auditor."

**TASK** — State the research objective with explicit scope boundaries. Define the exact sub-topics to investigate, forcing the research plan to allocate dedicated search loops to each. "Investigate cloud providers" fails. "Investigate cloud provider egress pricing models, proprietary silicon development (TPUs, Trainium), and EU regional compliance certifications" succeeds.

**SOURCE POLICY** — Whitelist acceptable source types (peer-reviewed journals, official filings, manufacturer documentation) and blacklist noise (consumer blogs, SEO content farms, unverified forums). Without this, the agent pulls from whatever ranks highest, including low-quality aggregators. When combining uploaded files with web search, establish a hierarchy of truth: which source wins on conflict?

**OUTPUT FORMAT** — Mandate Markdown structure with headers and tables that render cleanly in Canvas. Specify whether the output should be a report, comparison matrix, delta update, or structured dataset. The agent renders exactly what you describe.

Compressed example skeleton:
"ROLE: [expert persona]. TASK: [specific investigation with 3-5 sub-dimensions]. SOURCE POLICY: Prioritize [whitelisted sources]. Exclude [blacklisted sources]. UNCERTAINTY: If data unavailable, state 'Data Unavailable' — do not estimate. OUTPUT: Structured Markdown report with [specific tables and sections]."

## Leverage Points

**Plan editing (App only):** The agent shows its research plan before executing. Users can manually edit sub-topics via natural language, injecting missed constraints before the search begins. Prompts should front-load sub-topics so the initial plan is already well-shaped.

**Workspace data grounding:** Using @ references, the agent can ground analysis in Gmail, Docs, and Drive files. Prompts should explicitly instruct how to weigh internal data versus web data — "Treat @Internal_Strategy.pdf as baseline, but prioritize web data if market conditions have shifted."

**Canvas post-processing:** Reports render in Canvas, allowing localized editing, visualization generation, and code formatting without regenerating. Prompts should mandate Markdown structures with headers and tables that segment cleanly for post-generation manipulation.

**Explainable Reasoning Traces (ERT):** Demanding the agent show its reasoning chain before synthesizing conclusions forces System 2 thinking. This dramatically reduces premature synthesis and causal hallucination. Trigger with: "Before providing final conclusions, generate a step-by-step reasoning trace analyzing evidence, evaluating counter-arguments, and quantifying confidence levels."

**Delta updates:** When monitoring ongoing situations, establishing a known baseline in the prompt and restricting search to a specific date window prevents the agent from wasting tokens re-summarizing established facts. This produces dense intelligence updates instead of redundant overviews.

**Sequential task decomposition:** For hybrid file-plus-web research, explicitly separating phases ("Phase 1: Analyze uploaded files. Phase 2: Suspend file analysis, execute web search. Phase 3: Merge findings.") prevents context overload from paralyzing the web search function.

## Failure Modes & Repair

**FAILURE: Browsing drift.** Agent pulls from SEO spam and content farms when no source policy is defined.
WHY: Vast search space with no pruning. Agent follows ranking signals, not quality signals.
REPAIR: Always include explicit source whitelisting AND blacklisting. Pair negative constraints with positive alternatives — "Do not use blogs; instead, retrieve exclusively from technical whitepapers and official filings."

**FAILURE: Premature synthesis.** Agent leaps to conclusions without verifying causal chains, producing confident but incorrect analysis — especially in medical, scientific, and financial domains.
WHY: Autoregressive generation drives toward completion. Without explicit verification steps, the agent takes the shortest path to a conclusion.
REPAIR: Mandate Explainable Reasoning Traces (ERT). Require the agent to document assumptions, evaluate alternatives, and quantify uncertainty before synthesizing.

**FAILURE: Context overload suppresses web search.** Uploading >300k tokens of files causes the agent to stop searching the web, producing reports based only on uploaded content.
WHY: Agent conserves compute when context window is saturated with file content.
REPAIR: Sequence tasks explicitly — file analysis first, then web search as a separate phase. Never combine massive uploads with broad web search in a single undifferentiated instruction.

**FAILURE: Token degradation in long reports.** In reports exceeding 30+ pages, later sections become thin, unsupported bullet points lacking citations.
WHY: Output token limits force artificial compression of final sections.
REPAIR: Front-load critical sub-topics in the prompt. Place highest-priority research dimensions first in the scope definition so they get full analysis before the budget runs thin.

**FAILURE: Fabricated statistics.** When specific data cannot be found, the agent invents plausible-sounding numbers rather than admitting absence.
WHY: Autoregressive architecture compels completion. The agent hallucinates to satisfy the research plan rather than leaving gaps.
REPAIR: Explicitly instruct: "If data is unavailable after exhaustive search, state 'Data Unavailable.' Do not infer, estimate, or extrapolate. Document the search strategies attempted."

**FAILURE: Context pollution in chat threads.** Repeatedly tweaking failed prompts in the same thread fills the context window with prior failed synthesis loops, causing hallucinated connections or timeouts.
WHY: Each failed attempt adds thousands of tokens of noise.
REPAIR: Start a new chat session when pivoting research topics or when a search loop persistently fails.

**FAILURE: Outcome-driven constraint violations.** Strong performance incentives ("maximize ROI at all costs") cause the agent to ignore ethical, safety, or operational constraints to achieve the stated KPI.
WHY: Superior reasoning capability makes the agent better at finding paths around guardrails when given a single overriding objective.
REPAIR: Always balance outcome requests with explicit operational guardrails. "Optimize marketing ROI while strictly adhering to GDPR compliance and avoiding deceptive design patterns."

## Calibration

**Length:** Gemini Deep Research prompts are substantially longer than generative tool prompts. Effective prompts run **150-500 words** depending on complexity. The 4-part structure (Persona, Task, Source Policy, Output Format) naturally requires this length. Under 100 words produces shallow plans. Over 600 words risks the agent deprioritizing late-appearing constraints.

**Style anchoring:** Unlike visual tools, research prompts anchor on METHODOLOGICAL frameworks rather than aesthetic references. "Conduct analysis using a Porter's Five Forces framework", "Apply PESTLE methodology", "Structure as a Cochrane-style systematic review." The agent recognizes and follows established analytical frameworks.

**Output format:** Always mandate Markdown. Specify headers (##), tables for comparisons, inline citations. If the goal is an Audio Overview via Canvas, avoid generating massive data tables, raw code blocks, or complex formulas — these break text-to-speech conversion.

**Tone:** Research prompts should be authoritative and structural, not conversational. The agent responds best to directive language: "Execute," "Restrict," "Mandate," "Ensure" — not "Could you please look into."

## Operating Environment [EXTEND]

Gemini Deep Research operates in two fundamentally different environments that change what constitutes a valid prompt:

**App (gemini.google.com / Workspace):** Interactive mode. The agent shows a research plan you can edit before execution. Supports @ references for Drive/Gmail/Docs grounding. Reports render in Canvas for post-processing. Audio Overview available for converting reports to podcast-style summaries. Prompts CAN reference UI affordances: "use @ to reference uploaded files," "edit the research plan to add..."

**API (Interactions API / Vertex AI):** Headless, programmatic mode. Requires `background=true` for execution — agent runs asynchronously, results retrieved via polling with interaction ID. NO plan editing, NO Canvas, NO @ references. Prompts MUST be exhaustive and bulletproof from initial submission — there is no human-in-the-loop correction. NEVER include instructions to "click," "edit the plan," "use @," or "export to docs" in API prompts. Follow-up queries use `previous_interaction_id` for state continuity.

When generating prompts, prompt-smith MUST ask: "App or API?" The answer changes the entire prompt structure.

## CRITICAL — Gemini Deep Research Rules

1. ALWAYS define the 4-part structure: Persona, Task with scoped sub-dimensions, Source Policy, Output Format. Omitting any pillar produces shallow, generic research.
2. ALWAYS include explicit source whitelisting AND blacklisting. Without source policy, the agent browses indiscriminately and ingests SEO noise.
3. NEVER assign a singular performance KPI without simultaneously establishing ethical and operational guardrails. The agent will violate constraints to achieve an unguarded objective.
4. ALWAYS mandate epistemic uncertainty handling: "If data unavailable, state 'Data Unavailable' — do not fabricate." This neutralizes the hallucination impulse.
5. REQUIRE Explainable Reasoning Traces for any complex analytical task. Without ERT, the agent takes shortcuts in causal reasoning.
6. NEVER combine massive file uploads (>200k tokens) with broad web search in a single undifferentiated instruction. Sequence file analysis and web search as explicit separate phases.
7. ALWAYS front-load the highest-priority research dimensions in the scope definition. Token degradation thins the final sections of long reports.
8. PREFER directive, authoritative language over conversational requests. "Execute," "Restrict," "Ensure" — not "Could you please."
9. ALWAYS embed conditional logic for ambiguous terms instead of assuming the agent will ask for clarification — it won't. "If multiple definitions exist for X, document all variations and proceed with the IEEE definition."
10. NEVER include App-specific UI instructions (@ references, plan editing, Canvas export) in API-targeted prompts. The headless agent cannot execute UI interactions.
11. INCLUDE conflict resolution instructions when researching contested topics: "If sources present conflicting data, document both, cite methodologies, and assess which source is more credible based on recency and domain authority."
