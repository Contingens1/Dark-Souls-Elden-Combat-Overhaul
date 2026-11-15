"""
add_land_anims.py - Elden Ring landings after a jump as new DSR animations, and the ER flight loop as the fall pose.

  904 <- a000_202115 Jump_Land_To_Run          (landing into a run)
  905 <- a000_202125 Jump_Land_To_Dash_Light   (landing into a sprint)
  a00_1550.hkx <- a000_202040 Jump_Loop       (--fall-loop, default on: the game's "fall after a jump" pose, shown
                                                after the DLL ends the jump clip; DSR's own pose made the arms and
                                                legs jump at longer falls, player test 2026-11-15)

TAE events of 904/905: a clone of 1790 (DSR landing after a jump) without roll invincibility (JT8) and turn lock
(JT7); the cancel windows are moved to the ER times. er_engine.dll plays them on layer 7 after a touchdown from a run
or sprint jump ([Jump] LandToRun), while the game's state machine is already in the move state, so the windows only
matter for the engine-side jump tables. 1790 itself is not changed (the 2026-11-1x version of this tool rewrote it).

Works on mod files only. Default target: the night package (dist/mods/bossy_nightreign/files_c0000_night/chr); a
file missing there (c0000_a00_lo) is taken from the main mod (dist/mods/c0000_er_engine/files/chr). Re-running
replaces the entries it added.

Usage (CMD, from ds1-elden-port):
    python tools\\add_land_anims.py [--chr <dir>] [--no-fall-loop]
"""
from __future__ import annotations

import argparse
import ntpath
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sfbridge import load_soulsformats, read_binder, read_file, to_memory  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
MAIN_CHR = ROOT / "dist/mods/c0000_er_engine/files/chr"
NIGHT_CHR = ROOT / "dist/mods/bossy_nightreign/files_c0000_night/chr"
REPO = Path(r"C:\Users\nemos\workspace\toolsy\Player Animations Repository"
            r"\(ER) c0000 Tarnished_c0000 Chosen Undead-748-ER-1-001-1723291686"
            r"\Base Game\2016 (DSR)\a000 - Base Movement")
NEW = {904: "a000_202115.hkx", 905: "a000_202125.hkx"}
FALL_LOOP = ("a00_1550.hkx", "a000_202040.hkx")
SOURCE = 1790
ER_CANCEL = {4: 0.03, 16: 0.13, 22: 0.13, 26: 0.13, 29: 0.13, 31: 0.13, 11: 0.17, 32: 0.03}
DROP = {7, 8}  # turn lock, roll invincibility


def jt(e):
    p = bytes(e.GetParameterBytes(False))
    return struct.unpack_from("<i", p)[0] if int(e.Type) == 0 and len(p) >= 4 else None


def er_events(src, TAE):
    out = []
    for e in src.Events:
        j = jt(e)
        if j in DROP:
            continue
        start = ER_CANCEL.get(j, e.StartTime)
        out.append(TAE.Event(start, e.EndTime, e.Type, e.Unk04, e.GetParameterBytes(False), False))
    return out


def source_path(chr_dir: Path, name: str) -> Path:
    p = chr_dir / name
    return p if p.exists() else MAIN_CHR / name


def write_binder(binder, path: Path):
    tmp = path.with_suffix(".tmp")
    binder.Write(str(tmp))
    binder.Dispose()
    tmp.replace(path)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chr", type=Path, default=NIGHT_CHR, help="target chr folder (mod files)")
    ap.add_argument("--no-fall-loop", action="store_true", help="keep the game's a00_1550 fall pose")
    args = ap.parse_args(argv)
    chr_dir: Path = args.chr
    chr_dir.mkdir(parents=True, exist_ok=True)
    load_soulsformats()
    from SoulsFormats import BND3, TAE, BinderFile
    from System import Array, Byte

    # TAE (c0000.anibnd, a00.tae): 904/905 = clone of 1790 with ER windows
    ani = read_binder(BND3, str(source_path(chr_dir, "c0000.anibnd.dcx")))
    tf = next(f for f in ani.Files if ntpath.basename(f.Name).lower() == "a00.tae")
    tae = read_file(TAE, tf.Bytes)
    src = next(a for a in tae.Animations if int(a.ID) == SOURCE)
    for a in [a for a in tae.Animations if int(a.ID) in NEW]:
        tae.Animations.Remove(a)
    for new_id in NEW:
        clone = TAE.Animation(new_id, src.AnimFileReference, src.Unknown1, src.Unknown2, f"a00_{new_id:04d}.HKXwin")
        for e in er_events(src, TAE):
            clone.Events.Add(e)
        tae.Animations.Add(clone)
    anims = sorted(list(tae.Animations), key=lambda a: a.ID)
    tae.Animations.Clear()
    for a in anims:
        tae.Animations.Add(a)
    tf.Bytes = to_memory(tae.Write())
    write_binder(ani, chr_dir / "c0000.anibnd.dcx")
    print(f"  TAE: {sorted(NEW)} = clone of {SOURCE} without JT{sorted(DROP)}, ER cancel windows")

    # HKX (c0000_a00_lo.anibnd)
    lo = read_binder(BND3, str(source_path(chr_dir, "c0000_a00_lo.anibnd.dcx")))
    ref = next(f for f in lo.Files if ntpath.basename(f.Name).lower() == "a00_0900.hkx")
    id_base = int(ref.ID) - 900  # entry ID = animation ID (otherwise T-pose)
    for f in [f for f in lo.Files if int(f.ID) - id_base in NEW]:
        lo.Files.Remove(f)
    for new_id, hkx in NEW.items():
        data = (REPO / hkx).read_bytes()
        name = ntpath.join(ntpath.dirname(ref.Name), f"a00_{new_id:04d}.hkx")
        lo.Files.Add(BinderFile(ref.Flags, id_base + new_id, name, to_memory(Array[Byte](list(data)))))
        print(f"  {new_id} <- {hkx} ({len(data)} B)")
    if not args.no_fall_loop:
        target, hkx = FALL_LOOP
        f = next(f for f in lo.Files if ntpath.basename(f.Name).lower() == target)
        data = (REPO / hkx).read_bytes()
        f.Bytes = to_memory(Array[Byte](list(data)))
        print(f"  {target} <- {hkx} ({len(data)} B)")
    files = sorted(list(lo.Files), key=lambda f: int(f.ID))
    lo.Files.Clear()
    for f in files:
        lo.Files.Add(f)
    write_binder(lo, chr_dir / "c0000_a00_lo.anibnd.dcx")
    print(f"OK -> {chr_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
