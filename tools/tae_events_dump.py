"""Print the TAE events of chosen animations in a chr anibnd (read only).

  python tools/tae_events_dump.py <anibnd.dcx> 3007 3009 [--types 1 2 ...]
"""
from __future__ import annotations

import argparse
import ntpath
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sfbridge import load_soulsformats, read_binder, read_file  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("anibnd", type=Path)
    ap.add_argument("ids", type=int, nargs="+")
    ap.add_argument("--types", type=int, nargs="*", default=[])
    ap.add_argument("--tae", help="only this TAE, e.g. a33")
    args = ap.parse_args(argv)
    path = str(args.anibnd.resolve())
    load_soulsformats()
    from SoulsFormats import BND3, BND4, TAE
    with open(path, "rb") as fh:
        head = fh.read(64)
    # DCX-compressed or plain: an Elden Ring / Nightreign binder is BND4
    is4 = b"BND4" in head or "nuxe" in path.lower() or "nightreign" in path.lower()
    try:
        binder = read_binder(BND4 if is4 else BND3, path)
    except Exception:  # DCX-compressed: the header does not tell; try the other binder version
        binder = read_binder(BND3 if is4 else BND4, path)
    for f in binder.Files:
        name = ntpath.basename(str(f.Name)).lower()
        if not name.endswith(".tae") or (args.tae and name != f"{args.tae.lower()}.tae"):
            continue
        tae = read_file(TAE, f.Bytes)
        for a in tae.Animations:
            if int(a.ID) % 1000000 not in args.ids:
                continue
            print(f"== {name} {int(a.ID)}")
            for e in sorted(a.Events, key=lambda x: float(x.StartTime)):
                t = int(e.Type)
                if args.types and t not in args.types:
                    continue
                p = bytes(e.GetParameterBytes(False))
                ints = struct.unpack_from(f"<{min(len(p) // 4, 6)}i", p) if len(p) >= 4 else ()
                print(f"  {float(e.StartTime):6.2f}-{float(e.EndTime):6.2f}  type {t:4d}  {list(ints)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
