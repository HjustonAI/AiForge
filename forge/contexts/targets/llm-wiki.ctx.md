<!-- @meta
  name: llm-wiki
  tags: knowledge-base, wiki, agentic-ide, karpathy, setup-prompt
  priority: 7
  category: analytical
  last_validated: 2026-04-13
-->

## Mental Model

You are not writing a query. You are commissioning a software architect to build a personal knowledge system from scratch.

The agent receiving this prompt will read Karpathy's idea file as a complete architectural blueprint — three layers (raw sources, wiki, schema), three operations (ingest, query, lint), two navigation files (index.md, log.md). From that blueprint it will generate: a directory structure tailored to your domain, a schema file (CLAUDE.md / AGENTS.md / OPENCODE.md) with domain-specific page types and workflows, and a guided first ingest.

The shift that matters: the idea file already contains the full pattern. Your prompt's job is NOT to explain the wiki concept — it's to provide the agent with four binding constraints: **domain**, **platform**, **sources**, and **tooling**. Everything else the agent will figure out. Underprovide these four and the agent builds something generic. Provide them precisely and it builds something that fits your actual workflow.

The output is a live, committed file system — not a chat response. Think of this as opening a project kickoff with a contractor: you state the goal, the materials you have, the tools you're working with, and you ask them to start. The agent writes files and asks for your review after each step.

## Prompt Architecture [OVERRIDE]

**Structure: Context Drop → Domain Declaration → Source Inventory → Tool Preferences → Request**

**1. Context Drop** (mandatory, verbatim)
Paste the full llm-wiki.md idea file. Never summarize. The agent needs the complete schema patterns, operation definitions, and example workflows. Even if the agent "knows" the pattern, the paste anchors the session to Karpathy's exact conventions.

**2. Domain Declaration** (1-2 sentences, specific)
Name the topic precisely. Not "research" — "ML paper reading focused on efficient inference". Not "business" — "competitive analysis of B2B SaaS pricing pages". The schema's concept page types, frontmatter fields, and ingest emphasis all flow from this declaration.

**3. Source Inventory** (3-5 bullet points)
List the types and rough count of sources you have or plan to gather. Examples: "10 PDF papers", "20 web articles clipped to markdown", "5 meeting transcripts". This shapes the `raw/` directory taxonomy.

**4. Tool Preferences** (1-2 sentences)
State your markdown viewer (Obsidian / VS Code / other) and whether you want git. Obsidian unlocks Dataview, graph view, and Web Clipper conventions in the schema.

**5. Request** (explicit, phased)
Ask for: setup → schema file → walk me through first ingest. Phrasing matters: "walk me through" activates interactive coaching mode where the agent pauses for your review after each step.

**Example skeleton:**
```
Here is an idea file from Karpathy about building an LLM Wiki:

[paste full llm-wiki.md]

I want to build one for [specific domain].

My sources: [list types + counts].
Tools: [Obsidian / VS Code + git / other].
Agent: [Claude Code / Codex / OpenCode].

Please set up the directory structure, create the schema file, and walk me through ingesting my first source.
```

## Leverage Points

**Full paste triggers full pattern.** The agent receives not just intent but the complete spec: ingest workflow steps, query workflow, lint checklist, index.md format, log.md format. All of this becomes the default behavior — no re-explanation needed in future sessions.

**Domain specificity forces domain-tuned schema.** A precise domain declaration causes the agent to define domain-specific concept categories, entity types, and frontmatter fields in CLAUDE.md. "ML paper reading" → concept pages for architectures, benchmarks, authors; confidence field for claims. Generic domains produce generic schemas.

**Source inventory shapes directory taxonomy.** Listing source types (papers vs. articles vs. transcripts vs. data files) causes the agent to create the right `raw/` subdirectories and ingest conventions for each type.

**Platform name determines schema file.** Claude Code reads `CLAUDE.md`. Codex reads `AGENTS.md`. OpenCode reads `OPENCODE.md`. Naming the agent prevents a wrong-filename schema that gets silently ignored.

**"Walk me through" activates interactive mode.** Without this phrase, the agent may batch-execute all setup steps silently. With it, the agent narrates each action, pauses for approval, and teaches you the workflow as it builds.

**First source in hand unlocks real schema tuning.** If you describe (or drop) your first source when requesting setup, the agent writes frontmatter fields that actually match the data in your sources — not hypothetical fields.

## Failure Modes & Repair

**FAILURE: Summarizing the idea file instead of pasting it verbatim.**
WHY: The agent loses the exact operation definitions, example CLAUDE.md, and index.md format. It falls back to generic wiki behavior.
REPAIR: Paste the full llm-wiki.md content. It's ~1000 words — worth every token.

