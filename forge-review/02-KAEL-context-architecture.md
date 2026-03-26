# PERSPEKTYWA KAEL — Analiza Architektury Kontekstu

> *"Ile tokenów? Jaki przepływ? Gdzie bottleneck? Zmierzmy, zanim zdecydujemy."*

---

## PRE-MORTEM: Dlaczego to zawiodło?

**Scenariusz 1: Taxonomy Collapse**
Jest lipiec 2026. Użytkownik potrzebuje promptu do "technicznej analizy wizualnej" — SEM microscopy images. Gdzie to żyje? creative/visual? technical? Żadna gałąź nie pasuje. Tworzy creative/visual/scientific.ctx.md, ale ten dziedziczy po creative/_.ctx.md który mówi "bądź kreatywny i artystyczny". Dla naukowej analizy to ANTY-instrukcja. Musi zrobić @override na połowę sekcji creative — a wtedy po co w ogóle dziedziczy?

**Scenariusz 2: Diamond Problem**
Kontekst A dziedziczy po creative/_.ctx.md i po technical/_.ctx.md (multiple inheritance). Oba definiują sekcję "Tone" — creative mówi "swobodny, artystyczny", technical mówi "precyzyjny, formalny". Architektura mówi "ostatni na liście wygrywa". Ale to prowadzi do subtelnych, trudnych do debugowania niespójności, bo RESZTA creative nadal obowiązuje — więc masz "precyzyjny ton" + "artystyczne wzorce". Dysonans.

**Scenariusz 3: Phantom Inheritance Chain**
Ktoś dodaje folder creative/interactive/ z plikiem game-design.ctx.md, ale ZAPOMINA stworzyć _.ctx.md w tym folderze. Context Engine idzie w górę szukając _.ctx.md — przeskakuje interactive/ (brak pliku) i łączy game-design bezpośrednio z creative/_.ctx.md. Pomija cały poziom. Nikt tego nie zauważa, bo wyniki "wyglądają OK" — ale specyfika interaktywna jest utracona.

---

## OCENA ELEMENTÓW ARCHITEKTURY

### 1. Hierarchia kontekstów — Information Architecture Analysis

**Steel-man:**
Drzewowa hierarchia to naturalny model organizacji wiedzy. Ludzie myślą hierarchicznie. creative/visual/video-gen to intuicyjne zagnieżdżenie.

**Atak — Problem ekskluzywności kategorii:**

Obecna taksonomia zakłada, że kategorie są rozłączne:
```
creative/  ←→  technical/  ←→  research/
```

Ale realne zadania często przekraczają granice:

| Zadanie | creative? | technical? | research? |
|---------|:---------:|:----------:|:---------:|
| Prompt do Veo3 | tak | nie | nie |
| Skill do analizy promptów | nie | tak | nie |
| Zbadanie jak role-framing wpływa na image-gen | tak | tak | tak |
| Techniczny prompt do naukowej wizualizacji | tak | tak | nie |
| Kreatywne kodowanie (vibe coding) | tak | tak | nie |

3 z 5 realnych zadań przekracza granice kategorii. To ~60% cross-cutting concerns.

**Kwantyfikacja problemu:**
Przy 3 gałęziach głównych i wzroście do 20 liści, ~12 z nich będzie cross-cutting. Każdy wymaga albo (a) multiple inheritance z ryzykiem conflictów, albo (b) arbitralnego przypisania do jednej gałęzi z utratą kontekstu z drugiej.

**Kontrpropozycja — Tag-based system zamiast (lub obok) drzewa:**

```markdown
<!-- @meta
  name: veo3-cinematic
  tags: [creative, visual, video, cinematic, veo3]
  compose: [creative-base, visual-base, video-patterns]
-->
```

Zamiast hierarchii, konteksty mają TAGI. Context Engine buduje łańcuch na podstawie tagów, nie lokalizacji w drzewie. Pozwala to na naturalną wielokategoryjność bez diamond problem.

### 2. Algorytm Resolution — Determinism Analysis

**Steel-man:**
Algorytm jest prosty: idź od liścia do korzenia, zbieraj pliki, child overrides parent. Prostota = przewidywalność.

