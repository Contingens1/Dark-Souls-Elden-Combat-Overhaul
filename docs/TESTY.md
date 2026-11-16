# Testy do zrobienia

Stan: 2026-11-16 wieczór, nocna DLL = `main` (ze sprintem przy namierzeniu v3.1) + Gwyn. Wydanie 0.5.5 w przygotowaniu. **To jedyna aktualna lista testów.** Po każdym teście poprawiam ten plik.

## Jak uruchomić

- **Prawie wszystko:** `dist\mods\bossy_nightreign\launch_test_all.bat`.
  - DLL ma to samo co wydanie 0.5.4, plus diagnostykę, F8, sprint przy namierzeniu v3.1 i dwie fazy Gwyna (punkt 2).
  - Zawiera wszystkich przerobionych bossów: Artoriasa, Capra, Gaping, Centipede, Stray i Gwyna.
- **Wyjątek, punkt 3 (Centipede):** `dist\mods\c0000_er_engine\launch_er_engine.bat` (sam mod, bez bossów).
- Gdy coś jest nie tak: **F8** od razu (zapisuje log). W wiadomości napisz mniej więcej godzinę.

## Do przetestowania

1. **Skok, przy okazji** (skok jest zaliczony i jest w 0.5.3; tych przypadków log jeszcze nie obejmował):
   - skok z miejsca;
   - skok z marszu (wolno, gałka lekko wychylona);
   - zaraz po lądowaniu: puszczenie gałki, unik, atak;
   - skok z bronią oburącz i z uniesioną tarczą.
2. **Gwyn: dwie fazy** (Kiln of the First Flame, nowe 15.11 w nocy). Faza 1 to Gwyn z DS1 (stare ruchy i stare AI), faza 2 to ruchy i AI z Soul of Cinder (te z testu 15.11).
   - Test 15.11 w nocy, pierwsza próba: faza 1 w porządku. Przy 0 HP Gwyn został na 1 HP, ale przejście się nie zaczęło (AI go nie zleciło), a po 20 s zginął. Poprawione.
   - Druga próba: **przejście działa** (klęk, wbicie miecza, fala, pełny pasek HP). Fala z bliska jeszcze nie sprawdzona.
   - Z logu (16.11): w fazie 2 grają ruchy SoC (inne czasy i zasięgi niż w fazie 1, takie same jak w teście paczki SoC). Na oko różnią się mało; wyraźna różnica przyjdzie z nowymi atakami.
   - Poprawione 16.11: przejście czekało 0–11 s, bo zwykła reakcja z fazy 1 (np. na łyk Estusa) wypychała je z kolejki. **Teraz ma ruszyć zaraz po ciosie, który właśnie trwa (1–2 s).**
   - **Przejście przy 0 HP:** Gwyn nie ginie. Cofa się i opada na kolano z lewą ręką na ziemi, wstaje, unosi miecz oburącz i wbija go w ziemię. W chwili wbicia: wybuch ognia przy mieczu, fala światła wokół niego (jak cud Wrath of the Gods, ok. 4 m), a pasek HP wraca do pełna w około sekundę.
   - Sprawdzić przejście:
     - startuje raz, przy 0 HP;
     - w trakcie boss nie traci HP i nie da się go przerwać;
     - fala trafia tylko w zasięgu widocznego efektu, a przewrót we właściwej chwili albo odejście ją omija (trafienie powala).
   - **Znak fazy 2 (nowe 16.11, decyzja gracza „dodaj znak”):** od wbicia miecza do końca walki:
     - ogień na całym ostrzu (dotąd Gwyn ma płomień tylko przy rękojeści; dochodzi ten sam płomień w połowie ostrza i na czubku);
     - czerwona poświata z piersi, jak z Red Tearstone Ring.
     - Ocenić każdą część osobno: widać, ładne, za mało, za dużo, zostawić czy usunąć. Jeśli którejś nie widać, też napisać.
   - Sprawdzić fazę 2:
     - reakcje na trafienie i śmierć wyglądają normalnie;
     - chwyt i rzut działają;
     - (przy okazji) włosy i broda.
   - Długość walki: każdy pasek ma teraz 900 HP zamiast jednego 1550. Czy razem nie wychodzi za długo albo za krótko?
   - Nowych ataków SoC (piorun, włócznia, burza, kombinacja z wybuchem) jeszcze nie ma: to kolejne etapy.
   - F8 po walce.
