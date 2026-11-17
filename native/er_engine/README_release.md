# ER-Inspired DSR Remake v{VERSION} — Dark Souls Remastered

Ruch, uniki, skok i picie estusa w stylu Elden Ringa w Dark Souls Remastered. Od 0.4.0 także pierwszy przerobiony boss: Rycerz Artorias z drugą fazą i atakami z Nightreign. Od 0.5.4 w fazie testów także Capra Demon i Gaping Dragon, od 0.5.5 Gwyn z drugą fazą (Soul of Cinder z Dark Souls III).

## Wymagania

> **Do działania moda WYMAGANY jest Mod Engine 2 w wersji wspierającej Dark Souls Remastered.**
> Bez niego mod się nie uruchomi. Mod Engine 2 nie jest dołączony do paczki.

- **Mod Engine 2 z obsługą Dark Souls Remastered** — wydanie, które w swoim folderze ma plik `launchmod_darksoulsremastered.bat` (launcher przyjmuje `-t dsr`). Działający build dla DSR: <https://www.nexusmods.com/darksoulsremastered/mods/790>. Oficjalne wydanie z GitHuba (`ModEngine-2.1.0.0`) nie ma wsparcia dla DSR. Starsze wydania, tylko dla Dark Souls 3 / Elden Ring, też nie zadziałają. Rozpakuj go w dowolne miejsce (nie musi być w katalogu gry).
- **Dark Souls Remastered** (Steam), wersja exe z SHA-256 `A45AAA36…` (aktualna w chwili wydania moda). Narzędzie konfiguracji sprawdza to samo i ostrzega, jeśli masz inną.
- Windows 10 / 11. Linux (Steam + Proton): eksperymentalnie, sekcja „Linux”.

## Uruchomienie (bez instalacji)

Mod niczego nie instaluje: nie zmienia plików gry ani Mod Engine 2. Wystarczy rozpakować folder i raz wskazać, gdzie leży Mod Engine 2.

1. Rozpakuj **całe** archiwum do zwykłego folderu, np. `Dokumenty\ER-Inspired_DSR_Remake_v{VERSION}`. **Nie rozpakowuj do katalogu gry.**
2. Uruchom **`Setup.bat`** (dwuklik). Otworzy się okno „konfiguracja”.
3. Narzędzie samo poszuka Mod Engine 2 na dyskach. Jeśli go nie znajdzie albo znajdzie nie ten, kliknij **Przeglądaj...** i wskaż folder, w którym leży `modengine2_launcher.exe`.
4. Zielony komunikat oznacza poprawny Mod Engine 2 z obsługą DSR. Kliknij **Utwórz launcher**.
5. Grę z modem uruchamiasz plikiem **`Launch_ER-Inspired_DSR_Remake.bat`** albo skrótem na pulpicie (jeśli zostawisz zaznaczone tworzenie skrótu).

**Co robi `Setup.bat`:** zapisuje ścieżkę do Mod Engine 2 i tworzy w folderze moda dwa pliki (`ER-Inspired_DSR_Remake.toml` i `Launch_ER-Inspired_DSR_Remake.bat`) oraz opcjonalny skrót na pulpicie. Nic więcej: niczego nie kopiuje do gry ani do Mod Engine 2 i niczego nie rejestruje w systemie.

Jeśli przeniesiesz folder Mod Engine 2 w inne miejsce, uruchom `Setup.bat` jeszcze raz. Folder moda możesz przenosić dowolnie; skrót na pulpicie trzeba wtedy utworzyć ponownie (znów `Setup.bat`).

**Usunięcie moda:** usuń folder moda i skrót. Pliki gry nie są modyfikowane — gra uruchomiona ze Steama działa zawsze bez moda.

## Aktualizacje *(od 0.3.0)*

