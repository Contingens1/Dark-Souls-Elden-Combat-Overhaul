"""
gen_attack_speed_table.py - tabela przyspieszania atakow DSR do czasow ER (dla er_engine.dll).

Animacja i TAE zostaja z DSR; DLL zmienia predkosc odtwarzania (ChrAnimData+0xA8) odcinkami tak,
zeby punkty kluczowe DSR wypadly w czasach ER:
    0 -> poczatek trafienia -> koniec trafienia -> okno kolejnego ataku (DSR JT4 <- ER JT115/JT4)
Po ostatnim punkcie predkosc wraca do 1.0. Pary z anim_map_attacks.json.

Weapons with unique attacks (EquipParamWeapon.spAtkcategory SS >= 50: Great Club R2 = 693300 / 694300, the whole
moveset of Server / Murakumo = a51) play them from TAE aSS, so until 2026-11-15 they kept the DSR tempo while the
rest of their group was sped up (player: "they will stand out from the ER-shaped ones"). Their rows use the same
pairs: DSR events from TAE aSS (an entry that only references another animation takes that animation's events, as
the game does), ER target from the ER TAE of the weapon's group (wepmotionCategory). The "never ahead of ER" rule
(a segment is never sped up past the ER time) is applied to all of them, as they are untested. Animations are never
slowed down, so an attack that is already faster than its ER counterpart in DSR stays faster, as in the normal
groups (Server R1: hit 0.54 s like ER, next-attack window 0.81 s, ER 0.93 s, because its DSR recovery is short).

Uzycie (CMD): python tools\\gen_attack_speed_table.py   -> native/er_engine/attack_speed_table.h
"""
from __future__ import annotations

import json
import ntpath
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sfbridge import load_soulsformats, read_binder, read_file  # noqa: E402
from tae_compare import DSAS, ER_ANI, template  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
MAP = ROOT / "tools" / "anim_map_attacks.json"
DSR_SRC = ROOT / "work" / "c0000.anibnd.before_attacks.dcx"  # TAE DSR bez zmian okien atakow
OUT = ROOT / "native" / "er_engine" / "attack_speed_table.h"
SPEED_MIN, SPEED_MAX = 1.0, 2.0  # bez zwalniania animacji DSR (wyglada zle) - tylko przyspieszenia
# Zamach i trafienie przyspieszone widac golym okiem (test: atak z przewrotu x2 wygladal niewiarygodnie)
SWING_MAX = 1.35
# Ciezkie bronie: przyspieszony powrot widac (test: Dragon Tooth R2 x1.95) - nizszy limit koncowki
HEAVY_GROUPS, HEAVY_RECOVERY_MAX = {32, 35}, 1.5
# Groups where the "never ahead of ER" rule is applied (2026-11-13: halberds, reported as absurdly fast).
# Other groups keep the speeds the player has already tested; the script lists what would change there.
CUMULATIVE_GROUPS = {"a38"}
GAME = Path(r"F:\SteamLibrary\steamapps\common\DARK SOULS REMASTERED")
MOD_PARAM = ROOT / "dist/mods/c0000_er_engine/files/param/GameParam/GameParam.parambnd.dcx"
DEFS = Path(r"C:\Users\nemos\workspace\toolsy\Smithbox_2_2_6_2026_09_20_b\Assets\PARAM\DS1R\Defs")


def segment_speeds(kd, ke, gnum):
    """Speeds of the three segments (swing, hit, recovery) and the same with the 'never ahead of ER' rule."""
    speeds = [max(SPEED_MIN, min(SWING_MAX if i < 2 else (HEAVY_RECOVERY_MAX if gnum in HEAVY_GROUPS else SPEED_MAX),
                                 (kd[i + 1] - kd[i]) / max(1e-3, ke[i + 1] - ke[i])))
              for i in range(3)]
    # Never finish a segment earlier than ER does. Without this a DSR attack that hits much earlier
    # than its ER counterpart (halberd running R1: hit at 0.07 s, ER 0.50 s) still got its recovery
    # compressed to the ER segment length and ended at about half the ER time.
    real, capped = 0.0, []
    for i in range(3):
        seg = kd[i + 1] - kd[i]
        room = ke[i + 1] - real
        s = speeds[i] if room <= 1e-3 else max(SPEED_MIN, min(speeds[i], seg / room))
        capped.append(s)
        real += seg / s
    return speeds, capped


def special_categories(sf) -> dict[int, int]:
    """spAtkcategory -> weapon group (wepmotionCategory) for categories whose weapons all share one group."""
    param = MOD_PARAM if MOD_PARAM.exists() else GAME / "param/GameParam/GameParam.parambnd.dcx"
    f = next(f for f in read_binder(sf.BND3, str(param)).Files
             if ntpath.basename(str(f.Name)).lower() == "equipparamweapon.param")
    p = read_file(sf.PARAM, f.Bytes)
    p.ApplyParamdef(sf.PARAMDEF.XmlDeserialize(str(DEFS / "EquipParamWeapon.xml"), False))
    groups: dict[int, set[int]] = {}
    for r in p.Rows:
        sp = int(r["spAtkcategory"].Value)
        if sp:
            groups.setdefault(sp, set()).add(int(r["wepmotionCategory"].Value))
    for sp, gs in sorted(groups.items()):
        if len(gs) != 1:
            print(f"  a{sp}: weapons in several groups {sorted(gs)} - skipped")
    return {sp: next(iter(gs)) for sp, gs in groups.items() if len(gs) == 1}


def type_id(tpl, name):
    return next(i for i, (n, _) in tpl.items() if n == name)


