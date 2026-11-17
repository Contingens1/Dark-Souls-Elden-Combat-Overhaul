"""Summarise the differences between two DSR GameParam.parambnd.dcx files (read only).

  python tools/param_diff.py <a.parambnd.dcx> [<b.parambnd.dcx>] [--rows 5]
Default b = the game's own GameParam. Per param: rows added / removed / changed and the changed fields with counts,
plus a few example rows (old -> new). Paramdefs from Smithbox (DS1R).
"""
from __future__ import annotations

import argparse
import ntpath
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sfbridge import load_soulsformats, read_binder, read_file  # noqa: E402

GAME = Path(r"F:\SteamLibrary\steamapps\common\DARK SOULS REMASTERED\param\GameParam\GameParam.parambnd.dcx")
DEFS = Path(r"C:\Users\nemos\workspace\toolsy\Smithbox_2_2_6_2026_09_20_b\Assets\PARAM\DS1R\Defs")


def load(sf, defs, path):
    out = {}
    for f in read_binder(sf.BND3, str(Path(path).resolve())).Files:
        name = ntpath.basename(str(f.Name))
        raw = bytes(f.Bytes.ToArray())
        out[name] = (raw, f.Bytes)
    return out


def rows_of(sf, defs, net_bytes):
    p = read_file(sf.PARAM, net_bytes)
    for d in defs:
        if str(d.ParamType) == str(p.ParamType):
            p.ApplyParamdef(d)
            break
    else:
        return None
    rows = {}
    for r in p.Rows:
        rows[int(r.ID)] = {str(c.Def.InternalName): str(c.Value) for c in r.Cells}
    return rows


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("a", type=Path)
    ap.add_argument("b", type=Path, nargs="?", default=GAME)
    ap.add_argument("--rows", type=int, default=4)
    args = ap.parse_args(argv)
    sf = load_soulsformats()
    defs = [sf.PARAMDEF.XmlDeserialize(str(x), False) for x in sorted(DEFS.glob("*.xml"))]
    a, b = load(sf, defs, args.a), load(sf, defs, args.b)
    for name in sorted(set(a) | set(b)):
        if name not in a or name not in b:
            print(f"{name}: only in {'a' if name in a else 'b'}")
            continue
        if a[name][0] == b[name][0]:
            continue
        ra, rb = rows_of(sf, defs, a[name][1]), rows_of(sf, defs, b[name][1])
        if ra is None or rb is None:
            print(f"{name}: differs (no paramdef)")
            continue
        added = sorted(set(ra) - set(rb))
        removed = sorted(set(rb) - set(ra))
        fields, examples = Counter(), []
        changed = 0
        for rid in sorted(set(ra) & set(rb)):
            diff = [k for k in ra[rid] if ra[rid][k] != rb[rid].get(k)]
            if diff:
                changed += 1
                fields.update(diff)
                if len(examples) < args.rows:
                    examples.append(f"    {rid}: " + ", ".join(f"{k} {rb[rid].get(k)}->{ra[rid][k]}" for k in diff[:6]))
        print(f"{name}: changed {changed}, added {len(added)}, removed {len(removed)}")
        if fields:
            print("  fields: " + ", ".join(f"{k} x{n}" for k, n in fields.most_common(12)))
        for e in examples:
            print(e[:300])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