**Atak — Analiza determinizmu:**

Algorytm resolution w architekturze:
```
1. Zacznij od pliku docelowego
2. Sprawdź @inherits
3. Jeśli brak → idź w górę zbierając _.ctx.md
4. Na każdym poziomie: dziecko nadpisuje rodzica
5. Zwróć skompilowany kontekst
```

Problemy z determinizmem:

**Problem A: "Nadpisuje" nie jest zdefiniowane.**
Co znaczy "dziecko nadpisuje rodzica"? Jeśli root ma:
```
## Rules
- Bądź zwięzły
- Unikaj klisz
```
A child ma:
```
## Rules
- Opisuj szczegółowo sceny
```
Czy child NADPISUJE (wynik: tylko "opisuj szczegółowo"), czy ROZSZERZA (wynik: "bądź zwięzły + unikaj klisz + opisuj szczegółowo")? "Opisuj szczegółowo" KONFLIKTUJE z "bądź zwięzły" — ale system tego nie wykrywa.

**Problem B: Kolejność czytania plików.**
Context Engine czyta od root do leaf. Ale Claude (runtime) może przypisać RÓŻNĄ wagę różnym fragmentom w zależności od:
- Pozycji w conversation context (primacy/recency)
- Długości sekcji (dłuższe = więcej "attention mass")
- Specificity (bardziej szczegółowe instrukcje naturalnie wygrywają)

Więc nawet jeśli algorytm resolution jest deterministyczny, EFEKT nie jest — bo runtime (Claude) jest probabilistyczny.

**Kwantyfikacja:**
Dla prostych łańcuchów (2 poziomy, brak conflictów) — reliability ~90%.
Dla złożonych łańcuchów (4 poziomy, conflicty w sekcjach) — reliability ~60%.
Dla multiple inheritance z cross-branch — reliability ~40%.

**Kontrpropozycja — Explicit Conflict Detection:**

Context Engine powinien mieć krok walidacji:

```
Krok 3.5: CONFLICT CHECK
  Dla każdej sekcji w child:
    Jeśli parent ma sekcję o tej samej nazwie:
      Jeśli brak dyrektywy @override lub @extend:
        → WARN: "Sekcja 'Rules' w video-gen.ctx.md
          koliduje z 'Rules' w root _.ctx.md.
          Dodaj @override lub @extend."
```

To proste — Claude porównuje nagłówki sekcji w plikach. Nie wymaga kompilatora, wystarczy instrukcja.

### 3. Skalowalność — Growth Projection

**Steel-man:**
Na start system ma ~10 plików .ctx.md. To zarządzalne. Hierarchia rośnie organicznie.

**Atak — Projekcja wzrostu:**

```
Miesiąc 1:  ~10 plików .ctx.md, 3 gałęzie, max depth 3
Miesiąc 3:  ~25 plików, 5 gałęzi, max depth 4
Miesiąc 6:  ~50 plików, 8 gałęzi, max depth 5
Miesiąc 12: ~100+ plików (jeśli projekt żyje)
```

**Problemy przy >30 plikach:**

1. **Discoverability**: Użytkownik musi WIEDZIEĆ co jest w drzewie żeby wybrać właściwy kontekst. Przy 50 plikach — niemożliwe bez indeksu.

2. **Token budget**: Nawet jeśli single chain = 1800 tokenów, to Orchestrator musi WIEDZIEĆ jakie łańcuchy istnieją. Albo sam eksploruje drzewo (Read na katalogu + kilka plików = dodatkowe 500-1000 tokenów), albo ma hardcoded map w SKILL.md (który rośnie z każdym nowym kontekstem).

3. **Maintenance cascade**: Zmiana w root _.ctx.md propaguje do WSZYSTKICH liści. Przy 50 liściach — testowanie propagacji jest niemożliwe.

**Kontrpropozycja — Max Depth Rule + Index:**

Twarda reguła: maksymalna głębokość drzewa = 3 (root + category + specific).
Dlaczego 3? Bo:
- 2 to za mało — nie oddaje hierarchii
- 4+ to za dużo — środkowe warstwy stają się "pass-through" bez realnej wartości
- 3 = root kontekst + domenowa specjalizacja + konkretne zadanie

