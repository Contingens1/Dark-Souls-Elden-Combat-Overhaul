# ER-Inspired DSR Remake

English version: [README-en.md](README-en.md)

Projekt modyfikacji rozgrywki i silnika dla **Dark Souls: Remastered**, przenoszący responsywność ruchu, mechanikę uników, skoki, picie estusa w ruchu oraz tempo walki z **Elden Ringa** do pierwszego Dark Souls.

## Główne mechaniki

| Mechanika | Opis |
|---|---|
| **Skok z Elden Ringa** | Animacje wybicia z ER (z miejsca, w marszu, ze sprintu) z dedykowanym przyciskiem, sterowaniem w locie (obrót i dosuwanie), zachowaniem pędu przy skoku z półki oraz brakiem przewrotu po lądowaniu. |
| **Ataki z wyskoku** | Atak w trakcie skoku (R1 i R2, jedną ręką i oburącz) wykorzystujący animacje zamachu w locie i wykończenia na ziemi z ER wraz z kolejkowaniem wejść dla 14 grup broni białej. |
| **Przewrót we wszystkie strony (Omni-Roll)** | Własna implementacja w C++ (`er_engine.dll`) umożliwiająca unik w dowolnym kierunku względem kamery przy namierzonym celu oraz buforowanie klawisza uniku. |
| **Sprint przy namierzeniu** | Wyzwalanie przewrotu przy puszczeniu klawisza (jak w ER), eliminujące przypadkowe uniki w bok i w tył przy próbie wejścia w sprint. |
| **Przewroty i backstepy z ER** | Pełny zestaw animacji uników (4 progi obciążenia × 4 kierunki) i backstepów z klatkami nietykalności i oknami wyjścia (recovery) odwzorowanymi z Elden Ringa. |
| **Chód, bieg i sprint z ER** | Animacje poruszania się we wszystkich 9 postawach broni i 3 progach obciążenia. |
| **Tempo ataków z ER** | Dynamiczne skalowanie szybkości wybranych faz ataków DSR (wejście w cios i okno recovery) pod czasy z Elden Ringa dla 14 grup broni białej. |
| **Estus w ruchu** | Możliwość picia i skręcania w marszu (również z pustej flaszki) z oknami wyjścia w atak, unik i gardę odwzorowanymi z ER. Broń chowa się na czas picia, jak w ER. |
| **Podnoszenie w marszu** | Przedmioty podnosi się bez zatrzymywania się, jak w ER. |
| **Darmowy sprint** | Poza walką sprint nie zużywa wytrzymałości, jak w ER. |
| **Kamera przy namierzeniu** | Dostosowana odległość, pole widzenia (FOV) oraz wysokość kamery podczas namierzania celu. |

## Bossowie

Przeróbki walk z bossami trwają. W paczce są:

* **Rycerz Artorias** — druga faza z atakami z Nightreign.
* **Capra Demon** *(w fazie testów, od 0.5.4)* — część ciosów zastąpiona atakami Omen Killera z Elden Ringa.
* **Gaping Dragon** *(w fazie testów, od 0.5.4)* — nowe AI na wzór Nightreign.

Kolejni bossowie są w planie.

## Znane problemy

Mod jest w trakcie rozwoju. Poniżej to, co jest znane i jeszcze nie działa jak trzeba:

* **Ataki z wyskoku są niedopracowane.** Przy lądowaniu po atakach w skoku zdarzają się migotania i skoki animacji. Nie wszystkie bronie mają jeszcze pełny zestaw ataków z wyskoku, np. katana i zwykły atak toporem korzystają z zastępczych animacji, a pięści nie mają ataków z wyskoku. R2 ze sprintu i z wyskoku może wchodzić w teren, bo tak samo robi ER.
* **Skok przez ścianę (zamierzone, na razie zostaje).** Skok można zacząć przy ścianie i przeniknąć przez nią. Pozwala to na ciekawe skipy, więc na razie nie jest blokowane.
* **Blok tarczą w sprincie wygląda śmiesznie (zamierzone, na razie zostaje).** Animacja sprintu z ER jest na górnej części ciała, co wygląda nienaturalnie.
* **Kamera przy namierzeniu:** moby i otoczenie potrafią zasłaniać kamerę, a kamera czasem sama mocno unosi się w górę. Jest to w planie poprawek.
* **Sprint przy namierzeniu działa tylko w przód**, tak jak w oryginale. Sprint w bok i w tył z ER jest w planie.
* **Zawieszenie postaci (rzadkie):** po przewrocie postać może przez kilka sekund stać bez animacji, mimo że gałka jest wychylona. Kończy się to zwykle trafieniem albo kolejnym przewrotem. Przyczyna nie jest jeszcze znana. Paczka ma automatyczną próbę odblokowania, która może nie zadziałać.
* **Pady DualSense** przez DualSenseX (tryb X360) bywają ignorowane. Problem dotyczy też gry bez moda.

