"""
tae_move_hits.py - move attack (type 1) / bullet (type 2) events of a boss to a new start time (TAE only, test
packages only). The event is found by animation, type and behavior judge id (third int of its parameters, as in
tools/tae_events_dump.py); the end keeps its distance to the start unless END is given.

Stray Demon (player test 2026-11-14: shock waves come late after the impact, as in the original):
  3005 hip attack: impact / dust / camera shake 3.33 s, blast 151 from 3.53 s  -> 151 from 3.33 s
  3007 self-centred magic: spear impact 3.17 s, explosion bullet 170 at 3.50 s  -> 170 at 3.20 s
  python tools\\tae_move_hits.py --anibnd dist\\mods\\boss_stray_night\\files_c2230_night\\chr\\c2230.anibnd.dcx \\
         --move 3005:1:151:3.33 3007:2:170:3.20
"""
from __future__ import annotations

import argparse
import ntpath
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sfbridge import load_soulsformats, read_binder, read_file, to_memory  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--anibnd", type=Path, required=True)
    ap.add_argument("--move", nargs="+", required=True, metavar="ANIM:TYPE:JUDGE:START[:END]")
    args = ap.parse_args(argv)
    path = args.anibnd.resolve()
    if "steamapps" in str(path).lower() or "c0000_er_engine" in str(path):
        sys.exit("ERROR: only test packages are patched")
    load_soulsformats()
    from SoulsFormats import BND3, TAE
    bnd = read_binder(BND3, str(path))
    tf = next(f for f in bnd.Files if ntpath.basename(str(f.Name)).lower().endswith(".tae"))
    tae = read_file(TAE, tf.Bytes)
    anims = {int(a.ID): a for a in tae.Animations}
    for spec in args.move:
        parts = spec.split(":")
        aid, typ, judge, start = int(parts[0]), int(parts[1]), int(parts[2]), float(parts[3])
        end = float(parts[4]) if len(parts) > 4 else None
        hits = 0
        for e in anims[aid].Events:
            p = bytes(e.GetParameterBytes(False))
            if int(e.Type) != typ or len(p) < 12 or struct.unpack_from("<i", p, 8)[0] != judge:
                continue
            old = (float(e.StartTime), float(e.EndTime))
            e.StartTime = start
            e.EndTime = end if end is not None else start + (old[1] - old[0])
            hits += 1
            print(f"  {aid}: type {typ} judge {judge}: {old[0]:.2f}-{old[1]:.2f} -> {float(e.StartTime):.2f}-{float(e.EndTime):.2f} s")
        if not hits:
            print(f"  {aid}: type {typ} judge {judge}: not found")
    tf.Bytes = to_memory(tae.Write())
    tmp = path.with_suffix(".tmp")
    bnd.Write(str(tmp))
    bnd.Dispose()
    tmp.replace(path)
    print(f"OK: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
