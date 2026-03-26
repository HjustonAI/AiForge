# FORGE — Framework for Orchestrating Research, Generation & Engineering
## Architecture Document v0.1 (Post-Review)

> *"Knowledge as Asset, Pipeline as Infrastructure."*
> — Key insight from 4 review meetings with 5 expert personas

---

## 1. Wizja

FORGE to osobisty system zarządzania wiedzą operacyjną o narzędziach AI, z deterministycznym pipeline'em dostarczania tej wiedzy do Claude. To odpowiedź na pytanie: **jak sprawić, żeby Claude PAMIĘTAŁ co działa z Veo3, Midjourney, Gemini — i stosował tę wiedzę automatycznie?**

FORGE przenosi paradygmat vibe codingu na wszystko poza kodem: prompty, konteksty, wiedzę o modelach AI. Pliki kształtują zachowanie Claude tak jak kod źródłowy kształtuje zachowanie programu.

### Kluczowa analogia

```
┌─────────────────────┬──────────────────────────────┐
│   VIBE CODING       │   FORGE                      │
├─────────────────────┼──────────────────────────────┤
│ .cursorrules        │ Orchestrator SKILL.md        │
│ Kod źródłowy        │ Pliki kontekstu (.ctx.md)    │
│ Kompilator (build)  │ compile_context.py           │
│ /dist (output)      │ .cache/compiled.ctx.md       │
│ Biblioteki          │ Arsenal (saved prompts)      │
│ Klasy / interfejsy  │ Konteksty target-specific    │
│ package.json deps   │ Routing table (auto-select)  │
│ npm install         │ Auto-context resolution      │
│ Testy               │ A/B test framework (v0.2)    │
│ git log             │ Arsenal ratings + patterns   │
└─────────────────────┴──────────────────────────────┘
```

### Co się zmieniło vs. oryginalna wizja

Oryginalna architektura (rating 4.24/10) przeszła przez 4 spotkania review team z 5 ekspertami. Najważniejsze zmiany:

| Element oryginalny | Co się zmieniło | Dlaczego |
|---|---|---|
| Context Engine "kompiluje w głowie Claude" | Deterministyczny Python script | Determinizm > probabilizm |
| 4-level tree inheritance | Flat master + target-specific | Start simple, add when painful |
| Dyrektywy @override w komentarzach HTML | Dyrektywy w nagłówkach sekcji `## Tone [OVERRIDE]` | Bliżej treści = silniejszy wpływ |
| 4 Smiths (Prompt, Skill, Tool, Agent) | 1 Smith (Prompt-Smith) | Focus on #1 use case |
| Lab, Journal, Sandbox | WYCIĘTE z v0.1 | Unproven value |
| Arsenal z dual taxonomy | Prosty folder z _index.md | Filesystem is not a database |
| "Context as Code" | "Knowledge as Asset, Pipeline as Infrastructure" | Wiedza to prawdziwy asset |
| Brak feedback mechanism | Rating convention (quality: X/10) | Foundation for future learning |
| Brak limitów | Max 4 files, max 2500 tokens, depth 3 | Prevent uncontrolled growth |

**Wynikowy rating po rewizji: 6.5/10 (+53%)**

---

## 2. Zasada Projektowa: Iceberg Design

```
         ╱  Co user widzi  ╲
        ╱    Naturalną       ╲
       ╱     rozmowę          ╲
      ╱________________________╲
     ╱  Orchestrator + Routing  ╲
    ╱   Auto-compile + Fallback  ╲
   ╱  Arsenal search + Indexing   ╲
  ╱  Pattern extraction + Rating   ╲
 ╱  Scheduled maintenance + Snapshots╲
╱______________________________________╲
```

90% systemu jest pod wodą. User widzi naturalną konwersację z asystentem, który pamięta, uczy się, i produkuje wyniki. Cała mechanika — kompilator, konteksty, routing — jest NIEWIDOCZNA.

**"Invisible by default, transparent on demand, powerful when needed."**

---

## 3. Architektura Dwuwarstwowa

Kluczowa decyzja architektoniczna (jednogłośna, Meeting 2):

```
┌─────────────────────────┐
│    SELECTOR LAYER       │  ← Wymienny: manual → tag-based → adaptive
│    (dobiera pliki)      │     v0.1: routing table w Orchestratorze
├─────────────────────────┤
│    COMPILER LAYER       │  ← Stały: deterministyczny Python script
│    (merguje pliki)      │     compile_context.py — agnostyczny wobec organizacji
└─────────────────────────┘
```

**Kompilator** jest AGNOSTYCZNY wobec sposobu organizacji plików. Dostaje listę plików, merguje je deterministycznie, produkuje jeden output.

