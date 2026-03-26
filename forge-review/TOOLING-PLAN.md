# FORGE — Tooling & Implementation Plan

> Konkretna lista skilli, tooli, MCP, subagentów i mechanizmów do zbudowania.
> Wynik Meeting 1-4. Priorytetyzowana, z effort estimates.

---

## ZASADA PROJEKTOWA: Iceberg Design

```
User widzi:     Naturalną rozmowę z AI, który pamięta i uczy się
System robi:    Auto-routing, kompilacja, search, indexing, maintenance
```

---

## v0.1 — BUILD LIST (Cel: ~4-5h, użyteczne od pierwszej minuty)

### 1. SKILLS

#### `forge` — Orchestrator Skill
**Lokalizacja:** `.claude/skills/forge/SKILL.md`
**Trigger:** prompt do AI, tworzenie skilli/tooli/agentów, "forge:", praca z arsenałem
**Zawiera:**
- Routing table (target AI → context files) z aliases
- Quickest Path Rule (kiedy FORGE, kiedy direct)
- Auto-compilation flow (bash → compile → read → generate)
- Graceful fallback chain (no context? pracuj bez)
- forge:debug, forge:status commands
- Conversational save ("Zapisać? Ocena 1-10?")
- Session init (odpala forge-init.sh na starcie)

**Effort:** 1.5h
**Zależności:** compile_context.py, pliki kontekstu

---

### 2. TOOLS (Python/Bash scripts)

#### `compile_context.py` — Deterministyczny kompilator kontekstów
**Lokalizacja:** `forge/core/compile_context.py`
**Interface:**
```bash
# Jawne pliki:
python compile_context.py file1.ctx.md file2.ctx.md -o output.md

# Auto-select po target:
python compile_context.py --target veo3 -o output.md
# → czyta _index.md, znajduje pliki tagged "veo3", kompiluje
```

