# SPOTKANIE 2: "Jak budujemy Context Engine?"
## Decyzja architektoniczna o sercu systemu

> Symulacja zebrania zespołu FORGE Review Team
> Protokół: pełny (Fazy 1-5)
> Data: 2026-03-26 (bezpośrednio po Meeting 1)
> Kontekst: Zespół zdecydował GO na prototyp. Teraz decydujemy JAK.

---

## FAZA 1: Pozycje wyjściowe

Każdy ekspert deklaruje swój preferowany model PRZED dyskusją:

**[IRIS]:** "Nie obchodzi mnie czy drzewo czy flat. Obchodzi mnie: (1) compiled output — jeden plik, (2) attention markers — najważniejsze na końcu, (3) mierzalność — wiem czy działa."

**[KAEL]:** "Model A: Tree Inheritance, ale z max depth 3, conflict detection, i auto-indeksem. Drzewo daje deterministyczny path resolution."

**[NOVA]:** "Model pragmatyczny: cokolwiek, co da się zaimplementować w compile_context.py z czystą logiką. Jeśli reguły merge nie zmieszczą się na jednej stronie — za skomplikowane."

**[ORION]:** "Model B: Adaptive Composition. Flat pool z tagami, relevance ranking, top-N selection. Pasuje do tego JAK modele przetwarzają informację."

**[VEGA]:** "Model C: Minimum Flat. Master file + target overrides. Dwa pliki per operacja, zero komplikacji. Udowodnijcie, że potrzebujecie więcej."

---

## FAZA 2: Prezentacja trzech modeli

### [KAEL] prezentuje Model A: Tree Inheritance

```
contexts/
├── _.ctx.md                     ← ROOT
├── creative/
│   ├── _.ctx.md                 ← creative base
│   └── visual/
│       ├── _.ctx.md             ← visual base
│       └── video-gen.ctx.md     ← leaf
└── technical/
    ├── _.ctx.md
    └── prompt-eng.ctx.md
```

Algorytm resolution: od leaf w górę, zbieramy _.ctx.md aż do root. Kompilator (Python) merguje deterministycznie. Reguły:
- Identyczne nazwy sekcji: child OVERRIDE (chyba że oznaczony @extend)
- Brak identycznej sekcji: APPEND z parent
- Max depth: 3 (root + category + specific)
- Conflict detection: kompilator WARN gdy dwie sekcje mają tę samą nazwę bez explicit dyrektywy

Zalety: deterministic path, czytelna hierarchia, DRY.
Wady: rigid taxonomy, cross-cutting wymaga multiple inheritance.

### [ORION] prezentuje Model B: Adaptive Composition

```
contexts/
├── _index.md                    ← indeks z tagami
├── creative-base.ctx.md         [tags: creative, base]
├── visual-patterns.ctx.md       [tags: creative, visual]
├── video-gen.ctx.md             [tags: creative, visual, video, veo3]
├── prompt-engineering.ctx.md    [tags: technical, prompts]
├── cinematic-style.ctx.md       [tags: creative, visual, style]
└── scientific-viz.ctx.md        [tags: technical, visual, science]
```

Algorytm: user intent → Context Engine czyta _index.md → rankuje konteksty po relevance → ładuje top-3 → kompilator merguje.

Zalety: handles cross-cutting naturalnie (scientific-viz ma tags technical + visual), brak diamond problem, flexible.
Wady: relevance ranking — kto i jak rankuje? Niedeterministyczne jeśli Claude rankuje.

### [VEGA] prezentuje Model C: Minimum Flat

```
contexts/
├── master.ctx.md                ← ALL shared knowledge
└── targets/
    ├── veo3.ctx.md              ← target-specific override
    ├── midjourney.ctx.md
    └── gemini.ctx.md
```

Algorytm: załaduj master + załaduj target. Dwa pliki. Koniec.

Zalety: zero komplikacji, zero bugów, natychmiast zrozumiałe.
Wady: master rośnie bez granic, brak reuse między targets, repetition.

---

## FAZA 3: Cross-Examination

