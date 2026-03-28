<!-- @meta
  name: [target-name]
  tags: [tag1, tag2, tag3]
  priority: 7
  category: [generative | analytical | creative | voice]
-->

## Mental Model

[How does this tool THINK? Not what it is — how it PROCESSES prompts.
This is the most important section. It shapes how prompt-smith approaches
everything else. Write it as a cognitive frame shift.

BAD: "Gemini Deep Research is a research tool by Google."
GOOD: "Gemini Deep Research is an autonomous browsing AGENT. It doesn't
answer your question — it builds a research PLAN, then executes search
loops, reads pages, reasons across sources, and compiles a report. Your
prompt is not a question. It's an architectural brief that dictates what
the agent investigates, where it looks, and how it handles uncertainty."

This section should make prompt-smith think DIFFERENTLY about prompt
construction for this target. ~150-250 words.]

## Prompt Architecture [OVERRIDE]

[The skeleton of an optimal prompt for this target. Named parts, in order.
This OVERRIDES the master prompt structure because every tool has its own
grammar.

For generative tools: Opening → Subject → Action → Style → Atmosphere
For research agents: Persona → Task → Scope → Source Policy → Output Format
For voice tools: Character → Emotion → Pacing → Technical specs

Be specific about what goes in each part and WHY that order matters.
Include one compressed example showing the skeleton filled in.
~200-350 words.]

## Leverage Points

[What does this tool do EXCEPTIONALLY well? These are capabilities that
prompt-smith should ACTIVELY exploit when generating prompts.

Don't list features. List exploitable strengths with HOW to trigger them.

BAD: "Good at atmospheric lighting."
GOOD: "Atmospheric lighting is the primary differentiator. Trigger it by
specifying light SOURCE + light QUALITY + light INTERACTION with surfaces.
'Warm amber light streaming through dusty windows, catching on floating
particles' activates the full atmospheric pipeline."

5-8 leverage points, each 1-2 sentences. ~150-250 words.]

## Failure Modes & Repair

[What goes WRONG and how to PREVENT it. This section combines limitations
AND anti-patterns because prompt-smith needs both: what to avoid and what
to do instead.

Format each as: FAILURE → WHY → REPAIR

"FAILURE: Uploading >300k tokens of files suppresses web search.
WHY: Agent prioritizes file analysis over external retrieval when context
is saturated.
REPAIR: Sequence explicitly — 'Phase 1: Analyze uploaded files. Phase 2:
Suspend file analysis, execute exhaustive web search. Phase 3: Merge.'"

5-10 failure modes, prioritized by frequency and severity. ~250-400 words.]

## Calibration

[The tuning parameters. Length, style references, output format expectations.
Everything prompt-smith needs for the FINISHING PASS on a prompt.

- Optimal prompt length (range in words, with explanation)
- Style anchoring that works (specific references, frameworks, personas)
- Output format expectations (what the tool renders well vs. poorly)
- Tone and register (technical vs. conversational, dense vs. sparse)

~150-250 words.]

## Operating Environment [EXTEND]

[OPTIONAL — include only when the tool has meaningfully different modes.

App vs. API, free vs. paid tier, platform-specific behaviors.
Prompt-smith needs to know: does the ENVIRONMENT change what a valid prompt
looks like? If yes, describe each environment and its prompting implications.

If the tool has a single environment — SKIP this section entirely.
~100-300 words when present.]

## CRITICAL — [Target] Rules

[The absolute constraints. These go at the END of compiled output
(recency exploit — Claude pays most attention to recent tokens).

7-12 rules. Each starts with a verb: ALWAYS, NEVER, PREFER, INCLUDE,
AVOID, REQUIRE, ENSURE.

These are the rules that, if violated, produce BAD output regardless of
how good the rest of the prompt is. They should be the most validated,
most impactful knowledge in the file.

Rules should be OPERATIONAL, not philosophical.
BAD: "ALWAYS be specific." (too vague)
GOOD: "ALWAYS define source policy — whitelist accepted domains, blacklist
known spam. Without this, the agent pulls from SEO content farms." (actionable)

~150-250 words.]

<!--
TOKEN BUDGET GUIDE:
- Target: 1200-2000 tokens for the full .ctx.md file
- Compiled with master.ctx.md (~550 tokens): 1750-2550 total
- Compiler warns at 4000 tokens (generous headroom)
- CRITICAL rules get recency boost — invest tokens here
- Operating Environment is optional — skip for simple tools
- When in doubt, invest tokens in Failure Modes & Repair
  (preventing bad prompts > describing ideal prompts)

CATEGORIES:
- generative: video, image, 3D (visual output)
- analytical: research agents, coding assistants (information output)
- creative: music, writing (artistic output)
- voice: TTS, voice cloning (audio output)

Category affects which sections get the most token investment:
- generative → heavy Leverage Points + Calibration
- analytical → heavy Failure Modes + Operating Environment
- creative → heavy Mental Model + Calibration
- voice → heavy Prompt Architecture + Calibration
-->
