"""Print rows of one DSR param (read only): ID, row name and chosen fields (all non-zero fields if none given).

  python tools/param_rows.py BehaviorParam Behavior --ids 205260170-205260173
  python tools/param_rows.py AtkParam_Npc AtkParam --ids 526000300 --fields atkPhys hit0_Radius
Def name = the paramdef XML in Smithbox Defs (e.g. Behavior, AtkParam, Bullet, NpcParam).
Reads the main mod's GameParam (the game's own when --vanilla).
"""
from __future__ import annotations

import argparse
import ntpath
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sfbridge import load_soulsformats, read_binder, read_file  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
MOD = ROOT / "dist/mods/c0000_er_engine/files/param/GameParam/GameParam.parambnd.dcx"
GAME = Path(r"F:\SteamLibrary\steamapps\common\DARK SOULS REMASTERED\param\GameParam\GameParam.parambnd.dcx")
DEFS = Path(r"C:\Users\nemos\workspace\toolsy\Smithbox_2_2_6_2026_09_20_b\Assets\PARAM\DS1R\Defs")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("param", help="file name without .param, e.g. BehaviorParam")
    ap.add_argument("defname", help="paramdef name, e.g. Behavior")
    ap.add_argument("--ids", nargs="+", required=True, help="ID or lo-hi range")
    ap.add_argument("--fields", nargs="*", default=[])
    ap.add_argument("--vanilla", action="store_true")
    ap.add_argument("--src", type=Path)
    args = ap.parse_args(argv)
    src = args.src or (GAME if args.vanilla else MOD)
    ranges = [tuple(int(x) for x in (r.split("-") if "-" in r else (r, r))) for r in args.ids]
    sf = load_soulsformats()
    f = next(f for f in read_binder(sf.BND3, str(src)).Files
             if ntpath.basename(str(f.Name)).lower() == f"{args.param.lower()}.param")
    p = read_file(sf.PARAM, f.Bytes)
    p.ApplyParamdef(sf.PARAMDEF.XmlDeserialize(str(DEFS / f"{args.defname}.xml"), False))
    for r in p.Rows:
        rid = int(r.ID)
        if not any(lo <= rid <= hi for lo, hi in ranges):
            continue
        vals = []
        for c in r.Cells:
            name = str(c.Def.InternalName)
            if args.fields and name not in args.fields:
                continue
            v = c.Value
            try:
                if not args.fields and float(str(v)) == 0.0:
                    continue
            except ValueError:
                pass
            vals.append(f"{name}={v}")
        print(f"{rid}  [{r.Name or ''}]  " + "  ".join(vals))
    return 0


if __name__ == "__main__":
    sys.exit(main())
