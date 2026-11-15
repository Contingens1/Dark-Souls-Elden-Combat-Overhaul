"""Shared boss GameParam for the test launcher: the main mod's GameParam (ER lock-on camera) + the param rows of every
boss package under test, stacked in one file.

Why: Mod Engine 2 takes each game file whole from the FIRST mod folder (in the `mods` list of the toml) that has it;
it does not merge params. The Artorias test package ships its own GameParam (main mod + Artorias rows), so a second
boss package with its own GameParam (Gwyn phase 2: bullets, attacks, SpEffects) would be hidden by it, or hide it.
This tool writes one file with all rows; its folder goes first in config_test_all.toml.

Sources (each writes its rows into the open GameParam binder; order = --only order):
  artorias  tools/artorias_phase2.apply_params   (--artorias-tag picks the options of that package, see below)
  gwyn      tools/gwyn_phase2.apply_params        (stage 1 of docs/nieoficjalne/PLAN_GWYN_FAZA2.md; skipped while the
                                                   module does not exist)
A row that two sources add or change stops the build (collision). Rows are compared field by field (Smithbox DS1R
paramdefs) before and after each source; boss_rows.txt lists what each source added or changed.

Writes (never a game folder):
  dist/mods/bossy_nightreign/files_bosses_param/param/GameParam/GameParam.parambnd.dcx
  dist/mods/bossy_nightreign/files_bosses_param/boss_rows.txt

  python tools/boss_gameparam.py                                  # artorias (as files_c4100_v2_test) + gwyn
  python tools/boss_gameparam.py --only artorias --artorias-tag _v2 --dry-run \
         --check dist/mods/bossy_nightreign/files_c4100_v2/param/GameParam/GameParam.parambnd.dcx
--check REF: report the params (and rows) that differ from REF; with --dry-run nothing is written.
Rerun after any change of the main mod's GameParam, of artorias_phase2.py or of gwyn_phase2.py.
"""
from __future__ import annotations

import argparse
import datetime
import ntpath
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sfbridge import load_soulsformats, read_binder, read_file  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
MAIN = ROOT / "dist" / "mods" / "c0000_er_engine" / "files" / "param" / "GameParam" / "GameParam.parambnd.dcx"
PKG = ROOT / "dist" / "mods" / "bossy_nightreign" / "files_bosses_param"
OUT = PKG / "param" / "GameParam" / "GameParam.parambnd.dcx"
MANIFEST = PKG / "boss_rows.txt"
DEFS = Path(r"C:\Users\nemos\workspace\toolsy\Smithbox_2_2_6_2026_09_20_b\Assets\PARAM\DS1R\Defs")
# param file -> paramdef (only params that some source edits need one; add a line when a new param is touched)
DEF_OF = {"npcparam": "NpcParam", "speffectparam": "SpEffect", "speffectvfxparam": "SpEffectVfx",
          "atkparam_npc": "AtkParam", "atkparam_pc": "AtkParam", "bullet": "BulletParam",
          "behaviorparam": "BehaviorParam", "throwparam": "ThrowParam", "npcthinkparam": "NpcThinkParam"}
# options of the Artorias packages (artorias_phase2.py main(): --tag, --hp 880, --anim-offset 0, --easy)
ARTORIAS_TAGS = {"_v2": {"easy": False}, "_v2_test": {"easy": False}}


def snapshot(bnd) -> dict[str, bytes]:
    return {ntpath.basename(str(f.Name)).lower(): bytes(f.Bytes.ToArray()) for f in bnd.Files}


def rows_of(sf, name: str, data: bytes) -> dict[int, tuple]:
    from sfbridge import net_bytes, to_memory
    key = name.removesuffix(".param")
    if key not in DEF_OF:
        raise KeyError(f"{name}: no paramdef known - add it to DEF_OF")
    p = read_file(sf.PARAM, to_memory(net_bytes(data)))
    p.ApplyParamdef(sf.PARAMDEF.XmlDeserialize(str(DEFS / f"{DEF_OF[key]}.xml"), False))
    return {int(r.ID): (str(r.Name or ""),) + tuple(str(c.Value) for c in r.Cells) for r in p.Rows}


def row_diff(sf, name: str, before: bytes, after: bytes) -> tuple[list[int], list[int], list[int]]:
    a, b = rows_of(sf, name, before), rows_of(sf, name, after)
    added = sorted(set(b) - set(a))
    removed = sorted(set(a) - set(b))
    changed = sorted(i for i in set(a) & set(b) if a[i] != b[i])
    return added, changed, removed


def ranges(ids: list[int]) -> str:
    out, i = [], 0
    while i < len(ids):
        j = i
        while j + 1 < len(ids) and ids[j + 1] == ids[j] + 1:
            j += 1
        out.append(str(ids[i]) if i == j else f"{ids[i]}-{ids[j]}")
        i = j + 1
    return ", ".join(out)