Launcher przed każdym uruchomieniem gry sprawdza na GitHubie, czy jest nowsza wersja moda (trwa to najwyżej kilka sekund; bez internetu gra startuje normalnie). Jeśli jest, pyta, czy ją pobrać i zainstalować:
- **Tak** — pobiera paczkę, wymienia pliki w folderze moda i uruchamia grę już na nowej wersji. Twoje ustawienia z `bin\er_engine.ini` zostają, launcher i ścieżka do Mod Engine 2 też. Poprzednia wersja trafia do `_backup\v<wersja>` (cofnięcie = skopiować jej zawartość z powrotem do folderu moda).
- **Nie** — gra startuje na obecnej wersji, pytanie wróci przy następnym uruchomieniu.

Aktualizacja zmienia wyłącznie pliki w folderze moda — nie dotyka gry ani Mod Engine 2. Wyłączenie sprawdzania: `CheckForUpdates=0` w `bin\er_engine.ini`. Ręczne sprawdzenie: `powershell -ExecutionPolicy Bypass -File setup\Update.ps1 -Manual`.

**Przejście z 0.1.0 / 0.2.0:** te wersje nie mają aktualizacji. Rozpakuj nową wersję do nowego folderu i uruchom `Setup.bat` jeszcze raz (nowy launcher zawiera sprawdzanie aktualizacji). Ustawienia z `bin\er_engine.ini` przenieś ręcznie, jeśli je zmieniałeś.

**Konfiguracja bez okna** (dla zaawansowanych): `Setup.bat -Silent -ModEngine2Path "D:\ścieżka\do\ModEngine2" [-Shortcut]`. Ręcznie, bez `Setup.bat`: `modengine2_launcher.exe -t dsr -c "<folder moda>\ER-Inspired_DSR_Remake.toml"`.

## WAŻNE

- **Graj wyłącznie offline.** Mod zmienia działanie gry w pamięci — gra online grozi banem. Mod nie ma własnej blokady sieci; przed uruchomieniem przełącz Steama w tryb offline albo ustaw w grze start w trybie offline.
- Na innej wersji `DarkSoulsRemastered.exe` hooki się nie założą i mechaniki z DLL nie będą działać (log: `bin\er_engine.log`).

## Nowe w 0.5.7

Wersja testowa (pre-release).

- **Kamera przy dużych wrogach bez przeskoków.** Gra wypychała kamerę przez strefę wokół dużych wrogów (np. Taurus Demon), w jednej klatce o 3–4 m od gracza, prosto w model wroga. Teraz tego nie robi. Kamera może jeszcze na chwilę wejść w wroga, który stoi tuż przy niej, ale krócej i bez skoku. Ustawienie: `PushOut` w sekcji `[Camera]` (`1` = jak w grze).
- **Mniejsze obrażenia od upadku.** Gracz traci 60% obrażeń z gry (np. z 11 m ok. 210 HP zamiast 360 przy 1500 HP). Upadek zabija dopiero od 26 m, a nie od 20 m, więc między obrażeniami a śmiercią nie ma nagłego skoku. Wrogowie bez zmian. Ustawienie: `DamagePercent` w sekcji `[Fall]` (`100` = jak w grze).

## Nowe w 0.5.6

- **Namierzanie bez przeskoków.** Cel zmienia się tylko po ruchu prawej gałki albo myszy. Gra nie przeskakuje już sama na innego wroga (wcześniej najczęściej w sprincie przy kilku przeciwnikach, razem z kamerą). Gdy cel wyjdzie poza zasięg albo zginie, namierzenie się zwalnia, jak w Elden Ringu bez auto-namierzania. Zasięg namierzenia wynosi 20 m (w grze 15 m, a przy sprincie od celu puszczało już przy 11–12 m). Ustawienia: `LockOnTargetGuard` i `LockOnRange` w sekcji `[Roll]`.
- **Sprint przy namierzeniu** *(work in progress)*:
  - postać nie zwalnia przy obrocie;
  - przy gałce w bok lub po skosie biegnie bokiem do startu sprintu, jak w Elden Ringu;
  - namierzenie włączone w trakcie sprintu nie przerywa go;
  - przy włączaniu i wyłączaniu namierzenia w ruchu nie ma animacji zawrotu, postać obraca się płynnie.
