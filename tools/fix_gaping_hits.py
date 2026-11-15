"""
fix_gaping_hits.py - Gaping Dragon (c5260) hit timing fixes in a test package's anibnd (TAE only).

Player test 2026-11-14 (NR-AI package):
  1. Jump crush 3007 / 3009: "the shock wave comes late after the impact". Clip (tools/clip_height_timeline.py): the
     body reaches the ground at ~4.15 s; dust / camera shake / sound start 4.17 s. Damage: legs-wind 171 at 4.20 s,
     body 172 at 4.27 s, wind 173 (5 m) at 4.37 s (3009: +0.03 s). Fix: everything on the landing frame - body 172
     from 0.04 s before the dust, legs-wind 171 and wind 173 from the dust (same end times).
  2. Charge 3004: the charge hit 140 (310 damage, damage level 10) is re-opened 14 times every ~0.37 s and the six
     body-part hits 300-305 (100 each) 4-5 times each, so a player caught in the charge is hit again and again
     ("a few ticks one-shot me from almost full HP with 50 Vigor"; the original does the same). Fix: one window per
     hit from its first start to its last end - each can hit once per charge.
Never writes the game's or the main mod's files.

  python tools\\fix_gaping_hits.py --anibnd dist\\mods\\bossy_nightreign\\files_c5260_ai\\chr\\c5260.anibnd.dcx
"""
from __future__ import annotations

import argparse
import ntpath
import shutil
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sfbridge import load_soulsformats, read_binder, read_file, to_memory  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
JUMPS = (3007, 3009)
CHARGE = 3004
FX_LAND = 15263            # TAE 96 spawn FFX: landing dust
WIND_LEGS, BODY, WIND = 171, 172, 173


def judge(e) -> int | None:
    p = bytes(e.GetParameterBytes(False))
    return struct.unpack_from("<i", p, 8)[0] if int(e.Type) == 1 and len(p) >= 12 else None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--anibnd", type=Path, required=True)
    args = ap.parse_args(argv)
    path = args.anibnd.resolve()
    if "steamapps" in str(path).lower() or "c0000_er_engine" in str(path):
        sys.exit("ERROR: only test packages are patched")
    backup = ROOT / "work" / f"{path.stem.split('.')[0]}.anibnd.{path.parent.parent.name}_PRE_HITFIX_STABLE.dcx"
    if not backup.exists():
        shutil.copyfile(path, backup)
        print(f"backup: {backup}")
    load_soulsformats()
    from SoulsFormats import BND3, TAE

    bnd = read_binder(BND3, str(path))
    tf = next(f for f in bnd.Files if ntpath.basename(str(f.Name)).lower().endswith(".tae"))
    tae = read_file(TAE, tf.Bytes)
    anims = {int(a.ID): a for a in tae.Animations}
    for aid in JUMPS:
        ev = list(anims[aid].Events)
        fx = [e for e in ev if int(e.Type) == 96 and struct.unpack_from("<i", bytes(e.GetParameterBytes(False)))[0] == FX_LAND]
        if not fx:
            print(f"  {aid}: no landing dust {FX_LAND} - skipped")
            continue
        t0 = min(float(e.StartTime) for e in fx)
        for e in ev:
            j = judge(e)
            if j not in (WIND_LEGS, BODY, WIND):
                continue
            old = (float(e.StartTime), float(e.EndTime))
            if j == BODY:
                e.StartTime, e.EndTime = t0 - 0.04, t0 + 0.06
            else:
                e.StartTime = t0
            print(f"  {aid}: hit {j} {old[0]:.2f}-{old[1]:.2f} -> {float(e.StartTime):.2f}-{float(e.EndTime):.2f} s (dust {t0:.2f} s)")
    a = anims[CHARGE]
    by = {}
    for e in list(a.Events):
        j = judge(e)
        if j is not None:
            by.setdefault(j, []).append(e)
    for j, es in sorted(by.items()):
        if len(es) < 2:
            continue
        s, en = min(float(e.StartTime) for e in es), max(float(e.EndTime) for e in es)
        first = min(es, key=lambda e: float(e.StartTime))
        for e in es:
            if e is not first:
                a.Events.Remove(e)
        first.StartTime, first.EndTime = s, en
        print(f"  {CHARGE}: hit {j}: {len(es)} windows -> one {s:.2f}-{en:.2f} s")
    tf.Bytes = to_memory(tae.Write())
    tmp = path.with_suffix(".tmp")
    bnd.Write(str(tmp))
    bnd.Dispose()
    tmp.replace(path)
    print(f"OK: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