**Funkcjonalność:**
- Parsuje sekcje markdown (##)
- Rozpoznaje dyrektywy [OVERRIDE] i [EXTEND] w nagłówkach
- Merge: child wins by default, EXTEND appends
- Output z header (sources, timestamp) + sekcje generic→specific→CRITICAL
- Token count estimation (word count × 1.3)
- WARN jeśli >2500 tokenów
- Fallback: brak sekcji → concatenation
- Error handling: missing file → WARN + skip, circular → detect + abort

**Effort:** 2h
**Zależności:** pliki .ctx.md, _index.md

#### `forge-init.sh` — Session warm start
**Lokalizacja:** `forge/core/forge-init.sh`
**Funkcjonalność:**
- Liczy konteksty, artefakty w arsenale
- Pokazuje ostatnio modyfikowane pliki
- Flaguje stale contexts (>30 dni)
- Pokazuje last 5 arsenal items
- Output: zwięzły snapshot do kontekstu sesji

**Effort:** 20min
**Zależności:** folder structure

#### `arsenal-search.py` — Wyszukiwanie w arsenale
**Lokalizacja:** `forge/core/arsenal-search.py`
**Interface:**
```bash
python arsenal-search.py "veo3 space"
python arsenal-search.py --target veo3 --min-quality 7
python arsenal-search.py --recent 5
```
**Funkcjonalność:**
- Przeszukuje _index.md po keywords, tags, quality
- Sortuje po relevance/quality/date
- Output: lista z rating + path + date

**Effort:** 45min
**Priorytet:** v0.2 (ale prosty — warto mieć wcześniej)

---

### 3. PLIKI KONTEKSTU

#### `master.ctx.md` — Bazowy kontekst
**Lokalizacja:** `forge/contexts/master.ctx.md`
**Styl:** NARRATIVE ("Context as Landscape"), nie imperatywny
**Zawiera:**
- Filozofia tworzenia (ORION: "świat w którym działasz")
- Ogólne zasady promptów (specificity, sensory details, structure)
- Styl użytkownika (odkrywany iteracyjnie, na start: placeholder)
- Sekcja CRITICAL: najważniejsze patterns

**Effort:** 30min

#### `targets/veo3.ctx.md` — Target-specific (pierwszy)
**Lokalizacja:** `forge/contexts/targets/veo3.ctx.md`
**Zawiera:**
- Specyfika Veo3 (video gen, camera movements, lighting)
- Optymalna długość promptu
- Znane mocne/słabe strony
- Przykłady dobrych promptów
- Sekcja CRITICAL: "always include camera movement, lighting, pacing"

**Effort:** 20min

#### `_template.ctx.md` — Template formatu
**Lokalizacja:** `forge/contexts/_template.ctx.md`
**Zawiera:** pustą strukturę z @meta, sekcjami, dyrektywami

**Effort:** 10min

#### `_index.md` — Indeks kontekstów
**Lokalizacja:** `forge/contexts/_index.md`
**Zawiera:** tabela: name, path, tags, tokens, last-modified

**Effort:** 10min

---

### 4. INSTRUKCJE

#### `prompt-smith.md` — Instrukcja generowania promptów
**Lokalizacja:** `forge/core/prompt-smith.md`
**Zawiera:**
- Workflow: compiled context → analyze intent → generate → offer save
- Multi-variant stub (v0.1: single, v0.2: 3 variants)
- Save flow: "Zapisać? Ocena 1-10?"
- Format zapisu: YAML header (name, target, quality, date, tags) + prompt body
- Arsenal surfacing: "Masz X promptów do [target]. Najlepszy: Y."

**Effort:** 30min

---

### 5. FOLDER STRUCTURE

```bash
mkdir -p forge/{core,contexts/targets,arsenal/prompts,.cache}
```

**Effort:** 5min

---

### 6. POWER USER COMMANDS

Wbudowane w Orchestrator SKILL.md:

| Command | Działanie |
|---------|-----------|
| `forge:debug` | Pokaż last compilation: źródła, compiled output, token count |
| `forge:status` | Stan systemu: ile kontekstów, arsenal size, stale flags |
| `forge:prompt [target] [opis]` | Explicit prompt generation |
| `forge:search [query]` | Szukaj w arsenale |
| `forge:list contexts` | Lista kontekstów z tagami |
| `forge:list arsenal` | Lista artefaktów z ratingami |

**Effort:** Wbudowane w Orchestrator (0 dodatkowych)

---

## v0.2 — UPGRADE LIST (po A/B teście i 30-dniowym checkpoint)

### Skille / Rozszerzenia

| # | Element | Typ | Opis |
|---|---------|-----|------|
| 1 | **Multi-variant mode** | Prompt-Smith upgrade | 3 krótkie warianty → user wybiera → expand |
| 2 | **Proactive greeting** | Orchestrator upgrade | "Ostatnio Veo3. Kontynuujesz?" |
| 3 | **Auto-setup** | Orchestrator upgrade | First-run detection → create structure |

### Tools

| # | Element | Typ | Opis |
|---|---------|-----|------|
| 4 | **arsenal-search.py** | Python | Wyszukiwanie po keywords, tags, quality |
| 5 | **A/B test framework** | Python + Subagent | 10 tasks, 3 conditions, Claude-as-judge |
| 6 | **index-rebuild.py** | Python | Automatycznie regeneruj _index.md |

### Subagenci

| # | Element | Typ | Opis |
|---|---------|-----|------|
| 7 | **Pattern Extractor** | Subagent (weekly) | Czyta top-rated arsenal items → wyciąga patterns → zapisuje patterns.md |
| 8 | **Prompt Reviewer** | Subagent (on-demand) | Ocenia prompt jakościowo przed zapisem |

### Scheduled Tasks

| # | Element | Cron | Opis |
|---|---------|------|------|
| 9 | **forge-maintenance** | Niedziela 10:00 | Rebuild indexes, flag stale, archive unused |

### Dodatkowe konteksty

| # | Element | Opis |
|---|---------|------|
| 10 | targets/midjourney.ctx.md | Midjourney-specific |
| 11 | targets/gemini.ctx.md | Gemini Deep Research |
| 12 | targets/elevenlabs.ctx.md | Voice/audio generation |
| 13 | contexts/skill-creation.ctx.md | Kontekst dla tworzenia skilli |

---

## v0.3 — VISION LIST (jeśli v0.2 żyje)

### Integracje MCP

| # | Element | MCP | Opis |
|---|---------|-----|------|
| 1 | **Notion** | Notion MCP | Journal odkryć, knowledge base, workshop technik |
| 2 | **GitHub** | GitHub MCP | Versioning kontekstów i arsenału |

### Intelligence

| # | Element | Opis |
|---|---------|------|
| 3 | **Context auto-evolution** | Pattern analysis → proposed context updates → user confirms |
| 4 | **Adaptive selector** | Claude auto-picks contexts based on feedback history |
| 5 | **Sentiment rating** | Conversational sentiment → automatic quality score |
| 6 | **Arsenal intelligence** | Auto-surfacing, decay, "proven" badges |

### Visualization

| # | Element | Opis |
|---|---------|------|
| 7 | **HTML Dashboard** | Interaktywna mapa: konteksty, arsenal, patterns, history |
| 8 | **Evolution timeline** | Jak konteksty zmieniały się w czasie |

---

## BUILD SEQUENCE (v0.1)

```
KROK 1 (fundament):          ← ~2h
  ├── compile_context.py
  └── folder structure + bazowe pliki .ctx.md

KROK 2 (instrukcje):         ← ~1h
  ├── prompt-smith.md
  ├── _index.md + _template.ctx.md
  └── forge-init.sh

KROK 3 (entry point):        ← ~1.5h
  └── Orchestrator SKILL.md
      (routing table, quickest path, fallback, commands)

KROK 4 (validation):         ← ~30min
  └── End-to-end test: "prompt do Veo3 — kot w kosmosie"
      → triggeruje? → kompiluje? → generuje? → zapisuje?

TOTAL: ~5h (budowa) + ~30min (test)
```

---

## METRYKI SUKCESU

| Metryka | Target v0.1 | Jak mierzymy |
|---------|-------------|-------------|
| Time-to-Value | <20 sekund | Od requestu do gotowego prompta |
| Zero-config ops | >80% | Ile operacji NIE wymaga manual intervention |
| Trigger accuracy | >70% | Ile razy FORGE triggeruje się poprawnie |
| User satisfaction | >7/10 | Średni rating zapisanych promptów |
| Weekly usage | >3x | Kill switch metric |

---

*FORGE Tooling Plan v1.0*
*Output of Meetings 1-4*
*Created: 2026-03-26*