Plus automatyczny indeks:

```markdown
# contexts/_index.md (auto-generowany)
| Kontekst | Ścieżka | Tagi | Tokens |
|----------|---------|------|--------|
| Root | _.ctx.md | base | ~400 |
| Creative | creative/_.ctx.md | creative, base | ~300 |
| Video Gen | creative/visual/video-gen.ctx.md | creative, visual, video | ~500 |
```

Context Engine czyta indeks ZAMIAST eksplorować drzewo. O(1) zamiast O(depth).

### 4. Budżet kontekstu — System Overhead Analysis

**Mapowanie budżetu dla typowej operacji:**

```
┌─────────────────────────────────────┬─────────┬──────┐
│ Element                             │ Tokeny  │  %   │
├─────────────────────────────────────┼─────────┼──────┤
│ System prompt (Cowork)              │ ~8000   │ 4.0% │
│ Orchestrator SKILL.md               │ ~800    │ 0.4% │
│ Context Engine instructions         │ ~500    │ 0.3% │
│ Context chain (4 files)             │ ~1800   │ 0.9% │
│ Smith module                        │ ~600    │ 0.3% │
│ User message                        │ ~50     │ 0.0% │
├─────────────────────────────────────┼─────────┼──────┤
│ TOTAL before generation             │ ~11750  │ 5.9% │
│ Available for generation + conv.    │ ~188250 │ 94.1%│
└─────────────────────────────────────┴─────────┴──────┘
```

**Werdykt:**
6% overhead to akceptowalne tokenowo. Problem NIE jest w rozmiarze — jest w STRUKTURZE. 3700 tokenów FORGE overhead jest rozrzucone po 7+ fragmentach. Model musi syntetyzować 7 źródeł w spójne zachowanie. To kognitywnie trudniejsze niż 1 źródło o tej samej długości.

**Kontrpropozycja:**
"Pre-compile" — Context Engine generuje JEDEN plik tymczasowy z merged kontekstem. Smith czyta TEN plik, nie 4 oddzielne. Overhead tokenowy ten sam, ale cognitive load na modelu — niższy.

---

## OCENA KOŃCOWA

| Wymiar | Ocena (1-10) | Komentarz |
|--------|:---:|-----------|
| Scalability | 4/10 | Drzewo nie skaluje się powyżej ~30 plików bez indeksu i max depth rule |
| Information Architecture | 5/10 | Hierarchia intuicyjna, ale cross-cutting concerns (~60%) wymagają multiple inheritance |
| Attention Decay | 5/10 | Token budget OK, ale fragmentacja kontekstu zwiększa cognitive load |
| Resolution Determinism | 3/10 | "Nadpisuje" niezdefiniowane, brak conflict detection, runtime probabilistyczny |
| Redundancy Management | 6/10 | DRY principle działa, ale ryzyko ukrytych duplikacji przy multiple inheritance |

**Ocena zbiorcza: 4.6/10** — Solidny fundament konceptualny. Krytyczne braki: brak conflict detection, niezdefiniowana semantyka merge, brak indeksu. Skaluje się do ~20 plików, potem zaczną się problemy.

---

## REKOMENDACJE KAEL (priorytetyzowane)

1. **[CRITICAL] Definicja semantyki merge** — Precyzyjnie określ co znaczy "nadpisuje" dla sekcji, list, paragrafów
2. **[CRITICAL] Max depth = 3** — Twarda reguła, nie sugestia
3. **[CRITICAL] Conflict detection** — Context Engine musi wykrywać i raportować conflicty sekcji
4. **[IMPORTANT] Auto-indeks** — _index.md generowany przy każdej zmianie drzewa
5. **[IMPORTANT] Pre-compilation** — Merged output jako jeden plik tymczasowy
6. **[NICE-TO-HAVE] Tag-based composition** — Jako alternatywa/uzupełnienie hierarchii

---

*KAEL — Independent Analysis Report*
*FORGE Architecture Review, March 2026*
