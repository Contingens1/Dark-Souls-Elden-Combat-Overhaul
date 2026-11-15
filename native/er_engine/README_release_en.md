# ER-Inspired DSR Remake v{VERSION} — Dark Souls Remastered

Elden Ring-style movement, dodging, jumping and drinking Estus in Dark Souls Remastered. Since 0.4.0 also the first reworked boss: Knight Artorias, with a second phase and attacks from Nightreign.

## Requirements

> **Mod Engine 2 with Dark Souls Remastered support is REQUIRED to run the mod.**
> Without it the mod will not start. Mod Engine 2 is not included in the package.

- **Mod Engine 2 with Dark Souls Remastered support** — a release that contains the file `launchmod_darksoulsremastered.bat` in its folder (the launcher accepts `-t dsr`). Working DSR build: <https://www.nexusmods.com/darksoulsremastered/mods/790>. The official GitHub release (`ModEngine-2.1.0.0`) does not support DSR. Older releases made only for Dark Souls 3 / Elden Ring will not work either. Unpack it anywhere (it does not have to be in the game folder).
- **Dark Souls Remastered** (Steam), exe with SHA-256 `A45AAA36…` (the version current at the time of the mod release). The setup tool checks the same and warns if you have a different one.
- Windows 10 / 11.

## Running (no installation)

The mod does not install anything: it does not change game files or Mod Engine 2. Just unpack the folder and point the tool once to where Mod Engine 2 is.

1. Unpack the **whole** archive into a normal folder, e.g. `Documents\ER-Inspired_DSR_Remake_v{VERSION}`. **Do not unpack into the game folder.**
2. Run **`Setup.bat`** (double-click). A setup window opens.
3. The tool searches your drives for Mod Engine 2. If it does not find it, or finds the wrong one, click **Browse...** (*Przeglądaj...*) and select the folder containing `modengine2_launcher.exe`.
4. A green message means a correct Mod Engine 2 with DSR support. Click **Create launcher** (*Utwórz launcher*).
5. Start the game with the mod using **`Launch_ER-Inspired_DSR_Remake.bat`** or the desktop shortcut (if you left shortcut creation checked).

**What `Setup.bat` does:** it saves the path to Mod Engine 2, creates two files in the mod folder (`ER-Inspired_DSR_Remake.toml` and `Launch_ER-Inspired_DSR_Remake.bat`) and an optional desktop shortcut. Nothing else: it does not copy anything into the game or Mod Engine 2 and does not register anything in the system.

If you move the Mod Engine 2 folder elsewhere, run `Setup.bat` again. You can move the mod folder freely; the desktop shortcut then has to be created again (run `Setup.bat` again).

**Uninstalling the mod:** delete the mod folder and the shortcut. Game files are not modified — the game started from Steam always runs without the mod.

## Updates *(since 0.3.0)*

Before each game start, the launcher checks GitHub for a newer version of the mod (this takes a few seconds at most; without internet the game starts normally). If there is one, it asks whether to download and install it:
- **Yes** — downloads the package, replaces the files in the mod folder and starts the game on the new version. Your settings in `bin\er_engine.ini` are kept, and so are the launcher and the Mod Engine 2 path. The previous version goes to `_backup\v<version>` (to revert, copy its contents back into the mod folder).
- **No** — the game starts on the current version; the question will return at the next start.

An update changes only the files in the mod folder — it does not touch the game or Mod Engine 2. To disable the check: `CheckForUpdates=0` in `bin\er_engine.ini`. Manual check: `powershell -ExecutionPolicy Bypass -File setup\Update.ps1 -Manual`.

**Moving from 0.1.0 / 0.2.0:** these versions have no updater. Unpack the new version into a new folder and run `Setup.bat` again (the new launcher includes the update check). Move your settings from `bin\er_engine.ini` by hand if you changed them.