**[IRIS] → [ORION]:**
Relevance ranking. Kto rankuje? Claude czyta _index.md z 20 wierszami, pattern-matchuje tagi na intencję użytkownika, wybiera top-3. Ale to jest FREE-FORM CLASSIFICATION. Claude może wybrać inny zestaw dla identycznej intencji w różnych sesjach. Jak zapewniasz powtarzalność?

**[ORION]:**
Nie zapewniam 100% powtarzalności. I twierdzę, że to ZALETA, nie wada. Claude dobierając konteksty na podstawie rozumienia intencji jest LEPSZY niż sztywny tree path. Analogia: dobry bibliotekarz poleca książki lepiej niż system Dewey'a. Ale — akceptuję kompromis. Dodajemy "recipe" override: user może jawnie wskazać konteksty `forge:prompt [veo3, cinematic]`. Wtedy zero ambiguity — ładujemy dokładnie te pliki.

**[KAEL] → [ORION]:**
Przy 30 kontekstach, _index.md ma 30 wierszy. Claude czyta 30 wierszy, matchuje tagi na intencję, wybiera 3. Ile tokenów kosztuje ta operacja? I co jeśli "relevance" dwóch kontekstów jest bliska — Claude losowo wybiera ten czy tamten?

**[ORION]:**
30 wierszy = ~600 tokenów. Niskokoszowe. Bliska relevance — tak, może wybrać inny zestaw. Ale: dwa konteksty o bliskiej relevance to dwa konteksty, które OBA są przydatne. Nie ma złego wyboru.

**[NOVA] → [KAEL]:**
Conflict detection w kompilatorze. Dwa pliki mają sekcję "Tone". Kompilator mówi WARNING. I co dalej? Claude widzi warning i... co? Ignoruje? Pyta usera? Przerywamy kompilację? Potrzebuję konkretnego flow.

**[KAEL]:**
Warning jest dla USERA, nie dla Claude. Kompilator wypisuje: "CONFLICT: Tone in root vs Tone in video-gen. Using video-gen (child wins). Add @extend to merge both." User widzi, decyduje, poprawia. Przy kolejnej kompilacji — conflict resolved.

**[VEGA] → [KAEL]:**
Model A: max depth 3. Co gdy user potrzebuje creative → visual → video → veo3 → cinematic-style? To depth 5. Łamiesz swoją regułę czy zmuszasz usera do flat?

**[KAEL]:**
Creative → visual → video to za dużo granulacji. FLATTEN: creative-visual-video.ctx.md — jeden plik łączący to, co nie zmienia się między targetami. Wtedy: root → creative-visual-video → veo3-cinematic. Depth 3. Reguła max depth zmusza do KONSOLIDACJI zamiast rozrastania. To feature, nie bug.

**[IRIS] → [VEGA]:**
Model C: master.ctx.md rośnie. 200 linii. 500 linii. 1000. Na jakim etapie Model C się załamie i potrzebuje struktury?

**[VEGA]:**
Mogę zarządzać flat file do ~300 linii z dobrym formatowaniem (nagłówki, sekcje). Powyżej — potrzebuję struktury. Ale tu jest punkt: na START, w prototypie, 300 linii wystarczy na MIESIĄCE. Złożoność dodajesz gdy ból jest realny, nie gdy architekt mówi że "trzeba".

**[ORION] → [NOVA]:**
Budujesz compile_context.py. Czy mogłabyś zbudować go tak, żeby obsługiwał WSZYSTKIE trzy modele? Drzewo, tagi, i flat?

**[NOVA]:**
*pauza*
...tak. Kompilator nie musi wiedzieć o ORGANIZACJI plików. On dostaje LISTĘ plików do merge i reguły merge. Czy ta lista pochodzi z tree walk, tag matching, czy manual selection — kompilatorowi wszystko jedno.

```python
# compile_context.py
def compile(file_list, rules='child_wins'):
    # file_list = ['root.ctx.md', 'creative.ctx.md', 'veo3.ctx.md']
    # Rules: child_wins, extend_all, explicit_only
    sections = {}
    for f in file_list:
        parse_and_merge(f, sections, rules)
    return render(sections)
```

