# FORGE Review Team — Context-Smith Design Review

> **Temat:** Context-Smith — moduł destylacji surowych materiałów badawczych do plików .ctx.md
> **Data:** 2026-03-27
> **Materiały wejściowe:** Plan Context-Smith + przykładowy plik wejściowy (Gemini Deep Research, ~600 linii, ~17k tokenów)
> **Protokół:** Pełne zebranie (Fazy 1-5)

---

## FAZA 1: Independent Analysis

*Każdy ekspert przygotowuje samodzielnie, bez wpływu grupowego.*

---

### IRIS — Specjalistka Prompt Engineeringu

**Pre-mortem (projekt zawiódł po 3 miesiącach — dlaczego?):**
1. Context-smith.md stał się kolejnym masywnym dokumentem instrukcji, który sam zużywa 800+ tokenów budżetu uwagi ZANIM Claude zacznie właściwą pracę destylacji. Efekt: instrukcje destylacji konkurują z materiałem źródłowym o uwagę modelu.
2. Wynikowe pliki .ctx.md wyglądają dobrze strukturalnie (validator przechodzi), ale ich TREŚĆ jest generyczna — "Known Strengths: good at X" — bo Claude nie miał wystarczającego budżetu uwagi na głębokie przetworzenie 17k tokenów materiału źródłowego JEDNOCZEŚNIE z przestrzeganiem 7 sekcji szablonu + zasad narracyjnych + reguł CRITICAL.
3. Brak mechanizmu pomiaru jakości. Validator sprawdza STRUKTURĘ, nie TREŚĆ. Nikt nie wie, czy gemini.ctx.md jest lepsze od ręcznego napisania kontekstu.

**Top 3 Strengths:**
1. Wzorzec exemplar (czytanie veo3.ctx.md jako referencji jakości) — to empirycznie silna technika. Modele LLM generują lepiej, gdy widzą konkretny przykład docelowego outputu.
2. Deterministyczna walidacja w Pythonie — oddziela "czy format jest poprawny" od "czy treść jest dobra", co jest prawidłowym rozdzieleniem odpowiedzialności.
3. Integracja z istniejącym orchestratorem (forge:distill) zamiast nowego standalone skilla — mniej overhead'u, mniej plików do czytania.

**Top 3 Concerns:**
1. Budżet uwagi. Materiał wejściowy (np. Gemini = 17k tokenów) + context-smith.md (~800 tokenów instrukcji) + _template.ctx.md + veo3.ctx.md (exemplar) + prompt Claude = potencjalnie 20k+ tokenów kontekstu. Czy model jeszcze potrafi MYŚLEĆ w tym środowisku?
2. Zero testability. Plan nie przewiduje żadnego mechanizmu oceny: "Czy ten .ctx.md jest DOBRY?" Validator sprawdzi strukturę, ale "ALWAYS include lighting description" to lepsza reguła CRITICAL niż "ALWAYS be specific" — i żaden skrypt tego nie zmierzy.
3. Założenie, że jeden przebieg wystarczy. Materiał źródłowy to 600 linii surowej wiedzy. Destylacja do 70-80 linii .ctx.md to kompresja ~8:1. To wymaga wielokrotnego przejścia, nie jednorazowej generacji.

**Ocena (Token Efficiency & Instruction Clarity): 6/10**

---

### KAEL — Architekt Zarządzania Kontekstem

**Pre-mortem (projekt zawiódł po 3 miesiącach — dlaczego?):**
1. Powstało 8 plików .ctx.md, ale 6 z nich ma zduplikowaną wiedzę. Gemini.ctx.md i dalle.ctx.md oba mają sekcję "Known Limitations: hallucination" z niemal identyczną treścią, bo context-smith nie wie co jest w INNYCH kontekstach — przetwarza każdy plik izolowanie.
2. Materiały źródłowe różnią się drastycznie jakością i strukturą. Plik Gemini to 600 linii z tabelami, źródłami, priorytetami — profesjonalny. Przyszły plik o Midjourney to może 200 linii z Reddita. Context-smith musi radzić sobie z OBOMA, ale plan nie adresuje tej wariancji.
3. Nikt nie utrzymuje kontekstów. Veo4 wychodzi, veo3.ctx.md jest nieaktualny. Context-smith potrafi TWORZYĆ, ale nie ma mechanizmu UPDATE.

**Top 3 Strengths:**
1. Architektura modułowa — context-smith.md jako osobny plik instrukcji w forge/core/ jest czystym rozwiązaniem. Nie zanieczyszcza orchestratora, łatwo go wymienić.
2. Test compilation (master + nowy kontekst → compile_context.py) — weryfikuje, że nowy plik MERGE'UJE się poprawnie z master. To eliminuje klasę błędów, gdzie sekcja [OVERRIDE] jest źle nazwana i nie nadpisuje parent.
3. Aktualizacja _index.md i routing table — automatyzacja administracji jest kluczowa przy skalowaniu od 1 do 9 kontekstów.