def jt_start(events, wanted):
    for w in wanted:
        s = [e.StartTime for e in events if int(e.Type) == 0
             and struct.unpack_from("<i", bytes(e.GetParameterBytes(False)))[0] == w]
        if s:
            return min(s)
    return None


def knots(events, atk, cancel_jts):
    hits = [e for e in events if int(e.Type) == atk]
    c = jt_start(events, cancel_jts)
    if not hits or c is None:
        return None
    return [0.0, min(e.StartTime for e in hits), max(e.EndTime for e in hits), c]


def main() -> int:
    cfg = json.loads(MAP.read_text(encoding="utf-8-sig"))
    mapping = {k: v for k, v in cfg.items() if not k.startswith("_")}
    for g in cfg.get("_grupy", []):
        mapping.setdefault(g, cfg["_wspolne_pary"])
    sf = load_soulsformats()
    from SoulsFormats import BND3, BND4, TAE
    t1, te = template(DSAS / "TAE.Template.DS1.xml"), template(DSAS / "TAE.Template.ER.xml")
    a1, ae = type_id(t1, "InvokeAttackBehavior"), type_id(te, "InvokeAttackBehavior")
    dsr = {ntpath.basename(f.Name).lower(): f for f in read_binder(BND3, str(DSR_SRC)).Files}
    er = {ntpath.basename(f.Name).lower(): f for f in read_binder(BND4, str(ER_ANI)).Files}
    rows = []
    changed = []
    for g, pairs in mapping.items():
        if f"{g}.tae" not in dsr or f"{g}.tae" not in er:
            print(f"  {g}: brak TAE w DSR lub ER - pomijam")
            continue
        dt = {int(a.ID): list(a.Events) for a in read_file(TAE, dsr[f"{g}.tae"].Bytes).Animations}
        et = {int(a.ID): list(a.Events) for a in read_file(TAE, er[f"{g}.tae"].Bytes).Animations}
        gnum = int(g[1:])
        for d_id, e_id in pairs:
            kd = knots(dt.get(d_id, []), a1, (4,))
            ke = knots(et.get(e_id, []), ae, (115, 4))
            if not kd or not ke:
                pass  # brak animacji lub trafienia w jednej z gier
                continue
            speeds, capped = segment_speeds(kd, ke, gnum)
            if capped != speeds:
                changed.append((gnum, gnum * 10000 + d_id, speeds, capped))
                if g in CUMULATIVE_GROUPS:
                    speeds = capped
            full = gnum * 10000 + d_id
            rows.append((full, kd, speeds))
            print(f"  {full}: DSR {['%.2f' % x for x in kd]} -> ER {['%.2f' % x for x in ke]}  "
                  f"predkosci {['%.2f' % s for s in speeds]}")
    # Unique attacks (spAtkcategory): DSR events from TAE aSS, ER target from the weapon group's ER TAE.
    dsr_taes = {}

    def dsr_anims(gnum):
        if gnum not in dsr_taes:
            tf = dsr.get(f"a{gnum}.tae")
            dsr_taes[gnum] = {int(a.ID): a for a in read_file(TAE, tf.Bytes).Animations} if tf else {}
        return dsr_taes[gnum]

    special = 0
    for sp, gg in sorted(special_categories(sf).items()):
        pairs = mapping.get(f"a{gg}")
        if not pairs or f"a{gg}.tae" not in er or not dsr_anims(sp):
            continue
        et = {int(a.ID): list(a.Events) for a in read_file(TAE, er[f"a{gg}.tae"].Bytes).Animations}
        for d_id, e_id in pairs:
            a = dsr_anims(sp).get(d_id)
            if a is None:
                continue  # this attack comes from the group's own TAE (row above)
            kd = knots(list(a.Events), a1, (4,))
            ref = int(a.Unknown1) if kd is None and a.AnimFileReference else 0
            if ref:  # an entry without events of its own plays another animation with that one's events
                r = dsr_anims(ref // 10000).get(ref % 10000)
                kd = knots(list(r.Events), a1, (4,)) if r is not None else None
            ke = knots(et.get(e_id, []), ae, (115, 4))
            if not kd or not ke:
                continue
            _, speeds = segment_speeds(kd, ke, gg)
            full = sp * 10000 + d_id
            rows.append((full, kd, speeds))
            special += 1
            print(f"  {full} (a{gg}{', events of %d' % ref if ref else ''}): DSR {['%.2f' % x for x in kd]} -> "
                  f"ER {['%.2f' % x for x in ke]}  predkosci {['%.2f' % s for s in speeds]}")
    print(f"unique attacks (spAtkcategory): {special} rows")
    print(f"'never ahead of ER' rule: {len(changed)} rows would change; applied to groups {sorted(CUMULATIVE_GROUPS)}")
    for gnum, full, old, new in changed:
        mark = "APPLIED" if f"a{gnum}" in CUMULATIVE_GROUPS else "not applied"
        print(f"  cap {full}: {['%.2f' % s for s in old]} -> {['%.2f' % s for s in new]}  ({mark})")
    lines = ["// Wygenerowane przez tools/gen_attack_speed_table.py - nie edytowac recznie.",
             "// anim, punkty DSR (s): 0, trafienie start, trafienie koniec, okno ataku; predkosc odcinkow.",
             "#pragma once",
             "struct AttackSpeedRow { int anim; float knot[4]; float speed[3]; };",
             "static const AttackSpeedRow kAttackSpeed[] = {"]
    for full, kd, sp in rows:
        lines.append(f"    {{{full}, {{{', '.join('%.4ff' % x for x in kd)}}}, {{{', '.join('%.4ff' % s for s in sp)}}}}},")
    lines.append("};")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"OK -> {OUT} ({len(rows)} animacji)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
