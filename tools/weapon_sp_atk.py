"""List DSR weapons with a special attack category (EquipParamWeapon.spAtkcategory != 0), read only.

A weapon's normal attacks come from its animation group aGG (wepmotionCategory); with spAtkcategory = SS some
attacks (usually the R2) come from TAE aSS instead (player log 2026-11-15: Great Club R2 = 693300 / 694300,
R1 = 354000). Prints weapon ID, English name, wepmotionCategory, spAtkcategory, and which a<SS> attacks exist.

  python tools/weapon_sp_atk.py [--category 69] [--vanilla]
"""
from __future__ import annotations

import argparse
import ntpath
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sfbridge import load_soulsformats, read_binder, read_file  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
GAME = Path(r"F:\SteamLibrary\steamapps\common\DARK SOULS REMASTERED")
MOD_PARAM = ROOT / "dist/mods/c0000_er_engine/files/param/GameParam/GameParam.parambnd.dcx"
DEFS = Path(r"C:\Users\nemos\workspace\toolsy\Smithbox_2_2_6_2026_09_20_b\Assets\PARAM\DS1R\Defs")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--category", type=int, nargs="*", default=[])
    ap.add_argument("--vanilla", action="store_true")
    args = ap.parse_args(argv)
    param_path = str((GAME / "param/GameParam/GameParam.parambnd.dcx") if args.vanilla else MOD_PARAM)
    msg_path = str(GAME / "msg/ENGLISH/item.msgbnd.dcx")
    ani_path = str(GAME / "chr/c0000.anibnd.dcx")
    sf = load_soulsformats()
    f = next(f for f in read_binder(sf.BND3, param_path).Files
             if ntpath.basename(str(f.Name)).lower() == "equipparamweapon.param")
    p = read_file(sf.PARAM, f.Bytes)
    p.ApplyParamdef(sf.PARAMDEF.XmlDeserialize(str(DEFS / "EquipParamWeapon.xml"), False))

    names = {}
    try:
        for mf in read_binder(sf.BND3, msg_path).Files:
            n = ntpath.basename(str(mf.Name))
            if n.startswith("武器名") or "weapon" in n.lower():
                for e in read_file(sf.FMG, mf.Bytes).Entries:
                    if e.Text:
                        names.setdefault(int(e.ID), str(e.Text))
    except Exception as ex:  # noqa: BLE001
        print("names unavailable:", type(ex).__name__, ex)

    from SoulsFormats import TAE
    tae_ids = {}
    for tf in read_binder(sf.BND3, ani_path).Files:
        n = ntpath.basename(str(tf.Name)).lower()
        if n.endswith(".tae") and n[0] == "a" and n[1:-4].isdigit():
            tae_ids[int(n[1:-4])] = tf

    by_cat = defaultdict(list)
    for r in p.Rows:
        sp = int(r["spAtkcategory"].Value)
        if sp == 0 or (args.category and sp not in args.category):
            continue
        wid = int(r.ID)
        # upgrades and infusions are rows of their own (+1..+15, +100..+900): keep the base row
        if wid % 1000 != 0:
            continue
        by_cat[sp].append((wid, names.get(wid, str(r.Name or "")), int(r["wepmotionCategory"].Value)))

    for sp in sorted(by_cat):
        anims = []
        tf = tae_ids.get(sp)
        if tf is not None:
            tae = read_file(TAE, tf.Bytes)
            anims = sorted(int(a.ID) for a in tae.Animations)
        print(f"== spAtkcategory {sp}: TAE a{sp}: {len(anims)} animations"
              + (f" ({', '.join(str(a) for a in anims[:40])}{' ...' if len(anims) > 40 else ''})" if anims else " (missing)"))
        seen = set()
        for wid, name, mot in sorted(by_cat[sp]):
            key = (name, mot)
            if key in seen:
                continue
            seen.add(key)
            print(f"   {wid:>9}  a{mot:02d}  {name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
