"""Where are a boss's weapon bones during its hit windows? (read-only) For each attack: every TAE hit window (type 1)
of the DSR clip and of the ported clip, and the height range / forward reach of the chosen bones in that window
(model space, metres; forward = -Z as in the DSR root motion). Used for "Capra's swings pass over the player"
(2026-11-15).

  python tools\\weapon_reach_in_hits.py --dsr c2240 --ported c2240_omen \\
         --port-anibnd dist\\mods\\bossy_nightreign\\files_c2240_omen\\chr\\c2240.anibnd.dcx --anims 3000 3001 \\
         --bones "Weapon|Hand"
"""
from __future__ import annotations

import argparse
import ntpath
import re
import struct
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from boss_anim_port import BP, parents_of, ref_arrays  # noqa: E402
from boss_clip_compare import load_clip  # noqa: E402
from havokbridge import load_havok  # noqa: E402
from sfbridge import load_soulsformats, read_binder, read_file, to_memory  # noqa: E402


def hit_windows(tae, aid):
    a = next((x for x in tae.Animations if int(x.ID) % 1000000 == aid), None)
    out = []
    for e in (a.Events if a is not None else []):
        p = bytes(e.GetParameterBytes(False))
        if int(e.Type) == 1 and len(p) >= 12:
            out.append((float(e.StartTime), float(e.EndTime), struct.unpack_from("<i", p, 8)[0]))
    return sorted(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dsr", required=True)
    ap.add_argument("--ported", required=True)
    ap.add_argument("--port-anibnd", type=Path, required=True)
    ap.add_argument("--anims", type=int, nargs="+", required=True)
    ap.add_argument("--bones", default="Weapon")
    ap.add_argument("--pad", type=float, nargs=2, default=(0.0, 0.0), metavar=("BEFORE", "AFTER"),
                    help="widen the ported clip's windows by this many seconds (preview of a longer window)")
    ap.add_argument("--timeline", action="store_true", help="lowest height / reach of the bones every 0.05 s")
    args = ap.parse_args(argv)
    port_path = str(args.port_anibnd.resolve())
    sf = load_soulsformats()
    DD = BP / f"dsr_{args.dsr}" / "anibnd"
    dsr_tae = read_file(sf.TAE, to_memory(next(DD.glob("*.tae")).read_bytes()))
    pf = next(f for f in read_binder(sf.BND3, port_path).Files if ntpath.basename(str(f.Name)).lower().endswith(".tae"))
    port_tae = read_file(sf.TAE, pf.Bytes)
    load_havok()
    from soulstruct.havok.fromsoft import darksouls1r as d
    skel = d.SkeletonHKX.from_path(next(p for p in DD.iterdir() if p.name.lower() == "skeleton.hkx")).skeleton
    names = [str(b.name) for b in skel.bones]
    par = parents_of(skel)
    ref = ref_arrays(skel)
    sel = [i for i, n in enumerate(names) if re.search(args.bones, n)]
    if not sel:
        print("no bone matches; skeleton bones:", ", ".join(names))
        return 1
    # the bone chain below the chosen bones too (blade tips)
    kids = set(sel)
    for i, p in enumerate(par):
        if p in kids:
            kids.add(i)
    sel = sorted(kids)
    print("bones:", ", ".join(names[i] for i in sel))
    for aid in args.anims:
        for tag, folder, tae in (("DSR ", DD, dsr_tae), ("port", BP / "nr_ported" / args.ported, port_tae)):
            path = folder / f"a00_{aid:04d}.hkx"
            if not path.exists():
                continue
            P, dur = load_clip(d, path, par, ref)
            dt = dur / max(len(P) - 1, 1)
            parts = []
            for s, e, j in hit_windows(tae, aid):
                if tag == "port":
                    s, e = max(0.0, s - args.pad[0]), e + args.pad[1]
                i0, i1 = int(s / dt), min(int(e / dt) + 1, len(P))
                if i0 >= len(P):
                    parts.append(f"{j}@{s:.2f}: after clip end")
                    continue
                W = P[i0:i1][:, sel, :]
                y0, y1 = float(W[:, :, 1].min()), float(W[:, :, 1].max())
                fwd = float((-W[:, :, 2]).max())
                parts.append(f"{j}@{s:.2f}-{e:.2f}: height {y0:+.1f}..{y1:+.1f}, reach {fwd:+.1f}")
            print(f"{aid} {tag} ({dur:.2f} s): " + (" | ".join(parts) or "no hits"))
            if args.timeline:
                cells = []
                for k in range(0, len(P), max(1, int(round(0.05 / dt)))):
                    W = P[k][sel, :]
                    cells.append(f"{k * dt:.2f}:{float(W[:, 1].min()):+.1f}/{float((-W[:, 2]).max()):+.1f}")
                for k in range(0, len(cells), 10):
                    print("     " + "  ".join(cells[k:k + 10]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
