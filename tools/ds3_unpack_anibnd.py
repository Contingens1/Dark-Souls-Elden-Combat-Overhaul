"""Unpack a DS3 chr anibnd (from tools/ds3_extract.py) into the boss-port layout used by tools/nr_boss_port.py:
work/boss_port/nr_<tag>/anibnd/{skeleton.hkx, aSSS_NNNNNN.hkx, <chr>.tae, compendium_map.json}. Read only.
Also prints the skeleton bone names (soulstruct darksouls3).

  python tools/ds3_unpack_anibnd.py c5280            # -> work/boss_port/nr_ds3c5280/anibnd
"""
from __future__ import annotations

import argparse
import json
import ntpath
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sfbridge import load_soulsformats, read_binder  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
BP = ROOT / "work" / "boss_port"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("chr")
    args = ap.parse_args(argv)
    src = (ROOT / "work" / "ds3" / "chr" / f"{args.chr}.anibnd.dcx").resolve()
    out = (BP / f"nr_ds3{args.chr}" / "anibnd").resolve()
    out.mkdir(parents=True, exist_ok=True)
    sf = load_soulsformats()
    n = 0
    for f in read_binder(sf.BND4, str(src)).Files:
        name = ntpath.basename(str(f.Name))
        low = name.lower()
        if low == "skeleton.hkx" or low.endswith(".hkx") or low.endswith(".tae"):
            (out / low).write_bytes(bytes(f.Bytes.ToArray()))
            n += 1
    (out / "compendium_map.json").write_text("{}", encoding="utf-8")
    print(f"{n} files -> {out}")
    from havokbridge import load_havok
    load_havok()
    from soulstruct.havok.fromsoft import darksouls3 as d3
    sk = d3.SkeletonHKX.from_path(out / "skeleton.hkx").skeleton
    names = [str(b.name) for b in sk.bones]
    print(f"skeleton: {len(names)} bones: " + ", ".join(names))
    return 0


if __name__ == "__main__":
    sys.exit(main())
