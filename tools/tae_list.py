"""List the animations of one TAE inside an anibnd (read only): ID, HKX source, event count, last event end, and
the attack behaviours (type 1) / JumpTable ids (type 0) with their start times.

  python tools/tae_list.py <anibnd.dcx> a33 [--min 3000 --max 3999]
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
    ap.add_argument("tae", help="TAE name without extension, e.g. a33 (ER: a033)")
    ap.add_argument("--min", type=int, default=0)
    ap.add_argument("--max", type=int, default=10**9)
    ap.add_argument("--bnd4", action="store_true", help="Elden Ring anibnd (BND4)")
    args = ap.parse_args(argv)
    path = str(args.anibnd.resolve())
    load_soulsformats()
    from SoulsFormats import BND3, BND4, TAE
    for f in read_binder(BND4 if args.bnd4 else BND3, path).Files:
        if ntpath.basename(str(f.Name)).lower() != f"{args.tae.lower()}.tae":
            continue
        tae = read_file(TAE, f.Bytes)
        for a in sorted(tae.Animations, key=lambda x: int(x.ID)):
            aid = int(a.ID)
            if not args.min <= aid <= args.max:
                continue
            ev = list(a.Events)
            end = max((float(e.EndTime) for e in ev), default=0.0)
            hits, jts = [], []
            for e in sorted(ev, key=lambda x: float(x.StartTime)):
                p = bytes(e.GetParameterBytes(False))
                if int(e.Type) == 1 and len(p) >= 12:
                    hits.append(f"{struct.unpack_from('<i', p, 8)[0]}@{float(e.StartTime):.2f}")
                elif int(e.Type) == 0 and len(p) >= 4:
                    jts.append(struct.unpack_from("<i", p)[0])
            src = int(a.Unknown2) if int(a.Unknown1) == 256 else aid
            print(f"{aid:7d}  src {src:7d}  ev {len(ev):3d}  end {end:5.2f}  hits {' '.join(hits) or '-'}  JT {sorted(set(jts))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
