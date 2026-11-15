"""
widen_hits.py - longer hit windows (TAE type 1) for chosen animations of a boss in a test package.

Capra -> Omen Killer (player test 2026-11-14): many swings "pass over the player" without a hit. The ported clips
carry ER's 0.10 s windows on fast ER swings (DSR's own Capra windows are 0.13-0.23 s); tools/weapon_reach_in_hits.py
shows the cleavers at 1.0-2.3 m height inside those windows, the DSR originals down to 0.2-0.7 m. A wider window
lets the swing's lower, later part count. Default: 0.05 s earlier, 0.10 s later (0.25 s in total).

  python tools\\widen_hits.py --anibnd dist\\mods\\bossy_nightreign\\files_c2240_omen\\chr\\c2240.anibnd.dcx \\
         --anims 3000 3001 3002 3003 3004 3005
Run it again only on a freshly installed anibnd (it widens again on every run).
"""
from __future__ import annotations

import argparse
import ntpath
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sfbridge import load_soulsformats, read_binder, read_file, to_memory  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--anibnd", type=Path, required=True)
    ap.add_argument("--anims", type=int, nargs="+", required=True)
    ap.add_argument("--before", type=float, default=0.05)
    ap.add_argument("--after", type=float, default=0.10)
    args = ap.parse_args(argv)
    path = args.anibnd.resolve()
    if "steamapps" in str(path).lower() or "c0000_er_engine" in str(path):
        sys.exit("ERROR: only test packages are patched")
    load_soulsformats()
    from SoulsFormats import BND3, TAE
    bnd = read_binder(BND3, str(path))
    tf = next(f for f in bnd.Files if ntpath.basename(str(f.Name)).lower().endswith(".tae"))
    tae = read_file(TAE, tf.Bytes)
    for a in tae.Animations:
        if int(a.ID) not in args.anims:
            continue
        for e in a.Events:
            if int(e.Type) != 1:
                continue
            old = (float(e.StartTime), float(e.EndTime))
            e.StartTime = max(0.0, old[0] - args.before)
            e.EndTime = old[1] + args.after
            print(f"  {int(a.ID)}: hit {old[0]:.2f}-{old[1]:.2f} -> {float(e.StartTime):.2f}-{float(e.EndTime):.2f} s")
    tf.Bytes = to_memory(tae.Write())
    tmp = path.with_suffix(".tmp")
    bnd.Write(str(tmp))
    bnd.Dispose()
    tmp.replace(path)
    print(f"OK: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