**Top 3 Concerns:**
1. Rozmiar materiału źródłowego. Plik Gemini = ~17k tokenów. To DUŻO. Context-smith musi to przeczytać + instrukcje + exemplar + szablon. Łączny kontekst wejściowy: ~20k tokenów. Ale budżet wyjściowy .ctx.md to ~800 tokenów. To kompresja 25:1. Czy model skutecznie kompresuje przy takiej proporcji?
2. Brak cross-context awareness. Każdy kontekst jest tworzony w izolacji. Nie ma mechanizmu: "Sprawdź, czy ta wiedza nie jest już w master.ctx.md." Ryzyko: redundancja między kontekstami, co oznacza marnowanie tokenów przy kompilacji.
3. Format materiału źródłowego jest nieprzewidywalny. Plan zakłada "MD files containing internet research", ale plik Gemini ma 10 sekcji, tabelę źródeł z 47 pozycjami, 12 szablonów promptów. Przyszły materiał o ElevenLabs może mieć 3 paragrafy z bloga. Context-smith musi obsługiwać oba ekstrema.

**Ocena (Information Architecture & Scalability): 6.5/10**

---

### NOVA — Developer platformy Cowork

**Pre-mortem (projekt zawiódł po 3 miesiącach — dlaczego?):**
1. Użytkownik uploaduje plik, mówi "forge:distill gemini", ale Claude nie trigeruje forge skilla — trigeruje bezpośrednią odpowiedź. Routing w SKILL.md orchestratora wymaga dodania nowych triggerów, a "distill" nie jest naturalnym słowem, którego użytkownik użyje.
2. validate_context.py ma zależności (np. tiktoken do liczenia tokenów), które nie są zainstalowane w sandboxie Cowork. Skrypt pada na import error.
3. Workflow wymaga zbyt wielu kroków sekwencyjnych: Read source → Read template → Read exemplar → Read context-smith.md → Generate → Write file → Run validator → Run compiler → Read output → Present. To ~10 tool calls minimum. Przy timeoutach i latency to 30-60 sekund czekania.

**Top 3 Strengths:**
1. Żadna część planu nie wymaga czegoś, czego Cowork nie potrafi. Read, Write, Bash (Python) — to standardowe operacje. Brak magii.
2. validate_context.py jako osobny skrypt to dobry pattern — Claude uruchamia go przez Bash, czyta output, reaguje. Deterministyczne, debugowalne.
3. Power user command `forge:distill` integruje się z istniejącą tabelą komend. Użytkownik nie musi uczyć się nowego interfejsu.

**Top 3 Concerns:**
1. Rozmiar pliku źródłowego. Gemini = 17k tokenów. Read tool w Cowork czyta pliki do kontekstu Claude'a. 17k tokenów jednorazowego Read to dużo — ale mieści się w oknie. Problem: Claude musi JEDNOCZEŚNIE trzymać ten plik + instrukcje + generować output. W praktyce: czy Claude nie zacznie "gubić" szczegółów z końca pliku źródłowego?
2. validate_context.py — implementacja jest trywialna (regex + string matching), ALE: plan nie specyfikuje, czy ma liczyć tokeny (potrzebuje tiktoken/cl100k), czy szacować (words/4). Jeśli tiktoken — pip install w każdej sesji. Jeśli szacowanie — mniej precyzyjne, ale zero dependencies.
3. Brak obsługi wielu plików źródłowych. Plan mówi "one or more MD files", ale workflow pokazuje Read jednego pliku. Jak Claude ma czytać 3 pliki źródłowe po 10k tokenów każdy? To 30k tokenów wejściowych + instrukcje. Granica praktyczności.

**Ocena (Technical Feasibility): 7/10**

---

### ORION — Kreatywny strateg AI

**Pre-mortem (projekt zawiódł po 3 miesiącach — dlaczego?):**
1. Context-smith produkuje pliki .ctx.md, które są poprawne, ale NUDNE. Nie mają "duszy" veo3.ctx.md. Veo3 mówi "Veo3 thinks in SCENES, not frames" — to zdanie zmienia sposób myślenia promptera. Context-smith generuje "Gemini Deep Research processes queries asynchronously" — to zdanie informuje, ale nie TRANSFORMUJE perspektywy.
2. System traktuje materiał źródłowy jak RUDĘ, z której wyciąga ZŁOTO. Ale prawdziwa wartość nie jest w ekstrakcji — jest w TRANSFORMACJI. Surowa informacja "Gemini ma 1M token context window" musi stać się operacyjną wiedzą "Nie zalewaj Gemini plikami — po ~300k tokenów uploadowanych plików agent przestaje szukać w webie."
3. Brak mechanizmu KALIBRACJI. Veo3.ctx.md powstał ręcznie, z intuicją i doświadczeniem. Context-smith próbuje zautomatyzować coś, co jest częściowo sztuką. Bez feedbacku z rzeczywistego użycia (czy prompty generowane z tego kontekstu są DOBRE?) system nie wie, czy destylacja się udała.

**Top 3 Strengths:**
1. Idea "context-smith" jako paraleli do "prompt-smith" jest ELEGANCKA. Kuźnia ma kowala promptów i kowala kontekstów. To spójna metafora, która ułatwia zrozumienie architektury.
2. Rozdzielenie na instruction file (context-smith.md) + validator (Python) + orchestrator routing oddaje różne natury tych zadań: kreacja (Claude), weryfikacja (deterministyczna), routing (konfiguracja).
3. Pomysł testu kompilacji (master + nowy kontekst) jako weryfikacji integracyjnej — to nie tylko test formatu, to test SYNERGII. Czy nowy kontekst dobrze współgra z master? To głębokie.