- **Przycisk uniku osobno dla klawiatury i myszy oraz dla pada.** Po przejściu z jednego na drugie unik i sprint przy namierzeniu działają od pierwszego wciśnięcia.
- **Skok:**
  - skok w sprincie działa też na klawiaturze: po lądowaniu sprint leci dalej;
  - lądowanie w bieg lub sprint bez ściągania postaci w dół, bez przeskoku rąk i bez szarpnięć prędkości;
  - nie ma już pyłu i dźwięku lądowania z DS1 przy lądowaniu w biegu;
  - lekkie lądowanie (postać staje) dopiero od 3,5 m spadania (wcześniej od 2 m).

## Nowe w 0.5.5

Wersja testowa (pre-release).

- **Sprint w każdą stronę przy namierzeniu** *(work in progress)*. Przy namierzonym celu przytrzymanie klawisza sprintu z gałką w bok, do tyłu albo po skosie daje sprint w tę stronę, jak w Elden Ringu: postać obraca się po najkrótszym kącie w stronę gałki i przechodzi w sprint, w trakcie skręca za gałką, a po puszczeniu klawisza wraca przodem do celu. Kamera zostaje na celu. Start sprintu jest jeszcze trochę sztywny (krótkie zwolnienie przy obrocie) — poprawka w drodze. Wyłączenie: `LockOnSprintFree=0` w sekcji `[Roll]` w `bin\er_engine.ini` (sprint przy namierzeniu znów tylko w przód).
- **Gwyn z dwiema fazami** *(w fazie testów)*: sekcja „Bossowie w fazie testów”.
- **Log do zgłaszania błędów (F8):** sekcja „Zgłaszanie błędów”.
- **Linux (eksperymentalnie):** skrypt `setup/Setup.sh`, sekcja „Linux”.

## Zgłaszanie błędów *(od 0.5.5)*

Gdy coś działa źle (np. postać się zawiesza), uruchom grę plikiem **`Launch_with_logs.bat`** zamiast zwykłego launchera. To ta sama wersja moda, tylko z zapisem logu:
1. Graj normalnie. Gdy coś pójdzie nie tak, od razu naciśnij **F8** (zapisuje ostatnie zdarzenia).
2. Po wyjściu z gry wyślij plik **`bin\er_engine.log`** z folderu moda (np. w zgłoszeniu na GitHubie) i napisz, co się stało i mniej więcej kiedy. Poprzednie uruchomienie zostaje w `bin\er_engine.prev.log`.

Log zawiera tylko zdarzenia z gry (animacje, przyciski, pozycje postaci), bez danych osobistych. `Launch_with_logs.bat` korzysta z Mod Engine 2 wskazanego w `Setup.bat`, więc najpierw raz uruchom `Setup.bat`.

## Linux *(eksperymentalnie, od 0.5.5)*

Nie sprawdzone na wielu systemach — zgłoszenia mile widziane.
1. Rozpakuj mod poza folderem gry, np. do `~/Games/`.
2. Pobierz Mod Engine 2 z obsługą Dark Souls Remastered (jak w „Wymagania”) i rozpakuj gdziekolwiek.
3. W Steamie włącz dla gry Proton (Właściwości → Zgodność) i uruchom ją raz, żeby powstał prefiks.
4. W terminalu: `bash setup/Setup.sh` (opcjonalnie `--me2 /ścieżka/do/ModEngine2`). Skrypt niczego nie instaluje i nie zmienia gry ani Steama, tylko zapisuje pliki w folderze moda.
5. Wklej wypisaną linię w Opcje uruchamiania gry w Steamie: `"/ścieżka/do/moda/Launch_ER-Inspired_DSR_Remake.sh" %command%`. Wersja z logiem (zgłaszanie błędów): `--logs` przed `%command%`.
6. Graj offline, uruchamiając grę zwykłym przyciskiem Graj w Steamie. Usunięcie: wyczyść Opcje uruchamiania.

## Nowe w 0.5.4

Wersja testowa (pre-release): poprawki sprawdzone w grze, ale mogą pojawić się błędy.

