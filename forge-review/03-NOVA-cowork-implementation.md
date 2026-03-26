# PERSPEKTYWA NOVA — Analiza Implementacji w Claude Cowork

> *"OK, pokaż mi wywołanie narzędzia. Jakie Read? Jakie Write? Krok po kroku. Reszta to poezja."*

---

## PRE-MORTEM: Dlaczego to zawiodło?

**Scenariusz 1: Skill Triggering Failure**
Jest maj 2026. Użytkownik pisze "pomóż mi z prezentacją". Cowork triggeruje skill `pptx` zamiast FORGE orchestratora. Użytkownik pisze "stwórz mi ładny opis do obrazka AI" — Cowork nie triggeruje żadnego skilla, Claude odpowiada z głowy. FORGE orchestrator triggeruje się TYLKO gdy użytkownik jawnie mówi "forge:" lub bardzo konkretnie odnosi się do systemu. W praktyce — 70% interakcji omija FORGE.

**Scenariusz 2: Context Engine = Prompt Stuffing**
Architektura mówi "Context Engine kompiluje łańcuch". Dekonstruuję to do wywołań narzędzi:
```
1. Claude czyta context-engine.md          → Read tool
2. Claude czyta _.ctx.md                   → Read tool
3. Claude czyta creative/_.ctx.md          → Read tool
4. Claude czyta creative/visual/_.ctx.md   → Read tool
5. Claude czyta video-gen.ctx.md           → Read tool
6. Claude "kompiluje" — w głowie           → reasoning (nie narzędzie)
7. Claude czyta prompt-smith.md            → Read tool
8. Claude generuje prompt                  → output
```

To 6 wywołań Read + reasoning. "Kompilacja" to krok 6 — nie ma narzędzia, nie ma skryptu, nie ma mechanizmu. Claude po prostu MA w kontekście treść 5 plików i próbuje zachowywać się zgodnie ze wszystkimi naraz. Nie ma gwarancji, że "skompilował" poprawnie. Nie ma outputu kompilacji, który można zweryfikować.

**Scenariusz 3: Subagent Context Isolation**
Orchestrator postanawia delegować do subagenta (Prompt-Smith jako Agent tool). Subagent startuje z CZYSTYM kontekstem. Nie widzi plików, które Orchestrator czytał. Musi sam:
- Przeczytać context-engine.md
- Przeczytać 4 pliki kontekstu
- Przeczytać prompt-smith.md
- Wygenerować prompt

Każdy subagent robi TO SAMO od zera. Żadnego cache'a, żadnego shared state.

---

## OCENA ELEMENTÓW ARCHITEKTURY

### 1. Orchestrator SKILL.md — Trigger & Scope Analysis

**Steel-man:**
Jeden zarejestrowany skill = czysta architektura. Orchestrator wie o wszystkim i routuje.

**Atak — Analiza systemu triggerowania Cowork:**

Jak działa triggering w Cowork:
1. Każdy skill ma `description` w frontmatter YAML
2. Claude widzi WSZYSTKIE descriptions jednocześnie
3. Decyduje czy konsultować skill na podstawie description
4. Skill triggeruje się TYLKO dla "substantive" queries (nie trivial)

Problem z FORGE orchestratorem: musi mieć MEGA-szeroką description żeby łapać:
- Tworzenie promptów do AI
- Tworzenie skilli
- Tworzenie narzędzi
- Tworzenie subagentów
- Eksperymenty badawcze
- Zarządzanie kontekstami
- Przeglądanie arsenału

Tak szeroka description będzie KOLIDOWAĆ z innymi skillami:
- "Stwórz mi skill" — FORGE orchestrator vs. skill-creator?
- "Pomóż z dokumentem" — FORGE vs. docx?
- "Stwórz skrypt Python" — FORGE Tool-Smith vs. bezpośrednie kodowanie?

**Kwantyfikacja:**
Przy 8 zainstalowanych skillach (forge + 7 istniejących), szacuję konflikty triggerowania:
- forge vs. skill-creator: ~40% overlap
- forge vs. inne (docx/pdf/pptx/xlsx): ~15% overlap
- forge poprawnie triggerowany bez konfliktu: ~60% szans

**Kontrpropozycja A — Multiple registered skills:**
Zamiast jednego mega-orchestratora, zarejestruj 4-5 wyspecjalizowanych skilli:

```
.claude/skills/
├── forge-prompt/SKILL.md      ← triggeruje na: prompt, opis do AI
├── forge-factory/SKILL.md     ← triggeruje na: skill, tool, agent
├── forge-lab/SKILL.md         ← triggeruje na: eksperyment, badanie
└── forge-context/SKILL.md     ← triggeruje na: kontekst, dziedziczenie
```