## Architektura repozytorium

* `native/er_engine/` — kod źródłowy biblioteki hooków (`er_engine.dll` oparta na MinHook), tabele prędkości ataków i skoków oraz skrypty budujące paczki wydań.
* `native/ghidra_scripts/` — skrypty automatyzujące statyczną analizę i dekompilację funkcji silnika gry w Ghidrze.
* `tools/` — zestaw narzędzi w Pythonie i C# do rozpakowywania kontenerów (`.dcx`, `.bnd`), synchronizacji zdarzeń `.tae`, mapowania animacji oraz modyfikacji parametrów i stanów ESD.
* `docs/` — dokumentacja techniczna, mapy ID animacji oraz referencje offsetów pamięci.

## Pobieranie i instalacja

Gotowe do uruchomienia paczki dla testerów (niewymagające kompilacji kodu) znajdują się w zakładce **[Releases](../../releases)**. Szczegółowa instrukcja uruchomienia przez **Mod Engine 2** jest dołączona wewnątrz każdego archiwum (`README_release.md`).

## Podziękowania i wykorzystane zasoby

* **Player Animations Repository** (Nexus Mods, DSR #748) — animacje z Elden Ringa przeniesione na szkielet DSR (wykorzystane w plikach `.anibnd.dcx`). **Zabrania się dalszej redystrybucji tych plików bez zgody autorów repozytorium.**
* **DSROmniRoll** (Nexus Mods, DSR #1378) oraz **Simple Estus Walking** — inspiracje koncepcyjne dla własnych implementacji przewrotu we wszystkie strony i picia w ruchu (ich pliki nie są częścią projektu).
* **Mod Engine 2** (`soulsmods`) — środowisko ładowania modyfikacji dla Dark Souls: Remastered.
* **MinHook** (Tsuda Kageyu) — biblioteka hooków wykorzystana w `er_engine.dll`.
* **Elden Ring Nightreign** (FromSoftware) — animacje ataków drugiej fazy Artoriasa przeniesione do paczki; animacje i logika AI Gaping Dragona jako wzór.
* **Elden Ring** (FromSoftware) — animacje ataków Omen Killera przeniesione na Capra Demona.
* **Narzędzia społecznościowe:** SoulsFormats, soulstruct, Ghidra, DS Anim Studio.

**Licencja:** kod projektu (`native/`, `tools/` i skrypty) udostępniany jest na licencji **GPL-3.0** — zob. plik [LICENSE](LICENSE). Licencja nie obejmuje plików gier, animacji z Elden Ringa i Nightreign ani zewnętrznych narzędzi (Mod Engine 2, MinHook, Ghidra itd.), które podlegają własnym licencjom.

## Disclaimer

This is an unofficial, non-commercial, fan-made modification created for educational and personal use.

All original game assets, animations, names, and trademarks belong to **FromSoftware, Inc.** and **Bandai Namco Entertainment Inc.**

To use this mod, you must legally own copies of the respective games (*Dark Souls: Remastered*, *Elden Ring* and *Elden Ring Nightreign*). Do not monetize, re-upload, or redistribute these files commercially.

## Wesprzyj projekt

Ten mod jest i zawsze pozostanie w 100% darmowy i open-source. Jeśli jednak podoba Ci się ta praca i chcesz wesprzeć dalsze aktualizacje, możesz postawić mi kawę:

☕ **[Wesprzyj na Buy Me a Coffee](https://www.buymeacoffee.com/contingens)**

[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-ffdd00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://www.buymeacoffee.com/contingens)