**Top 3 Concerns:**
1. Plik Gemini Deep Research to ZUPEŁNIE INNY gatunek wiedzy niż veo3. Veo3 to wiedza o generowaniu wideo — sensoryczna, wizualna, cinematograficzna. Gemini to wiedza o sterowaniu agentem badawczym — proceduralna, architektoniczna, techniczna. Czy JEDEN context-smith.md potrafi destylować oba? Czy nie potrzebujemy ARCHETYPÓW materiałów wejściowych?
2. **Pomysł radykalnie alternatywny:** A co jeśli zamiast "destylacji przez instrukcje" użyjemy "destylacji przez dialog"? Context-smith nie czyta materiału i produkuje output. Context-smith ROZMAWIA z materiałem — zadaje pytania: "Co jest NAJWAŻNIEJSZE dla kogoś, kto pisze prompty dla tego narzędzia?", "Jakie są 3 błędy, które KAŻDY popełnia?", "Gdybyś miał 80 tokenów na opisanie tego narzędzia prompt architektowi — co byś napisał?" To multi-pass approach, gdzie każde przejście wyciąga inną warstwę.
3. Brak mechanizmu INKUBACJI. Najlepsze konteksty powstają po iteracji — napisz, użyj, popraw. Context-smith produkuje gotowy plik w jednym cyklu. Gdzie jest pętla feedbacku?

**Ocena (Emergent Potential & Model Cognition Fit): 5.5/10**

---

### VEGA — Devil's Advocate / Systemowy Sceptyk

**Pre-mortem (projekt zawiódł po 3 miesiącach — dlaczego?):**
1. Użytkownik (Hjuston) stworzył 3 konteksty z context-smith, a potem wrócił do ręcznego pisania, bo "i tak muszę poprawiać 60% tekstu." Context-smith zaoszczędził może 10 minut na formatowaniu, ale kosztował godziny na setup.
2. Materiały źródłowe się nie pojawiają. Plan zakłada regularny napływ "MD files containing internet research." Ale kto je generuje? Jeśli użytkownik sam musi zamówić research od Gemini, sformatować, uploadować — to pipeline, nie jedno kliknięcie. Friction > value.
3. validate_context.py daje fałszywe poczucie jakości. "All checks passed!" — ale kontekst jest średni. Użytkownik ufa validatorowi i nie czyta kontekstu uważnie. Jakość spada, bo brakuje human review.

**Top 3 Strengths:**
1. *Steel-manning:* Uzasadnienie jest solidne. Masz 8 pustych slotów w routing table. Ręczne pisanie każdego to 2-4 godziny pracy. Context-smith obiecuje skrócić to do 20 minut. Nawet jeśli jakość wymaga poprawek, oszczędność czasu jest realna.
2. Plan jest MINIMALNY. 2 nowe pliki + 1 modyfikacja. W porównaniu do typowego feature creep w projektach AI, to powściągliwe.
3. Podejście "human-in-the-loop" (pokazanie pliku przed zapisem) chroni przed blind acceptance.

**Top 3 Concerns:**
1. **Analiza 10/10/10:**
   - Za 10 dni: Context-smith działa, stworzyłeś 2-3 konteksty, satysfakcja. Ale: ile czasu spędziłeś na poprawkach vs. pisaniu od zera?
   - Za 10 tygodni: Masz 6 kontekstów. Ale AI tools się zmieniły — Veo4 wyszedł, Midjourney v7. Konteksty wymagają aktualizacji. Context-smith nie pomaga w UPDATE, tylko w CREATE. Połowa kontekstów jest stale.
   - Za 10 miesięcy: FORGE ma 9 kontekstów, z których 4 są outdated. Context-smith stoi nieużywany, bo nowe modele AI pojawiają się rzadziej niż raz na miesiąc. Koszt utrzymania > koszt stworzenia.
2. **Fundamentalny problem kompresji.** Plik Gemini ma 600 linii z 12 szablonami promptów, 7 regułami, tabelami anty-patternów, ledgerem źródeł. Docelowy .ctx.md ma mieć ~70 linii. Co wyrzucamy? Szablony? Anty-patterny? Źródła? To nie jest decyzja techniczna — to decyzja EDYTORSKA. Czy naprawdę chcemy, żeby Claude podejmował te decyzje za nas?
3. **Czy problem jest rzeczywisty?** Masz 1 kontekst (veo3). Budujesz narzędzie do masowej produkcji kontekstów. Ale: czy kiedykolwiek potrzebujesz 8 kontekstów na raz? Może lepsze podejście to: pisz konteksty ręcznie gdy ich POTRZEBUJESZ (just-in-time), zamiast budować fabrykę do masowej produkcji (just-in-case).

**Ocena (Adoption Likelihood & Complexity Proportionality): 5/10**

---

## FAZA 2: Round Table

*Prezentacja stanowisk. Inni słuchają, nie komentują.*

---

### IRIS prezentuje:

Kluczowa kwestia to **budżet uwagi modelu**. Policzyłam. Materiał Gemini Deep Research: ~17 000 tokenów. context-smith.md (instrukcje): szacuję ~600-800 tokenów. _template.ctx.md: ~200 tokenów. veo3.ctx.md (exemplar): ~800 tokenów. System prompt Claude'a + skill orchestratora: ~2000 tokenów. Suma: **~21 000 tokenów kontekstu** zanim Claude napisze pierwsze słowo outputu.