3. **Centipede Demon: test rozstrzygający** (Demon Ruins), z `launch_er_engine.bat`, **bez paczek bossów**.
   - Czy w oryginale da się trafić wyciągniętą mackę, zwłaszcza jej koniec z paszczą.
   - Od tego zależy, czy problem jest w naszych zmianach, czy w samej grze.
4. **Linux (nowe 16.11, paczka 0.5.5):** skrypt `setup/Setup.sh` (eksperymentalny, nigdy nie uruchomiony na Linuksie).
   - Kroki:
     1. Rozpakuj paczkę poza folderem gry, np. `~/Games/`. Mod Engine 2 z obsługą DSR rozpakuj obok, np. `~/Games/ModEngine2`.
     2. W Steamie wymuś Proton dla gry i uruchom ją raz do menu.
     3. `bash ~/Games/ER-Inspired_DSR_Remake_v0.5.5/setup/Setup.sh` (albo z `--me2 <folder>`); skrypt wypisze linię do Opcji uruchamiania: `"/ścieżka/Launch_ER-Inspired_DSR_Remake.sh" %command%`.
     4. Graj. Mod działa, jeśli przy namierzeniu przewrót idzie w każdą stronę.
   - Kontrola bez gry: `Launch_ER-Inspired_DSR_Remake.sh --dry-run <coś> .../DarkSoulsRemastered.exe` wypisze przepisaną komendę.
   - Wariant z logiem: `--logs` przed `%command%`; F8 zapisuje `bin/er_engine.log`.
   - Gdy gra startuje bez moda albo jest błąd `Couldn't create process: 2e4`: spróbuj też z `--no-game-path`, a wyjście Steama uruchomionego z terminala (`steam`) zachowaj dla mnie.
   - Największa niewiadoma: czy launcher ME2 pod Protonem przyjmie ścieżkę gry (`-p`). Dlatego jest opcja `--no-game-path`.

## Na bieżąco, przy zwykłej grze

- **Zawieszenie postaci** (stoi w miejscu mimo wciśniętego kierunku): F8 od razu.
- **Paczka 0.5.5:** jeśli zagrasz z zainstalowanej paczki (launcher wydania zaproponuje aktualizację), napisz, czy wszystko działa jak w wersji testowej. Nowe w niej: sprint w każdą stronę przy namierzeniu (v3.1), Gwyn z dwiema fazami (w fazie testów), `Launch_with_logs.bat` (log i F8 dla testerów), skrypt pod Linuksa. Przy okazji sprawdź raz `Launch_with_logs.bat`: F8 w grze, potem czy `bin\er_engine.log` powstał i ma wpisy z gry.

## Znane problemy (nie trzeba zgłaszać)

- **Zawieszenie w arenie Stray Demona** (test 15.11: wiele razy, gdzie indziej rzadko). Przyczyna jest w logu do zbadania; na razie odłożone.
- **Stray Demon ma tylko 2 ataki:** paczka zmienia tylko animacje, AI jest z gry. Nowe ataki wymagają pracy nad AI (na później).
- **Lądowanie po ataku z wyskoku: przeskok pozy** (biodra i nogi w dół, przy katanie też ręce), poza R2 młota. Próba z 15.11 w nocy (szybsze opadanie, żeby ziemia przyszła przed uderzeniem) wyłączona: łuk wyglądał na ściągnięty w dół. Druga próba (wolniejszy zamach w powietrzu) też wyłączona: lądowanie wypadało we właściwej chwili, a przeskok przy R2 katany został i doszło mignięcie na początku zamachu. Temat odłożony.
- Broń wchodzi w teren przy R2 ze sprintu i z wyskoku (koszt tego, że się nie odbija; w ER tak samo).
- Przedmiot, którego masz już 99, zostaje na ziemi bez komunikatu (tak działa gra).

