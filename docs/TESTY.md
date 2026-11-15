# Testy do zrobienia

Stan: 2026-11-15 noc, po teście bossów; paczka nocna ma sterowanie w powietrzu przy skoku w dół (trzecia wersja). **To jedyna aktualna lista testów.** Po każdym teście poprawiam ten plik.

## Jak uruchomić

- **Prawie wszystko:** `dist\mods\bossy_nightreign\launch_test_all.bat`.
  - DLL ma to samo co wydanie 0.5.3, plus diagnostykę, F8 i poprawkę z punktu 1.
  - Zawiera wszystkich przerobionych bossów: Artoriasa, Capra, Gaping, Centipede, Stray i Gwyna.
- **Wyjątek, punkt 4 (Centipede):** `dist\mods\c0000_er_engine\launch_er_engine.bat` (sam mod, bez bossów).
- Gdy coś jest nie tak: **F8** od razu (zapisuje log). W wiadomości napisz mniej więcej godzinę.

## Do przetestowania

1. **Skok w dół: sterowanie w powietrzu** (trzecia wersja, 15.11 w nocy; w dwóch pierwszych obrót nie działał, bo gra w powietrzu zostawia kierunek z chwili wybicia). Po końcu animacji skoku postać obraca się w powietrzu do kierunku gałki, wolno jak w ER (60°/s, czyli pół obrotu w 3 s), a lot idzie za nią.
   - Daleki skok w dół (kilka metrów) z gałką w bok: czy postać skręca przez cały lot, także pod koniec.
   - Czy skręt nie jest za wolny ani za szybki i czy nie wygląda dziwnie (obrót w miejscu, szarpnięcie).
   - **F8 zaraz po wylądowaniu** (log zapisuje się tylko przy F8): pokaże, skąd DLL bierze kierunek gałki w powietrzu.
   - Skok po płaskim i w górę ma działać jak dotąd.
2. **Skok, przy okazji** (skok jest zaliczony i jest w 0.5.3; tych przypadków log jeszcze nie obejmował):
   - skok z miejsca;
   - skok z marszu (wolno, gałka lekko wychylona);
   - zaraz po lądowaniu: puszczenie gałki, unik, atak;
   - skok z bronią oburącz i z uniesioną tarczą.
3. **Gwyn** (Kiln of the First Flame), ruchy z Soul of Cinder z DS3. Test 15.11: miecz, płaszcz i ciosy wyglądają dobrze. Zostało:
   - chwyt i rzut działają jak wcześniej;
   - (przy okazji) włosy i broda.
   - Różnic względem DS1 prawie nie widać i tak ma być: druga faza SoC to te same ataki Gwyna w odświeżonych animacjach. Log walki potwierdza nowe AI (kombinacja 3000 → 3011 z SoC). Prawdziwie nowe ruchy to faza 2 (decyzja niżej).
4. **Centipede Demon: test rozstrzygający** (Demon Ruins), z `launch_er_engine.bat`, **bez paczek bossów**.
   - Czy w oryginale da się trafić wyciągniętą mackę, zwłaszcza jej koniec z paszczą.
   - Od tego zależy, czy problem jest w naszych zmianach, czy w samej grze.

## Na bieżąco, przy zwykłej grze

- **Zawieszenie postaci** (stoi w miejscu mimo wciśniętego kierunku): F8 od razu.
- **Paczka 0.5.3:** jeśli zagrasz z zainstalowanej paczki (launcher wydania zaproponuje aktualizację z 0.5.2), napisz, czy wszystko działa jak w wersji testowej.

## Znane problemy (nie trzeba zgłaszać)

- **Zawieszenie w arenie Stray Demona** (test 15.11: wiele razy, gdzie indziej rzadko). Przyczyna jest w logu do zbadania; na razie odłożone.
- **Stray Demon ma tylko 2 ataki:** paczka zmienia tylko animacje, AI jest z gry. Nowe ataki wymagają pracy nad AI (na później).
- **Lądowanie po ataku z wyskoku: przeskok pozy** (biodra i nogi w dół, przy katanie też ręce), poza R2 młota. Próba z 15.11 w nocy (szybsze opadanie, żeby ziemia przyszła przed uderzeniem) wyłączona: łuk wyglądał na ściągnięty w dół. Druga próba (wolniejszy zamach w powietrzu) też wyłączona: lądowanie wypadało we właściwej chwili, a przeskok przy R2 katany został i doszło mignięcie na początku zamachu.
- Broń wchodzi w teren przy R2 ze sprintu i z wyskoku (koszt tego, że się nie odbija; w ER tak samo).
- Sprint przy namierzeniu: postać biegnie zamiast sprintować (czeka na poprawkę).
- Przedmiot, którego masz już 99, zostaje na ziemi bez komunikatu (tak działa gra).

## Decyzje bez gry

- **Gwyn, faza 2** (gracz 15.11: „jak najbardziej za”): nowe ataki SoC (piorun w ziemię, włócznia pioruna, burza piorunów, kombinacja z wybuchem).
  - Decyzje 15.11: faza 1 = Gwyn z DS1, faza 2 = cały SoC, przejście przy 0 HP z odnowieniem paska.
  - Etap 0 zrobiony bez gry, **nic do testowania**. Launcher bierze teraz parametry bossów ze wspólnego pliku `files_bosses_param` (dziś identyczny z plikiem Artoriasa, więc Artorias działa jak dotąd).
  - Etap 1 po zakończeniu pracy nad skokiem.
  - Otwarte pytania:
    - kolor piorunów (złoty Sunlight Spear czy niebieski);
    - rozmiar wybuchów (11,5 m jak w DS3 czy dopasowany do efektu);
    - burza: 12 czy 24 pioruny;
    - dodatki (doskok, ciosy z opóźnieniem, buff po chwycie);
    - czy Gwyn ma wejść do wydania.
- **Postura i cios krytyczny po przełamaniu** (jak w ER): czy zaczynamy od Black Knighta? Wynik analizy: animacja 2100 Black Knighta ma w TAE zdarzenia JumpTable 41 i typ 67, których zwykłe animacje nie mają. Hipoteza: „można wykonać ripostę”. Test: przełącznik w nocnej DLL, który po kilku trafieniach zleca 2100 najbliższemu Black Knightowi.

## Zaliczone ostatnio

- 15.11 noc: Capra Demon jako Omen Killer w porządku. Gaping Dragon bez krytycznych problemów (gracz chce do niego kiedyś wrócić, ma potencjał).
- 15.11 wieczór (weszło do 0.5.3): skok z lądowaniem w bieg i w sprint, bez hamowania, bez poślizgu (także po skoku na wyższe), bez przeskoku rąk i broni w locie.
- 15.11 (decyzja): wstawanie po powaleniu zostaje jak w DSR. Pierwszy unik i ruch są w tych samych chwilach co w ER; ER różni się tylko wyglądem (postać wstaje ~0,3 s wcześniej) i krótszą nietykalnością na ziemi.
- 15.11 (po południu): bronie z unikalnym zestawem ruchów (Quelaag's Furysword, Dark Silver Tracer). Zwykłe ataki zostają unikalne, dodane (z wyskoku, ze sprintu) są z grupy broni, atak po przewrocie dobry. Atak z biegu Dark Silver Tracer wygląda jak R2: to oryginał DS1 (w DSR to sztylet, grupa 20; klip `a20_4500` jest taki sam w plikach gry). R2 ze sprintu w stylu ER mają na razie tylko młoty (grupy 33 i 35).