**FAILURE: Vague topic declaration ("I want to do research" / "business stuff").**
WHY: The schema gets generic page types (concept, entity, source) with no domain vocabulary. You'll spend sessions retro-fitting it.
REPAIR: One precise sentence: "ML paper reading focused on transformer efficiency post-2024." The agent extracts concept categories from this.

**FAILURE: Omitting agent platform name.**
WHY: Agent may create CLAUDE.md when you're using Codex (reads AGENTS.md) — the schema file is invisible to your agent.
REPAIR: State "I'm using Claude Code / Codex / OpenCode" explicitly in the prompt.

**FAILURE: Requesting setup without a first source ready.**
WHY: Without a real first source, the agent generates a template schema with placeholder page types instead of domain-calibrated ones.
REPAIR: Drop at least one source file into `raw/` before running the setup prompt, then mention it: "My first source is raw/articles/[filename].md — include it in the first ingest."

**FAILURE: Over-specifying schema fields in the prompt ("the frontmatter must have fields X, Y, Z...").**
WHY: Prevents the agent from applying domain judgment. You get technically correct but practically wrong schemas.
REPAIR: Describe your domain and what you want to be able to ask the wiki later. Let the agent infer the fields.

**FAILURE: Batch-requesting 10+ sources in the first session.**
WHY: First-session setup needs iteration — the agent may create page structures that need adjustment. Batch ingest locks in wrong conventions.
REPAIR: First session: setup + 1 source. After reviewing the output, iterate the schema. Then batch.

**FAILURE: Skipping the git initialization request.**
WHY: Without version control, bad ingest results are unrecoverable. The schema may also not include commit steps in the ingest workflow.
REPAIR: Include "initialize git and add commit steps to the ingest workflow" in your request.

## Calibration

**Prompt length:** 200-400 words for the framing prompt, plus the full llm-wiki.md paste (~1000 words). Total context: ~1200-1400 words. This is normal and necessary.

**Tone:** Project brief. Directive, not interrogative. State what you want built, not what you're thinking about. "I want to build one for X" over "I'm considering maybe building something like X."

**Output format expectations:** The agent will typically: (1) confirm it understood the setup, (2) propose a directory tree and schema draft, (3) ask for approval, (4) write files, (5) guide the first ingest interactively. If the agent skips step 3, ask explicitly: "Show me the proposed structure before writing files."

**Style anchoring:** The idea file's example CLAUDE.md is a strong reference. If the agent produces a schema that looks substantially different from that example (missing the Ingest/Query/Lint workflow sections), prompt: "Follow the schema format from the idea file more closely."

**Iteration signal:** After first ingest, check: do the frontmatter fields match what the agent wrote in index.md? If not, the schema needs one revision pass before ingesting more sources.

## Operating Environment [EXTEND]

**Claude Code (CLAUDE.md):** The most capable environment for this pattern. CLAUDE.md is read at session start automatically. Bash access enables `git` commits in the ingest workflow. The LLM can touch 15 files per ingest without needing separate commands. Preferred environment.

**OpenAI Codex (AGENTS.md):** Same pattern, different schema filename. Codex has strong file manipulation but weaker cross-file awareness — the schema's ingest workflow should be more explicit about which files to update and in what order.

**OpenCode / generic agentic IDE:** Use `OPENCODE.md` or check your tool's documentation for the schema file name. The principle is identical — a markdown file at project root that the agent reads automatically.

**Critical cross-environment rule:** Always verify that your schema file is being read by the agent. On first session, ask: "Confirm you've read the schema file and describe the ingest workflow it defines." If the agent can't answer, the schema filename is wrong.

## CRITICAL — LLM Wiki Setup Rules

ALWAYS paste the full llm-wiki.md verbatim — never summarize or truncate.
ALWAYS declare your topic in one precise sentence before any other context.
ALWAYS name your agent platform (Claude Code / Codex / OpenCode) explicitly.
ALWAYS have at least one source file ready before requesting setup.
ALWAYS include "walk me through first ingest" to activate interactive coaching mode.
NEVER specify exact frontmatter fields — describe domain goals and let the agent derive fields.
NEVER batch-ingest multiple sources in the first session before reviewing the schema output.
PREFER "setup + first ingest" as a single prompt over two separate requests.
REQUIRE git initialization in your setup request — include it explicitly.
ENSURE you request a schema file review before approving file writes.
INCLUDE your markdown viewer (Obsidian / VS Code) so the schema gets viewer-specific conventions.
AVOID topic declarations that could apply to any domain ("research", "notes", "business").
