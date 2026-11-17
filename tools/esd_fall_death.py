"""
esd_fall_death.py - move the fall height at which the player dies on landing, in the player ESD (c0000.esd).

Test 2026-11-17: with er_engine.dll [Fall] DamagePercent=50 a 20.5 m fall took only 614 of 1310 HP, then the
player died 360 ms later anyway. The death does not come from the fall damage formula: c0000.esd (group 0) sends
every fall that lands from f224() >= 20 m (env 224 = fall height in metres) to state 97, the landing-death
animation 6070:
    if ((f224() >= 20) || (f1000() < 0)) && ...   -> 97
    (state 164: f224() >= 20 && ...               -> 97)
This tool rewrites the literal 20 in those f224() comparisons (only in conditions whose target is state 97) to the
new height. The f1000() branch and every other condition stay as they are. Keep [Fall] DeathHeight in
er_engine.ini equal to this height (the DLL moves the same limit in the damage formula, 0x141A2B61C).

Usage (CMD, from ds1-elden-port):
    python tools\\esd_fall_death.py --height 26 [--src <c0000.esd.dcx>] [--out <c0000.esd.dcx>]
Default: the night package's ESD in place (dist\\mods\\bossy_nightreign\\files_c0000_night\\chr).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS_DIR))
from sfbridge import load_soulsformats, net_bytes, read_file  # noqa: E402

ROOT = TOOLS_DIR.parent
DEFAULT_ESD = ROOT / "dist/mods/bossy_nightreign/files_c0000_night/chr/c0000.esd.dcx"
DEATH_STATE = 97
F224 = b"\x82\xe0\x00\x00\x00\x84"  # int 224, call with 0 args
OP_GE = 0x92


def ezl_small(val: int) -> int:
    if not 0 <= val <= 63:
        raise ValueError("height must be a whole number of metres, 0-63")
    return val + 64


def rewrite(ev: bytes, old: int, new: int) -> bytes:
    """Replace f224() >= old (optionally with the 0xA6 short-circuit byte after the call) by f224() >= new."""
    out = ev
    for mid in (b"", b"\xa6"):
        out = out.replace(F224 + mid + bytes([ezl_small(old), OP_GE]), F224 + mid + bytes([ezl_small(new), OP_GE]))
    return out


def patch(src: Path, out: Path, height: int) -> int:
    load_soulsformats()
    from SoulsFormats import ESD

    esd = read_file(ESD, str(src.resolve()))
    group0 = next(kv.Value for kv in esd.StateGroups if int(kv.Key) == 0)
    changed = []

    def find_old(ev: bytes) -> int | None:
        for old in range(1, 64):
            if rewrite(ev, old, old + 1 if old < 63 else 1) != ev:
                return old
        return None

    def walk(conds, sid):
        for i in range(conds.Count):
            c = conds[i]
            ev = bytes(c.Evaluator)
            if c.TargetState is not None and int(c.TargetState) == DEATH_STATE:
                old = find_old(ev)
                if old is not None and old != height:
                    # clone: SoulsFormats shares identical Condition objects between states
                    nc = ESD.Condition(DEATH_STATE, net_bytes(rewrite(ev, old, height)))
                    for pc in c.PassCommands:
                        nc.PassCommands.Add(pc)
                    for sc in c.Subconditions:
                        nc.Subconditions.Add(sc)
                    conds[i] = nc
                    changed.append((sid, old))
            walk(conds[i].Subconditions, sid)

    for kv in group0:
        walk(kv.Value.Conditions, int(kv.Key))
    if not changed:
        print(f"  nothing to change (no f224() limit -> {DEATH_STATE} other than {height} m)")
        return 0
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(".tmp")
    esd.Write(str(tmp.resolve()))
    tmp.replace(out)
    olds = sorted({o for _, o in changed})
    print(f"  {len(changed)} conditions -> state {DEATH_STATE}: f224() >= {olds} m -> {height} m "
          f"(states {sorted({s for s, _ in changed})})")

    # check: re-read, every f224() limit towards state 97 is the new height
    esd2 = read_file(ESD, str(out.resolve()))
    g0 = next(kv.Value for kv in esd2.StateGroups if int(kv.Key) == 0)
    limits: list[int] = []

    def count(conds):
        for c in conds:
            if c.TargetState is not None and int(c.TargetState) == DEATH_STATE:
                o = find_old(bytes(c.Evaluator))
                if o is not None:
                    limits.append(o)
            count(c.Subconditions)

    for kv in g0:
        count(kv.Value.Conditions)
    print(f"  check: {len(limits)} limits, values {sorted(set(limits))} -> {out} ({out.stat().st_size} B)")
    return 0 if set(limits) == {height} else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Move the landing-death fall height in c0000.esd.")
    ap.add_argument("--height", type=int, required=True, help="fall height in metres (vanilla 20)")
    ap.add_argument("--src", type=Path, default=DEFAULT_ESD)
    ap.add_argument("--out", type=Path, default=None, help="default: --src in place")
    args = ap.parse_args(argv)
    src = args.src.resolve()  # before load_soulsformats, which changes the working directory
    return patch(src, (args.out or src).resolve(), args.height)


if __name__ == "__main__":
    sys.exit(main())