Każdy ma wąską description = precyzyjne triggerowanie. Każdy wie, gdzie szukać danych w forge/.

**Kontrpropozycja B — Namespace triggering:**
Orchestrator triggeruje się TYLKO na jawny prefix `forge:`. Wszystko inne = Claude działa normalnie. To eliminuje konflikty, ale wymaga, żeby użytkownik PAMIĘTAŁ o forge:.

### 2. Context Engine — Implementation Reality Check

**Steel-man:**
Czysto tekstowa kompilacja (Claude czyta pliki i syntetyzuje) jest elegancka bo zero external dependencies.

**Atak — "Kompilacja" to złudzenie:**

Prawdziwa kompilacja (w programowaniu) ma 3 właściwości:
1. **Determinizm** — ten sam input → ten sam output, ZAWSZE
2. **Verifiability** — mogę sprawdzić output kompilacji
3. **Error handling** — kompilator mówi mi gdzie jest błąd

"Kompilacja" w Context Engine:
1. **Nie-deterministyczna** — Claude probabilistycznie "merguje" konteksty
2. **Nie-weryfikowalna** — nie ma outputu kompilacji do sprawdzenia
3. **Bez error handling** — jeśli konteksty są sprzeczne, Claude po cichu wybiera jeden

To fundamentalna różnica. Architektura NAZYWA to kompilacją, ale to jest INTERPRETACJA. Model interpretuje wiele źródeł naraz i produkuje output. To bardziej jak tłumacz pracujący z 4 słownikami jednocześnie, niż jak kompilator.

**Kontrpropozycja — Zrób kompilację LITERALNIE:**

```python
# scripts/compile_context.py
# Czyta łańcuch .ctx.md, merguje sekcje, produkuje JEDEN plik

import sys, re

def compile_chain(leaf_path):
    chain = resolve_chain(leaf_path)  # walk up to root
    sections = {}
    for file in chain:  # root first, leaf last
        for section_name, content, directive in parse_sections(file):
            if directive == 'OVERRIDE' or section_name not in sections:
                sections[section_name] = content
            elif directive == 'EXTEND':
                sections[section_name] += '\n' + content
    return render_compiled(sections)
```

To ~50 linii Pythona. Deterministyczne. Weryfikowalne (output to plik). Error handling (brak pliku, circular inheritance, undefined section). FORGE odpalałby ten skrypt przed każdą operacją.

### 3. Subagenci — Context Propagation Problem

**Steel-man:**
Subagenci pozwalają na paralelizm — Prompt-Smith może działać niezależnie.

**Atak — Context jest LOST przy delegacji do subagenta:**

Gdy Orchestrator spawnt subagenta przez Agent tool:
```python
Agent(
    prompt="Generate a Veo3 prompt for cat in space.
            Read forge/core/smiths/prompt-smith.md first.
            Then resolve context chain for video-gen.",
    subagent_type="general-purpose"
)
```

Subagent:
- NIE widzi, co Orchestrator czytał
- NIE ma kontekstu z SKILL.md orchestratora
- MUSI sam przeczytać wszystkie pliki
- Ma WŁASNY, oddzielny conversation context

To oznacza, że KAŻDA delegacja do Smitha kosztuje ponowne przeczytanie ~5-7 plików. Nie ma skrótu.

**Kwantyfikacja:**
Bez subagenta (inline): 6 Read calls + 1 generation = ~10-15 sekund
Z subagentnem: spawn overhead + 6 Read calls + reasoning + 1 generation = ~30-60 sekund

Subagent jest 2-4x wolniejszy, bez dodatkowej korzyści (bo i tak nie paralelizuje — user czeka na prompt).

**Kontrpropozycja:**
Nie deleguj do subagentów dla prostych operacji (prompt generation, context lookup). Subagent ma sens TYLKO gdy:
1. Operacja jest długotrwała (skill creation + testing)
2. Potrzebujesz paralelizmu (3 warianty prompta naraz)
3. Potrzebujesz izolacji (eksperyment w sandboxie)

Dla core flow (prompt generation, context resolution) — Orchestrator robi WSZYSTKO inline.

### 4. Session Lifecycle — State Persistence

**Steel-man:**
Pliki na filesystemie = persistent state. Arsenal, konteksty, journal przetrwają restart sesji.

**Atak — "Cold start" problem:**

Każda nowa sesja Cowork = Claude nie wie nic o FORGE poza tym, co jest w SKILL.md (jeśli skill się triggeruje). Użytkownik otwiera nową sesję:

1. Pisze "daj mi prompt do Veo3"
2. FORGE orchestrator triggeruje się (hopefully)
3. Claude czyta SKILL.md → dowiaduje się o forge/
4. Claude musi odkryć STRUKTURĘ projektu (jakie konteksty istnieją, co jest w arsenale)
5. Claude eksploruje filesystem (ls, Read na _index.md...)
6. TERAZ może zacząć pracować

Kroki 3-5 to "cold start" — kosztują ~5-15 sekund i ~3000+ tokenów KAŻDEJ sesji.

**Kontrpropozycja:**
SKILL.md orchestratora powinien zawierać SNAPSHOT stanu projektu:

```yaml
---
name: forge
description: ...
---

## Project State (auto-updated)
- Contexts: 12 files, 3 branches (creative, technical, research)
- Arsenal: 8 prompts, 3 skills, 2 tools
- Last session: 2026-03-26, created veo3 prompt
- Active experiment: "role-framing impact"
```

Skrypt aktualizujący ten snapshot na końcu każdej sesji:
```bash
python forge/scripts/update_snapshot.py > .claude/skills/forge/SKILL.md
```

Cold start = przeczytanie SKILL.md z aktualnym snapshot. Zero eksploracji.

### 5. Arsenal — Discovery & Retrieval

**Steel-man:**
Organizacja by-target i by-purpose daje dwie osie wyszukiwania.

**Atak — Filesystem to kiepska baza danych:**

Przy 50+ promptach w arsenale:
```
arsenal/prompts/by-target/veo3/
├── cosmic-cat-2026-03-26.md
├── urban-timelapse-2026-03-28.md
├── underwater-documentary-2026-04-02.md
├── ...15 more files...
```

Jak znaleźć "ten prompt o kosmosie, który działał super"? Claude musi:
1. `ls arsenal/prompts/by-target/veo3/` → lista plików
2. Read na każdym pliku? Na 18 plikach? Nie.
3. Szukać po nazwie? Nazwy to konwencja, nie gwarancja.

**Kontrpropozycja — Arsenal Index:**

```markdown
# arsenal/_index.md (auto-generated)

## Prompts (18 total)
| Name | Target | Purpose | Quality | Date | Path |
|------|--------|---------|---------|------|------|
| Cosmic Cat | veo3 | creative | 9/10 | 2026-03-26 | prompts/by-target/veo3/cosmic-cat.md |
| Urban Timelapse | veo3 | documentary | 7/10 | 2026-03-28 | prompts/by-target/veo3/urban-timelapse.md |

## Skills (3 total)
...
```

Claude czyta JEDEN plik, ma pełny przegląd. User-rated quality pozwala na sortowanie.

---

## OCENA KOŃCOWA

| Wymiar | Ocena (1-10) | Komentarz |
|--------|:---:|-----------|
| Feasibility | 5/10 | Technicznie możliwe, ale "Context Engine" to prompt stuffing z ładną nazwą |
| Skill System Compatibility | 4/10 | Mega-orchestrator będzie kolidował z innymi skillami |
| Subagent Utilization | 3/10 | Subagenci tracą kontekst przy spawnie, overhead > benefit dla core flows |
| Session Lifecycle | 4/10 | Cold start problem, brak snapshot mechanism |
| File I/O Reality | 6/10 | Działa, ale skalowanie arsenału wymaga indeksu |

**Ocena zbiorcza: 4.4/10** — Można zbudować, ale architektura traktuje Cowork jak tradycyjny framework, a nie jak LLM-powered environment. "Kompilacja" kontekstów to złudzenie kontroli. Realne rozwiązanie: Python skrypt kompilujący + snapshot w SKILL.md + indeks arsenału.

---

## REKOMENDACJE NOVA (priorytetyzowane)

1. **[CRITICAL] Literalny kompilator** — Python skrypt compile_context.py, nie "Claude czyta i merguje w głowie"
2. **[CRITICAL] Skill splitting lub namespace** — Albo osobne skille per moduł, albo forge: prefix
3. **[IMPORTANT] Inline execution** — Orchestrator robi core flows inline, subagenci tylko dla heavy ops
4. **[IMPORTANT] Session snapshot** — Auto-update SKILL.md z aktualnym stanem projektu
5. **[IMPORTANT] Arsenal index** — _index.md z metadanymi wszystkich artefaktów
6. **[NICE-TO-HAVE] Hot start script** — Skrypt bash odpalany na starcie sesji, ładujący snapshot

---

*NOVA — Independent Analysis Report*
*FORGE Architecture Review, March 2026*
