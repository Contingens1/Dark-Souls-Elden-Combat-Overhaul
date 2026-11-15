"""Disable the weapon's wall / ground clang for the whole hit of the ported ER attacks (TAE JumpTable 56 / 57).

DSR authors JT56 "Disable Wall Attack Clang" (57 = NPC variant) only around the frame where its own swing meets the
ground (great hammer R2 a35 3300: hit 1.27-1.40 s, JT56 1.37-1.40 s). The generators shift those events together
with the hit onto the ER clips (sprint R2 3320: 0.87-0.90 s, jump R2 3710: 0.63-0.67 s), but the ER swings touch the
ground earlier and longer, on a slope earlier still, so for the rest of the hit the weapon bounces off the terrain
(player tests 2026-11-14 / 2026-11-15: jump R2 uphill, sprint R2 "often bounces"). Here JT56 and JT57 cover the
first hit start to the last hit end, as in Elden Ring, where jump and running attacks do not clang on the ground.

Used by tools/add_jump_attacks.py and tools/add_sprint_heavy.py (cover_wall_clang) and on its own for an existing
anibnd (only the ER attacks the generators add: x700 / x710 swings, x701 / x711 landings with a hit, x320 sprint R2):
  python tools\\tae_wall_clang.py dist\\mods\\bossy_nightreign\\files_c0000_night\\chr\\c0000.anibnd.dcx [--dry-run]
"""
from __future__ import annotations

import argparse
import ntpath
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sfbridge import load_soulsformats, read_binder, read_file, to_memory  # noqa: E402

JT_CLANG = (56, 57)
HIT_TYPES = {1, 5}  # InvokeAttackBehavior, InvokePCBehavior (fists)
PORTED = (3700, 3701, 3710, 3711, 4700, 4701, 4710, 4711, 3320, 4320)


def _jt(e):
    pb = bytes(e.GetParameterBytes(False))
    return struct.unpack_from("<i", pb)[0] if int(e.Type) == 0 and len(pb) >= 4 else None


def cover_wall_clang(anim, hit_types=HIT_TYPES) -> tuple[float, float] | None:
    """Replace the animation's JT56 / JT57 events by one each spanning all its hits. Returns the span or None."""
    from SoulsFormats import TAE
    from System import Array, Byte
    events = list(anim.Events)
    hits = [e for e in events if int(e.Type) in hit_types]
    tpl = next((e for e in events if int(e.Type) == 0), None)
    if not hits or tpl is None:
        return None
    start, end = min(e.StartTime for e in hits), max(e.EndTime for e in hits)
    tpl = next((e for e in events if _jt(e) in JT_CLANG), tpl)  # prefer the attack's own JT56 as the pattern
    for e in events:
        if _jt(e) in JT_CLANG:
            anim.Events.Remove(e)
    for j in JT_CLANG:
        p = bytearray(bytes(tpl.GetParameterBytes(False)))
        # as DSR writes them: [jump table id, 0, -1]
        struct.pack_into("<iii", p, 0, j, 0, -1) if len(p) >= 12 else struct.pack_into("<i", p, 0, j)
        anim.Events.Add(TAE.Event(start, end, tpl.Type, tpl.Unk04, Array[Byte](list(p)), False))
    return start, end


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("anibnd", type=Path)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)
    path = args.anibnd.resolve()
    load_soulsformats()
    from SoulsFormats import BND3, TAE
    ani = read_binder(BND3, str(path))
    changed = 0
    for tf in ani.Files:
        n = ntpath.basename(str(tf.Name)).lower()
        if not (n.endswith(".tae") and n[0] == "a" and n[1:-4].isdigit() and 20 <= int(n[1:-4]) < 50):
            continue
        tae = read_file(TAE, tf.Bytes)
        touched = False
        for a in tae.Animations:
            if int(a.ID) not in PORTED:
                continue
            before = [(e.StartTime, e.EndTime) for e in a.Events if _jt(e) == 56]
            span = cover_wall_clang(a)
            if span is None:
                continue
            touched = True
            changed += 1
            old = ", ".join(f"{s:.2f}-{e:.2f}" for s, e in before) or "none"
            print(f"  {n[:-4]} {int(a.ID)}: JT56 {old} -> {span[0]:.2f}-{span[1]:.2f}")
        if touched and not args.dry_run:
            tf.Bytes = to_memory(tae.Write())
    if args.dry_run:
        print(f"dry run: {changed} animations")
        return 0
    tmp = path.with_suffix(".tmp")
    ani.Write(str(tmp))
    ani.Dispose()
    tmp.replace(path)
    print(f"OK: {changed} animations -> {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
