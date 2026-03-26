# FORGE Review — Agenda & Scenariusze Spotkań

> Dokument sterujący przebiegiem spotkań zespołu FORGE Review Team.
> Zawiera 3 gotowe scenariusze spotkań + syntezę punktów zapalnych.

---

## PODSUMOWANIE NIEZALEŻNYCH ANALIZ

### Oceny zbiorcze

```
IRIS  (Prompt Engineering):     4.0 / 10
KAEL  (Context Architecture):   4.6 / 10
NOVA  (Cowork Implementation):  4.4 / 10
ORION (Creative Strategy):      4.8 / 10
VEGA  (Devil's Advocate):       3.4 / 10
─────────────────────────────────────────
ŚREDNIA:                        4.24 / 10
```

### Mapa konsensusów i konfliktów

**KONSENSUS (4/5 lub 5/5 zgadza się):**
1. Context Engine potrzebuje literalnej kompilacji (skrypt Python), nie "Claude merguje w głowie" — IRIS, KAEL, NOVA, ORION
2. Brak mechanizmu A/B testowania to critical gap — IRIS, KAEL, VEGA
3. Arsenal bez indeksu i surfacingu stanie się graveyard — NOVA, ORION, VEGA
4. System overhead musi być mniejszy niż direct approach dla >50% use cases — VEGA (pozostali nie komentowali explicite, ale implikują)

**OTWARTE KONFLIKTY:**
1. **Inheritance vs. Composition vs. Emergence**
   - KAEL: Utrzymaj inheritance, ale z max depth=3 i conflict detection
   - ORION: Zamień na adaptive composition (relevance-based ranking)
   - VEGA: Zacznij od flat, dodaj złożoność gdy ból realny
   - IRIS: Obojętne — ważny jest compiled output, nie mechanizm

2. **Scope v0.1 — ile budować?**
   - VEGA: Minimum Viable (1 flat context + Prompt-Smith + folder)
   - NOVA: Lite (Prompt-Smith + compile script + arsenal index)
   - KAEL/IRIS: Moderate (2-level inheritance + Prompt-Smith + compiled output)
   - ORION: Full but different (adaptive composition + feedback loop + jam mode)

3. **Skill registration strategy**
   - NOVA: Multiple narrow skills (forge-prompt, forge-factory, forge-lab)
   - Reszta: Jeden orchestrator (ale z lepszym triggering)

4. **Metafora fundamentalna**
   - Architektura: "Context as Code"
   - ORION: "Context as Landscape" — narracja > imperatywy
   - VEGA: "Context as Suggestion" — probabilistic, nie deterministic

---

## SCENARIUSZ SPOTKANIA 1: "Czy budujemy?"
**Cel:** Decyzja go/no-go dla FORGE
**Czas:** 45-60 minut
**Kluczowe pytanie:** Czy wielopoziomowe dziedziczenie kontekstów daje mierzalnie lepsze wyniki niż flat prompt?

### Agenda

**1. VEGA otwiera (5 min)**
Przedstawia ROI analysis z jej raportu. 10h inwestycji, 4h/miesiąc maintenance, break-even przy 48 złożonych operacjach/miesiąc. Stawia pytanie: "Czy jesteśmy pewni, że to się opłaci?"

**2. IRIS kontruje dane (10 min)**
Proponuje design eksperymentu A/B: 10 zadań, flat vs. inheritance, ślepa ocena. Definiuje metryki sukcesu. Argumentuje, że BEZ danych decyzja jest spekulacją.

**3. ORION reframing (10 min)**
Proponuje, że pytanie "inheritance vs flat" jest ŹLEDNE. Prawdziwe pytanie: "jak dać Claude NAJLEPSZY kontekst dla konkretnego zadania?" Inheritance to jedna odpowiedź. Adaptive composition to inna. Flat to trzecia. Testujmy WSZYSTKIE.

**4. KAEL gruntuje dyskusję (10 min)**
Przedstawia token budget analysis. Pokazuje, że overhead jest akceptowalny tokenowo, ale problematyczny kognitywnie (7 fragmentów vs 1 dokument). Proponuje pre-compilation jako test — jeśli skompilowany kontekst > flat, FORGE ma sens.