**Selector** jest WYMIENNY. Zmiana modelu organizacji nie wymaga zmiany kompilatora:
- v0.1: Rule-based manual (routing table w SKILL.md)
- v0.2: Tag-based (keyword matching na _index.md)
- v0.3: Hybrid (Claude suggests + user confirms)
- v1.0: Adaptive (auto-select trained on feedback)

---

## 4. Struktura Systemu (v0.1 — zbudowany)

```
.claude/skills/forge/
└── SKILL.md                          ← Orchestrator (entry point)
                                         Routing table, Quickest Path Rule,
                                         fallback chain, power user commands

forge/
├── core/
│   ├── compile_context.py            ← Deterministyczny kompilator (Python)
│   ├── prompt-smith.md               ← Instrukcja generowania promptów
│   └── forge-init.sh                 ← Session warm start script
│
├── contexts/
│   ├── _index.md                     ← Indeks kontekstów (tags, tokens, dates)
│   ├── _template.ctx.md              ← Template formatu dla nowych kontekstów
│   ├── master.ctx.md                 ← Bazowy kontekst (narrative style)
│   └── targets/
│       └── veo3.ctx.md               ← Target-specific: Google Veo3
│
├── arsenal/
│   ├── _index.md                     ← Indeks artefaktów (name, quality, tags)
│   └── prompts/                      ← Zapisane prompty z ratingami
│       └── veo3-cosmic-cat.md        ← Przykład: prompt 9/10
│
└── .cache/
    └── compiled.ctx.md               ← Output kompilatora (nadpisywany)
```

**10 plików. 4 foldery. 1 Smith. Zero Lab.**
Porównanie z oryginalnym designem: ~25 plików, 6 folderów, 4 Smiths, Lab, Projects — redukcja 60%.

---

## 5. Kompilator — compile_context.py

### Format wejścia (.ctx.md)

```markdown
<!-- @meta
  name: veo3
  tags: [veo3, video, google]
  priority: 7
-->

## Sekcja normalna
Treść...

## Sekcja z nadpisaniem [OVERRIDE]
Ta sekcja zastąpi rodzicielską o tej samej nazwie.

## Sekcja z rozszerzeniem [EXTEND]
Ta treść zostanie DOŁĄCZONA do rodzicielskiej sekcji.

## CRITICAL — Najważniejsze reguły
Sekcje z CRITICAL w nazwie lądują na KOŃCU compiled output.
```

### Reguły merge

