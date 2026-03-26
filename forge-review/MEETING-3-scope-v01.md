# SPOTKANIE 3: "Scope v0.1 — co budujemy TERAZ?"
## Definicja MVP FORGE

> Symulacja zebrania zespołu FORGE Review Team
> Protokół: skrócony (constraint-driven)
> Data: 2026-03-26 (po Meeting 1 i 2)
> Kontekst: GO na prototyp, architektura Compiler+Selector, rule-based selection v0.1

---

## CONSTRAINT (VEGA otwiera)

**[VEGA]:** Zanim cokolwiek — ramy. Prototyp FORGE v0.1 musi:
1. Być **zbudowalny w ~2-3 godziny** (łącznie z testowaniem)
2. Być **użyteczny od pierwszej minuty** po zbudowaniu
3. Pokrywać **najczęstszy use case** (prompt generation)
4. Nie wymagać **instrukcji obsługi** — powinien być intuicyjny

Wszystko co nie mieści się w tych ramach — idzie do backlogu. Nie do v0.2, nie do "potem". Do BACKLOGU. Z priorytetem. Ale NIE budujemy tego teraz.

Zgoda?

**[Wszyscy]:** Zgoda.

---

## FEATURE AUCTION: Każdy nominuje max 3, broni

### [IRIS] nominuje:

**1. compile_context.py** — serce systemu. Bez tego "Context Engine" to prompt stuffing.
- Uzasadnienie: jedyne co transformuje FORGE z "Claude czyta pliki" w "deterministyczny system"
- Effort: ~1.5h (z edge cases, fallback dla free-form, token counting)
- Value: fundamentalna — wszystko inne zależy od tego

**2. A/B test framework** — 5 zadań, 3 warunki, automated scoring.
- Uzasadnienie: bez danych nie wiemy czy system działa
- Effort: ~1h (skrypt + prompty testowe)
- Value: validacyjna — decyduje o przyszłości FORGE

**3. Compiled output z attention markers** — sekcje CRITICAL na końcu.
- Uzasadnienie: exploiting recency bias to free improvement
- Effort: ~15 min (w ramach compile_context.py)
- Value: quality improvement at zero cost

### [KAEL] nominuje:

**1. Bazowe pliki kontekstu** — minimum 3: root, creative, jeden target.
- Uzasadnienie: kompilator bez plików do kompilowania jest bezużyteczny
- Effort: ~45 min (3 pliki × 15 min)
- Value: fundamentalna — treść systemu

**2. _index.md** — indeks wszystkich kontekstów z metadanymi.
- Uzasadnienie: nawet przy 5 plikach — indeks daje overview i jest przyszłościowy
- Effort: ~15 min (ręcznie dla v0.1)
- Value: organizacyjna + przygotowanie pod tag-based selection v0.2

**3. Format .ctx.md ze strict rules** — template z @meta i section directives.
- Uzasadnienie: jeśli nie ustalimy formatu od dnia zero, rozbieżność rośnie
- Effort: ~15 min (jeden template file)
- Value: standardyzacyjna

### [NOVA] nominuje:

**1. compile_context.py** — zgadzam się z IRIS, to must-have #1. Dodam: piszę to jako narzędzie CLI z clear interface.
```bash
python compile_context.py master.ctx.md targets/veo3.ctx.md -o .cache/compiled.ctx.md
```
- Effort: ~1.5h (z token counting, fallback, error handling)

**2. Orchestrator SKILL.md** — bez niego FORGE się nie triggeruje.
- Uzasadnienie: wejście do systemu. Musi mieć routing table i snapshot stanu.
- Effort: ~30 min (minimalistyczny, ale functional)
- Value: krytyczna — brama do systemu

