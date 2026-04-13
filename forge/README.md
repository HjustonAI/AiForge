# FORGE — Personal AI Prompt Architect

> v0.3 | Global install at `C:/Users/Barte/00_aLearning`
> Skill file: `C:/Users/Barte/.claude/skills/forge/SKILL.md`

FORGE is a personal prompt architecture system. It generates production-ready prompts for AI models using accumulated operational knowledge stored in context files, and deploys knowledge systems (like Karpathy-style LLM Wikis) directly into project directories.

---

## Directory Structure

```
forge/
├── core/                        # System modules (internal)
│   ├── forge-init.sh            # Session warm-start snapshot
│   ├── compile_context.py       # Merges master + target context
│   ├── validate_context.py      # Checks .ctx.md structure + token budget
│   ├── arsenal-sync.py          # Detects ghost index entries
│   ├── chunk-reader.py          # Large file reader (>10k tokens)
│   ├── prompt-smith.md          # Prompt generation instructions
│   └── context-smith.md        # Context distillation instructions
│
├── contexts/                    # Knowledge assets (HOW to prompt each AI)
│   ├── master.ctx.md            # Universal rules — compiled into every prompt
│   ├── _template.ctx.md         # Blank template for new contexts
│   ├── _index.md                # Registry of all contexts + routing keywords
│   └── targets/
│       ├── veo3.ctx.md
│       ├── gemini-deep-research.ctx.md
│       ├── midjourney.ctx.md
│       ├── claude-cowork.ctx.md
│       └── llm-wiki.ctx.md      # How to craft Karpathy Wiki setup prompts
│
├── arsenal/                     # Memory (saved, rated prompts)
│   ├── _index.md                # Registry of all saved prompts
│   └── prompts/
│       └── [target]-[name].md
│
├── seeds/                       # Deployable artifacts (canonical idea files)
│   └── llm-wiki.md              # Karpathy's full LLM Wiki gist (verbatim)
│
└── .cache/
    └── compiled.ctx.md          # Last compiled context (deterministic output)
```

---

## Three Storage Categories

| Category | Directory | Purpose | Who modifies |
|----------|-----------|---------|--------------|
| **Contexts** | `contexts/targets/` | Operational knowledge: how to prompt a specific AI | Context-Smith (distill) |
| **Arsenal** | `arsenal/prompts/` | Memory: saved prompts with quality ratings | User approval → auto-save |
| **Seeds** | `seeds/` | Deployable artifacts: canonical idea files for system setup | Manual (add once, never edit) |

**Contexts** accumulate over time — each one makes FORGE smarter at prompting that AI.
**Arsenal** grows as prompts are rated and saved — enables pattern recognition across sessions.
**Seeds** are immutable references — FORGE reads them to bootstrap external projects.

---

## Modes

### PROMPT MODE (default)
Generate a production-ready prompt for an AI model.

**Trigger:** any request to create/generate/write a prompt, or `forge:prompt [target] [description]`

**Flow:**
1. Session Init (`forge-init.sh`)
2. Identify target → resolve context files
3. Compile: `master.ctx.md` + `targets/[target].ctx.md`
4. Optional: check arsenal for high-rated reference prompts (quality ≥ 8)
5. Generate via Prompt-Smith
6. Offer to save to arsenal (user rates 1-10)

---

### DISTILL MODE
Create a new `.ctx.md` target context from research material.

**Trigger:** `forge:distill [target]`, "create context", or uploading research + asking to build context

**Flow:**
1. Gather source material (uploaded file or description)
2. Assess input quality: HIGH / MEDIUM / LOW + coverage %
3. Two-pass distillation (extraction notes → composition)
4. Validate + test compile
5. Generate one test prompt as quality proxy
6. On approval: save context, update `_index.md`

---

### WIKI DEPLOY MODE
Initialize a Karpathy-style LLM Wiki in the current project directory.

**Trigger:** `forge:wiki [topic]`, "set up an LLM wiki", "karpathy wiki", "build a wiki for [topic]"

**Flow:**
1. Capture CWD as `WIKI_DIR` (exception: `pwd` runs without FORGE root prefix)
2. 3-question wizard: domain / sources / agent platform
3. Read `forge/seeds/llm-wiki.md` + compile `llm-wiki` context
4. Generate plan: directory tree + full schema file (CLAUDE.md / AGENTS.md / OPENCODE.md)
5. **Show plan, wait for approval — never write before approval**
6. Execute: mkdir structure, write files, git init — all in `WIKI_DIR`
7. Guide first ingest interactively