def src_artorias(sf, bnd, args) -> bool:
    import artorias_phase2 as ap2
    opts = ARTORIAS_TAGS[args.artorias_tag]
    easy = opts["easy"] if args.artorias_easy is None else args.artorias_easy
    print(f"artorias: options of files_c4100{args.artorias_tag} (hp {args.artorias_hp}, anim offset "
          f"{args.artorias_anim_offset}, easy {easy})")
    ap2.apply_params(sf, bnd, args.artorias_hp, args.artorias_anim_offset, fx=True, easy=easy)
    return True


def src_gwyn(sf, bnd, args) -> bool:
    try:
        import gwyn_phase2
    except ModuleNotFoundError:
        print("gwyn: tools/gwyn_phase2.py does not exist yet (stage 1 of PLAN_GWYN_FAZA2) - skipped")
        return False
    gwyn_phase2.apply_params(sf, bnd)
    return True


SOURCES = {"artorias": src_artorias, "gwyn": src_gwyn}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="+", choices=sorted(SOURCES), default=["artorias", "gwyn"])
    ap.add_argument("--artorias-tag", choices=sorted(ARTORIAS_TAGS), default="_v2_test",
                    help="which Artorias package's options (the test launcher loads files_c4100_v2_test)")
    ap.add_argument("--artorias-hp", type=int, default=880)
    ap.add_argument("--artorias-anim-offset", type=int, default=0)
    ap.add_argument("--artorias-easy", type=lambda s: s.lower() in ("1", "true", "yes"), default=None,
                    help="override the package's --easy (1/0)")
    ap.add_argument("--check", type=Path, help="reference parambnd: list params / rows that differ")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)
    check = args.check.resolve() if args.check else None   # SoulsFormats changes the working directory
    sf = load_soulsformats()
    bnd = read_binder(sf.BND3, str(MAIN))
    base = snapshot(bnd)
    owner: dict[tuple[str, int], str] = {}
    report = [f"# Shared boss GameParam, built {datetime.datetime.now():%Y-%m-%d %H:%M}",
              f"# base: {MAIN} (modified {datetime.datetime.fromtimestamp(MAIN.stat().st_mtime):%Y-%m-%d %H:%M})"]
    for name in args.only:
        before = snapshot(bnd)
        if not SOURCES[name](sf, bnd, args):
            report.append(f"{name}: skipped")
            continue
        after = snapshot(bnd)
        report.append(f"{name}:")
        for pname in sorted(after):
            if after[pname] == before.get(pname):
                continue
            added, changed, removed = row_diff(sf, pname, before[pname], after[pname])
            if removed:
                raise RuntimeError(f"{name} removed rows from {pname}: {ranges(removed)}")
            for rid in added + changed:
                if (pname, rid) in owner:
                    raise RuntimeError(f"collision: {pname} row {rid} written by {owner[(pname, rid)]} and {name}")
                owner[(pname, rid)] = name
            report.append(f"  {pname}: added {ranges(added) or '-'}; changed {ranges(changed) or '-'}")
    final = snapshot(bnd)
    report.append("params changed against the base: " + ", ".join(sorted(p for p in final if final[p] != base.get(p))))
    print("\n".join(report))
    if check:
        ref = read_binder(sf.BND3, str(check))
        rsnap = snapshot(ref)
        ref.Dispose()
        diff = sorted(p for p in set(final) | set(rsnap) if final.get(p) != rsnap.get(p))
        print(f"check against {check}: {len(final)} params here, {len(rsnap)} there, {len(diff)} differ")
        for p in diff:
            if p not in final or p not in rsnap:
                print(f"  {p}: only {'here' if p in final else 'there'}")
                continue
            try:
                added, changed, removed = row_diff(sf, p, rsnap[p], final[p])
                print(f"  {p}: rows only here {ranges(added) or '-'}; differ {ranges(changed) or '-'}; "
                      f"only there {ranges(removed) or '-'}")
            except KeyError:
                print(f"  {p}: bytes differ (no paramdef for a row diff)")
    if args.dry_run:
        print("dry-run: nothing written")
        return 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    tmp = OUT.with_name(OUT.name + ".tmp")
    bnd.Write(str(tmp))
    bnd.Dispose()
    import gc
    gc.collect()
    tmp.replace(OUT)
    MANIFEST.write_text("\n".join(report) + "\n", encoding="utf-8")
    chk = read_binder(sf.BND3, str(OUT))
    print(f"written {OUT} ({OUT.stat().st_size} B, {chk.Files.Count} params) and {MANIFEST.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
