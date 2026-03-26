# PERSPEKTYWA IRIS — Analiza Prompt Engineeringu

> *"Pokażcie mi tekst, który faktycznie trafi do modelu. Resztę możecie sobie narysować na tablicy."*

---

## PRE-MORTEM: Dlaczego to zawiodło?

**Scenariusz 1: Instruction Dilution**
Jest czerwiec 2026. Użytkownik prosi o prompt do Veo3. Orchestrator ładuje SKILL.md (~800 tokenów), potem context-engine.md (~500), potem 4 pliki .ctx.md (~1800 łącznie), potem prompt-smith.md (~600). Razem ~3700 tokenów instrukcji ZANIM model zaczyna generować prompt. Model traktuje to jako masę tekstu o mniej więcej równej wadze. Kluczowa instrukcja z video-gen.ctx.md ("preferuj opisy do 150 słów dla Veo3") tonie w morzu ogólniejszych instrukcji. Wynikowy prompt jest generyczny — nie gorszy niż bez systemu, ale nie lepszy.

**Scenariusz 2: Override Illusion**
Dyrektywy @override i @extend brzmią jak mechanizmy kompilacyjne, ale w rzeczywistości Claude nie ma kompilatora. Czyta 4 pliki, widzi sekcję "Tone" w root i sekcję "Tone" w video-gen. Nic nie mówi mu, że druga NADPISUJE pierwszą — musi to WYDEDUKOWAĆ z dyrektyw, które same są częścią kontekstu i podlegają instruction dilution. W ~30% przypadków model łączy oba "Tone" zamiast nadpisywać.

**Scenariusz 3: Prompt Ossification**
Po 2 miesiącach konteksty zawierają nagromadzone "mądrości" z 50 sesji. Każdy plik .ctx.md rośnie. Root ma 800 tokenów, creative ma 600, visual ma 500, video-gen ma 900. Łańcuch to już 2800 tokenów kontekstu — i rośnie. Nikt nie robi "garbage collection" bo boi się usunąć coś ważnego.

---

## OCENA ELEMENTÓW ARCHITEKTURY

### 1. Context Inheritance — Token Budget Analysis

**Steel-man (najsilniejszy argument ZA):**
Dziedziczenie eliminuje powtórzenia. Bez niego, video-gen.ctx.md musiałby zawierać WSZYSTKO: i bazowe zasady, i kreatywne rozszerzenia, i wizualne specyfiki. To byłby wielki flat file. Inheritance pozwala na DRY principle — zmieniasz ton w root, zmienia się wszędzie.

**Atak:**
Teoretycznie eleganckie. Ale empirycznie: czy model lepiej reaguje na 4 oddzielne pliki w łańcuchu, czy na 1 dobrze napisany flat prompt?

Moje szacunki tokenowe dla typowego scenariusza "prompt do Veo3":

```
BEZ FORGE (flat prompt):
  "Stwórz prompt do Veo3 — kot w kosmosie" + własna wiedza Claude = ~50 tokenów input

Z FORGE (pełna kompilacja):
  Orchestrator SKILL.md:     ~800 tokenów
  context-engine.md:         ~500 tokenów
  _.ctx.md (root):           ~400 tokenów
  creative/_.ctx.md:         ~300 tokenów
  creative/visual/_.ctx.md:  ~250 tokenów
  video-gen.ctx.md:          ~500 tokenów
  prompt-smith.md:           ~600 tokenów
  ────────────────────────────────────────
  TOTAL overhead:            ~3350 tokenów
```

3350 tokenów to ~1.7% okna kontekstowego (200K). Na papierze — luzik. Ale problem nie jest w rozmiarze okna. Problem jest w ATTENTION DISTRIBUTION.

**Kluczowy insight z badań attention patterns:**
Instrukcje w promptach systemowych mają różną wagę w zależności od pozycji. Początek i koniec mają najsilniejszy wpływ (primacy/recency effect). Środek — najsłabszy. Gdy ładujemy 7 plików sekwencyjnie, ROOT (najważniejszy fundamentalnie) ląduje w "dolinie uwagi" — za daleko od początku (który zajmuje Orchestrator) i za daleko od końca (który zajmuje prompt-smith).