Kompilator jest AGNOSTYCZNY wobec modelu organizacji. To rozwiązuje debatę. Budujemy kompilator, model organizacji jest pluggable.

---

## FAZA 4: Moment przełomu

**[NOVA]** (kontynuuje):
Chwila. Jeśli kompilator jest agnostyczny... to nie musimy WYBIERAĆ między tree, tags, i flat. Potrzebujemy:

1. **Kompilator** — bierze listę plików, merguje, produkuje jeden output
2. **Selector** — coś, co DOBIERA pliki do kompilacji

Selector może być:
- Tree walker (KAEL): idź od leaf do root
- Tag matcher (ORION): matchuj tagi na intent
- Manual (VEGA): user jawnie wskazuje pliki
- Hybrid: Claude rekomenduje, user potwierdza

To DWIE ODDZIELNE WARSTWY. Kompilator jest uniwersalny. Selector jest wymienny. Możemy zacząć od Minimum Flat (Model C — manual selection), a potem DODAĆ tree walking lub tag matching jako upgrade. Bez zmiany kompilatora.

**[KAEL]:**
...to jest czyste. Architektura warstwowa. Compile layer + selection layer. Selector jest pluggable. Mogę żyć z tym podejściem. Z zastrzeżeniem — nawet w manual selection, max 3 pliki per kompilacja.

**[IRIS]:**
I niezależnie od selectora — compiled output z attention markers. Najważniejsze sekcje na KOŃCU pliku. Recency bias pracuje DLA nas zamiast PRZECIW.

**[ORION]:**
Teraz WIDZĘ ścieżkę ewolucji:
```
v0.1: Manual selection (VEGA's flat) + Compiler
v0.2: Tag-based selection + Compiler (mój model)
v0.3: Hybrid (Claude suggests + user confirms) + Compiler
v1.0: Adaptive (Claude auto-selects, trained on feedback) + Compiler
```

Każda wersja DODAJE inteligencję selectora bez zmiany kompilatora.

**[VEGA]:**
Akceptuję. Pod warunkiem, że v0.1 jest GENUINELY usable z manual selection. Nie "stub czekający na v0.2". Jeśli manual selection + compiler daje wartość samo w sobie — budujemy.

**[NOVA]:**
Daje wartość. User pisze: `forge:prompt veo3`. Orchestrator wie że veo3 → ładuj `master.ctx.md` + `targets/veo3.ctx.md`. Runs compile. Claude czyta ONE compiled file. Generuje prompt. Proste, szybkie, deterministyczne.

---

## FAZA 4b: Devil's Advocate (VEGA)

**[VEGA]:** Zanim zamkniemy — stress test propozycji NOVA.

**Punkt 1:** Kompilator jest w Pythonie. Ale Claude musi go URUCHOMIĆ przed każdą operacją. To znaczy Bash call → Python script → output file → Read file. Cztery narzędzia. Na KAŻDĄ operację. Czy to nie wolniejsze niż "Claude czyta 2 pliki bezpośrednio"?

**[NOVA]:** Bash + Python kompilacja ~1 sekunda. Read jednego pliku ~0.5 sekundy. Versus 2x Read bez kompilacji = 1 sekunda. Delta: ~0.5 sekundy na deterministyczny merge. Warto.

**Punkt 2:** Kompilator parsuje markdown — sekcje wyznaczane przez `##`. Co jeśli user pisze kontekst bez nagłówków? Free-form prose? Kompilator się wykrzaczy.