**5. NOVA reality-check (5 min)**
Mówi: "Mogę zbudować prototyp compile_context.py w 30 minut. Mogę zbudować A/B test framework w godzinę. Zróbmy to zamiast debatować."

**6. Decyzja (10 min)**
Team głosuje: Build prototype + run A/B test BEFORE full build? Albo go ahead?

### Oczekiwane outcomes:
- Decyzja: prototyp + test, albo full build
- Jeśli prototyp: design eksperymentu (IRIS prowadzi)
- Jeśli full build: scope v0.1 (VEGA jako strażnik scope)

---

## SCENARIUSZ SPOTKANIA 2: "Jak budujemy Context Engine?"
**Cel:** Decyzja architektoniczna o sercu systemu
**Czas:** 45-60 minut
**Kluczowe pytanie:** Jaki mechanizm doboru kontekstów najlepiej służy power userowi?

### Agenda

**1. Prezentacja 3 modeli (15 min)**

**Model A: Tree Inheritance** (obecna architektura, zmodyfikowana przez KAEL)
```
Struktura: root → category → specific
Max depth: 3
Mechanism: walk up tree, collect _.ctx.md
Compile: Python script → single output file
Conflict: detected and reported
```
Champion: KAEL
Critic: ORION ("zbyt sztywne")

**Model B: Adaptive Composition** (propozycja ORION)
```
Struktura: flat pool of tagged contexts
Mechanism: relevance ranking based on user intent + tags
Compile: top-3 by relevance → single output (recency order)
Conflict: natural (relevance = priority)
```
Champion: ORION
Critic: KAEL ("niedeterministyczne"), IRIS ("jak mierzysz relevance?")

**Model C: Minimum Flat** (propozycja VEGA)
```
Struktura: 1 master context + per-target overrides
Mechanism: load master + load target-specific
Compile: concatenation, target section overrides master
Conflict: impossible (2 files only)
```
Champion: VEGA
Critic: ORION ("nie skaluje się"), KAEL ("za proste")

**2. Cross-examination (15 min)**

IRIS → ORION: "Relevance ranking brzmi pięknie. Ale KTO rankuje? Claude? Na podstawie czego? Czy ranking jest powtarzalny?"

NOVA → KAEL: "Conflict detection wymaga porównania sekcji między plikami. To ile Read calls? Dla 4 plików z 5 sekcjami każdy — 20 porównań? Claude to ogarnie?"

VEGA → ORION: "Adaptive composition przy 50 kontekstach. Claude czyta _index.md z 50 wierszami, rankuje relevance, ładuje top-3. Ile to kosztuje vs. proste drzewo?"

KAEL → VEGA: "Model C z 2 plikami. Co gdy user pracuje z 8 targetami AI i każdy ma specyfikę kreatywną + techniczną? 16 plików target-specific, każdy z powtórzeniami?"

**3. Hybryda? (15 min)**

Prawdopodobnie żaden model nie wygra sam. Team szuka hybrydy:

```
Propozycja Kael-Orion:
- Flat pool z tagami (jak Model B)
- ALE z hierarchicznym fallback (jak Model A)
- I max 3 konteksty per operation (jak Model C)
- Kompilacja przez Python script (konsensus)
```

**4. Decyzja (10 min)**

### Oczekiwane outcomes:
- Wybrany model (lub hybryda) z uzasadnieniem
- Specyfikacja compile_context.py
- Definicja formatu plików .ctx.md
- Max limits (depth, files per operation, total files)

---

## SCENARIUSZ SPOTKANIA 3: "Scope v0.1 — co budujemy TERAZ?"
**Cel:** Zdefiniować MVP FORGE — minimum, które daje wartość
**Czas:** 30-45 minut
**Kluczowe pytanie:** Jaki jest NAJMNIEJSZY zestaw, który jest użyteczny?

### Agenda

**1. VEGA stawia constraint (5 min)**
"v0.1 musi być buildable w 2 godziny i usable od pierwszego dnia. Wszystko co nie spełnia tego kryterium — idzie do v0.2."

**2. Feature auction — każdy walczy o swoje (20 min)**

Każdy ekspert nominuje MAX 3 features do v0.1 i musi je obronić:

