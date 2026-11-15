"""Gwyn (c5370, AI 537000) battle script with Soul of Cinder's phase-2 combos (DS3 LastBoss_Gwyn) - build step.

Source: work/boss_ai/537000_battle.soc_ai.lua = the decompiled DS1 script (work/boss_ai/dsr_m18_00/) with the
changes marked "(mod)":
  - Act01: 3000 -> 3011 and 3000 -> 3013 -> 3014 / 3016 next to the DS1 chains (SoC Act01);
  - Act03: thrust 3008 alone 25 %, else into 3012 / 3009 / the grab 3006 (SoC Act03);
  - Act04: lunge 3010 into the two-hand thrust 3015 (SoC Act04);
  - Act09: kick 3021 into the grab 3006 (SoC Act08, grab cooldown timer 0 as in DS1);
  - side steps after combos 30 % instead of always (SoC keeps pressing).
The decompiler writes decimals with a comma (locale); they are turned back into points here. Writes the Kiln of
the First Flame map script (m18_00_00_00) of the Gwyn test package.

  python tools/make_gwyn_ai.py
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "work" / "boss_ai" / "537000_battle.soc_ai.lua"
TMP = ROOT / "work" / "boss_ai" / "537000_battle.soc_ai.build.lua"
OUT = ROOT / "dist" / "mods" / "bossy_nightreign" / "files_c5370_soc" / "script" / "m18_00_00_00.luabnd.dcx"


def main() -> int:
    text = SRC.read_text(encoding="shift_jis")
    fixed = re.sub(r"(\d),(\d)", r"\1.\2", text)
    TMP.write_text(fixed, encoding="shift_jis")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    rc = subprocess.call([sys.executable, str(ROOT / "tools" / "ai_lua.py"), "build", "m18_00_00_00",
                          "537000_battle.lua", str(TMP), str(OUT)])
    if rc == 0:
        rc = subprocess.call([sys.executable, str(ROOT / "tools" / "ai_lua.py"), "verify", str(OUT), "537000_battle.lua"])
    return rc


if __name__ == "__main__":
    sys.exit(main())