**Key distinction from PROMPT MODE:** FORGE reads from its own root but writes to `WIKI_DIR` (the user's project directory). The `seeds/llm-wiki.md` eliminates the manual copy-paste step.

---

## Power User Commands

| Command | Mode | Action |
|---------|------|--------|
| `forge:prompt [target] [desc]` | Prompt | Explicit prompt generation |
| `forge:distill [target]` | Distill | Create new context from research |
| `forge:wiki [topic]` | Wiki Deploy | Bootstrap Karpathy wiki in CWD |
| `forge:validate [target]` | Utility | Run validator on existing context |
| `forge:debug` | Utility | Show last compilation details |
| `forge:status` | Utility | Full system state (runs forge-init.sh) |
| `forge:search [query]` | Utility | Search arsenal by keywords |
| `forge:list contexts` | Utility | List contexts with tags + token estimates |
| `forge:list arsenal` | Utility | List saved prompts with ratings |
| `forge:save` | Utility | Save last generated prompt to arsenal |
| `forge:template` | Utility | Show context template |
| `forge:sync` | Utility | Fix index/file mismatches |

---

## Context Routing Table

When a target is mentioned, FORGE auto-selects context files:

| Keywords | Target | Context files |
|----------|--------|---------------|
| veo3, veo, video google | veo3 | master + veo3.ctx.md |
| midjourney, mj, midja | midjourney | master + midjourney.ctx.md |
| dalle, dall-e, openai image | dalle | master + dalle.ctx.md |
| stable diffusion, sd, flux | sd-flux | master + sd-flux.ctx.md |
| gemini, deep research | gemini-deep-research | master + gemini-deep-research.ctx.md |
| elevenlabs, voice, tts | elevenlabs | master + elevenlabs.ctx.md |
| sora, openai video | sora | master + sora.ctx.md |
| suno, udio, music | music | master + music.ctx.md |
| runway, pika, kling | runway | master + runway.ctx.md |
| llm wiki, karpathy wiki, knowledge base | llm-wiki | master + llm-wiki.ctx.md |
| (none recognized) | general | master only |

---

## How to Add a New Context

1. Gather research material about the target AI (300+ lines = HIGH quality input)
2. Run: `forge:distill [target-name]`
3. Context-Smith runs two-pass distillation
4. Approve the output → auto-saved to `contexts/targets/[target].ctx.md`
5. `contexts/_index.md` and routing table in SKILL.md are updated automatically

**Token budget:** 1200–2000 tokens per context file. Compiled with master: 1800–2600 tokens.

---

## How to Add a New Seed

Seeds are canonical idea files — patterns or architectures that FORGE can deploy into projects.

1. Obtain the source document (ideally the original, verbatim)
2. Save to `forge/seeds/[name].md`
3. Create a matching context in `contexts/targets/[name].ctx.md` (via `forge:distill`)
4. Add a deploy mode section to SKILL.md (follow the WIKI DEPLOY WORKFLOW pattern)
5. Add the trigger keywords to MODE DETECTION in SKILL.md
6. Commit both files together

**Current seeds:**
| Seed | Source | Deployed by |
|------|--------|-------------|
| `llm-wiki.md` | Karpathy's GitHub gist (Apr 2026) | `forge:wiki [topic]` |

---

## Token Economics

| Component | Tokens (est.) |
|-----------|--------------|
| master.ctx.md | ~600 |
| target context (avg) | ~1800 |
| Compiled total | ~2400 |
| prompt-smith.md | ~800 |
| context-smith.md | ~1200 |
| forge-init.sh output | ~200 |
| **Full session overhead** | **~3400–4000** |

Arsenal references add ~300–500 tokens when a rated prompt (≥8/10) is found for the target.

---

## Version History

| Version | Changes |
|---------|---------|
| v0.1 | Initial system: contexts, arsenal, prompt generation |
| v0.2 | Compile gate (blocking), plan mode handling, large file chunking, coverage tracking, arsenal-aware generation, freshness checks |
| v0.3 | `seeds/` category, WIKI DEPLOY MODE, `forge:wiki` command, CWD-aware deployment, approval gate |