Czy to dużo? Okno Claude to 200k tokenów — więc 21k to ~10%. Nie jest źle. ALE — attention decay. Tokeny z początku materiału źródłowego (sekcje 1-3 Gemini) będą ważyły więcej niż sekcje 8-10. A sekcje końcowe (szablony promptów, anty-patterny, ledger źródeł) to często NAJCENNIEJSZA wiedza operacyjna.

Moja rekomendacja: context-smith.md musi JAWNIE instruować Claude'a o kolejności przetwarzania. "Czytaj materiał od końca. Sekcje z regułami i anty-patternami mają najwyższy priorytet. Narracyjne opisy tła przetwarzaj jako ostatnie."

Druga kwestia: **brak testability**. Plan nie ma odpowiednika A/B testu. Propozycja: po wygenerowaniu .ctx.md, context-smith powinien wygenerować również JEDEN testowy prompt z tego kontekstu. Użytkownik widzi: kontekst + przykładowy prompt z niego. Jeśli prompt jest dobry — kontekst jest dobry. To proxy metryka, ale lepsza niż zero.

---

### KAEL prezentuje:

Patrzę na to przez pryzmat **przepływu informacji**. Materiał wejściowy to ~17k tokenów surowej wiedzy. Output to ~800 tokenów skompresowanej wiedzy operacyjnej. Stosunek kompresji: **21:1**.

To jest DUŻO. Dla porównania: veo3.ctx.md ma ~800 tokenów i pokrywa 6 wymiarów (landscape, structure, strengths, limitations, length, style, rules). Materiał Gemini ma 10 sekcji + 12 szablonów + tabelę źródeł + sekcję open questions. Z tego musimy WYBRAĆ i SKOMPRESOWAĆ do 7 sekcji szablonu.

Moja główna obawa: **co z wiedzą, która nie pasuje do szablonu?** Plik Gemini ma "Product Model Map" (App vs. API) — to krytyczna wiedza. Ale _template.ctx.md nie ma na to sekcji. Szablon jest zaprojektowany dla modeli GENERATYWNYCH (video, image, voice). Gemini Deep Research to model BADAWCZY. Struktura szablonu może nie pasować.

Propozycja: szablon powinien mieć opcjonalną sekcję "## Domain-Specific Knowledge" dla wiedzy, która nie mieści się w standardowych 7 sekcjach. Albo: context-smith.md powinien mieć instrukcję "Jeśli materiał nie pasuje do standardowej struktury — adaptuj sekcje, nie wymuszaj dopasowania."

Trzecia kwestia: **cross-context awareness**. Plan nie adresuje tego, ale: master.ctx.md mówi "NEVER use generic filler phrases." Jeśli context-smith wrzuci to samo do gemini.ctx.md — mamy redundancję. Instrukcje context-smith powinny zawierać: "Wiedza, która jest już w master.ctx.md, NIE powinna być powtarzana w target context."

---

### NOVA prezentuje:

Patrzę na to pragmatycznie: **jak wygląda faktyczny workflow w Cowork?**

```
1. User uploads gemini-research.md
2. User types: "forge:distill gemini"
3. FORGE orchestrator triggers → reads SKILL.md
4. SKILL.md mówi: "context-smith" → Claude reads forge/core/context-smith.md
5. Claude reads _template.ctx.md (format reference)
6. Claude reads targets/veo3.ctx.md (quality exemplar)
7. Claude reads uploaded file (17k tokens)
8. Claude generates gemini.ctx.md
9. Claude writes to forge/contexts/targets/gemini.ctx.md
10. Claude runs: python forge/core/validate_context.py forge/contexts/targets/gemini.ctx.md
11. Claude runs: python forge/core/compile_context.py --target gemini -o forge/.cache/compiled.ctx.md
12. Claude reads compiled output, presents to user
13. User approves → Claude updates _index.md
```

To 13 kroków i minimum **8 tool calls** (4x Read, 1x Write, 2x Bash, 1x Edit). Realistyczny czas: 20-40 sekund. Jest to akceptowalne — użytkownik robi to raz na target, nie co godzinę.

Ale jest **problem z validate_context.py**: jak liczyć tokeny? Opcje:
- `pip install tiktoken` — instalacja ~15 sekund przy każdej sesji. Albo sprawdzamy, czy jest zainstalowane.
- Heurystyka: `words * 1.3` — szybko, zero dependencies, ~90% dokładne.
- Pomiń liczenie tokenów, ogranicz się do structurl checks — upraszcza skrypt.

Moja rekomendacja: **heurystyka words * 1.3**. Nie potrzebujemy precyzji tiktoken. Potrzebujemy sygnału ostrzegawczego: "ten kontekst ma >1200 tokenów, rozważ skrócenie."

Ostatnia kwestia: **obsługa wielu plików źródłowych**. Jeśli user uploaduje 3 pliki, Claude dostanie je w /mnt/uploads/. Context-smith.md powinien instruować: "Czytaj wszystkie uploadowane pliki. Jeśli łączny rozmiar >30k tokenów, przetwarzaj plik po pliku i konsoliduj notatki."

---

### ORION prezentuje:

Cofam się na orbitę i widzę coś, czego nie powiedziałby żaden z poprzednich mówców.

**Plik Gemini to nie jest "surowy materiał do destylacji." To jest GOTOWY KONTEKST DLA INNEGO SYSTEMU.** Przeczytajcie jego nagłówek: "Machine-optimized context file for downstream Large Language Models." Ten plik już JEST kontekstem — tyle że dla systemu, który generuje prompty bezpośrednio, bez architektury FORGE.

Więc context-smith nie destyluje "surowej wiedzy" — on TRANSFORMUJE kontekst z jednego formatu na drugi. Z formatu "płaski, kompletny, LLM-czytelny" na format "modułowy, kompilacja, .ctx.md-kompatybilny." To jest fundamentalnie inna operacja niż "ekstrakcja wiedzy z chaosu."

Implikacja: materiały źródłowe BĘDĄ różnej natury. Czasem dostaniesz profesjonalny machine-optimized file jak Gemini. Czasem dostaniesz chaotyczny zbiór notatek z Reddit. Context-smith musi rozpoznać JAKOŚĆ wejścia i dostosować strategię.

**Moja radykalna alternatywa:** Co jeśli context-smith nie jest jednorazowym generatorem, lecz DIALOGIEM?

Przebieg:
1. Claude czyta materiał źródłowy.
2. Claude generuje DRAFT kontekstu — szybko, 80% jakości.
3. Claude SAM generuje 3-5 "pytań kontrolnych" do draftu: "Czy sekcja Known Limitations jest wystarczająco specyficzna? Czy ktoś czytając to by wiedział, że NIGDY nie powinien uploadować >300k tokenów plików?"
4. Claude iteruje na draft odpowiadając na własne pytania.
5. Output: kontekst 2. generacji, znacznie głębszy.

To "self-dialogue" — model recenzuje własną pracę. Kosztuje więcej tokenów, ale jakość rośnie znacząco. I co ważne — NIE wymaga dodatkowego tool calla. To wewnętrzna pętla w jednej generacji, kontrolowana przez context-smith.md.

---

### VEGA prezentuje:

Wysłuchałam wszystkich. Teraz mówię rzeczy, których nikt nie chce słyszeć.

**Pytanie numer 1: Czy potrzebujemy context-smith, czy potrzebujemy LEPSZEGO SZABLONU?**

Veo3.ctx.md powstał ręcznie i jest ŚWIETNY. Dlaczego? Bo twórca (Hjuston) ROZUMIE Veo3 z doświadczenia. Nie destylował dokumentacji — napisał z głowy, z intuicji, z prób i błędów. Context-smith próbuje zastąpić tę intuicję automatem. Ale automat nie ma doświadczenia UŻYTKOWANIA danego modelu AI.

Propozycja: może context-smith powinien generować nie GOTOWY kontekst, lecz DRAFT + LISTĘ PYTAŃ, na które użytkownik odpowiada z własnego doświadczenia. "Przeczytałem dokumentację Gemini. Oto draft kontekstu. Ale brakuje mi odpowiedzi na: 1) Jaka jest optymalna długość prompta w Twoim doświadczeniu? 2) Które style promptowania dawały Ci najlepsze wyniki? 3) Jakie błędy popełniałeś najczęściej?"

**Pytanie numer 2: Kompresja 21:1 to nie optymalizacja — to UTRATA.**

Plik Gemini ma 12 szablonów promptów (Due Diligence, Literature Review, Delta Update, etc.). Żaden z nich nie zmieści się w .ctx.md. A to jest NAJBARDZIEJ WARTOŚCIOWA część materiału. Context-smith zredukuje "12 szablonów" do "## Style Anchoring That Works: Gemini responds well to structured 4-part prompts (Persona, Task, Context, Format)." Jedno zdanie zamiast 12 szablonów. To nie jest kompresja — to amputacja.

**Pytanie numer 3: Koszt maintenance przewyższy koszt creation.**

Stworzenie gemini.ctx.md z context-smith: ~30 minut (z poprawkami). Utrzymanie gemini.ctx.md gdy wyjdzie Gemini 4.0: kto to zrobi? Context-smith nie pomoże w update — jest zaprojektowany do create-from-scratch. A manual update wymaga: 1) znalezienia nowego materiału, 2) porównania ze starym kontekstem, 3) chirurgicznego update'u. Plan nie adresuje tego.

---

## FAZA 3: Cross-Examination

*Każdy ekspert zadaje max 2 pytania innemu ekspertowi.*

---

**IRIS → ORION:**
"Twój pomysł self-dialogue jest intrygujący, ale ile dodatkowych tokenów generacji to kosztuje? Jeśli Claude generuje draft (800 tokenów) + 5 pytań (200 tokenów) + odpowiedzi na pytania (500 tokenów) + iterowany draft (800 tokenów) = 2300 tokenów generacji vs. 800 tokenów jednorazowych. Czy 3x koszt generacji jest uzasadniony, skoro używamy tego raz na target?"