- **Sterowanie przy dłuższym skoku w dół.** W locie postać obraca się w stronę gałki przez cały czas, wolno jak w Elden Ringu (60°/s), więc przy dalekim skoku w dół sterowanie już nie znika po chwili. Tempo obrotu: `AirTurnSpeed` w sekcji `[Jump]` w `bin\er_engine.ini` (`0` = wyłączone).
- **Dwóch nowych bossów w fazie testów** (sekcja „Bossowie w fazie testów”): Capra Demon z atakami Omen Killera z Elden Ringa i Gaping Dragon z nowym AI na wzór Nightreign. Przeszli test bez krytycznych błędów, ale mogą jeszcze wymagać dopracowania. Zgłoszenia mile widziane.

## Bossowie w fazie testów *(od 0.5.4)*

- **Capra Demon** (Miasto Nieumarłych, niższa część) — część ciosów zastąpiona atakami Omen Killera z Elden Ringa (m.in. cios oboma tasakami); ogon porusza się jak w oryginale. AI z Dark Souls.
- **Gaping Dragon** (Głębiny) — nowe AI na wzór Nightreign: atak dobierany do odległości i strony gracza, przerwy między atakami, obrót w trakcie ataku, plucie kwasem poniżej 70% HP. Fala po skoku trafia w chwili uderzenia, szarża rani raz.
- **Gwyn, Pan Popiołu** *(od 0.5.5)* (Piec Pierwszego Płomienia) — dwie fazy. Faza 1 to Gwyn z Dark Souls. Przy 0 HP Gwyn nie ginie: cofa się, opada na kolano, wbija miecz w ziemię (wybuch ognia i fala wokół niego, ok. 4 m — przewrót albo odejście ją omija) i odzyskuje pełny pasek HP. W fazie 2 walczy ruchami Soul of Cinder z Dark Souls III; płomień na całym ostrzu i czerwona poświata na piersi oznaczają fazę 2. Każdy pasek ma mniej HP niż oryginalny, razem walka jest trochę dłuższa.
- Wyłączenie: usuń z `files\chr` plik `c2240.anibnd.dcx` (Capra), `c5260.anibnd.dcx` razem z `files\script\m10_00_00_00.luabnd.dcx` (Gaping Dragon) albo `c5370.anibnd.dcx` razem z `files\script\m18_00_00_00.luabnd.dcx` (Gwyn; do tego `GwynPhase2=0` w `bin\er_engine.ini`). Aktualizator przywróci pliki przy następnej aktualizacji.

## Nowe w 0.5.3

Wersja testowa (pre-release): poprawki sprawdzone w grze, ale mogą pojawić się błędy. Z przerobionych bossów paczka zawiera nadal tylko Artoriasa.

- **Lądowanie po skoku jak w Elden Ringu.** Po skoku z biegu postać ląduje w bieg, a ze sprintu z trzymanym B w sprint, bez hamowania i bez rozpędzania od nowa. Po dłuższym spadaniu zostaje krótkie lądowanie (jak w ER). Wyłączenie: `LandToRun=0` w `bin\er_engine.ini`.
- **Bez poślizgu** po lądowaniu, także po skoku z niższego miejsca na wyższe (schody, krawędź).
- **Bez przeskoku rąk i broni w locie:** animacja skoku z ER gra do końca i przechodzi płynnie w pozę lotu z ER.
- **Znane problemy:** przy lądowaniu po ataku z wyskoku poza przeskakuje (biodra i nogi w dół, przy katanie też ręce), poza R2 młota; poprawka w przygotowaniu.

## Nowe w 0.5.2

Wersja testowa (pre-release): poprawki sprawdzone w grze, ale mogą pojawić się błędy. Z przerobionych bossów paczka zawiera nadal tylko Artoriasa.

