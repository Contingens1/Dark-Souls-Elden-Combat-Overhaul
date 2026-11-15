"""List the physics bodies of a DSR character (chrbnd -> cNNNN.hkx ragdoll, read only): every rigid body with its
shape (capsule radius / length) and the animation bone it follows (ragdoll -> animation skeleton mapper).
Used for "Centipede's tentacles cannot be hit" (2026-11-15): only bones with a body can be struck.

  python tools/ragdoll_bodies.py c5200 [--grep hand]
"""
from __future__ import annotations

import argparse
import ntpath
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sfbridge import load_soulsformats, read_binder  # noqa: E402

GAME = Path(r"F:\SteamLibrary\steamapps\common\DARK SOULS REMASTERED\chr")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("chr")
    ap.add_argument("--grep", default="")
    args = ap.parse_args(argv)
    sf = load_soulsformats()
    data = None
    for f in read_binder(sf.BND3, str(GAME / f"{args.chr}.chrbnd.dcx")).Files:
        if ntpath.basename(str(f.Name)).lower() == f"{args.chr}.hkx":
            data = bytes(f.Bytes.ToArray())
    tmp = Path(tempfile.gettempdir()) / f"{args.chr}_ragdoll.hkx"
    tmp.write_bytes(data)
    from havokbridge import load_havok
    load_havok()
    from soulstruct.havok.core import HKX
    hkx = HKX.from_path(tmp)
    seen = 0
    for obj in hkx.root.namedVariants:
        print(f"variant {obj.name}: {type(obj.variant).__name__}")
    # walk everything that looks like a rigid body / ragdoll instance
    stack = [v.variant for v in hkx.root.namedVariants]
    visited = set()
    while stack:
        o = stack.pop()
        if o is None or id(o) in visited:
            continue
        visited.add(id(o))
        tn = type(o).__name__
        if tn == "hkaRagdollInstance":
            names = [str(b.name) for b in o.skeleton.bones]
            print(f"ragdoll: {len(o.rigidBodies)} bodies, skeleton bones: " + ", ".join(names))
            for i, rb in enumerate(o.rigidBodies):
                shape = rb.collidable.shape
                st = type(shape).__name__
                extra = ""
                for k in ("radius", "vertexA", "vertexB"):
                    if hasattr(shape, k):
                        extra += f" {k}={getattr(shape, k)}"
                nm = names[i] if i < len(names) else "?"
                if args.grep.lower() in nm.lower():
                    print(f"  body {i:3d} bone {nm:24s} {st}{extra[:120]}")
                    seen += 1
        if tn == "hkaSkeletonMapper":
            m = o.mapping
            try:
                a = [str(b.name) for b in m.skeletonA.bones]
                b = [str(x.name) for x in m.skeletonB.bones]
                pairs = [(a[s.boneA], b[s.boneB]) for s in m.simpleMappings]
                print(f"mapper {m.skeletonA.name} -> {m.skeletonB.name}: {len(pairs)} simple mappings: " +
                      ", ".join(f"{x}->{y}" for x, y in pairs if args.grep.lower() in (x + y).lower())[:3000])
            except Exception as ex:  # noqa: BLE001
                print("mapper:", type(ex).__name__, ex)
        for attr in getattr(o, "__slots__", ()):
            try:
                v = getattr(o, attr)
            except AttributeError:
                continue
            if isinstance(v, list):
                stack.extend(x for x in v if hasattr(x, "__slots__"))
            elif hasattr(v, "__slots__"):
                stack.append(v)
    print(f"{seen} bodies listed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