**ORION → IRIS:**
Tak, bo porównujesz koszt tokenów z kosztem LUDZKIEGO CZASU. 2300 tokenów to <$0.01. 30 minut ręcznego poprawiania kiepskiego kontekstu to $15-50 w wartości czasu użytkownika. Ale pod warunkiem, że self-dialogue faktycznie poprawia jakość — a tego nie wiemy. Stąd moja modyfikacja: context-smith.md powinien wspominać o self-dialogue jako OPCJI, nie wymaganiu. "Jeśli materiał źródłowy jest złożony (>300 linii), zastosuj iterację wewnętrzną."

**KAEL → NOVA:**
"Powiedziałaś, że workflow to 13 kroków i 8 tool calls. Ale czy brałaś pod uwagę, że po Read dużego pliku (17k tokenów), kolejne tool calls operują z tym plikiem W KONTEKŚCIE? Czy nie ma ryzyka, że przy 5. tool callu Claude 'zapomniał' co było w sekcji 8 materiału źródłowego?"

**NOVA → KAEL:**
To realne ryzyko, ale mniejsze niż myślisz. Claude ma 200k okna. 17k to 8.5% okna. Przy 5. tool callu mamy ~25k tokenów w kontekście (materiał + narzędzia + output). To wciąż 12.5% okna. Attention decay istnieje, ale w tych proporcjach nie jest krytyczny. Ryzyko rośnie, gdy materiałów źródłowych jest WIELE — 3 pliki po 15k = 45k, to już 22% okna.

**VEGA → IRIS:**
"Zaproponowałaś 'proxy metrykę' — generowanie testowego prompta z nowego kontekstu. Ale kto ocenia, czy ten testowy prompt jest dobry? Jeśli Claude — to model ocenia własną pracę (bias). Jeśli użytkownik — to dodatkowy krok manualny. Czy ta metryka nie jest iluzją pomiaru?"

**IRIS → VEGA:**
Ma rację, że Claude oceniając własny prompt to circular evaluation. Ale: użytkownik WIDZI testowy prompt i instynktownie wie: "to wygląda jak prompty, które mi działają" albo "to jest generyczne". To nie metryka w sensie naukowym — to szybki signal. Lepszy niż "validator passed: ✅" bez żadnego kontekstu jakościowego. Pod warunkiem że nie traktujemy tego jako "test przeszedł = jakość OK."

**ORION → VEGA:**
"Powiedziałaś, że 12 szablonów z pliku Gemini to 'amputacja' przy kompresji do .ctx.md. Ale czy .ctx.md POWINIEN zawierać szablony? Master.ctx.md + target.ctx.md to instrukcje dla prompt-smith, nie biblioteka szablonów. Może szablony powinny trafić do ARSENAŁU, nie do kontekstu?"

**VEGA → ORION:**
To elegancka myśl — pod warunkiem, że context-smith ma mechanizm ROZDZIELENIA materiału na "wiedza do kontekstu" vs. "szablony do arsenału." Obecny plan tego nie przewiduje. Ale jeśli to dodamy — context-smith nie produkuje jednego pliku, lecz DWA outputy: .ctx.md + zestaw arsenałowych szablonów. To zmienia architekturę.

**NOVA → VEGA:**
"Powiedziałaś, że material źródłowe 'się nie pojawiają' — kto je generuje? Ale jest coś, co możemy sprawdzić: w pliku Gemini jest sekcja 6.5 'The Build Me a Context File Research' — to SZABLON PROMPTU do generowania materiału źródłowego w Gemini Deep Research. Czy rozwiązaniem problemu 'kto generuje materiały' nie jest właśnie ten szablon?"

**VEGA → NOVA:**
Zauważyłam to. I to jest prawdopodobnie najcenniejszy element całego pliku Gemini — nie treść, lecz META-SZABLON do generowania materiałów dla context-smith. Ale to tworzy łańcuch zależności: user → Gemini Deep Research (szablon 6.5) → materiał.md → context-smith → .ctx.md. Ile ogniw musi nie zawieść, żeby system działał?

---

## FAZA 4: Devil's Advocate Synthesis

*VEGA prowadzi. Zespół musi odpowiedzieć na KAŻDY punkt.*

---

### VEGA: Zbiorcza krytyka i scenariusz najgorszego przypadku

**Scenariusz najgorszego przypadku:**

Jest lipiec 2026. Hjuston ma 9 kontekstów wygenerowanych przez context-smith. 7 z nich jest "OK" — poprawne strukturalnie, ale pozbawione głębi i intuicji veo3.ctx.md. Prompt-smith generuje prompty z nich, ale jakość jest wyraźnie niższa niż z ręcznie napisanego veo3. Hjuston zaczyna dodawać ręczne poprawki do każdego .ctx.md po generacji, co zabiera tyle samo czasu co pisanie od zera. Jednocześnie 3 konteksty (veo3, sora, midjourney) są outdated, bo wyszły nowe wersje modeli. Context-smith nie pomaga w update. System ma 12 plików .ctx.md, z których 4 są stale, 7 jest generycznych, i tylko 1 (oryginalny veo3) jest naprawdę dobry.

**Punkty krytyczne wymagające odpowiedzi zespołu:**

**1. Kompresja 21:1 bez utraty wartości — jak?**