- **Podnoszenie przedmiotów w marszu: naprawiony błąd z 0.5.1.** Po podniesieniu w ruchu kolejne przedmioty potrafiły zostawać na ziemi, a postać czasem stawała w miejscu.
- **R2 ze sprintu** (młoty i wielkie młoty, jedną ręką i oburącz): atak z biegu jak w Elden Ringu, zamiast zatrzymania i zwykłego R2.
- **Bronie z unikalnymi atakami** (np. Great Club, Smough's Hammer, Grant, Large Club, Claymore, Moonlight Greatsword):
  - mają ataki z wyskoku swojej grupy broni z ER (młoty także R2 ze sprintu); wcześniej R2 z wyskoku nie działało;
  - ich unikalne ataki zachowują się w tym samym tempie co reszta broni (dopasowanym do ER); wcześniej miały tempo z DSR.
- **Ataki z wyskoku i R2 ze sprintu nie odbijają się od terenu**, także przy skoku pod górę. Broń może przy tym wejść w ziemię, jak w Elden Ringu.
- Przedmiot, którego masz już maksymalną liczbę (np. 99 mchów), zostaje na ziemi bez komunikatu. Tak działa sama gra.
- **Znane problemy:** przy lądowaniu po R1 postać jest jeszcze ściągana w dół; po skoku ze sprintu model lekko się ślizga, a po skoku z biegu postać lekko wyhamowuje.

## Nowe w 0.5.1

Wersja testowa (pre-release): poprawki sprawdzone w grze, ale mogą pojawić się błędy. Z przerobionych bossów paczka zawiera nadal tylko Artoriasa.

- **Estus chowa broń** na czas picia, jak w Elden Ringu, w miejscu i w marszu. Ręka z flaszką trafia do ust, bez mignięcia broni między łykami.
- **Podnoszenie przedmiotów w marszu** (jak w ER): postać nie zatrzymuje się, przedmiot trafia do ekwipunku. Wyłączenie: `PickupWhileMoving=0` w `bin\er_engine.ini`.
- **Ataki z wyskoku:**
  - katana z własnymi atakami z wyskoku z ER (wcześniej zastępcze) i z poprawnym układem rąk; R2 katany w powietrzu działa;
  - pięści i R2 młota z atakami z ER;
  - lądowanie bez ślizgu i bez skoku pozy, koniec lądowania bez przeskakiwania nóg (sekcja `[Jump]` w `bin\er_engine.ini`).
- **Znane problemy:** przy lądowaniu R1 postać jest jeszcze wyraźnie ściągana w dół (przy R2 słabiej); młot przy R2 potrafi się odbić od ziemi, zwłaszcza po skoku na wyższe podłoże.

## Nowe w 0.5.0

- **Artorias — dopracowane efekty drugiej fazy** (sprawdzone w grze):
  - Na mieczu przez całą drugą fazę widać gęstą mroczną aurę. W 0.4.0 efekt na mieczu w ogóle się nie wyświetlał. Z ciała aura zniknęła, żeby się z nią nie zlewała.
  - Trzy skoki (salta zakończone skokiem z góry i dwa wielkie skoki) zapowiadają iskry z końca miecza w locie.
  - Przy uderzeniu miecz wbija się w ziemię, a chwilę później wybucha mały mroczny wybuch z dźwiękiem, na 2 m wokół ostrza. W 0.4.0 ten wybuch nie zadawał obrażeń.
  - Dobrze wyczuty przewrót omija i cios, i wybuch. Przy zbyt wczesnym przewrocie trafi cię wybuch.
  - Skok po saltach ma dźwięk uderzenia miecza o ziemię, a pierwszy z dwóch wielkich skoków jest krótszy (12 m zamiast 15 m).
  - Przejście do drugiej fazy rusza zaraz po zakończeniu bieżącego ciosu (wcześniej czasem z opóźnieniem do 3 s).

## Nowe w 0.4.0

- **Rycerz Artorias — przerobiona walka z drugą fazą** (sekcja „Artorias”). Wczesna wersja: efekty drugiej fazy (dym na mieczu, iskry przed uderzeniem, wybuch przy lądowaniu skoków) są jeszcze do sprawdzenia i dopracowania.
- **Darmowy sprint:** wróg, który już walczy z graczem (goni go albo atakuje) w promieniu 40 m, też wyłącza darmowy sprint — nawet bez namierzenia i bez trafienia.
- **Zawieszenie po przewrocie:** gdy postać po przewrocie stoi w miejscu mimo wciśniętego kierunku, mod przywraca jej swobodny ruch (`HangRepair`, sekcja „Ustawienia”). Naprawa na podstawie dwóch zarejestrowanych przypadków — jeszcze nie sprawdzona na prawdziwym zawieszeniu.

## Artorias *(od 0.4.0)*

- **Faza 1** — tylko ataki z Dark Souls, bez wzmocnienia; krótsza niż oryginalna walka.
- **Przejście** — gdy pasek HP spadnie do zera, Artorias nie ginie: klęka w animacji wzmocnienia (nie da się jej przerwać ani zadać obrażeń), odnawia całe HP i kończy wybuchem oraz dwoma pierścieniami mrocznych kul.
- **Faza 2** — wzmocnienie na stałe (mocniejsze ciosy) i nowe ataki przeniesione z Elden Ring Nightreign: długie combo, szarże z cięciem, dwa wielkie skoki pod rząd, salta zakończone skokiem z ciosem z góry. Na mieczu przez całą fazę mroczna aura; skoki zapowiadają iskry z końca miecza, a po wbiciu miecza w ziemię wybucha mały mroczny wybuch.
- Obie fazy mają razem ok. 1,2× HP oryginalnego Artoriasa. Po zabiciu w fazie 2 Artorias daje swoją duszę bossa; dusze pojawiają się z kilkusekundowym opóźnieniem.
- Wyłączenie drugiej fazy: `ArtoriasPhase2=0` w `bin\er_engine.ini` (domyślnie `2`, patrz „Ustawienia”). Ataki z Nightreign zostają w plikach, ale bez przejścia Artorias ginie przy 0 HP.

## Nowe w 0.3.0

- **Aktualizacje z poziomu launchera** (sekcja „Aktualizacje”).
- **Sprint poza walką nie zużywa wytrzymałości** (jak w ER). Przewroty, skoki i ataki kosztują zawsze.
- **Trafienie przerywa picie i użycie przedmiotu** — flaszka nie zostaje już w ręce przy powaleniu.
- **Dusze i człowieczeństwo w ruchu** — przy ich użyciu postać zwalnia do chodu jak przy estusie (wcześniej mogła biec i miała zablokowany kierunek).
- **Estus:** limit prędkości nie wyłącza się już przy długim ciągu łyków.
- **Przewroty przy namierzeniu:** przewrót skolejkowany w trakcie innej animacji (np. reakcji na trafienie) zachowuje wybrany kierunek, zamiast iść w przód; przewrót przy puszczeniu klawisza działa też przy gałce po skosie (przód–bok).
- **Halabardy:** atak z rozbiegu nie jest już nienaturalnie szybki.

## Co zmienia

| Mechanika | Opis |
|---|---|
| **Skok z ER** | Animacje wybicia z Elden Ringa (z miejsca, w marszu, ze sprintu) z przysiadem i wysokością ok. 1,15 m. Sterowanie w locie: obrót i dosuwanie gałką/WASD. Osobny przycisk skoku z miejsca i w marszu. Skok z półki w dół zachowuje rozpęd. Bez przewrotu po lądowaniu. |
| **Ataki z wyskoku z ER** *(wczesna wersja)* | Atak w trakcie skoku (R1 i R2, jedną ręką i oburącz) używa animacji ataków z wyskoku z Elden Ringa: zamach w locie, cios dokończony na ziemi, recovery w czasach ER. Kliknięcie tuż po skoku jest kolejkowane. 14 grup broni białej. |
| **Przewrót we wszystkie strony** | Przy namierzonym celu przewrót w dowolnym kierunku względem kamery zamiast 4 kierunków (własna implementacja w `er_engine.dll`). Bufor klawisza uniku: unik wciśnięty tuż przed kierunkiem nie przepada. |
| **Sprint przy namierzeniu** *(od 0.2.0)* | Przy namierzonym celu przewrót wychodzi przy puszczeniu klawisza (jak w ER i jak w DSR bez namierzenia), więc przytrzymanie klawisza nie robi już przewrotu w bok ani w tył. Od 0.5.5 *(work in progress)* sprint w każdą stronę: postać obraca się w stronę gałki, a po puszczeniu wraca przodem do celu. |
| **Przewroty i backstepy z ER** | Animacje przewrotów (4 progi obciążenia × 4 kierunki) i backstepów z Elden Ringa, z czasami ER: szybsze wyjście z przewrotu, nietykalność 13 klatek. Od 0.2.0 każda akcja po przewrocie ma własny czas z ER (atak najwcześniej, potem przedmiot i kolejny unik, ruch, garda) — ciężkiego przewrotu nie da się już spamować. |
| **Chód, bieg i sprint z ER** | Animacje ruchu z Elden Ringa we wszystkich 9 zestawach postaw broni (bez broni, jedną ręką, oburącz, łuk, kusza, tarcza oburącz) i 3 progach obciążenia. |
| **Tempo ataków z ER** | Ataki zostają z DSR, ale są odtwarzane szybciej w tych fragmentach, gdzie ER jest szybszy: wejście w cios do trafienia (maks. ×1,35) i końcówka do okna następnej akcji (maks. ×2). Nigdy nie zwalnia. Obejmuje R1 jedną ręką i oburącz, atak z biegu i z przewrotu dla 14 grup broni białej (bez pięści, tarcz, łuków, kusz i katalizatorów). R2: przyspieszona końcówka po trafieniu. Ciężkie bronie (wielkie młoty, wielkie topory) mają łagodniejsze przyspieszenie końcówki (maks. ×1,5). |
| **Estus w ruchu** | Picie w marszu, ze skręcaniem (także z pustej flaszki); na czas picia postać zwalnia do wolnego chodu i nie sprintuje (jak w ER). Od 0.2.0 czasy po łyku jak w ER: atak, unik i garda 0,2 s po rozpoczęciu odkładania flaszki, pełny ruch po 0,3 s. |
| **Kamera przy namierzeniu** | Odległość, pole widzenia i wysokość kamery przy namierzonym celu jak w Elden Ringu. |

## Sterowanie

- **Skok:** `J` (klawiatura) lub **L3** (wciśnięcie lewej gałki). Skok ze sprintu jak w DSR (przycisk przewrotu w sprincie).
- **Atak z wyskoku:** zwykły przycisk ataku (R1 / R2) w trakcie skoku.
- **Szybkie wyjście do pulpitu:** przytrzymaj `Ctrl+Q` przez 1 s (jak Alt+F4 — nie w trakcie zapisu).

## Ustawienia

`bin\er_engine.ini`:
- `OmniRoll=1` — przewrót we wszystkie strony przy namierzeniu (`0` = 4 kierunki jak w DSR),
- `RollBuffer=1` — bufor klawisza uniku (`0` = wyłączony),
- `LockOnSprint=1` — przy namierzeniu przewrót przy puszczeniu klawisza (`0` = jak w DSR: przewrót w bok i w tył od razu przy wciśnięciu),
- `LockOnSprintFree=1` — sprint w każdą stronę przy namierzeniu, work in progress (`0` = jak w DSR: tylko w przód). Strojenie: `LockOnSprintTurnIn` / `LockOnSprintTurnOut` (tempo obrotu w °/s), `LockOnSprintTurnStart` (po ilu ms trzymania klawisza zaczyna się obrót),
- `AttackFaceTarget=1` — atak zaraz po przewrocie przy namierzeniu obraca postać do celu, jak w Elden Ring (`0` = jak w DSR: cios idzie w kierunku przewrotu),
- `FreeOutOfCombat=1` (sekcja `[Stamina]`) — poza walką sprint nie zużywa wytrzymałości; przewroty, skoki i ataki kosztują zawsze (`0` = jak w DSR). „Walka" = namierzony cel, utrata HP w ostatnich 8 s albo atak bronią w ostatnich 5 s.
- `HitCancelsItem=1` (sekcja `[Items]`) — reakcja na trafienie przerywa picie estusa / użycie przedmiotu (`0` = wyłączone; flaszka potrafi wtedy zostać w ręce przy powaleniu),
- `HangRepair=1` (sekcja `[Fixes]`) — naprawa zawieszenia po przewrocie (`0` = wyłączona),
- `ArtoriasPhase2=2` (sekcja `[Bosses]`) — druga faza Artoriasa: `2` = automatycznie (włączona, gdy w paczce są pliki bossa), `1` = włączona, `0` = wyłączona,
- `GwynPhase2=2` (sekcja `[Bosses]`) — druga faza Gwyna (w fazie testów), wartości jak wyżej,
- `CheckForUpdates=1` (sekcja `[Update]`) — sprawdzanie nowej wersji przy uruchomieniu (`0` = wyłączone),
- `PushOut=0` (sekcja `[Camera]`) — gra nie wypycha kamery przez strefę dużych wrogów (`1` = jak w grze),
- `DamagePercent=60` (sekcja `[Fall]`) — obrażenia od upadku gracza w % obrażeń z gry (`100` = jak w grze). `DeathHeight=26` zostaw bez zmian: musi się zgadzać z plikiem `files\chr\c0000.esd.dcx` z paczki.

## Znane ograniczenia

- Ataki z wyskoku: przy dotknięciu ziemi widać lekkie szarpnięcie postaci i mały przeskok animacji. Przy bardzo długim upadku zamach kończy się w powietrzu i dalej leci zwykłe spadanie.
- Sprint w każdą stronę przy namierzeniu (work in progress): start jest jeszcze trochę sztywny, przy obrocie postać na chwilę zwalnia.
- Sporadycznie postać potrafi „zawisnąć” bez animacji (stoi mimo wciśniętego kierunku) do następnego trafienia lub akcji. Od 0.4.0 przypadek po przewrocie jest naprawiany automatycznie (`HangRepair`); jeśli zawieszenie nadal się zdarza, zgłoś je.
- Artorias: balans sprawdzany tylko na NG+; wybuch przy skokach wygląda jeszcze skromnie (mechanika jest ważniejsza). Przejście do drugiej fazy czeka, aż Artorias dokończy cios, którego nie da się przerwać.
- Ślizganie przy lądowaniu po R1 i po skoku ze sprintu (patrz „Nowe w 0.5.2”); z bronią ręce przeskakują do innej pozy przy przejściu skok → spadanie.
- Blok tarczą w sprincie wygląda nienaturalnie (animacja sprintu z ER).
- Unik kończący się na ścianie przy namierzeniu potrafi sporadycznie zawiesić postać w pozie do następnej akcji.

## Podziękowania

- **Player Animations Repository** (Nexus Mods, DSR #748) — animacje Elden Ringa przeniesione na szkielet DSR, użyte w plikach `files\chr\*.anibnd.dcx`. **Nie publikuj tej paczki dalej bez zgody autorów tego repozytorium.**
- **DSROmniRoll** (Nexus Mods, DSR #1378) i **Simple Estus Walking** — pomysły, na których wzorowane są własne implementacje przewrotu we wszystkie strony i picia w ruchu. Ich pliki nie są częścią tej paczki.
- **Elden Ring Nightreign** (FromSoftware) — animacje ataków Artoriasa drugiej fazy przeniesione na jego szkielet z DSR (`files\chr\c4100.anibnd.dcx`); animacje ataków i logika AI Gaping Dragona z Nightreign jako wzór dla `files\chr\c5260.anibnd.dcx` i `files\script\m10_00_00_00.luabnd.dcx`.
- **Elden Ring** (FromSoftware) — animacje ataków Omen Killera przeniesione na szkielet Capra Demona (`files\chr\c2240.anibnd.dcx`).
- **Dark Souls III** (FromSoftware) — animacje i przejście fazy Soul of Cinder przeniesione na szkielet Gwyna (`files\chr\c5370.anibnd.dcx`); kombinacje ataków SoC jako wzór dla `files\script\m18_00_00_00.luabnd.dcx`.
- **Mod Engine 2** (soulsmods; wersja z obsługą DSR od AltimorFP, z paczki Nikolay97) — ładowanie modów (nie jest dołączony).
- **MinHook** (Tsuda Kageyu) — biblioteka hooków wkompilowana w `er_engine.dll`.

Narzędzia: SoulsFormats, soulstruct, Ghidra, DS Anim Studio (szablon TAE).
