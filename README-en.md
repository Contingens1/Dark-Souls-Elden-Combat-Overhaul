# ER-Inspired DSR Remake

Polish version: [README.md](README.md)

A gameplay and engine modification for **Dark Souls: Remastered** that brings the movement responsiveness, dodge mechanics, jumping, drinking Estus while moving, and combat pace of **Elden Ring** to the first Dark Souls.

## Main mechanics

| Mechanic | Description |
|---|---|
| **Elden Ring jump** | Takeoff animations from Elden Ring (standing, walking, sprinting) on a dedicated button, air control (turning and drifting), momentum kept when jumping off a ledge, and no roll after landing. |
| **Jump attacks** | Attacks during a jump (R1 and R2, one-handed and two-handed) using Elden Ring's in-air swing animations and ground finishers, with input queueing for 14 melee weapon groups. |
| **Omni-Roll (all directions)** | Custom C++ implementation (`er_engine.dll`) that allows a dodge in any direction relative to the camera while locked on, with dodge input buffering. |
| **Sprint while locked on** | The roll fires on key release (as in ER), preventing accidental side and back rolls when you try to sprint. |
| **Elden Ring rolls and backsteps** | The full set of dodge animations (4 load tiers × 4 directions) and backsteps, with invincibility frames and recovery windows matched to Elden Ring. |
| **Walk, run and sprint from ER** | Locomotion animations for all 9 weapon stances and 3 encumbrance tiers. |
| **Elden Ring attack pace** | Dynamic speed scaling of selected DSR attack phases (commitment and recovery windows) matched to Elden Ring timings for 14 melee weapon groups. |
| **Estus while moving** | Drinking and turning while walking (including from an empty flask), with cancel windows into attack, dodge and guard matched to ER. The weapon hides while drinking, as in ER. |
| **Picking up while moving** | Items are picked up without stopping, as in ER. |
| **Free sprint** | Outside combat, sprinting does not use stamina, as in ER. |
| **Lock-on camera** | Adjusted distance, field of view (FOV) and height of the camera while locked on to a target. |

## Bosses

Boss reworks are in progress. The package contains:

* **Knight Artorias** — a second phase with attacks from Nightreign.
* **Capra Demon** *(in testing, since 0.5.4)* — some strikes replaced with Omen Killer attacks from Elden Ring.
* **Gaping Dragon** *(in testing, since 0.5.4)* — a new AI modelled on Nightreign.

More bosses are planned.

## Known issues

The mod is under development. Below are the known issues that do not work properly yet:

* **Jump attacks are unfinished.** Landing after attacks in a jump can flicker or jump between animation poses. Not every weapon has a full set of jump attacks yet: for example, the katana and the regular axe attack use placeholder animations, and fist weapons have no jump attacks. R2 from a sprint or a jump can clip into the ground, as it does in ER.
* **Jumping through walls (intentional, kept for now).** A jump can start next to a wall and pass through it. This allows interesting skips, so it is not blocked for now.
* **The shield block in a sprint looks odd (intentional, kept for now).** The ER sprint animation is played on the upper body, which looks unnatural.
* **Camera:** monsters and the environment can block the camera, and the camera sometimes rises up sharply on its own. Fixes are planned.
* **Sprint while locked on only works forward**, as in the original game. Sprinting sideways and backwards like in ER is planned.
* **Character freeze (rare):** after a roll, the character can stand without animation for a few seconds even while the stick is pushed. It usually ends with a hit or another roll. The cause is not known yet. The package has an automatic unlock attempt, which may not work.


## Repository layout

* `native/er_engine/` — source code of the hook library (`er_engine.dll`, based on MinHook), attack and jump speed tables, and the scripts that build release packages.
* `native/ghidra_scripts/` — scripts that automate static analysis and decompilation of game engine functions in Ghidra.
* `tools/` — Python and C# tools for unpacking containers (`.dcx`, `.bnd`), syncing `.tae` events, mapping animations, and editing parameters and ESD states.
* `docs/` — technical documentation, animation ID maps and memory offset references.

## Download and installation

Ready-to-run packages for testers (no compilation needed) are on the **[Releases](../../releases)** page. Detailed instructions for running the mod through **Mod Engine 2** are included in each archive (`README_release.md`).

## Acknowledgements and resources

* **Player Animations Repository** (Nexus Mods, DSR #748) — Elden Ring animations ported to the DSR skeleton (used in the `.anibnd.dcx` files). **Further redistribution of these files without the repository authors' permission is prohibited.**
* **DSROmniRoll** (Nexus Mods, DSR #1378) and **Simple Estus Walking** — conceptual inspiration for our own implementations of omni-directional rolling and drinking while moving (their files are not part of this project).
* **Mod Engine 2** (`soulsmods`) — mod loading environment for Dark Souls: Remastered.
* **MinHook** (Tsuda Kageyu) — hooking library used in `er_engine.dll`.
* **Elden Ring Nightreign** (FromSoftware) — second-phase Artorias attack animations ported into the package; Gaping Dragon animations and AI logic as the model.
* **Elden Ring** (FromSoftware) — Omen Killer attack animations ported to Capra Demon.
* **Community tools:** SoulsFormats, soulstruct, Ghidra, DS Anim Studio.

**License:** the project code (`native/`, `tools/` and scripts) is released under the **GPL-3.0 License**; see [LICENSE](LICENSE). The license does not cover game files, Elden Ring and Nightreign animations, or third-party tools (Mod Engine 2, MinHook, Ghidra, etc.), which remain under their own licenses.

## Disclaimer

This is an unofficial, non-commercial, fan-made modification created for educational and personal use.

All original game assets, animations, names, and trademarks belong to **FromSoftware, Inc.** and **Bandai Namco Entertainment Inc.**

To use this mod, you must legally own copies of the respective games (*Dark Souls: Remastered*, *Elden Ring* and *Elden Ring Nightreign*). Do not monetize, re-upload, or redistribute these files commercially.

## Support the Project

This mod is and will always remain 100% free and open-source. However, if you enjoy my work and want to support future updates, feel free to buy me a coffee:

☕ **[Support on Buy Me a Coffee](https://www.buymeacoffee.com/contingens)**

[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-ffdd00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://www.buymeacoffee.com/contingens)