**IRIS nominuje:**
- Compiled context output (nie 7 plików, 1 plik)
- A/B test framework (nawet prosty: 5 zadań, 2 warianty)
- Routing table w orchestratorze (zamiast free-form)

**KAEL nominuje:**
- Context index (_index.md)
- Max depth = 3 rule
- Conflict detection (przynajmniej warning)

**NOVA nominuje:**
- compile_context.py (Python script)
- Session snapshot w SKILL.md
- Arsenal _index.md

**ORION nominuje:**
- Feedback mechanism (choćby prosty rating 1-5)
- Narrative context format (landscape, nie imperatywy)
- Jam mode stub (nawet jeśli niezaimplementowany — architektura powinna na to pozwalać)

**VEGA nominuje:**
- Quickest Path Rule (jasna definicja kiedy FORGE, kiedy bez)
- Complexity budget (max 15 plików .ctx.md na start)
- Staleness detection (data last-modified w indeksie)

**3. Prioritization — MoSCoW (10 min)**

Team wspólnie kategoryzuje:

```
MUST HAVE (v0.1):
  - ?

SHOULD HAVE (v0.1 jeśli czas):
  - ?

COULD HAVE (v0.2):
  - ?

WON'T HAVE (backlog):
  - ?
```

**4. Build plan (10 min)**
- Kto buduje co (które elementy wymagają Python, które to pliki .md)
- Kolejność (dependency graph)
- Definition of Done dla v0.1

### Oczekiwane outcomes:
- Lista features v0.1 (6-10 items)
- Build plan z kolejnością
- Jasne granice co NIE wchodzi do v0.1

---

## GORĄCE PYTANIA DO DYSKUSJI

Lista pytań, które mogą wywołać produktywny konflikt podczas spotkań:

1. "Czy ktokolwiek przetestował, że 4-level context inheritance daje lepsze wyniki niż 1 dobrze napisany plik?"

2. "Context Engine 'kompiluje' konteksty. Ale dekonstruując to: Claude czyta pliki i 'merguje w głowie'. Czy to kompilacja, czy prompt stuffing z ładną nazwą?"

3. "FORGE musi być SZYBSZY niż 'zrób to sam' dla >50% operacji. Czy jest?"

4. "Arsenal za 6 miesięcy będzie miał 80+ artefaktów. Jak je przeszukujesz? Filesystem to nie baza danych."

5. "Orchestrator koliduje z skill-creator przy triggerowaniu. Kto wygrywa?"

6. "Konteksty napisane w marcu 2026 opisują Veo3 z marca. W czerwcu Veo3 się zmieni. Kto aktualizuje 6 plików .ctx.md?"

7. "ORION mówi: 'Context as Landscape, nie Code'. Czy to zmienia architekturę, czy tylko styl pisania kontekstów?"

8. "VEGA pyta: za 3 miesiące, czy FORGE oszczędza czas? Jak zmierzymy?"

---

## INSTRUKCJE DLA PROWADZĄCEGO SPOTKANIE

### Rozpoczęcie
```
Przeprowadź zebranie zespołu FORGE Review Team.
Scenariusz: [1, 2, lub 3]
Przeczytaj pliki: FORGE-ARCHITECTURE.md, FORGE-REVIEW-TEAM.md
oraz odpowiednią perspektywę:
  01-IRIS, 02-KAEL, 03-NOVA, 04-ORION, 05-VEGA

Zasady:
- Każda persona mówi SWOIM głosem (nie generycznym "ekspertem")
- Stosuj WSZYSTKIE zasady anty-konfirmacyjne z FORGE-REVIEW-TEAM.md
- Oznaczaj kto mówi: [IRIS], [KAEL], [NOVA], [ORION], [VEGA]
- Nie dąż do sztucznego konsensusu
- Pozwól na produktywne napięcia
- Zakończ listą rekomendacji z podziałem głosów
```

### Śledzenie decyzji
Po każdym spotkaniu zapisz:
- Decyzje podjęte (z argumentacją)
- Otwarte konflikty (z pozycjami stron)
- Action items (z przypisaniem do person)
- Zmiana oceny po dyskusji (czy ktoś zmienił zdanie? dlaczego?)

---

*FORGE Review — Meeting Scenarios v1.0*
*Created: 2026-03-26*