**Windowless setup** (advanced): `Setup.bat -Silent -ModEngine2Path "D:\path\to\ModEngine2" [-Shortcut]`. Manually, without `Setup.bat`: `modengine2_launcher.exe -t dsr -c "<mod folder>\ER-Inspired_DSR_Remake.toml"`.

## IMPORTANT

- **Play offline only.** The mod changes how the game works in memory — online play risks a ban. The mod has no network block of its own; before launching, switch Steam to offline mode or set the game to start offline.
- On a different version of `DarkSoulsRemastered.exe` the hooks will not install and the DLL mechanics will not work (log: `bin\er_engine.log`).

## New in 0.5.2

Test version (pre-release): fixes checked in the game, but bugs may still appear. The package still contains only the Artorias boss from the reworked bosses.

- **Picking up items while moving: fixed a bug from 0.5.1.** After picking up an item while moving, following items could stay on the ground, and the character sometimes stopped in place.
- **R2 from a sprint** (hammers and great hammers, one-handed and two-handed): a running attack as in Elden Ring, instead of stopping and a normal R2.
- **Weapons with unique attacks** (e.g. Great Club, Smough's Hammer, Grant, Large Club, Claymore, Moonlight Greatsword):
  - they have the jump attacks of their ER weapon group (hammers also R2 from a sprint); before, R2 from a jump did not work;
  - their unique attacks now run at the same tempo as other weapons (matched to ER); before, they used the DSR tempo.
- **Jump attacks and R2 from a sprint no longer bounce off the ground**, including when jumping uphill. The weapon may sink into the ground, as in Elden Ring.
- An item of which you already have the maximum amount (e.g. 99 moss) stays on the ground without a message. This is how the game itself works.
- **Known problems:** when landing after R1 the character is still pulled down; after a jump from a sprint the model slides slightly, and after a jump from a run the character slows down a little.

## New in 0.5.1

Test version (pre-release): fixes checked in the game, but bugs may still appear. The package still contains only the Artorias boss from the reworked bosses.

- **Estus hides the weapon** while drinking, as in Elden Ring, standing still and while moving. The hand holding the flask goes to the mouth, without the weapon flickering between sips.
- **Picking up items while moving** (as in ER): the character does not stop, the item goes to the inventory. To disable: `PickupWhileMoving=0` in `bin\er_engine.ini`.
- **Jump attacks:**
  - katana with its own ER jump attacks (previously stand-ins) and the correct hand position; katana R2 in the air works;
  - fists and hammer R2 with ER attacks;
  - landing without sliding and without the pose jump, no more legs snapping at the end of a landing (section `[Jump]` in `bin\er_engine.ini`).
- **Known problems:** when landing after R1 the character is still clearly pulled down (less so with R2); a hammer on R2 can bounce off the ground, especially after jumping onto higher ground.

## New in 0.5.0

- **Artorias — refined second-phase effects** (checked in the game):
  - A dense dark aura is visible on the sword throughout the second phase. In 0.4.0 the effect did not show on the sword at all. The aura on the body was removed so it does not blend with the sword.
  - Three jumps (flips ending with a downward strike and two large jumps) announce sparks from the sword tip in the air.
  - On impact the sword sinks into the ground, and a moment later a small dark explosion with sound erupts within 2 m around the blade. In 0.4.0 this explosion dealt no damage.
  - A well-timed dodge avoids both the strike and the explosion. If you roll too early, the explosion will hit you.
  - The jump after the flips has a sword-on-ground impact sound, and the first of the two large jumps is shorter (12 m instead of 15 m).
  - The transition to the second phase starts right after the current strike ends (previously sometimes delayed by up to 3 s).

## New in 0.4.0

- **Knight Artorias — reworked fight with a second phase** (section "Artorias"). Early version: the second-phase effects (smoke on the sword, sparks before a strike, explosion on landing of jumps) still need checking and polishing.
- **Free sprint:** an enemy already fighting the player (chasing or attacking them) within 40 m also disables free sprint — even without lock-on and without a hit.
- **Roll hang:** when the character stands still after a roll despite the direction being held, the mod restores free movement (`HangRepair`, section "Settings"). The fix is based on two recorded cases — not yet verified on a real hang.

## Artorias *(since 0.4.0)*

- **Phase 1** — only Dark Souls attacks, no empowerment; shorter than the original fight.
- **Transition** — when the HP bar drops to zero, Artorias does not die: he kneels in an empowerment animation (it cannot be interrupted or damaged), restores full HP, and ends with an explosion and two rings of dark orbs.
- **Phase 2** — permanent empowerment (stronger hits) and new attacks ported from Elden Ring Nightreign: long combos, charges with slashes, two large jumps in a row, flips ending with a downward strike. Throughout the phase the sword has a dark aura; the jumps announce sparks from the sword tip, and after the sword is driven into the ground a small dark explosion erupts.
- Both phases together have about 1.2× the HP of the original Artorias. After killing him in phase 2, Artorias gives his boss soul; souls appear with a delay of a few seconds.
- Disabling the second phase: `ArtoriasPhase2=0` in `bin\er_engine.ini` (default `2`, see "Settings"). Nightreign attacks stay in the files, but without the transition Artorias dies at 0 HP.

## New in 0.3.0

- **Updates from the launcher** (section "Updates").
- **Sprinting outside combat does not use stamina** (as in ER). Rolls, jumps and attacks always cost stamina.
- **A hit interrupts drinking and item use** — the flask no longer stays in hand when knocked down.
- **Souls and humanity while moving** — while using them the character slows to a walk, as with Estus (previously it could run and had its direction locked).
- **Estus:** the speed limit no longer switches off during a long series of sips.
- **Lock-on rolls:** a roll queued during another animation (e.g. a hit reaction) keeps the chosen direction instead of going forward; the roll on key release also works with the stick at a diagonal (forward–side).
- **Halberds:** an attack from a run-up is no longer unnaturally fast.

## What it changes

| Mechanic | Description |
|---|---|
| **Jump from ER** | Takeoff animations from Elden Ring (standing, walking, sprinting) with a crouch and a height of about 1.15 m. Air control: turning and drifting with the stick/WASD. A separate jump button from standing and walking. Jumping down from a ledge keeps momentum. No roll after landing. |
| **Jump attacks from ER** *(early version)* | An attack during a jump (R1 and R2, one-handed and two-handed) uses Elden Ring's jump attack animations: a swing in the air, the strike finished on the ground, recovery at ER timings. A press right after the jump is queued. 14 melee weapon groups. |
| **Roll in all directions** | When locked on, a roll in any direction relative to the camera instead of 4 directions (own implementation in `er_engine.dll`). Dodge buffer: a dodge pressed just before a direction is not lost. |
| **Sprint while locked on** *(since 0.2.0)* | When locked on, the roll fires on key release (as in ER and as in DSR without lock-on), so holding the key no longer makes a side or back roll. Sprint while locked on currently works only forward, as in DSR. |
| **Rolls and backsteps from ER** | Roll animations (4 load tiers × 4 directions) and backsteps from Elden Ring, with ER timings: faster exit from a roll, 13 frames of invincibility. Since 0.2.0 every action after a roll has its own ER timing (attack earliest, then item and another dodge, movement, guard) — a heavy roll can no longer be spammed. |
| **Walk, run and sprint from ER** | Movement animations from Elden Ring in all 9 weapon stance sets (unarmed, one-handed, two-handed, bow, crossbow, two-handed shield) and 3 load tiers. |
| **ER attack pace** | Attacks stay from DSR but are played faster in the parts where ER is faster: the commitment to a hit (max ×1.35) and the ending up to the next action window (max ×2). It never slows down. Covers R1 one-handed and two-handed, the running attack and the roll attack for 14 melee weapon groups (not fists, shields, bows, crossbows or catalysts). R2: a faster ending after a hit. Heavy weapons (great hammers, great axes) get a gentler ending speed-up (max ×1.5). |
| **Estus while moving** | Drinking while walking, including turning (also from an empty flask); during drinking the character slows to a slow walk and does not sprint (as in ER). Since 0.2.0 the timings after a sip match ER: attack, dodge and guard 0.2 s after the flask starts going down, full movement after 0.3 s. |
| **Lock-on camera** | Distance, field of view and camera height while locked on to a target, as in Elden Ring. |

## Controls

- **Jump:** `J` (keyboard) or **L3** (pressing the left stick). Jump from a sprint as in DSR (the roll button while sprinting).
- **Jump attack:** the normal attack button (R1 / R2) during a jump.
- **Quick exit to desktop:** hold `Ctrl+Q` for 1 s (like Alt+F4 — not during a save).

## Settings

`bin\er_engine.ini`:
- `OmniRoll=1` — roll in all directions when locked on (`0` = 4 directions as in DSR),
- `RollBuffer=1` — dodge key buffer (`0` = off),
- `LockOnSprint=1` — roll on key release when locked on (`0` = as in DSR: side and back rolls fire immediately on press),
- `AttackFaceTarget=1` — an attack right after a roll while locked on turns the character to the target, as in Elden Ring (`0` = as in DSR: the strike goes in the roll direction),
- `FreeOutOfCombat=1` (section `[Stamina]`) — outside combat sprinting does not use stamina; rolls, jumps and attacks always cost stamina (`0` = as in DSR). "Combat" = a locked-on target, HP loss in the last 8 s, or a weapon attack in the last 5 s.
- `HitCancelsItem=1` (section `[Items]`) — a hit reaction interrupts drinking Estus / using an item (`0` = off; the flask may then stay in hand when knocked down),
- `HangRepair=1` (section `[Fixes]`) — repair of a hang after a roll (`0` = off),
- `ArtoriasPhase2=2` (section `[Bosses]`) — Artorias's second phase: `2` = automatic (on when the boss files are in the package), `1` = on, `0` = off,
- `CheckForUpdates=1` (section `[Update]`) — check for a new version at startup (`0` = off).

## Known limitations

- Jump attacks: on touching the ground there is a slight jerk of the character and a small animation skip. Very long falls: the swing ends in the air and ordinary falling continues.
- Sprint while locked on works only forward (as in DSR); sideways and backwards the character walks.
- Sometimes the character can "hang" without animation (stands still despite a held direction) until the next hit or action. Since 0.4.0 this case after a roll is repaired automatically (`HangRepair`); if the hang still happens, report it.
- Artorias: balance tested only on NG+; the explosion on jumps still looks modest (the mechanic matters more). The transition to the second phase waits until Artorias finishes a strike that cannot be interrupted.
- A slight slide when landing after a jump; with a weapon, hands jump to a different pose on the jump → fall transition.
- A shield block while sprinting looks unnatural (sprint animation from ER).
- A roll ending against a wall while locked on can occasionally freeze the character in a pose until the next action.

## Credits

- **Player Animations Repository** (Nexus Mods, DSR #748) — Elden Ring animations ported to the DSR skeleton, used in the `files\chr\*.anibnd.dcx` files. **Do not redistribute this package further without the repository authors' permission.**
- **DSROmniRoll** (Nexus Mods, DSR #1378) and **Simple Estus Walking** — ideas that our own implementations of rolling in all directions and drinking while moving are based on. Their files are not part of this package.
- **Elden Ring Nightreign** (FromSoftware) — second-phase Artorias attack animations ported to his DSR skeleton (`files\chr\c4100.anibnd.dcx`).
- **Mod Engine 2** (soulsmods; DSR-capable build from AltimorFP, distributed in the Nikolay97 package) — mod loading (not included).
- **MinHook** (Tsuda Kageyu) — hooking library compiled into `er_engine.dll`.

Tools: SoulsFormats, soulstruct, Ghidra, DS Anim Studio (TAE template).