| Sytuacja | Zachowanie |
|----------|-----------|
| Ta sama nazwa sekcji, brak dyrektywy | Child wins (zastępuje) |
| Ta sama nazwa, `[OVERRIDE]` | Child wins (jawne) |
| Ta sama nazwa, `[EXTEND]` | Child content dołączony do parent |
| Nowa sekcja | Dodana do outputu |
| `_preamble` (tekst przed pierwszym ##) | Zawsze concatenacja |

### Format wyjścia (compiled.ctx.md)

```markdown
# Compiled Context: veo3
<!-- sources: master.ctx.md + veo3.ctx.md | compiled: 2026-03-26 21:30 -->

## [sekcje generic → specific, rosnący priorytet]

## CRITICAL — Universal Rules        ← na końcu
## CRITICAL — Veo3 Rules             ← najważniejsze = ostatnie (recency exploit)
```

**Recency exploit**: LLM przywiązuje większą wagę do treści na końcu kontekstu. Sekcje CRITICAL celowo lądują na końcu — najważniejsze reguły mają najsilniejszy wpływ.

### Interface

```bash
# Jawne pliki:
python compile_context.py master.ctx.md targets/veo3.ctx.md -o output.md

# Auto-select po target (czyta _index.md):
python compile_context.py --target veo3 -o output.md
```

### Limity (hard-coded)

- Max 4 source files per kompilacja
- Token estimation: words x 1.3
- WARN at 2500 tokens
- Missing file → WARN + skip (nie crash)
- No sections found → fallback do concatenation

---

## 6. Przepływ End-to-End

```
User: "Potrzebuję prompt do Veo3 — kot w kosmosie"
                    │
                    ▼
         ┌──────────────────┐
         │   ORCHESTRATOR   │  Routing table: "veo3" → [master, targets/veo3]
         │   (SKILL.md)     │  Quickest Path: complex request → use FORGE
         └────────┬─────────┘
                  │
                  ▼
         ┌──────────────────┐
         │    COMPILER      │  bash: python compile_context.py --target veo3
         │  (compile_       │        -o forge/.cache/compiled.ctx.md
         │   context.py)    │  Output: 1 file, ~1380 tokens, <100ms
         └────────┬─────────┘
                  │
                  ▼
         ┌──────────────────┐
         │  PROMPT-SMITH    │  Reads: compiled.ctx.md + prompt-smith.md
         │  (instruction)   │  Generates: optimized prompt for Veo3
         └────────┬─────────┘  Following: CRITICAL rules, structure, length
                  │
                  ▼
         ┌──────────────────┐
         │    ARSENAL       │  "Zapisać do arsenału? Ocena 1-10?"
         │    (save)        │  → forge/arsenal/prompts/veo3-cosmic-cat.md
         └──────────────────┘
```

**Czas end-to-end: <30 sekund** (init: 30ms, compile: 60ms, reszta = generowanie przez Claude)

---

## 7. Quickest Path Rule

Nie każde zadanie wymaga FORGE. System SAM decyduje:

```
SKIP kompilację (direct generation) gdy:
  - Request jest krótki (<15 słów) i prosty
  - User mówi "szybki prompt" lub "quick"
  - Request = edycja istniejącego prompta

USE full FORGE gdy:
  - Target AI jest w routing table I kontekst istnieje
  - Request jest złożony (>15 słów, multiple requirements)
  - User mówi "forge:" lub "użyj kontekstu"

Zasada: gdy wątpliwość — kompiluj. Overhead to <2 sekundy.
```

---

## 8. Graceful Fallback Chain

FORGE nigdy nie failuje. Zawsze produkuje output:

```
1. Próbuj: resolve target → compile context → generate z full knowledge
2. Jeśli target context brak: compile master only → generate z bazową wiedzą
3. Jeśli master brak: generate bezpośrednio → Claude's general knowledge
4. NIGDY nie pokazuj errora. ZAWSZE produkuj prompt.
```

Gorszy prompt bez kontekstu > żaden prompt z errorem.

---

## 9. Jak korzystać z FORGE

### Pierwszy raz — po prostu zacznij mówić

```
Ty:    "Zrób mi prompt do Veo3 — wilk w mglistym lesie o świcie"
FORGE:  [triggeruje się automatycznie → kompiluje kontekst → generuje]

        Cinematic wide shot, pre-dawn mist. A lone grey wolf stands
        motionless at the edge of an ancient pine forest, its breath
        visible in the cold air. Slow dolly forward through hanging
        fog layers, each one catching the first pale golden light
        filtering through the canopy. Dew drops on pine needles
        glisten as the camera passes. The wolf turns its head slowly,
        amber eyes catching the light. Shallow depth of field,
        muted forest greens with warm amber highlights from the
        rising sun. Ethereal, reverent pacing.

        Zapisać do arsenału? Ocena 1-10?

Ty:    "9, zapisz"
FORGE:  [zapisuje do forge/arsenal/prompts/veo3-misty-wolf.md]
```

**Zero konfiguracji. Zero pytań o konteksty. Po prostu intencja → wynik.**

### Codzienne użycie

```
Ty:    "Coś do Midjourney, portret w stylu Caravaggio"
FORGE:  [kompiluje master + targets/midjourney → generuje]

Ty:    "Daj mi prompt do ElevenLabs — narrator dokumentalny, głęboki bas"
FORGE:  [kompiluje master + targets/elevenlabs → generuje]

Ty:    "Szybki prompt Veo3: zachód słońca nad morzem"
FORGE:  [Quickest Path: prosty request → generuje BEZ kompilacji]
```

### Power User Commands

```
forge:debug          → co system zrobił: źródła, compiled output, token count
forge:status         → stan systemu: ile kontekstów, arsenal size, stale flags
forge:list contexts  → lista kontekstów z tagami
forge:list arsenal   → lista promptów z ratingami
forge:search [query] → szukaj w arsenale
forge:save           → zapisz ostatni prompt do arsenału
forge:template       → pokaż template do tworzenia nowych kontekstów
```

### Dodawanie nowego kontekstu (nowy model AI)

```
Ty:    "forge:template"
FORGE:  [pokazuje _template.ctx.md]

Ty:    "Stwórz kontekst dla Midjourney na podstawie tego template"
FORGE:  [tworzy forge/contexts/targets/midjourney.ctx.md]
        [aktualizuje _index.md]
        Gotowe. Od teraz prompty do Midjourney będą korzystać
        z dedykowanego kontekstu.
```

### Budowanie arsenału

Każdy zapisany prompt to knowledge asset. Im więcej promptów z ratingami, tym lepsze wzorce system wykryje (v0.2+):

```
arsenal/prompts/
├── veo3-cosmic-cat.md        (9/10)
├── veo3-misty-wolf.md        (9/10)
├── veo3-underwater-city.md   (7/10)
├── midjourney-caravaggio.md  (8/10)
└── elevenlabs-narrator.md    (8/10)
```

---

## 10. Konteksty — Knowledge as Landscape

Konteksty pisane są w stylu NARRACYJNYM (nie imperatywnym). Zamiast suchych list reguł — opisują "krajobraz" w którym Claude operuje.

**Dlaczego?** LLM lepiej reagują na narrację niż na instrukcje. "Veo3 myśli w SCENACH, nie w klatkach" to lepszy kontekst niż "Pamiętaj: Veo3 generuje wideo scena po scenie."

Struktura każdego kontekstu:

```markdown
<!-- @meta: name, tags, priority -->

## [Model] Landscape          — czym jest ten model, jak myśli
## Prompt Structure [OVERRIDE] — optymalna architektura prompta
## Known Strengths             — co model robi dobrze
## Known Limitations           — czego unikać
## Optimal Length              — sweet spot w słowach
## Style Anchoring             — co działa: referencje, style, nazwiska
## CRITICAL — [Model] Rules    — 5-7 najważniejszych zasad (na końcu!)
```

---

## 11. Roadmapa Ewolucji

```
v0.1 ★ ZBUDOWANE ★
├── compile_context.py (deterministyczny kompilator)
├── Prompt-Smith (jedyny smith)
├── 2 konteksty (master + veo3)
├── Manual selection (routing table)
├── Arsenal z prostym indeksem
├── Quickest Path Rule
├── Graceful Fallback Chain
└── Power user commands

v0.2 (po 30-dniowym checkpoint — jeśli >3 użycia/tydzień)
├── A/B test framework (empiryczna walidacja)
├── Tag-based selector (keyword matching)
├── 5-8 kontekstów (midjourney, dalle, gemini, elevenlabs...)
├── Multi-variant mode (3 krótkie → pick → expand)
├── Pattern Extractor subagent (weekly, async)
├── arsenal-search.py (wyszukiwanie po keywords/quality)
├── forge-maintenance scheduled task (weekly cleanup)
└── Proactive session greeting

v0.3 (jeśli v0.2 żyje)
├── Hybrid selector (Claude suggests + user confirms)
├── Context auto-evolution (patterns → proposed updates)
├── Sentiment-based rating (conversational → automatic score)
├── Notion MCP integration (journal, knowledge base)
└── HTML dashboard (arsenal/context visualization)

v1.0 (wizja)
├── Adaptive selector (auto-select trained on feedback)
├── Full feedback loop (arsenal → analysis → context → better prompts)
├── Multi-Smith factory (skill, tool, agent)
└── Plugin-ready architecture
```

**Zasada: każda wersja jest SELF-CONTAINED.** Jeśli v0.2 nigdy nie powstanie — v0.1 wciąż działa i daje wartość.

---

## 12. Filozofia Projektowa (po rewizji)

1. **Knowledge as Asset, Pipeline as Infrastructure** — Treść kontekstów to prawdziwy asset. Kompilator, selector, routing — to mechanika dostarczania. Ważna, ale służebna.

2. **Iceberg Design** — 90% systemu pod wodą. User widzi naturalną rozmowę, nie architekturę.

3. **Determinism over Probability** — Kompilator Python, nie "Claude merge w głowie". Same input → same output. Zawsze.

4. **Graceful Degradation** — Nigdy nie failuj. Gorszy output bez kontekstu > żaden output z errorem.

5. **Quickest Path** — Proste zadania = direct. Złożone = FORGE. System sam decyduje.

6. **Progressive Complexity** — Zacznij od manual. Dodaj inteligencję gdy ból jest realny, nie gdy architekt mówi "trzeba".

7. **Arsenal First** — Każdy prompt z ratingiem to data point. Im więcej data points, tym lepsze patterns. Im lepsze patterns, tym lepsze konteksty. Samonapędzający się cykl.

8. **Context as Landscape** — Konteksty to narracje, nie instrukcje. Opisuj świat, w którym Claude operuje.

---

## 13. Kill Switch

**Metryka:** <3 użycia FORGE tygodniowo przez 30 dni = kill.

Jeśli FORGE nie daje wartości ponad "Claude bez kontekstu" — nie ma sensu go utrzymywać. A/B test (v0.2) empirycznie zweryfikuje czy system wart jest dalszego rozwoju.

---

## 14. Metryki Sukcesu

| Metryka | Target v0.1 | Jak mierzymy |
|---------|-------------|-------------|
| Time-to-Value | <20 sekund | Od requestu do gotowego prompta |
| Zero-config ops | >80% | Ile operacji NIE wymaga manual intervention |
| Trigger accuracy | >70% | Ile razy FORGE triggeruje się poprawnie |
| User satisfaction | >7/10 | Średni rating zapisanych promptów |
| Weekly usage | >3x | Kill switch metric |

---

*FORGE Architecture Document v0.1 (Post-Review)*
*4 meetings, 5 expert perspectives, 209 minut symulacji*
*Original rating: 4.24/10 → Revised: 6.5/10 (+53%)*
*Built and tested: 2026-03-26*
