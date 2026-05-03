# FORGE

**Framework for Orchestrating Research, Generation & Engineering**

A personal AI prompt architecture system that treats accumulated knowledge as code. FORGE compiles model-specific context files into production-ready prompts — deterministically, every time.

---

## What is FORGE?

Most AI prompting is improvised. FORGE makes it systematic.

Instead of reinventing prompts from scratch, FORGE stores everything you've learned about each AI model (its strengths, failure modes, optimal structures, critical rules) in **context files**. When you need a prompt, a Python compiler merges the relevant files into a single knowledge package. Claude reads that package and generates a polished, production-ready prompt in seconds.

The result: your knowledge compounds. Every session builds on the last.

---

## Core Concepts

**Iceberg Design** — The infrastructure is invisible. On the surface: a natural conversation. Underneath: compiled knowledge from months of operational experience.

**Knowledge as Asset** — Context files are the real value of the system, not the prompts themselves. A great `.ctx.md` file is worth more than 100 individual prompts.

**Deterministic Compilation** — Same input files always produce the same compiled output. No probabilistic merging, no surprises.

**Arsenal as Memory** — Every saved, rated prompt is training data. The more you save, the better your pattern recognition becomes over time.

**Graceful Degradation** — FORGE never fails silently. If a target context is missing, it falls back to the master context. If compilation fails, it generates directly. You always get output.

---

## Architecture

```
User intent
     │
     ▼
┌─────────────────────────────┐
│  FORGE Orchestrator         │  ← Claude Code skill (SKILL.md)
│  - Identifies target AI     │
│  - Decides: compile or skip │
│  - Routes to Prompt-Smith   │
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│  Context Compiler           │  ← compile_context.py (Python)
│  - Merges .ctx.md files     │
│  - Resolves [OVERRIDE] &    │
│    [EXTEND] directives      │
│  - Outputs compiled context │
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│  Prompt-Smith               │  ← prompt-smith.md
│  - Reads compiled context   │
│  - Generates ONE prompt     │
│  - Offers arsenal save      │
└────────────┬────────────────┘
             │
             ▼
         Prompt
    (ready to paste)
```

**Two-layer design**: Selector (what to compile) + Compiler (how to merge). Swapping the selector (manual → tag-based → adaptive) doesn't require rewriting the compiler.

---

## File Structure

```
forge/
├── core/
│   ├── compile_context.py     # Context compiler — merges .ctx.md files deterministically
│   ├── forge-init.sh          # Session init — scans state, reports available contexts
│   └── prompt-smith.md        # Prompt generation instructions for Claude
├── contexts/
│   ├── _index.md              # Context registry (auto-maintained)
│   ├── _template.ctx.md       # Template for creating new contexts
│   ├── master.ctx.md          # Universal baseline — applies to ALL AI models
│   └── targets/
│       └── veo3.ctx.md        # Google Veo3 specific context
├── arsenal/
│   ├── _index.md              # Arsenal registry with ratings
│   └── prompts/
│       └── veo3-cosmic-cat.md # Example saved prompt (rated 9/10)
└── .cache/
    └── compiled.ctx.md        # Auto-generated output (gitignored)

.claude/
└── skills/forge/
    └── SKILL.md               # Claude Code skill entry point + orchestrator logic

FORGE-ARCHITECTURE.md          # Full system design document
FORGE-ARCHITECTURE-MAP.html    # Interactive architecture visualization
FORGE-REVIEW-TEAM.md           # Design review process & decisions
forge-review/                  # Detailed design meeting notes (4 sessions)
```

---

## Supported AI Targets

| Keyword(s) | Target | Status |
|-----------|--------|--------|
| `veo3`, `veo`, `google video` | Google Veo3 | v0.1 |
| `midjourney`, `mj` | Midjourney | context planned |
| `dalle`, `dall-e` | DALL-E | context planned |
| `stable diffusion`, `flux` | SD / Flux | context planned |
| `elevenlabs`, `voice`, `tts` | ElevenLabs | context planned |
| `sora`, `openai video` | Sora | context planned |
| `suno`, `udio`, `music` | Music generation | context planned |
| `runway`, `pika`, `kling` | Video tools | context planned |
| (unrecognized) | General | master.ctx.md only |

---

## Quick Start

### Prerequisites

- [Claude Code](https://claude.ai/code) installed
- Python 3.8+
- Bash (Git Bash on Windows works fine)

### Setup

```bash
git clone https://github.com/HjustonAI/AiForge.git
cd AiForge
```

No dependencies to install. The compiler uses only Python stdlib.

### Usage

FORGE runs inside Claude Code as a skill. Once Claude Code is open in this directory:

1. **Say anything that triggers FORGE:**
   - `"forge: cinematic shot of a whale breaching at golden hour, Veo3"`
   - `"make me a prompt for veo3 — cosmic cat in space"`
   - `"prompt do midjourney — brutalist architecture at night"`

2. **Claude will:**
   - Detect the target AI from your message
   - Compile the relevant context files
   - Generate a production-ready prompt
   - Ask if you want to save it to the arsenal with a 1-10 rating

3. **Power commands:**
   ```
   forge:status          — show system state (contexts, arsenal items)
   forge:list arsenal    — list all saved prompts with ratings
   forge:list contexts   — list all context files with tags
   forge:debug           — show last compilation details
   ```

### Running the compiler directly

```bash
# Compile master + veo3 context
python forge/core/compile_context.py --target veo3 -o forge/.cache/compiled.ctx.md

# Or specify files explicitly
python forge/core/compile_context.py forge/contexts/master.ctx.md forge/contexts/targets/veo3.ctx.md -o forge/.cache/compiled.ctx.md
```

---

## Adding a New Context

1. Copy the template:
   ```bash
   cp forge/contexts/_template.ctx.md forge/contexts/targets/[model-name].ctx.md
   ```

2. Fill in the model's strengths, limitations, optimal prompt structure, and CRITICAL rules.

3. Add it to the routing table in `.claude/skills/forge/SKILL.md`.

4. Update `forge/contexts/_index.md`.

---

## Philosophy

1. **Knowledge as Asset** — Context files outlive individual prompts. Invest in them.
2. **Iceberg Design** — 90% infrastructure, 10% visible. The conversation feels natural.
3. **Determinism > Probability** — Python compiler, not probabilistic Claude merging.
4. **Graceful Degradation** — Always produce output. Never fail silently.
5. **Progressive Complexity** — Start manual, add automation when the pain is real.
6. **Arsenal First** — Every saved prompt is data for future pattern learning.
7. **Context as Landscape** — Narrative descriptions beat dry instruction lists.

---

## Roadmap

| Version | Status | Features |
|---------|--------|---------|
| v0.1 | **Done** | Core compiler, Prompt-Smith, master + veo3 contexts, manual routing, arsenal index |
| v0.2 | Planned (if >3 uses/week) | A/B test framework, tag-based selector, 5-8 contexts, multi-variant mode |
| v0.3 | Conditional | Hybrid selector, context auto-evolution, Notion integration |
| v1.0 | Vision | Adaptive selector, full feedback loop, multi-Smith factory |
| v2 | Kickoff started | KMS framework, Compose/Distill/Deploy specs, meta prompt logging, inter-agent protocol, token strategy, phased implementation roadmap (`forge-review/FORGE-V2-IMPLEMENTATION-START.md`) |

**Kill switch:** If FORGE is used fewer than 3 times per week over 30 days, the system is discontinued. Simplicity wins.

---

## License

MIT — do whatever you want with it.
