"""
esd_land_threshold.py - raise the fall height of the game's light landing (1750) in the player ESD (c0000.esd).

Player test 2026-11-16: "a jump off a few stairs already gives the long landing". In c0000.esd (group 0) every fall
state picks the landing by env function 224 (fall height in metres since the fall started; log 16.11: 1750 from ~2 m,
1755 from ~8.5 m, 1760 at 16 m):
    if (<Bx> && (f224() >= 6))  -> 32   (1755, medium)        normal equip load; heavier loads use 4 / 8
    if (<Bx> && (f224() >= 2))  -> 31   (1750, light: the character stops for ~0.4 s)
    if <Bx>                     -> 0    (no landing animation: er_engine.dll plays its landing into a run)
This tool rewrites only the "f224() >= 2 -> 31" conditions (the normal and heavy-load branches; the overloaded branch
">= 1" stays) as "f224() * k >= round(h * k)", so the height can be fractional with integer literals only (the ESD has
no float literal in any comparison; if f224 returns whole metres, 3.5 acts as 4). Medium and heavy landings unchanged.

Usage (CMD, from ds1-elden-port):
    python tools\\esd_land_threshold.py [--height 3.5] [--src <c0000.esd.dcx>] [--out <c0000.esd.dcx>]
Default: the main mod's ESD -> the night package (dist\\mods\\bossy_nightreign\\files_c0000_night\\chr).
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS_DIR))
from sfbridge import load_soulsformats, net_bytes, read_file  # noqa: E402

ROOT = TOOLS_DIR.parent
DEFAULT_SRC = ROOT / "dist/mods/c0000_er_engine/files/chr/c0000.esd.dcx"
DEFAULT_OUT = ROOT / "dist/mods/bossy_nightreign/files_c0000_night/chr/c0000.esd.dcx"
LIGHT_LANDING_STATE = 31
# <Bx> && (f224() >= 2): cached value 0xB0..0xBF, 0xA6 (short-circuit), int 224, call/0, int 2, '>=', '&&', end
OLD = re.compile(rb"^([\xb0-\xbf])\xa6\x82\xe0\x00\x00\x00\x84\x42\x92\x98\xa1$")
OP_MUL, OP_GE = 0x8F, 0x92  # from the ESD itself: "1750 + (f246() * 15)" = ... 4f 8f 8c, "f224() >= 2" = ... 42 92


def ezl_int(val: int) -> bytes:
    if -64 <= val <= 63:
        return bytes([val + 64])
    return b"\x82" + val.to_bytes(4, "little", signed=True)


def new_evaluator(cache: int, height: float) -> bytes:
    k = next(k for k in (1, 2, 4, 10, 100) if abs(height * k - round(height * k)) < 1e-6)
    body = b"\x82\xe0\x00\x00\x00\x84"  # f224()
    if k > 1:
        body += ezl_int(k) + bytes([OP_MUL])
    body += ezl_int(round(height * k)) + bytes([OP_GE])
    return bytes([cache, 0xA6]) + body + b"\x98\xa1"


def patch(src: Path, out: Path, height: float) -> int:
    if src.resolve() == out.resolve():
        raise ValueError("refusing to overwrite the source ESD in place")
    load_soulsformats()
    from SoulsFormats import ESD

    esd = read_file(ESD, str(src.resolve()))
    group0 = next(kv.Value for kv in esd.StateGroups if int(kv.Key) == 0)
    changed = []

    def walk(conds, sid):
        for i in range(conds.Count):
            c = conds[i]
            ev = bytes(c.Evaluator)
            if c.TargetState is not None and int(c.TargetState) == LIGHT_LANDING_STATE and OLD.match(ev):
                # clone: SoulsFormats shares identical Condition objects between states
                nc = ESD.Condition(LIGHT_LANDING_STATE, net_bytes(new_evaluator(ev[0], height)))
                for pc in c.PassCommands:
                    nc.PassCommands.Add(pc)
                for sc in c.Subconditions:
                    nc.Subconditions.Add(sc)
                conds[i] = nc
                changed.append((sid, ev.hex()))
            walk(conds[i].Subconditions, sid)

    for kv in group0:
        walk(kv.Value.Conditions, int(kv.Key))
    if not changed:
        raise RuntimeError("no 'f224() >= 2 -> 31' condition found (already patched?)")
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(".tmp")
    esd.Write(str(tmp.resolve()))
    tmp.replace(out)
    states = sorted({s for s, _ in changed})
    print(f"  {len(changed)} conditions -> f224() >= {height} (states {states}), new evaluator "
          f"{new_evaluator(0xB1, height).hex()} (for <B1>)")

    # check: re-read, no old condition left, the new ones present
    esd2 = read_file(ESD, str(out.resolve()))
    g0 = next(kv.Value for kv in esd2.StateGroups if int(kv.Key) == 0)
    old_left, new_found = 0, 0

    def count(conds):
        nonlocal old_left, new_found
        for c in conds:
            ev = bytes(c.Evaluator)
            if c.TargetState is not None and int(c.TargetState) == LIGHT_LANDING_STATE:
                old_left += bool(OLD.match(ev))
                new_found += ev == new_evaluator(ev[0], height)
            count(c.Subconditions)

    for kv in g0:
        count(kv.Value.Conditions)
    print(f"  check: {new_found} new, {old_left} old left -> {out} ({out.stat().st_size} B)")
    return 0 if old_left == 0 and new_found == len(changed) else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Raise the light landing (1750) fall height in c0000.esd.")
    ap.add_argument("--height", type=float, default=3.5, help="fall height in metres (vanilla 2)")
    ap.add_argument("--src", type=Path, default=DEFAULT_SRC)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args(argv)
    return patch(args.src, args.out, args.height)


if __name__ == "__main__":
    sys.exit(main())
