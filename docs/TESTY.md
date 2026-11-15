# Testy do zrobienia

Stan: 2026-11-15, po wydaniu 0.5.2. **To jedyna aktualna lista testów.** Listy w raportach nocnych (14.11, 15.11) są już nieaktualne. Po każdym teście poprawiam ten plik.

## Jak uruchomić

- **Prawie wszystko:** `dist\mods\bossy_nightreign\launch_test_all.bat`.
  - DLL ma to samo co wydanie 0.5.2, plus włączony nowy skok (punkt 1).
  - Zawiera wszystkich przerobionych bossów: Artoriasa, Capra, Gaping, Centipede, Stray i Gwyna.
- **Wyjątek, punkt 7 (Centipede):** `dist\mods\c0000_er_engine\launch_er_engine.bat` (sam mod, bez bossów).
- Gdy coś jest nie tak: **F8** od razu (zapisuje log). W wiadomości napisz mniej więcej godzinę.

## Do przetestowania

1. **Skok z biegu i ze sprintu** (nowe ustawienie `FallSpeedFromGround`).
   - Z biegu: po lądowaniu postać nie hamuje, od razu biegnie dalej.
   - Ze sprintu: po lądowaniu bez poślizgu modelu.
   - Czy skok z biegu nadal wystarcza na przeskoki, które wcześniej się udawały.
   - Porównanie (jeśli nie wiesz, czy jest lepiej): ustaw `FallSpeedFromGround=0` w `dist\mods\c0000_er_engine_night\bin\er_engine.ini` i uruchom grę ponownie.
2. **Bronie z całym unikalnym zestawem ruchów** (dowolna, którą masz: Server, Murakumo, Quelaag's Furysword, Great Scythe, Gravelord Sword, Crescent Axe, Dark Silver Tracer, Gold Tracer).
   - R1 kilka razy pod rząd, R2, atak z biegu, atak po przewrocie.
   - Czy przyspieszony zamach wygląda naturalnie i czy tempo pasuje do innych broni.
3. **Gwyn** (Kiln of the First Flame), ruchy z Soul of Cinder z DS3.
   - Wygląd ataków: miecz, płaszcz, broda, włosy (czy się ruszają, czy nic nie odstaje).
   - Czy ciosy trafiają tam, gdzie widać miecz.
   - Chwyt i rzut działają jak wcześniej.
   - Nowe kombinacje (np. kopniak → chwyt, pchnięcie → cięcie oburącz) i tempo walki.
4. **Gaping Dragon** (Depths).
   - Fala po skoku z wysoka przychodzi razem z uderzeniem, nie później.
   - Szarża trafia najwyżej raz (wcześniej potrafiła zabić jednym przejazdem).
5. **Capra Demon → Omen Killer** (Undead Burg).
   - Ogon się porusza i nie wchodzi w podłogę.
   - Czy ataki trafiają częściej niż ostatnio (wcześniej część przelatywała nad postacią).
   - Ręce i tasaki opuszczone jak w ER, nie uniesione.
6. **Stray Demon** (Azyl, powrót).
   - Podmuch po skoku (ugniecenie zadem) i wybuch wokół niego przychodzą razem z uderzeniem.
7. **Centipede Demon: test rozstrzygający** (Demon Ruins), z `launch_er_engine.bat`, **bez paczek bossów**.
   - Czy w oryginale da się trafić wyciągniętą mackę, zwłaszcza jej koniec z paszczą.
   - Od tego zależy, czy problem jest w naszych zmianach, czy w samej grze.

## Na bieżąco, przy zwykłej grze

- **Zawieszenie postaci** (stoi w miejscu mimo wciśniętego kierunku): F8 od razu.
- **Paczka 0.5.2:** jeśli zagrasz z zainstalowanej paczki (launcher wydania), napisz, czy wszystko działa jak w wersji testowej. Samej paczki nikt jeszcze nie uruchamiał.

## Znane problemy (nie trzeba zgłaszać)

- Broń wchodzi w teren przy R2 ze sprintu i z wyskoku (koszt tego, że się nie odbija; w ER tak samo).
- Lądowanie po R1 z wyskoku: postać jest jeszcze ściągana w dół.
- Sprint przy namierzeniu: postać biegnie zamiast sprintować (czeka na poprawkę).
- Przedmiot, którego masz już 99, zostaje na ziemi bez komunikatu (tak działa gra).

## Decyzje bez gry

- **Postura i cios krytyczny po przełamaniu** (jak w ER): czy zaczynamy od Black Knighta? Wynik analizy: animacja 2100 Black Knighta ma w TAE zdarzenia JumpTable 41 i typ 67, których zwykłe animacje nie mają. Hipoteza: „można wykonać ripostę”. Test: przełącznik w nocnej DLL, który po kilku trafieniach zleca 2100 najbliższemu Black Knightowi.

## Zaliczone ostatnio

- 15.11 (weszło do 0.5.2): podnoszenie przedmiotów; R2 ze sprintu młotów; R2 z wyskoku i ze sprintu Great Club i Smough's Hammer; brak odbijania od terenu; tempo ataków unikalnych.
- 14.11: Estus chowa broń; podnoszenie w marszu; ataki z wyskoku katany i pięści; osłona przed zawieszeniem po wczytaniu.
