"""List a FromSoftware binder (BND3 / BND4, DCX or not): entry IDs, names, sizes; TAE animation counts.

  python tools/binder_ls.py work/ds3/chr/c5280.anibnd.dcx [--tae] [--grep hkx]
"""
from __future__ import annotations

import argparse
import ntpath
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sfbridge import load_soulsformats, read_binder, read_file  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("path", type=Path)
    ap.add_argument("--tae", action="store_true", help="also list TAE animations (ID, event count)")
    ap.add_argument("--grep", default="")
    ap.add_argument("--max", type=int, default=60)
    args = ap.parse_args(argv)
    p = str(args.path.resolve())  # before load_soulsformats(), which changes the working directory
    sf = load_soulsformats()
    try:
        b = read_binder(sf.BND4, p)
    except Exception:
        b = read_binder(sf.BND3, p)
    files = list(b.Files)
    print(f"{len(files)} entries")
    shown = 0
    for f in files:
        name = str(f.Name)
        if args.grep and args.grep.lower() not in name.lower():
            continue
        if shown < args.max:
            print(f"  {int(f.ID):10d}  {name}  {f.Bytes.Length} B")
        shown += 1
        if args.tae and name.lower().endswith(".tae"):
            t = read_file(sf.TAE, f.Bytes)
            ids = sorted(int(a.ID) for a in t.Animations)
            print(f"      TAE {ntpath.basename(name)}: {len(ids)} animations: {ids[:120]}")
    if shown > args.max:
        print(f"  ... {shown - args.max} more")
    return 0


if __name__ == "__main__":
    sys.exit(main())
