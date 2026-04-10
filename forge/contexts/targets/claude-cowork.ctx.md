<!-- @meta
  name: claude-cowork
  tags: cowork, agent, workflow, desktop, orchestration, multi-agent, skills, plugins
  priority: 8
  category: analytical
  last_validated: 2026-03-29
-->

## Mental Model

Claude Cowork is not a chatbot — it is a desktop workflow orchestration engine running inside an isolated VM. The fundamental shift: your prompt defines a **terminal state** (what "done" looks like), not the next step. Once defined, Cowork autonomously plans, loops, and executes — traversing directories, calling tools, spawning agents, and writing to disk — without pausing to ask questions.

Two critical asymmetries separate Cowork from standard Claude prompting. First, **ambiguity executes immediately**: there is no clarification loop by default. The agent guesses your intent and acts. Second, **side effects are permanent**: every tool call can modify your local file system. A Cowork prompt is a constraint on a live execution engine, not a conversational suggestion.

The "Done Framework" is the session backbone: define terminal state → agent builds execution plan → iterative tool loop until criteria met. Session memory is entirely ephemeral across restarts — the agent begins each new session with no history. Prompt authors must build explicit state persistence into every workflow.

Plugins extend Cowork with reusable "role playbooks" built from Markdown and JSON. Skills are persistent routing nodes — not text prompts — governed by YAML frontmatter that acts as the semantic router's control plane.

## Prompt Architecture [OVERRIDE]

Every Cowork prompt follows a six-part structure:

**1. GOAL STATE** — terminal condition + business outcome in one sentence.
"I want to [action] so that [outcome]." NOT: "Please do X, then Y, then Z."

**2. FILE/CONTEXT SCOPE** — explicit directory paths the agent may read and write.
Anything unlisted is off-limits by implication.

**3. GATE CLAUSE** — mandatory pause before execution.
"DO NOT start executing yet. Use the AskUserQuestion tool to ask clarifying questions. Only begin once we have aligned on the plan."

**4. EXECUTION RULES** — numbered, ordered steps with conditional logic.
("Step 3 only if Step 2 output contains X.")

**5. OUTPUT SPEC** — exact file paths and naming convention.
Format: YYYY-MM-DD_ProjectName_v1.ext. Never leave naming to the agent.

**6. CONSTRAINTS** — hard limits: directories off-limits, operations requiring human confirmation, tools disallowed.

**Compressed skeleton:**
```
I want to [goal] so that [outcome].
Scope: [directories the agent may touch].
DO NOT start yet. Use AskUserQuestion to confirm the plan.
Rules: 1. [step] 2. [step] 3. [step]
Output: Write to [exact path]. Name format: [convention].
Do not: [hard limits].
```

For SKILL.md files: YAML frontmatter → DCI pre-load (`!`command || fallback``) → variable slots ($ARGUMENTS, $0-$9, ${CLAUDE_SESSION_ID}, ${CLAUDE_SKILL_DIR}) → execution rules → output spec.

## Leverage Points

**Goal-State Execution** — Cowork evaluates all actions against the terminal condition. Trigger by front-loading "I want to [X] so that [Y]" — this anchors the entire execution loop.

**Dynamic Context Injection (DCI)** — shell commands fire at skill activation, injecting output into the prompt before LLM reasoning begins. Use for git status, directory scans, dependency checks — prevents the agent wasting turns probing the environment manually.

**Semantic Skill Auto-Routing** — agent continuously matches user intent to installed skill description fields and injects matched skill instructions autonomously. The description field IS the routing rule — write it as a precise activation condition.

**File Handoff State Machine** — agents communicate via disk files, not context-window transfers. Instruct each agent to write output to a named file and return only the file path. Zero token cost, permanent audit trail, crash-safe recovery.

**Agent Teams with Lateral Debate** — fully independent context windows where teammates communicate directly without routing through an orchestrator. Trigger by: "Do not use standard subagents; spawn fully independent teammates" with named roles and a Devil's Advocate seat.

**claude.md Anchor** — a root-level SOP file read by the agent on session init. Place formatting rules, directory topology, and agent role definitions in /project/claude.md before opening the session.

## Failure Modes & Repair

**FAILURE: Immediate execution on ambiguous task**
WHY: No gate clause — agent executes a plausible interpretation and writes to disk before you can correct.
REPAIR: Always open with the Gate Clause: "DO NOT start executing. Use AskUserQuestion first."

**FAILURE: Session memory wipe on restart**
WHY: Cowork sessions are stateful during active turns but entirely ephemeral across restarts.
REPAIR: Mandate creation of context.md at project root. Instruct agent to read it on boot and append operational summary before closing.

