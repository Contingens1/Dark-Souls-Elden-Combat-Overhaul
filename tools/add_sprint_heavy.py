"""
add_sprint_heavy.py - Elden Ring sprint heavy attacks (R2 while sprinting) as new animations of DSR weapon groups.

DS1 has no sprint R2: R2 while sprinting stops the player and plays the normal R2 (player test 2026-11-14, great
hammer: "the character stops and does a plain R2; in ER it is a spinning attack"). For a group aGG:
    3300 -> 3320 <- a0GG_030210 (ER dash heavy, one hand)
    4300 -> 4320 <- a0GG_032210 (ER dash heavy, two hands)
TAE: the DSR R2's events (damage / weapon behaviours of the DSR weapon, sounds, cancel windows) shifted so that the
first hit starts where ER's does; a DSR R2 that only references another animation (hammer a33 3300 -> 3600) takes
that animation's events. HKX: the repository's DSR conversion of the ER clip (same files as the jump attacks).
er_engine.dll plays the new animation instead of the R2 when the game's sprint flag was on just before the press
(native/er_engine/sprint_heavy_table.h, written here).

  python tools\\add_sprint_heavy.py --groups a33 a35 --chr dist\\mods\\bossy_nightreign\\files_c0000_night\\chr
Every run rewrites sprint_heavy_table.h from the groups given, so always pass all groups.
"""
from __future__ import annotations

import argparse
import ntpath
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sfbridge import load_soulsformats, read_binder, read_file, to_memory  # noqa: E402
from tae_compare import DSAS, ER_ANI, template  # noqa: E402
from add_jump_attacks import CHR, GAME_CHR, ROOT, er_hkx, first_hit, type_id  # noqa: E402
from tae_wall_clang import cover_wall_clang  # noqa: E402

PAIRS = [(3300, 3320, 30210), (4300, 4320, 32210)]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--groups", nargs="+", default=["a33", "a35"])
    ap.add_argument("--chr", type=Path, default=ROOT / "dist/mods/bossy_nightreign/files_c0000_night/chr",
                    help="folder written to; files missing there are read from the main mod, then from the game")
    args = ap.parse_args(argv)
    out_dir = args.chr.resolve()
    if out_dir == CHR.resolve():
        print("note: writing the main mod's files (only after the in-game test)")
    out_dir.mkdir(parents=True, exist_ok=True)
    load_soulsformats()
    from SoulsFormats import BND3, BND4, TAE, BinderFile
    from System import Array, Byte
    t1, te = template(DSAS / "TAE.Template.DS1.xml"), template(DSAS / "TAE.Template.ER.xml")
    a1 = {type_id(t1, "InvokeAttackBehavior"), type_id(t1, "InvokePCBehavior")}
    ae = type_id(te, "InvokeAttackBehavior")
    er_taes = {ntpath.basename(f.Name).lower(): f for f in read_binder(BND4, str(ER_ANI)).Files}

    ani_path = out_dir / "c0000.anibnd.dcx"
    ani = read_binder(BND3, str(ani_path if ani_path.exists() else CHR / "c0000.anibnd.dcx"))
    added = {}
    rows = []
    for g in args.groups:
        gg = g[1:]
        tf = next(f for f in ani.Files if ntpath.basename(f.Name).lower() == f"{g}.tae")
        tae = read_file(TAE, tf.Bytes)
        anims = {int(a.ID): a for a in tae.Animations}
        er_tae = read_file(TAE, er_taes[f"a{gg}.tae"].Bytes) if f"a{gg}.tae" in er_taes else None
        for src_id, new_id, er_id in PAIRS:
            src = anims.get(src_id)
            d_hit = first_hit(list(src.Events), a1) if src is not None else None
            if d_hit is None and src is not None and src.AnimFileReference and int(src.Unknown1) // 10000 == int(gg):
                ref = anims.get(int(src.Unknown1) % 10000)
                r_hit = first_hit(list(ref.Events), a1) if ref is not None else None
                if r_hit is not None:
                    print(f"  {g}: {src_id} references {int(src.Unknown1) % 10000} - events taken from there")
                    src, d_hit = ref, r_hit
            ea = next((a for a in er_tae.Animations if int(a.ID) == er_id), None) if er_tae else None
            hkx = er_hkx(gg, er_id)
            e_hit = first_hit(list(ea.Events), ae) if ea is not None else None
            if d_hit is None or e_hit is None or hkx is None:
                print(f"  {g}: {new_id} <- {er_id}: missing DSR hit / ER animation / usable HKX - skipped")
                continue
            shift = e_hit - d_hit
            if new_id in anims:
                tae.Animations.Remove(anims.pop(new_id))
            clone = TAE.Animation(new_id, src.AnimFileReference, src.Unknown1, src.Unknown2, f"{g}_{new_id:04d}.HKXwin")
            for e in src.Events:
                s, en = max(0.0, e.StartTime + shift), max(0.03, e.EndTime + shift)
                clone.Events.Add(TAE.Event(s, en, e.Type, e.Unk04, e.GetParameterBytes(False), False))
            cover_wall_clang(clone, a1)  # no bounce off the ground for the whole hit (tools/tae_wall_clang.py)
            tae.Animations.Add(clone)
            anims[new_id] = clone
            full = int(gg) * 10000 + new_id
            print(f"  {g}: {new_id} = events of {int(src.ID)} shifted {shift:+.2f} s (hit {d_hit:.2f} -> {e_hit:.2f}), HKX {hkx.name}")
            added.setdefault(f"c0000_a{gg[0]}x.anibnd.dcx", []).append((full, hkx, f"{g}_{new_id:04d}.hkx"))
            rows.append(full)
        srt = sorted(list(tae.Animations), key=lambda a: a.ID)
        tae.Animations.Clear()
        for a in srt:
            tae.Animations.Add(a)
        tf.Bytes = to_memory(tae.Write())
    tmp = ani_path.with_suffix(".tmp")
    ani.Write(str(tmp))
    ani.Dispose()
    tmp.replace(ani_path)

    for container, items in added.items():
        src_path = next(p for p in (out_dir / container, CHR / container, GAME_CHR / container) if p.exists())
        b = read_binder(BND3, str(src_path))
        ref = b.Files[0]
        for full_id, hkx, name in items:
            for f in [f for f in b.Files if int(f.ID) == full_id]:
                b.Files.Remove(f)
            path = ntpath.join(ntpath.dirname(ntpath.dirname(ref.Name)), name.split("_")[0], name)
            b.Files.Add(BinderFile(ref.Flags, full_id, path, to_memory(Array[Byte](list(hkx.read_bytes())))))
        files = sorted(list(b.Files), key=lambda f: int(f.ID))
        b.Files.Clear()
        for f in files:
            b.Files.Add(f)
        out = out_dir / container
        tmp = out.with_suffix(".tmp")
        b.Write(str(tmp))
        b.Dispose()
        tmp.replace(out)
        print(f"  {container}: +{len(items)} HKX")
    hdr = ROOT / "native/er_engine/sprint_heavy_table.h"
    lines = ["// Generated by tools/add_sprint_heavy.py - do not edit by hand.", "#pragma once",
             "// Sprint heavy attacks: group * 10000 + 3320 (one hand) / 4320 (two hands); the R2 they replace is",
             "// the same group's 3300 / 4300.",
             "static const int kSprintHeavy[] = {"]
    lines += [f"    {r}," for r in sorted(rows)] + ["    0,", "};"]
    hdr.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"OK ({len(rows)} sprint heavy attacks) -> {hdr}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