- IRIS: Priorytetyzacja sekcji + "czytaj od końca" w context-smith.md. Ale to łagodzi, nie rozwiązuje.
- KAEL: Adaptacyjna sekcja "Domain-Specific Knowledge" w szablonie. Pozwala zachować wiedzę niestandardową.
- ORION: Self-dialogue iteracja. Pierwszy draft kompresuje, iteracja odzyskuje utracone niuanse.
- NOVA: Heurystyka: jeśli materiał >10k tokenów, context-smith powinien NAJPIERW wygenerować "extraction notes" (kluczowe fakty, top-5 reguł, top-3 anty-patterny), a POTEM z notatek generować .ctx.md.
- **Odpowiedź zespołu:** Kombinacja extraction notes (NOVA) + self-dialogue (ORION) jest najlepsza. Dwu-przebiegowe podejście: Pass 1 = ekstrakcja kluczowej wiedzy, Pass 2 = kompozycja .ctx.md z notatek.

**2. Brak mechanizmu jakości — "validator passed" ≠ "kontekst dobry"**

- IRIS: Testowy prompt jako proxy metryka.
- VEGA: Circular evaluation risk.
- ORION: Testowy prompt + użytkownik ocenia nie kontekst, lecz prompt z kontekstu.
- **Odpowiedź zespołu:** Generowanie testowego prompta jest NAJLEPSZĄ dostępną proxy metryką. Nie jest idealna, ale: użytkownik widzi output pipeline'u end-to-end, nie abstrakcyjny plik konfiguracyjny. Implementacja: po wygenerowaniu .ctx.md, context-smith automatycznie prosi prompt-smith o wygenerowanie jednego prompta testowego. Użytkownik ocenia PROMPT, nie kontekst.

**3. Maintenance — context-smith tworzy, ale nie aktualizuje**

- VEGA: To biggest long-term risk.
- KAEL: forge-init.sh już raportuje stale contexts (>30 dni). Dodaj: "stale context detected, consider re-distilling."
- NOVA: Context-smith może mieć tryb "update": czytaj ISTNIEJĄCY .ctx.md + NOWY materiał źródłowy, merguj wiedzę.
- **Odpowiedź zespołu:** V0.1 context-smith skupia się na CREATE. Tryb "update" to v0.2 feature. ALE: forge-init.sh powinien od razu trackować datę ostatniego update'u kontekstu i ostrzegać agresywniej niż 30 dni — np. "veo3.ctx.md has 45 days, Veo4 may be available."

**4. Materiały źródłowe o różnej jakości — chaos z Reddit vs. profesjonalny Gemini file**

- ORION: Context-smith musi rozpoznawać jakość wejścia.
- IRIS: Proste rozwiązanie — context-smith.md powinien mieć sekcję "Input Quality Assessment" z instrukcją: "Jeśli materiał jest krótki (<200 linii), nieformalny, bez źródeł — oznacz output jako DRAFT i poinformuj użytkownika o niskiej pewności."
- **Odpowiedź zespołu:** Context-smith.md powinien instruować Claude'a o trójpoziomowej ocenie: HIGH (structured, sourced, >300 lines) → pełna destylacja. MEDIUM (semi-structured, 100-300 lines) → destylacja z oznaczeniem "[UNVERIFIED]" przy wątpliwych informacjach. LOW (<100 lines, informal) → generuj draft z wyraźnym komunikatem "This context requires manual enrichment."

**5. Szablony z materiału źródłowego — do kontekstu czy do arsenału?**

- ORION: Do arsenału.
- VEGA: Wymaga dual-output z context-smith.
- **Odpowiedź zespołu:** W v0.1 — pomiń. Context-smith generuje TYLKO .ctx.md. Szablony z materiału są wspomniane w sekcji "Style Anchoring" jako wzorce, nie jako pełne szablony. Dual-output to v0.2.

---

## FAZA 5: Convergence

---

### Konsensus (w czym się zgadzamy):

1. **Context-smith jest potrzebny.** 8 pustych slotów w routing table to realny problem. Ręczne pisanie każdego od zera nie jest skalowalne. (5/5 zgadza się)
2. **Architektura 3 komponentów jest poprawna:** context-smith.md (instrukcje) + validate_context.py (struktura) + routing w orchestratorze. Ale context-smith.md musi być BOGATSZY niż plan zakłada. (5/5)
3. **Dwu-przebiegowe podejście do destylacji:** extraction notes → kompozycja .ctx.md. (4/5, VEGA: "pod warunkiem że nie zajmie 2 minuty zamiast 30 sekund")
4. **Testowy prompt jako proxy metryka jakości.** (4/5, VEGA: "pod warunkiem jasnego komunikatu, że to nie jest gwarancja jakości")
5. **Heurystyka words * 1.3 zamiast tiktoken** dla liczenia tokenów w validatorze. (5/5)

### Otwarte konflikty:

1. **Self-dialogue (ORION) vs. single-pass (NOVA/IRIS):** ORION chce wewnętrznej iteracji w jednej generacji. NOVA i IRIS twierdzą, że to niepotrzebna złożoność w v0.1. ORION argumentuje, że to nie złożoność — to jedna dodatkowa sekcja w context-smith.md. **Rozwiązanie:** Implementuj self-dialogue jako OPCJONALNĄ ścieżkę, aktywowaną automatycznie gdy materiał >300 linii.
2. **Czy szablon .ctx.md pasuje do WSZYSTKICH typów targetów?** KAEL mówi nie (Gemini Deep Research ≠ Veo3). IRIS mówi: "to problem szablonu, nie context-smith." **Rozwiązanie:** Dodaj opcjonalną sekcję "## Domain-Specific" do szablonu + instrukcja w context-smith: "Adaptuj sekcje do natury modelu. Modele generatywne (video, image) → standardowe sekcje. Modele analityczne (research, coding) → zmodyfikowane sekcje."
3. **Czy context-smith realnie zaoszczędzi czas?** VEGA: "może nie." Reszta: "tak, jeśli materiał źródłowy jest dobrej jakości." **Rozwiązanie:** Mierz empirycznie. Przy pierwszych 3 kontekstach — zapisz czas (forge:distill + poprawki ręczne). Jeśli >70% czasu pisania od zera → kontynuuj. Jeśli <50% → re-evaluate.