## Decyzje bez gry

- **Gwyn, faza 2** (gracz 15.11: „jak najbardziej za”): nowe ataki SoC (piorun w ziemię, włócznia pioruna, burza piorunów, kombinacja z wybuchem).
  - Decyzje 15.11: faza 1 = Gwyn z DS1, faza 2 = cały SoC, przejście przy 0 HP z odnowieniem paska.
  - Etap 0 zrobiony bez gry. Launcher bierze parametry bossów ze wspólnego pliku `files_bosses_param`.
  - Etap 1 (dwie fazy, przejście, bez nowych ataków) jest w teście: punkt 2.
  - Otwarte pytania:
    - kolor piorunów (złoty Sunlight Spear czy niebieski);
    - rozmiar wybuchów (11,5 m jak w DS3 czy dopasowany do efektu);
    - burza: 12 czy 24 pioruny;
    - dodatki (doskok, ciosy z opóźnieniem, buff po chwycie);
    - czy Gwyn ma wejść do wydania.
- **Postura i cios krytyczny po przełamaniu** (jak w ER): czy zaczynamy od Black Knighta? Wynik analizy: animacja 2100 Black Knighta ma w TAE zdarzenia JumpTable 41 i typ 67, których zwykłe animacje nie mają. Hipoteza: „można wykonać ripostę”. Test: przełącznik w nocnej DLL, który po kilku trafieniach zleca 2100 najbliższemu Black Knightowi.

## Zaliczone ostatnio

- 16.11 (na `main`): sprint przy namierzeniu w każdą stronę, wersja 3.1. Gracz: hamowanie i powrót do celu bardzo dobre, obroty w trakcie sprintu bardzo dobre, różne kąty bez błędów. Start jeszcze trochę drewniany: postać od razu się obraca i zwalnia (z logu: przy zmianie animacji biegu tyłem → bokiem → przodem prędkość spada z ~4 do 2,3–3 m/s, sprint dochodzi do 6 m/s dopiero po ~0,3 s). Poprawka startu: następna wersja.
- 15.11 noc (na `main`, wejdzie do następnego wydania): sterowanie w powietrzu przy dalekim skoku w dół. Postać obraca się do gałki przez cały lot, wolno jak w ER (60°/s); gracz: „na początku większa sterowność, potem mniejsza, ale działa”.
- 15.11 noc: Capra Demon jako Omen Killer w porządku. Gaping Dragon bez krytycznych problemów (gracz chce do niego kiedyś wrócić, ma potencjał).
- 15.11 wieczór (weszło do 0.5.3): skok z lądowaniem w bieg i w sprint, bez hamowania, bez poślizgu (także po skoku na wyższe), bez przeskoku rąk i broni w locie.
- 15.11 (decyzja): wstawanie po powaleniu zostaje jak w DSR. Pierwszy unik i ruch są w tych samych chwilach co w ER; ER różni się tylko wyglądem (postać wstaje ~0,3 s wcześniej) i krótszą nietykalnością na ziemi.
- 15.11 (po południu): bronie z unikalnym zestawem ruchów (Quelaag's Furysword, Dark Silver Tracer). Zwykłe ataki zostają unikalne, dodane (z wyskoku, ze sprintu) są z grupy broni, atak po przewrocie dobry. Atak z biegu Dark Silver Tracer wygląda jak R2: to oryginał DS1 (w DSR to sztylet, grupa 20; klip `a20_4500` jest taki sam w plikach gry). R2 ze sprintu w stylu ER mają na razie tylko młoty (grupy 33 i 35).