**3. Folder structure + .cache/** — fizyczna struktura projektu.
- Uzasadnienie: foldery muszą istnieć zanim cokolwiek zadziała
- Effort: ~10 min (mkdir + README)
- Value: infrastrukturalna

### [ORION] nominuje:

**1. Prompt-Smith instrukcje** — to jest #1 use case. User chce generować prompty.
- Uzasadnienie: bez Prompt-Smitha FORGE nie ma powodu do istnienia w v0.1
- Effort: ~30 min (instrukcja .md z workflow)
- Value: najwyższa — core use case

**2. Rating mechanism** — choćby `quality: 8/10` w headerze zapisywanych promptów.
- Uzasadnienie: bez ratingu Arsenal nie rozróżnia dobrego od złego. Feedback = learning.
- Effort: ~5 min (konwencja w template, zero kodu)
- Value: foundational dla przyszłej ewolucji

**3. Narrative context format** — konteksty jako "świat w którym działasz", nie imperatywy.
- Uzasadnienie: LLM lepiej reaguje na narratives niż rule lists
- Effort: ~0 min dodatkowych (to jest kwestia STYLU pisania kontekstów, nie kodu)
- Value: jakościowa — better context = better output

### [VEGA] nominuje:

**1. Quickest Path Rule** — jawna definicja KIEDY używać FORGE, a kiedy nie.
- Uzasadnienie: jeśli user nie wie kiedy system pomaga — będzie frustrowany
- Effort: ~10 min (sekcja w Orchestrator SKILL.md)
- Value: adoption — zapobiega frustration from overhead

```markdown
## When to use FORGE
- Complex prompts requiring domain knowledge → YES
- Repeated operations with known targets → YES
- Quick one-off prompt → NO, just ask Claude directly
- Exploring new AI model → NO, experiment first, codify later
```

**2. Complexity budget** — max 10 plików .ctx.md, max 20 artefaktów w arsenale na start.
- Uzasadnienie: hard limits zapobiegają rozrostowi
- Effort: ~5 min (reguła w README)
- Value: sustainability

**3. 30-day checkpoint template** — prosty formularz ewaluacyjny.
- Uzasadnienie: ustaliliśmy kill switch. Potrzebujemy narzędzia do oceny.
- Effort: ~10 min (markdown template)
- Value: accountability

---

## PRIORITIZATION — MoSCoW

**[VEGA]** prowadzi: Układamy to. Każdy item — głosujemy: Must/Should/Could/Won't.

### MUST HAVE (v0.1 — bez tego nie ruszamy):

| # | Feature | Champion | Effort | Głosy |
|---|---------|----------|--------|-------|
| M1 | **compile_context.py** — deterministyczny kompilator | IRIS, NOVA | 1.5h | 5/5 ✓ |
| M2 | **3 bazowe pliki .ctx.md** (root + creative-base + veo3-target) | KAEL | 45min | 5/5 ✓ |
| M3 | **Prompt-Smith instrukcja** (.md z workflow) | ORION | 30min | 5/5 ✓ |
| M4 | **Orchestrator SKILL.md** (z routing table) | NOVA | 30min | 5/5 ✓ |
| M5 | **Folder structure** (forge/ z podfolderami) | NOVA | 10min | 5/5 ✓ |
| M6 | **Format .ctx.md template** (standard) | KAEL | 15min | 5/5 ✓ |

**Estimated total: ~3h 10min**

**[VEGA]:** Przekraczamy 2h constraint. Co tniesz?

**[NOVA]:** compile_context.py w 1.5h to pesymistyczny estimate. Realistycznie 1h jeśli zacznę od core i dodam edge cases later. Happy path first.

**[KAEL]:** 3 pliki kontekstu — mogę napisać szkielety w 30 min zamiast 45. Treść rozwiniemy iteracyjnie.

**[VEGA]:** OK. Revised: ~2h 30min. Akceptuję z marginesem.

### SHOULD HAVE (v0.1 jeśli zmieścimy się w czasie):

| # | Feature | Champion | Effort | Głosy |
|---|---------|----------|--------|-------|
| S1 | **Quickest Path Rule** w Orchestrator | VEGA | 10min | 5/5 ✓ |
| S2 | **_index.md** (konteksty + arsenal) | KAEL | 15min | 4/5 (VEGA: "nice-to-have") |
| S3 | **Rating convention** (quality: X/10 w artefaktach) | ORION | 5min | 4/5 (IRIS: "dodaj po A/B teście") |
| S4 | **Compiled output z recency markers** | IRIS | 0min* | 5/5 ✓ |

*S4 = 0min bo jest częścią compile_context.py

### COULD HAVE (v0.2):

| # | Feature | Champion | Rationale |
|---|---------|----------|-----------|
| C1 | A/B test framework | IRIS | Ważne, ale AFTER prototyp działa |
| C2 | Tag-based selector | ORION | Upgrade z manual selection |
| C3 | Feedback loop | ORION | Rating → analysis → context update |
| C4 | Arsenal auto-surfacing | ORION | Suggestions na starcie sesji |
| C5 | Conflict detection w kompilatorze | KAEL | Warning system |
| C6 | Session snapshot | NOVA | Auto-update SKILL.md |
| C7 | Staleness detection | VEGA | Date-based warnings |
| C8 | 30-day checkpoint | VEGA | Ewaluacja |

### WON'T HAVE (backlog, nie planujemy kiedy):

| # | Feature | Reason |
|---|---------|--------|
| W1 | Skill-Smith | Duplikacja skill-creator |
| W2 | Tool-Smith | Zbyt niche na start |
| W3 | Agent-Smith | Zbyt niche na start |
| W4 | Lab / Experiments framework | Złożoność bez dowodu wartości |
| W5 | Journal / Notion integration | Zewnętrzne zależności |
| W6 | Jam mode (3-wariantowy) | Złożoność subagentowa |
| W7 | Multiple registered skills | Jeden orchestrator wystarczy na start |
| W8 | Cross-project deployment | Żaden inny projekt jeszcze nie istnieje |

---

## BUILD PLAN

**[NOVA]** prowadzi — dependency graph i kolejność budowy:

```
KROK 1 (parallel):
├── [NOVA] compile_context.py              → 1h
└── [KAEL] 3 pliki .ctx.md + template      → 30min

KROK 2 (zależy od Kroku 1):
├── [NOVA] Folder structure + .cache/      → 10min
└── [ORION] Prompt-Smith instruction       → 30min

KROK 3 (zależy od Kroku 1-2):
└── [NOVA] Orchestrator SKILL.md           → 30min
    (routing table wymaga znajomości plików)

KROK 4 (validation):
└── [IRIS] Smoke test — end-to-end flow    → 20min
    (user → orchestrator → compile → prompt-smith → output)

KROK 5 (polish):
├── [VEGA] Quickest Path Rule              → 10min
├── [KAEL] _index.md                       → 15min
└── [ORION] Rating convention              → 5min
```

**Total estimated: 2h 30min — 3h**
**Critical path: compile_context.py → orchestrator → smoke test**

---

## DEFINITION OF DONE (v0.1)

**[IRIS]** definiuje:

FORGE v0.1 jest DONE gdy:

1. ✅ User pisze "potrzebuję prompt do Veo3 — kot w kosmosie"
2. ✅ Orchestrator triggeruje się (lub user mówi "forge:")
3. ✅ Kompilator scala master.ctx.md + veo3.ctx.md → compiled.ctx.md
4. ✅ Claude czyta compiled.ctx.md + prompt-smith.md
5. ✅ Claude generuje prompt WYRAŹNIE lepszy niż bez kontekstu
6. ✅ Prompt opcjonalnie zapisywany do arsenal/ z ratingiem

**End-to-end flow time: < 30 sekund** (od zapytania do gotowego prompta)

**[VEGA]** dodaje:
7. ✅ User rozumie KIEDY użyć FORGE, a kiedy pisać prompt sam (Quickest Path Rule)
8. ✅ Żaden krok nie wymaga czytania dokumentacji

---

## ZAMKNIĘCIE: Zobowiązania

**[NOVA]:** Buduję compile_context.py + folder structure + orchestrator SKILL.md.
**[KAEL]:** Piszę 3 pliki .ctx.md + format template + _index.md.
**[ORION]:** Piszę Prompt-Smith instruction + narrative context guidelines + rating convention.
**[IRIS]:** Projektuję smoke test + przygotowuję design A/B testu (do v0.2).
**[VEGA]:** Piszę Quickest Path Rule + complexity budget + 30-day checkpoint template (do v0.2).

---

*Meeting 3 — ZAKOŃCZONE*
*Czas: 38 minut (symulacja)*
*Decyzja: 6 Must-Have features, build plan z dependency graph, Definition of Done*