**[KAEL]:** Dobry punkt. Rozwiązanie: kompilator ma fallback — jeśli nie znajdzie sekcji (nagłówków ##), traktuje cały plik jako JEDNĄ sekcję. Concatenation zamiast merge. Degraduje gracefully.

**Punkt 3:** Compiled output to plik tymczasowy. Gdzie żyje? Kto go sprząta? Przy 10 operacjach w sesji mam 10 .compiled.md?

**[NOVA]:** Jeden plik, nadpisywany: `forge/.cache/compiled.ctx.md`. Zawsze jeden. Nadpisywany przy każdej kompilacji. Sprzątanie = nie potrzebne.

**[VEGA]:** Akceptuję. Mam jeszcze jedno pytanie, do ORIONA. Twoja ścieżka ewolucji v0.1→v1.0 — kto ją wykona? Kto NAPISZE tag matcher w v0.2? Kto zaimplementuje hybrid w v0.3? To solo project. Roadmapa z 4 wersjami to obietnica, nie plan.

**[ORION]:** Uczciwe. Roadmapa to MOŻLIWOŚĆ, nie zobowiązanie. v0.1 musi stać samodzielnie. Jeśli v0.2 nigdy nie powstanie — v0.1 wciąż działa. Każda wersja jest self-contained.

---

## FAZA 5: Convergence — Decyzje

### DECYZJA 1: Architektura dwuwarstwowa
**WYNIK: COMPILER + SELECTOR (rozdzielone)**
- Compiler: deterministyczny Python script, agnostyczny wobec organizacji plików
- Selector: wymienny mechanizm doboru plików (v0.1 = manual/rule-based)
**Głosy:** jednogłośnie

### DECYZJA 2: Format plików .ctx.md
**WYNIK:**
```markdown
<!-- @meta
  name: nazwa-kontekstu
  tags: [tag1, tag2, tag3]
  priority: 1-10 (opcjonalnie)
-->

## Sekcja [OVERRIDE|EXTEND|—]
Treść...
```
- `@meta` w komentarzu HTML (nie wpływa na rendering)
- Sekcje wyznaczane przez `##`
- Dyrektywa OVERRIDE/EXTEND w nagłówku (nie w komentarzu — bliżej treści = silniejszy wpływ na model)
- Brak dyrektywy = domyślnie APPEND (child dodaje po parent)
**Głosy:** IRIS ✓ (dyrektywy w nagłówkach!), KAEL ✓, NOVA ✓, ORION ✓, VEGA ✓

### DECYZJA 3: Compiled output format
**WYNIK:**
```markdown
# Compiled Context: [nazwa operacji]
# Sources: root.ctx.md → creative.ctx.md → veo3.ctx.md
# Compiled: 2026-03-26 14:30

## [sekcje w kolejności: generic → specific]

## CRITICAL — Highest Priority [zawsze na końcu]
[sekcje oznaczone priority: 10 lub target-specific]
```
- Header z metadanymi (debugowalność)
- Sekcje od generic do specific (natural flow)
- Sekcje CRITICAL na KOŃCU (exploiting recency bias)
**Głosy:** IRIS ✓ (recency!), KAEL ✓, NOVA ✓, ORION ✓, VEGA ✓

### DECYZJA 4: Limity
**WYNIK:**
- Max 4 source files per compilation (hard limit w kompilatorze)
- Max 2000 tokenów compiled output (kompilator liczy i WARN jeśli przekroczone)
- Max depth organizacji: 3 (jeśli używamy drzewa)
**Głosy:** KAEL ✓, IRIS ✓, NOVA ✓, VEGA ✓. ORION: "4 pliki OK, ale 2000 tokenów to arbitralny limit. Niech będzie 3000."
**Kompromis:** 2500 tokenów z WARN, nie hard stop.

### DECYZJA 5: Selector v0.1
**WYNIK: Rule-based manual**
- Orchestrator ma ROUTING TABLE: intent → [lista plików do kompilacji]
- User może override: `forge:prompt [file1, file2]`
- Brak auto-selection w v0.1 (Claude nie rankuje)
**Głosy:** NOVA ✓, VEGA ✓, KAEL ✓. IRIS ✓ (routing table = testowalne). ORION: ✓ z zastrzeżeniem ("dodajmy tag matching w v0.2 plan")

### OTWARTE do Meeting 3:
- Scope v0.1 — CO DOKŁADNIE budujemy? Ile plików, jakie?
- Prompt-Smith — inline czy subagent?
- Arsenal — jakie minimum?

---

*Meeting 2 — ZAKOŃCZONE*
*Czas: 58 minut (symulacja)*
*Decyzja: Dwuwarstwowa architektura (Compiler + Selector), format plików, compiled output z recency exploit, hard limits*