**Kwantyfikacja ryzyka:** Prawdopodobieństwo, że root _.ctx.md ma mniej niż 60% wpływu jaki powinien mieć = szacuję na ~40-50%. To poważny problem.

**Kontrpropozycja:**
Context Engine powinien nie tylko CZYTAĆ pliki w łańcuchu, ale KOMPILOWAĆ je w jeden spójny dokument z explicity attention markers:

```markdown
=== KONTEKST SKOMPILOWANY (video-gen → veo3) ===

[FUNDAMENT — stosuj ZAWSZE]
{treść z root, skondensowana do esencji}

[SPECYFIKA DOMENY — stosuj dla tego zadania]
{treść z creative + visual, zmerge'owana i deduplikowana}

[INSTRUKCJE KRYTYCZNE — najwyższy priorytet]
{treść z video-gen, szczególnie target-specific}

=== KONIEC KONTEKSTU ===
```

Jeden dokument, jasna hierarchia, explicit attention markers. Claude czyta JEDEN plik, nie siedem.

### 2. Dyrektywy @override / @extend — Reliability Analysis

**Steel-man:**
Dyrektywy dają deklaratywny sposób kontroli jak konteksty się łączą. To lepsze niż "wrzuć wszystko i módl się".

**Atak:**
Dyrektywy @override i @extend to komentarze HTML (`<!-- @override: tone -->`). Claude musi:
1. Rozpoznać je jako dyrektywy (nie jako komentarze)
2. Zrozumieć semantykę (override = zastąp, extend = dodaj)
3. Zastosować poprawnie podczas "kompilacji"
4. Zrobić to DETERMINISTYCZNIE — ten sam input, ten sam output

Problem: Claude to probabilistyczny model języka. "Deterministycznie" nie istnieje w jego słowniku. Mogę oszacować reliability:

```
Rozpoznanie dyrektyw:             ~95% (format jest jasny)
Poprawna interpretacja semantyki: ~85% (override vs extend)
Poprawne zastosowanie:            ~75% (trudne przy conflictach)
────────────────────────────────────────────────────────────
Łączna reliability:               ~60%
```

60% reliability przy operacji fundamentalnej dla systemu to czerwona flaga.

**Kontrpropozycja:**
Zamiast dyrektyw w komentarzach HTML, użyj formatu, który WYMUSZA poprawne przetwarzanie:

```markdown
## Tone [OVERRIDE — zastępuje rodzica]
Cinematograficzny, dynamiczny...

## Rules [EXTEND — dodaj do rodzica]
- Opisuj ruch kamery...
```

Tag w nagłówku sekcji jest bliżej treści, więc model silniej go wiąże z instrukcją. Komentarz HTML jest "niewidoczny" — model może go przeoczyć.

### 3. Prompt-Smith — Instruction Clarity Analysis

**Steel-man:**
Wyspecjalizowany moduł do generowania promptów to świetna idea. Każdy target AI ma swoją specyfikę — prompt do Veo3 wygląda zupełnie inaczej niż do Gemini Deep Research.

**Atak:**
Architektura mówi "Prompt-Smith rozumie różnice między targetami" — ale SKĄD je rozumie? Z prompt-smith.md? Z kontekstu video-gen.ctx.md? Z obu?

Jeśli z obu — mamy potencjalną redundancję. Prompt-smith.md mówi "Veo3 lubi cinematic lighting", a video-gen.ctx.md mówi "Veo3 preferuje opisy do 150 słów". To dwie instrukcje z dwóch miejsc o tym samym target — ale rozrzucone po różnych plikach.

**Kwantyfikacja:**
Przy 5 target AI i 2 źródłach wiedzy per target (smith + context), mamy 10 miejsc, gdzie instrukcje mogą być niespójne. Przy 10 targets — 20 miejsc. To nie skaluje się.

**Kontrpropozycja:**
Wiedza o targetach powinna żyć w JEDNYM miejscu. Proponuję:

```
core/targets/
├── veo3.target.md      ← WSZYSTKO o Veo3 w jednym pliku
├── gemini.target.md    ← WSZYSTKO o Gemini
├── midjourney.target.md
└── elevenlabs.target.md
```

Prompt-smith czyta odpowiedni .target.md — i TYLKO ten plik zawiera wiedzę o konkretnym AI. Zero rozproszenia, zero redundancji.

### 4. Orchestrator — Routing Reliability

**Steel-man:**
Hybrydowy routing (automatyczny + bezpośredni) jest pragmatyczny. Pokrywa zarówno casual use jak i power-user scenarios.

**Atak:**
Routing automatyczny opiera się na tym, że Claude z SKILL.md orkiestratora poprawnie zidentyfikuje: (a) którego Smitha użyć, (b) który kontekst załadować, (c) jaki target.

Architektura zakłada keyword-based routing: "prompt" → Prompt-Smith. Ale:
- "Stwórz mi coś fajnego do Midjourney" — nie zawiera słowa "prompt", ale to Prompt-Smith
- "Potrzebuję skrypt do batch rename" — to Tool-Smith, ale "skrypt" mógłby triggerować Skill-Smith
- "Zbadaj dlaczego moje prompty do Veo3 są słabe" — to Lab/Sandbox? Prompt-Smith? Oba?

**Kwantyfikacja:**
Szacuję accuracy routingu automatycznego na ~70-80%. To oznacza, że co 4-5 zapytanie zostanie źle zroutowane.

**Kontrpropozycja:**
Orchestrator powinien mieć EXPLICIT routing table, nie implicit reasoning:

```markdown
## Routing Table
| Sygnał | Smith | Kontekst |
|--------|-------|----------|
| prompt, opis do [AI], wygeneruj [AI] | prompt-smith | creative/* lub targets/* |
| skill, zdolność, SKILL.md | skill-smith | technical/* |
| skrypt, narzędzie, automatyzacja | tool-smith | technical/* |
| agent, subagent, asystent | agent-smith | technical/* |
| zbadaj, eksperyment, przetestuj | lab | research/* |
| kontekst, gałąź, dziedziczenie | context-engine | — |
```

Explicit table > implicit reasoning. Model jest lepszy w table lookup niż w free-form classification.

---

## OCENA KOŃCOWA

| Wymiar | Ocena (1-10) | Komentarz |
|--------|:---:|-----------|
| Token Economy | 5/10 | 3350+ tokenów overhead na prostą operację. Nie katastrofa, ale nie elegancja. |
| Instruction Clarity | 4/10 | 7 plików, brak explicit attention markers, dyrektywy w komentarzach HTML. |
| Attention Budget | 4/10 | Root context w "dolinie uwagi". Brak strategii pozycjonowania kluczowych instrukcji. |
| Testability | 3/10 | ZERO mechanizmów A/B testowania. Skąd wiem, że skompilowany kontekst daje lepsze prompty niż flat prompt? |

**Ocena zbiorcza: 4/10** — Koncepcyjnie obiecujące, ale bez empirycznej walidacji i optymalizacji pod mechanikę attention, ryzyko instruction dilution jest zbyt wysokie.

---

## REKOMENDACJE IRIS (priorytetyzowane)

1. **[CRITICAL] Compiled Output** — Context Engine powinien produkować JEDEN dokument z explicit hierarchią, nie sekwencję oddzielnych plików
2. **[CRITICAL] Empiryczna walidacja** — Zanim zbudujesz system, zrób A/B test: flat prompt vs. 4-level inheritance. Na 10 zadaniach. Zmierz jakość.
3. **[IMPORTANT] Dyrektywy w nagłówkach** — Przenieś @override/@extend z komentarzy HTML do nagłówków sekcji
4. **[IMPORTANT] Target files** — Centralizuj wiedzę o targetach w jednym miejscu per AI
5. **[NICE-TO-HAVE] Routing table** — Explicit routing zamiast free-form classification

---

*IRIS — Independent Analysis Report*
*FORGE Architecture Review, March 2026*