**FAILURE: Subagent quota depletion / context bloat**
WHY: Subagent prints full contents of large files directly into the orchestrator's context window.
REPAIR: File Handoff pattern — "Write analysis to /path/output.md. Return only the file path to the main context."

**FAILURE: Skill auto-discovery fails silently**
WHY: Block scalar (> or |) in SKILL.md YAML description field. Semantic router ingests literal formatting characters instead of the intent string.
REPAIR: Description must be a single-line inline string. No multi-line block scalars in YAML frontmatter.

**FAILURE: Plugin components not discovered**
WHY: skills/, commands/, or agents/ placed inside .claude-plugin/ instead of at the plugin root.
REPAIR: Only plugin.json lives inside .claude-plugin/. All component directories sit at the plugin root alongside it.

**FAILURE: QA / evaluation hallucination**
WHY: Zero-shot quality judgment without scaffolding. LLM identifies structural errors then self-corrects to false approval.
REPAIR: Force intermediate file: "Write raw diffs and stack traces to /reports/qa-raw.md before producing qualitative judgment."

**FAILURE: Prompt injection via processed documents**
WHY: Agent cannot distinguish system instructions from text inside ingested files (PDFs, scraped pages).
REPAIR: Define exact directory scope in every prompt. Mandate human confirmation before any permanent side effect.

**FAILURE: DCI shell command crash**
WHY: Required executable missing from host environment — DCI command errors and skill halts.
REPAIR: Always pair DCI injections with fallback: `!`command || echo 'not available'``

## Calibration

**Tone and register:** Programmatic, imperative. "Write to /path/file.md" beats "Please create a file." Goal-state framing ("I want X so that Y") produces dramatically more accurate execution plans than enumerating steps.

**SKILL.md constraints:** Name: max 64 characters, lowercase and hyphens only, no XML tags, no "claude" or "anthropic" namespace. Description: single-line inline string only — this IS the routing signal. Argument-hint: document expected input. Allowed-tools: allowlist only what is required.

**DCI injections:** Small summaries and status checks only — never full file dumps. One DCI command per environmental concern. Always include `|| echo` fallback.

**Output naming:** Always specify a naming convention. YYYY-MM-DD_ProjectName_v1.ext is the established standard. Never let the agent choose names.

**Multi-agent budget:** Subagents = efficient, isolated, good for extraction or routing to cheaper models (Haiku). Agent Teams = expensive (multiple full parallel context windows), reserve for tasks requiring genuine debate or multi-disciplinary synthesis.

## Operating Environment [EXTEND]

**Solo Session (GUI)**
Standard desktop session. Agent reads claude.md anchor on init. Plugin skills auto-route via semantic matching. DCI runs at skill activation. File Handoffs and context.md persistence are the primary state mechanisms. No UI-level execution restrictions — all constraints must come from your prompt.

**Multi-Agent Orchestration**
Invoke with explicit spawning language: "Do not use standard subagents; spawn fully independent teammates." Requires named roles, lateral communication assignments, Devil's Advocate designation, and output file targets per agent. User can inject feedback directly into individual teammate streams. Introduced in Claude Code v2.1.32. Highly token-expensive — budget accordingly.

**Plugin / Skill Authoring**
YAML frontmatter is the control plane for the semantic router. DCI runs before LLM sees the prompt. Slot-filling happens before LLM reasoning. Directory rule: plugin.json inside .claude-plugin/, all component directories (skills/, commands/, agents/, hooks/) at the plugin root alongside .claude-plugin/.

## CRITICAL — Claude Cowork Rules

1. ALWAYS open with the Gate Clause for any task writing to disk: "DO NOT execute yet. Use AskUserQuestion first."
2. ALWAYS define terminal state in the first sentence: "I want to [goal] so that [outcome]."
3. ALWAYS specify exact output file paths and naming convention — never let the agent choose.
4. ALWAYS mandate context.md persistence for any session that needs to resume across restarts.
5. ALWAYS define explicit directory scope — apply principle of least privilege, mandate human confirmation before permanent side effects.
6. ALWAYS pair DCI injections with a fallback (`|| echo 'not available'`) to prevent skill crashes.
7. NEVER place skills/, commands/, or agents/ inside .claude-plugin/ — they must sit at the plugin root.
8. NEVER use block scalars (> or |) in SKILL.md YAML description fields — single-line inline strings only.
9. NEVER instruct a subagent to return large content directly — File Handoff: write to disk, return only the path.
10. NEVER request QA judgment without first mandating an intermediate raw output file (diffs, logs, stack traces).
11. PREFER Agent Teams over Subagents when the task requires debate, devil's advocacy, or multi-disciplinary synthesis.
12. REQUIRE named roles and output file targets for every Agent Team spawn.