### Rekomendacje (action items):

| # | Co zmienić | Dlaczego | Priorytet | Kto się zgadza / nie |
|---|-----------|----------|-----------|---------------------|
| 1 | **Dwu-przebiegowa destylacja w context-smith.md:** Pass 1 = extraction notes (kluczowe fakty, reguły, ograniczenia, siły), Pass 2 = kompozycja .ctx.md z notatek | Kompresja 21:1 wymaga pośredniego kroku; single-pass gubi niuanse z końca długich materiałów | **CRITICAL** | IRIS ✅ KAEL ✅ NOVA ✅ ORION ✅ VEGA ✅ |
| 2 | **Trójpoziomowa ocena materiału źródłowego** (HIGH/MEDIUM/LOW) z różnym traktowaniem outputu | Materiały będą różnej jakości; context-smith musi jawnie komunikować niepewność | **CRITICAL** | IRIS ✅ KAEL ✅ NOVA ✅ ORION ✅ VEGA ✅ |
| 3 | **Testowy prompt jako proxy metryka:** po generacji .ctx.md automatycznie uruchom mini-kompilację i wygeneruj 1 testowy prompt | Jedyny sposób na quick quality signal bez ręcznej oceny kontekstu | **IMPORTANT** | IRIS ✅ KAEL ✅ NOVA ✅ ORION ✅ VEGA ⚠️ (nie blokuje, ale ostrzega przed fałszywym poczuciem jakości) |
| 4 | **Opcjonalny self-dialogue** gdy materiał >300 linii: Claude generuje draft → pytania kontrolne → iteracja | Duże materiały wymagają głębszej refleksji; koszt tokenowy minimalny vs. wzrost jakości | **IMPORTANT** | ORION ✅ IRIS ✅ KAEL ✅ NOVA ⚠️ (mówi: "implementuj, ale mierz czy naprawdę pomaga") VEGA ⚠️ |
| 5 | **Opcjonalna sekcja "## Domain-Specific" w szablonie + adaptacyjna instrukcja** dla modeli nie-generatywnych (research, coding, analysis) | Gemini Deep Research ≠ Midjourney; sztywny szablon wymuszający "Known Strengths w kontekście generowania obrazów" nie pasuje do modeli badawczych | **IMPORTANT** | KAEL ✅ ORION ✅ NOVA ✅ IRIS ✅ VEGA ✅ |
| 6 | **validate_context.py: heurystyka words × 1.3, zero external dependencies** + structural checks only | tiktoken to zbędna zależność; heurystyka wystarcza do sygnału ostrzegawczego | **IMPORTANT** | NOVA ✅ IRIS ✅ KAEL ✅ ORION ✅ VEGA ✅ |
| 7 | **Instrukcja "cross-context dedup"** w context-smith.md: "Wiedza z master.ctx.md nie powinna być powtarzana" | Redundancja = marnowanie tokenów przy kompilacji | **NICE-TO-HAVE** | KAEL ✅ IRIS ✅ NOVA ✅ ORION ✅ VEGA ✅ |
| 8 | **Empiryczny pomiar czasu** przy pierwszych 3 kontekstach: time(forge:distill + edits) vs. estimated time(manual write) | Jedyny sposób walidacji, czy narzędzie oszczędza czas | **CRITICAL** | VEGA ✅ IRIS ✅ KAEL ✅ NOVA ✅ ORION ✅ |

### Końcowa ocena zespołu:

| Ekspert | Ocena przed debatą | Ocena po debacie | Zmiana |
|---------|-------------------|--------------------|--------|
| IRIS | 6.0 | 7.0 | +1.0 (dwu-przebiegowe podejście i proxy metryka rozwiązują główne obawy) |
| KAEL | 6.5 | 7.0 | +0.5 (adaptacyjny szablon + dedup redukują ryzyko redundancji) |
| NOVA | 7.0 | 7.5 | +0.5 (heurystyka tokenów i pragmatyczny workflow się trzymają) |
| ORION | 5.5 | 7.0 | +1.5 (self-dialogue jako opcja + dwu-przebiegowe podejście dodają głębię) |
| VEGA | 5.0 | 6.0 | +1.0 (rekomendacje łagodzą obawy, ale maintenance risk pozostaje) |

**Średnia po debacie: 6.9/10** (pre-debata: 6.0/10)

**Werdykt: PROCEED z implementacją, uwzględniając 8 rekomendacji.** VEGA zastrzega: "Wracam za 30 dni sprawdzić, czy ktoś tego używa."

---

*FORGE Review Team — Context-Smith Design Review*
*Zakończono: 2026-03-27*
