"""
jump_attack_touch.py - swing time at which a jump attack should touch the ground (read only, ER files in nuxe\\chr).

The ER landing clip (swing ID + 40) has the same arms and weapon as the swing up to the hit, but its legs stand on
the ground the whole time and its pelvis drops into the impact crouch (-0.4..-0.5 m) around the hit. A touchdown in
that crouch made the pose snap (player test 2026-11-15: every jump attack except the hammer R2, which touched down at
0.53 s). The best touchdown is the swing time before the hit (window 0.20 s .. hit + 0.05 s) where the landing at the
same time differs least from the swing: pelvis height (0.06 m), hands relative to the pelvis (0.10 m) and the right
weapon axis (10 deg) weigh the same; feet are ignored (tucked in the air, planted in the landing). Typical result:
0.33-0.53 s.

For every row of native/er_engine/jump_attack_table.h the ER group is picked the same way as in add_jump_attacks.py
(own clip, then FALLBACK). Writes native/er_engine/jump_attack_touch.h; er_engine.dll sets the fall gravity after a jump
attack so that the touchdown on flat ground comes at that time ([Jump] JumpAtkTouchTiming).

  python tools\\jump_attack_touch.py
"""
from __future__ import annotations

import ntpath
import re
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from add_jump_attacks import FALLBACK, LAND_OFFSET, PAIRS, er_hkx, first_hit, type_id  # noqa: E402
from boss_anim_port import frames_to_arrays, parents_of, ref_arrays, to_model_space  # noqa: E402
from er_land_settle import _ctx, _entries  # noqa: E402
from tae_compare import DSAS, ER_ANI, template  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
TABLE = ROOT / "native/er_engine/jump_attack_table.h"
OUT = ROOT / "native/er_engine/jump_attack_touch.h"
DT = 1 / 30
W_PELVIS, W_HANDS, W_WPN = 0.06, 0.10, 10.0
_clips: dict = {}


def clip(group: int, anim: int):
    key = (group, anim)
    if key not in _clips:
        c = _ctx()
        ents, comp = _entries(f"c0000_a{group // 10}x")
        data = ents.get(f"a{group:03d}_{anim:06d}.hkx")
        if data is None:
            _clips[key] = None
            return None
        ac = c["e"].AnimationHKX.from_bytes(data, compendium=comp).animation_container
        ci = ac.to_interleaved_container() if ac.is_spline else ac
        sk = c["skel"]
        names = [b.name for b in sk.bones]
        T, Q = frames_to_arrays(ci.interleaved_data, list(ac.hkx_binding.transformTrackToBoneIndices), len(names),
                                ref_arrays(sk))
        P, rots = to_model_space(parents_of(sk), T, Q)
        _clips[key] = (P, rots, float(ac.hkx_animation.duration), names)
    return _clips[key]


def pose(c, t):
    P, rots, dur, names = c
    k = min(len(P) - 1, int(round(min(t, dur) / dur * (len(P) - 1))))
    pel = P[k, names.index("Pelvis")]
    hands = np.array([P[k, names.index(b)] - pel for b in ("R_Hand", "L_Hand")])
    wpn = rots[names.index("R_Weapon")][k].apply([1, 0, 0])
    return pel[1], hands, wpn


def mismatch(s, land, t):
    ps, hs, ws = pose(s, t)
    pl, hl, wl = pose(land, t)
    dp = pl - ps
    dh = float(np.linalg.norm(hs - hl, axis=1).max())
    ang = float(np.degrees(np.arccos(np.clip(np.dot(ws, wl), -1, 1))))
    return abs(dp) / W_PELVIS + dh / W_HANDS + ang / W_WPN, dp, dh, ang


def main() -> int:
    rows = [tuple(int(x) for x in m.groups()) for m in re.finditer(r"\{(\d+), (\d+), \d+, (\d+),", TABLE.read_text())]
    rows = [(anim, hit) for anim, hit, land in rows if anim and land]
    load = _ctx()["sf"]
    from SoulsFormats import TAE
    from sfbridge import read_binder, read_file
    ae = type_id(template(DSAS / "TAE.Template.ER.xml"), "InvokeAttackBehavior")
    er_taes = {ntpath.basename(f.Name).lower(): f for f in read_binder(load.BND4, str(ER_ANI)).Files}
    tae_cache: dict = {}
    out = []
    for anim, hit_ms in sorted(rows):
        gg, new_id = f"{anim // 10000:02d}", anim % 10000
        er_id = next(e for _s, n, e in PAIRS if n == new_id)
        pick = None
        for need_land in (True, False):  # same order as add_jump_attacks.py
            for eg in [gg] + FALLBACK.get(gg, []):
                if eg not in tae_cache:
                    tae_cache[eg] = read_file(TAE, er_taes[f"a{eg}.tae"].Bytes) if f"a{eg}.tae" in er_taes else None
                et = tae_cache[eg]
                ea = next((a for a in et.Animations if int(a.ID) == er_id), None) if et else None
                if er_hkx(eg, er_id) is None or ea is None or first_hit(list(ea.Events), ae) is None:
                    continue
                el = next((a for a in et.Animations if int(a.ID) == er_id + LAND_OFFSET), None)
                land_ok = er_hkx(eg, er_id + LAND_OFFSET) is not None and el is not None and \
                    first_hit(list(el.Events), ae) is not None
                if need_land and not land_ok:
                    continue
                pick = eg
                break
            if pick:
                break
        s, land = (clip(int(pick), er_id), clip(int(pick), er_id + LAND_OFFSET)) if pick else (None, None)
        if s is None or land is None:
            print(f"  {anim}: no ER swing / landing clip - left out (the DLL keeps the old gravity)")
            continue
        hi = hit_ms / 1000 + 0.05
        best = min((mismatch(s, land, k * DT), k * DT) for k in range(int(0.2 / DT), int(hi / DT) + 1))
        (_score, dp, dh, ang), t = best
        out.append((anim, int(round(t * 1000))))
        print(f"  {anim} <- a{int(pick):03d}_{er_id:06d}: touchdown {t:.2f} s (hit {hit_ms / 1000:.2f} s), "
              f"pelvis {dp:+.2f} m, hands {dh:.2f} m, weapon {ang:.0f} deg")
    lines = ["// Generated by tools/jump_attack_touch.py - do not edit by hand.", "#pragma once",
             "// anim = swing in the air (jump_attack_table.h); touchMs = swing time at which a touchdown fits the ER",
             "// landing best (pelvis, hands, weapon); er_engine.dll times the fall after a jump attack to it.",
             "struct JumpAttackTouchRow { int anim; unsigned touchMs; };",
             "static const JumpAttackTouchRow kJumpAttackTouch[] = {"]
    lines += [f"    {{{a}, {ms}}}," for a, ms in out] + ["    {0, 0},", "};"]
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"OK ({len(out)} jump attacks) -> {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
