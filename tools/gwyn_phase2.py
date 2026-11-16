"""Gwyn (c5370) phase 2 = Soul of Cinder (DS3), data side: param rows and the transition animations of the phase-2
test package files_c5370_p2 (docs/PLAN_PROJEKTU.md §6c; stage 1 of the working plan).

Player decisions 2026-11-15: phase 1 = the DS1 Gwyn (game clips 3000-3021, DS1 AI), phase 2 = the Soul of Cinder
clips as a variant set 13000-13021 (a SpEffect with animIdOffset 10000 makes every 3xxx request play 13xxx, as the
game's own c2360 / c2540 do), transition at HP 0 with the HP bar refilled (as Artorias: the DLL keeps the boss alive
with NoDead until the transition has played).

Transition = the DS3 one (m41_00_00_00.emevd: 20010 then 20005), ported by tools/nr_boss_port.py:
  3028 (DS3 20010, 3.93 s): steps back and drops to one knee with the left hand on the ground, gets up;
       SpEffect 53700 at the start (no damage taken), super armor (JT24), no turning except while getting up
       (90 deg/s 2.73-3.40 s as in DS3), combo window at the end -> 3029 (AI: ComboAttackTunableSpin -> ComboFinal);
  3029 (DS3 20005, 7.97 s): raises the sword with both hands and drives it into the ground (~3.75 s), kneels, gets
       up; at the plunge SpEffect 53703 (HP refilled in 1.2 s; DS3 refills in one go with SpEffect 12119
       changeHpRate -100, here the tick refill tested on Artorias), SpEffect 53701 = phase 2 (animIdOffset 10000,
       endless; the AI reads it), Gwyn's own grab-explosion fire FFX 15374 at the blade tip, a camera shake and the
       explosion sound; at 3.97 s the wave: bullet 53740 = the game's Wrath of the Gods bullet (its own expanding
       FFX 20176, 4 m - the damage area is the size of the effect, the Artorias lesson) with Gwyn's fire damage.
  Exit windows (JT23 / 78 / 79 / 86) from 7.47 s as in DS3.
Phase-2 marker (player 2026-11-16: a lasting visible sign, since the SoC clips look almost like DS1), given at the
plunge with 53701 and kept for the whole phase: Gwyn's own sword flame along the whole blade and a red glow on the
chest (details: MARK_* below).
13023 = the SoC grab 13006 under the grab-into-throw number 3023 (DS1 3023 is the clip of 3006 with attack
behaviour 350 instead of 160): own clip entry (copy of a01_3006.hkx) as the game's own 13xxx entries, events of
13006 with 160 -> 350. Without it phase 2 would fall back to the DS1 3023.
NpcParam 537000 hp 1550 -> 900: two bars together about 1.16x the vanilla fight (Artorias: 1500 -> 880).

Writes:
  the anibnd of files_c5370_p2 in place (rerun after every `nr_boss_port.py --install --tag _p2` + widen_hits);
  param rows only through apply_params (tools/boss_gameparam.py stacks them with the Artorias rows into the shared
  files_bosses_param GameParam).

  python tools/gwyn_phase2.py [--dry-run]
"""
from __future__ import annotations

import argparse
import gc
import ntpath
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sfbridge import load_soulsformats, net_bytes, read_binder, read_file, to_memory  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
PKG = ROOT / "dist" / "mods" / "bossy_nightreign" / "files_c5370_p2"
ANIBND = PKG / "chr" / "c5370.anibnd.dcx"
GAME_C4100 = Path(r"F:\SteamLibrary\steamapps\common\DARK SOULS REMASTERED\chr\c4100.anibnd.dcx")  # read only
DEFS = Path(r"C:\Users\nemos\workspace\toolsy\Smithbox_2_2_6_2026_09_20_b\Assets\PARAM\DS1R\Defs")

NPC_ID, HP = 537000, 900
SP_NEUTRAL, SP_OFFSET = 5400, 5401        # vanilla: endless, no stats / "weapon change, anim ID offset 10000"
SP_TRANSITION, SP_PHASE2, SP_HEAL = 53700, 53701, 53703   # free rows 53700-53719 (PLAN_GWYN_FAZA2 §3.3)
TRANSITION_TIME = 8.2                     # s; given at the start of 3028 and again of 3029 (7.97 s)
HEAL_TIME, HEAL_INTERVAL, HEAL_RATE = 1.2, 0.1, -10.0      # % of max HP per tick (negative = heal)
ATK_SRC, ATK_WAVE = 537026, 537035        # Gwyn's grab explosion (fire, no spheres) -> the wave
WAVE_FIRE, WAVE_STAM, WAVE_SA, WAVE_LEVEL = 179, 100, 70, 10   # DS3 bullet 5280904: 179 fire, level 10 knockdown
BULLET_SRC, BULLET_WAVE = 10100, 53740    # Wrath of the Gods (FFX 20176 / hit 20275, 4 m, 0.2 s, through walls)
BEH_SRC, BEH_WAVE = 241000510, 253700440  # a bullet behaviour row (Artorias buff burst) -> Gwyn variation 53700

ANIM_KNEEL, ANIM_PLUNGE = 3028, 3029
ANIM_GRAB, ANIM_GRAB_THROW = 13006, 13023
BEH_GRAB, BEH_GRAB_THROW = 160, 350
KEEP_TYPES = {16: 0.267, 303: 10.0}       # Blend / PlayAnimation(100000): every Gwyn animation has them, 0 s to this
KNEEL_TURN = (2.733, 3.400, 90.0)         # DS3 20010 SetTurnSpeed
PLUNGE = 3.733                            # DS3 20005: SpEffect 12119 (HP) at 3.733, FFX on the ground at 3.767
WAVE_TIME = 3.967                         # DS3 bullet 904
EXIT_PLUNGE = 7.467                       # DS3 JT23 / JT86
FFX_FIRE, DMY_BLADE_TIP, DMY_GROUND = 15374, 12, 230
SOUND_BOOM = (1, 537004002)               # Gwyn bank, right before the grab explosion in 3300

# Phase-2 marker: endless SpEffects given by TAE 401 at the plunge (one per effect: a SpEffect shows one SpEffectVfx
# row through stateInfo, a row one FFX on one dummypoly). Both parts at once, so the player can judge each:
#   - burning sword: Gwyn's own sword flame FFX 15371 (vanilla: one, on dummypoly 11 at the base of the blade, a slot
#     event in animation 0) also mid-blade (13) and at the tip (12) - all loaded in Kiln (FRPG_SfxBnd_m18_00);
#   - red glow: the Red Tearstone Ring aura FFX 24003 (CommonEffects, SpEffectVfx 48) on the chest, dummypoly 220
#     (the player's aura dummypoly; c5370 has it on Spine1).
# SpEffectVfx rows: clones of 205 (the DLC dark aura, existEffectForLarge 1 - the one shown on Artorias; 48 has 0) in
# the empty online-arena rows 206-208 (rows past 242 are ignored by the game; Artorias uses 220-231 and 241). The
# weapon-buff effects (effectType 1) show nothing on a boss dummypoly (Artorias test 13.11 #7).
VFX_TEMPLATE = 205
FFX_SWORD_FLAME, FFX_RED_GLOW = 15371, 24003
DMY_BLADE_MID, DMY_CHEST = 13, 220
MARK = {  # SpEffect -> (SpEffectVfx row, ffx, dummypoly, what)
    53710: (206, FFX_SWORD_FLAME, DMY_BLADE_MID, "sword flame mid-blade"),
    53711: (207, FFX_SWORD_FLAME, DMY_BLADE_TIP, "sword flame at the tip"),
    53712: (208, FFX_RED_GLOW, DMY_CHEST, "red glow on the chest"),
}


def set_value(cell, value) -> None:
    import System
    t = str(cell.Def.DisplayType).lower()
    conv = {"s8": System.SByte, "u8": System.Byte, "s16": System.Int16, "u16": System.UInt16,
            "s32": System.Int32, "u32": System.UInt32, "f32": System.Single, "b32": System.Int32}
    if t not in conv:
        raise TypeError(f"{cell.Def.InternalName}: unsupported type {t}")
    cell.Value = conv[t](value)


def edit_row(row, values: dict) -> list[str]:
    cells = {str(c.Def.InternalName): c for c in row.Cells}
    out = []
    for k, v in values.items():
        if k not in cells:
            raise KeyError(f"row {int(row.ID)}: no field {k}")
        old = cells[k].Value
        set_value(cells[k], v)
        out.append(f"{k} {old} -> {cells[k].Value}")
    return out


def clone_row(sf, param, src_id: int, new_id: int, name: str):
    """Copy of row src_id under new_id (replaced if it already exists), inserted in ID order."""
    src = next(r for r in param.Rows if int(r.ID) == src_id)
    for r in list(param.Rows):
        if int(r.ID) == new_id:
            param.Rows.Remove(r)
    row = sf.PARAM.Row(src)
    row.ID = new_id
    row.Name = name
    pos = next((i for i, r in enumerate(param.Rows) if int(r.ID) > new_id), param.Rows.Count)
    param.Rows.Insert(pos, row)
    return row


def apply_params(sf, bnd, hp: int | None = HP) -> None:
    """Write the Gwyn phase-2 rows into an open GameParam binder (called by tools/boss_gameparam.py, which passes
    hp=None - NpcParam untouched - while the launcher does not load the phase-2 package)."""
    files = {ntpath.basename(str(f.Name)).lower(): f for f in bnd.Files}

    def open_param(file_name: str, def_name: str):
        f = files[f"{file_name.lower()}.param"]
        p = read_file(sf.PARAM, f.Bytes)
        p.ApplyParamdef(sf.PARAMDEF.XmlDeserialize(str(DEFS / f"{def_name}.xml"), False))
        return f, p

    changed = []
    if hp is not None:
        f_npc, npc = open_param("NpcParam", "NpcParam")
        row = next(r for r in npc.Rows if int(r.ID) == NPC_ID)
        print(f"NpcParam {NPC_ID}: " + "; ".join(edit_row(row, {"hp": hp})))
        changed.append((f_npc, npc))

    f_sp, sp = open_param("SpEffectParam", "SpEffect")
    cut = {k: 0.0 for k in ("slashDamageCutRate", "blowDamageCutRate", "thrustDamageCutRate", "neutralDamageCutRate",
                            "magicDamageCutRate", "fireDamageCutRate", "thunderDamageCutRate")}
    r = clone_row(sf, sp, SP_NEUTRAL, SP_TRANSITION, "c5370 Gwyn phase transition (mod)")
    print(f"SpEffect {SP_TRANSITION} (from {SP_NEUTRAL}): " + "; ".join(edit_row(r, {
        "effectEndurance": TRANSITION_TIME, "spCategory": 0, **cut})))
    # the game's own offset row (category 100 as on the c2360 / c2540 enemies), made the phase marker
    r = clone_row(sf, sp, SP_OFFSET, SP_PHASE2, "c5370 Gwyn phase 2, anim ID offset 10000 (mod)")
    print(f"SpEffect {SP_PHASE2} (from {SP_OFFSET}): " + "; ".join(edit_row(r, {
        "effectEndurance": -1.0, "animIdOffset": 10000})))
    r = clone_row(sf, sp, SP_NEUTRAL, SP_HEAL, "c5370 Gwyn phase 2 HP refill (mod)")
    print(f"SpEffect {SP_HEAL} (from {SP_NEUTRAL}): " + "; ".join(edit_row(r, {
        "effectEndurance": HEAL_TIME, "spCategory": 0, "motionInterval": HEAL_INTERVAL, "changeHpRate": HEAL_RATE})))
    # marker tracks: category 0, or they would replace 53701 (category 100 of the 5400 / 5401 template)
    for sid, (vrow, _ffx, _dmy, what) in MARK.items():
        r = clone_row(sf, sp, SP_NEUTRAL, sid, f"c5370 Gwyn phase 2 marker: {what} (mod)")
        print(f"SpEffect {sid} (from {SP_NEUTRAL}): " + "; ".join(edit_row(r, {
            "effectEndurance": -1.0, "spCategory": 0, "stateInfo": vrow})))
    changed.append((f_sp, sp))

    f_vfx, vfx = open_param("SpEffectVfxParam", "SpEffectVfx")
    for sid, (vrow, ffx, dmy, what) in MARK.items():
        v = clone_row(sf, vfx, VFX_TEMPLATE, vrow, f"c5370 Gwyn phase 2 marker: {what} (mod)")
        print(f"SpEffectVfx {vrow} (from {VFX_TEMPLATE}): " + "; ".join(edit_row(v, {
            "midstSfxId": ffx, "midstDmyId": dmy})))
    changed.append((f_vfx, vfx))

    f_atk, atk = open_param("AtkParam_Npc", "AtkParam")
    # a bullet with no spheres hits with the Bullet hitRadius (Artorias test 13.11 #4)
    a = clone_row(sf, atk, ATK_SRC, ATK_WAVE, "c5370 Gwyn phase transition fire wave (mod)")
    print(f"AtkParam_Npc {ATK_WAVE} (from {ATK_SRC}): " + "; ".join(edit_row(a, {
        "atkPhys": 0, "atkFire": WAVE_FIRE, "atkStam": WAVE_STAM, "atkSuperArmor": WAVE_SA, "dmgLevel": WAVE_LEVEL,
        "hit0_Radius": 0.0, "hit0_DmyPoly1": -1, "hit1_DmyPoly1": -1})))
    changed.append((f_atk, atk))

    f_bu, bu = open_param("Bullet", "BulletParam")
    b = clone_row(sf, bu, BULLET_SRC, BULLET_WAVE, "[Gwyn] Phase transition wave (mod)")
    print(f"Bullet {BULLET_WAVE} (from {BULLET_SRC}): " + "; ".join(edit_row(b, {"atkId_Bullet": ATK_WAVE})))
    changed.append((f_bu, bu))

    f_be, be = open_param("BehaviorParam", "BehaviorParam")
    r = clone_row(sf, be, BEH_SRC, BEH_WAVE, "c5370 Gwyn phase transition wave (mod)")
    print(f"BehaviorParam {BEH_WAVE} (from {BEH_SRC}): " + "; ".join(edit_row(r, {
        "variationId": NPC_ID // 10, "behaviorJudgeId": BEH_WAVE % 1000, "refId": BULLET_WAVE})))
    changed.append((f_be, be))

    for f, p in changed:
        f.Bytes = to_memory(p.Write())


def jt_of(ev):
    p = bytes(ev.GetParameterBytes(False))
    return struct.unpack_from("<i", p)[0] if int(ev.Type) == 0 and len(p) >= 4 else None


def ints_of(ev) -> tuple:
    p = bytes(ev.GetParameterBytes(False))
    return struct.unpack_from(f"<{len(p) // 4}i", p) if len(p) >= 4 else ()


def add_event(sf, anim, start: float, end: float, template, ints: dict[int, int] | None = None,
              floats: dict[int, float] | None = None) -> None:
    """Append an event of the template's type/size with params overwritten at the given byte offsets."""
    p = bytearray(bytes(template.GetParameterBytes(False)))
    for off, val in (ints or {}).items():
        struct.pack_into("<i", p, off, val)
    for off, val in (floats or {}).items():
        struct.pack_into("<f", p, off, val)
    anim.Events.Add(sf.TAE.Event(float(start), float(end), template.Type, template.Unk04, net_bytes(bytes(p)), False))


def find_event(tae, anim_id: int, pred):
    a = next(a for a in tae.Animations if int(a.ID) == anim_id)
    ev = next((e for e in a.Events if pred(e)), None)
    if ev is None:
        raise RuntimeError(f"no template event in animation {anim_id}")
    return ev


def build_anibnd(sf) -> object:
    bnd = read_binder(sf.BND3, str(ANIBND))
    files = {ntpath.basename(str(f.Name)).lower(): f for f in bnd.Files}
    tentry = files["c5370.tae"]
    tae = read_file(sf.TAE, tentry.Bytes)
    art = read_binder(sf.BND3, str(GAME_C4100))
    atae = read_file(sf.TAE, next(f for f in art.Files if ntpath.basename(str(f.Name)).lower() == "c4100.tae").Bytes)
    t = {
        401: find_event(atae, 3013, lambda e: int(e.Type) == 401),      # SpEffect on self (int 0)
        2: find_event(atae, 3013, lambda e: int(e.Type) == 2),          # bullet (int 0 dummypoly, int 8 behaviour)
        "jt": find_event(tae, 3018, lambda e: jt_of(e) == 24),            # JumpTable (int 0)
        224: find_event(tae, 3018, lambda e: int(e.Type) == 224),       # SetTurnSpeed (float 0)
        96: find_event(tae, 3300, lambda e: int(e.Type) == 96),         # one-shot FFX (ffx, dummypoly, slot)
        144: find_event(tae, 3300, lambda e: int(e.Type) == 144),       # camera shake
        128: find_event(tae, 3300, lambda e: int(e.Type) == 128),       # sound (type, id)
    }

    def jt(anim, s, e, j):
        add_event(sf, anim, s, e, t["jt"], {0: j})

    def reset(anim_id: int):
        a = next(a for a in tae.Animations if int(a.ID) == anim_id)
        old = list(a.Events)
        a.Events.Clear()
        for ev in old:
            if int(ev.Type) in KEEP_TYPES:
                ev.StartTime, ev.EndTime = 0.0, KEEP_TYPES[int(ev.Type)]   # the port stretched them with the clip
                a.Events.Add(ev)
        return a, len(old) - a.Events.Count

    # 3028: kneel
    a, removed = reset(ANIM_KNEEL)
    end = 3.933
    jt(a, 0.0, end, 24)
    jt(a, 0.0, KNEEL_TURN[0], 7)
    jt(a, KNEEL_TURN[1], end, 7)
    add_event(sf, a, KNEEL_TURN[0], KNEEL_TURN[1], t[224], floats={0: KNEEL_TURN[2]})
    add_event(sf, a, 0.0, 0.033, t[401], {0: SP_TRANSITION})
    jt(a, 3.533, end, 79)
    jt(a, 3.667, end, 23)
    jt(a, 3.667, end, 78)
    print(f"anibnd: {ANIM_KNEEL}: {a.Events.Count} events ({removed} template events removed): SpEffect "
          f"{SP_TRANSITION}, JT24 0-{end:.2f}, turn {KNEEL_TURN[2]:.0f} deg/s {KNEEL_TURN[0]:.2f}-{KNEEL_TURN[1]:.2f}, "
          f"combo window {3.667:.2f}")

    # 3029: sword into the ground
    a, removed = reset(ANIM_PLUNGE)
    end = 7.967
    jt(a, 0.0, 7.500, 24)
    jt(a, 0.0, EXIT_PLUNGE, 7)
    add_event(sf, a, 0.0, 0.033, t[401], {0: SP_TRANSITION})
    add_event(sf, a, PLUNGE, PLUNGE + 0.033, t[401], {0: SP_HEAL})
    add_event(sf, a, PLUNGE, PLUNGE + 0.033, t[401], {0: SP_PHASE2})
    for sid in MARK:
        add_event(sf, a, PLUNGE, PLUNGE + 0.033, t[401], {0: sid})
    add_event(sf, a, PLUNGE, PLUNGE + 0.100, t[128], {0: SOUND_BOOM[0], 4: SOUND_BOOM[1]})
    add_event(sf, a, PLUNGE + 0.033, PLUNGE + 0.133, t[96], {0: FFX_FIRE, 4: DMY_BLADE_TIP, 8: -1})
    add_event(sf, a, PLUNGE + 0.033, PLUNGE + 0.133, t[144])
    add_event(sf, a, WAVE_TIME, WAVE_TIME + 0.033, t[2], {0: DMY_GROUND, 8: BEH_WAVE % 1000})
    for j in (79, 23, 78, 86):
        jt(a, EXIT_PLUNGE, end, j)
    print(f"anibnd: {ANIM_PLUNGE}: {a.Events.Count} events ({removed} template events removed): SpEffect "
          f"{SP_TRANSITION} at 0, at {PLUNGE:.2f} {SP_HEAL} + {SP_PHASE2} + marker {'/'.join(map(str, MARK))} "
          f"+ FFX {FFX_FIRE} (dummypoly {DMY_BLADE_TIP}) "
          f"+ shake + sound, wave {BEH_WAVE % 1000} at {WAVE_TIME:.2f} (dummypoly {DMY_GROUND}), exit {EXIT_PLUNGE:.2f}")

    # 13023: the SoC grab clip under the grab-into-throw number
    src = files["a01_3006.hkx"]
    for f in list(bnd.Files):
        if int(f.ID) == ANIM_GRAB_THROW:
            bnd.Files.Remove(f)
    name = str(src.Name).replace("a01_3006", "a01_3023")
    entry = sf.BinderFile(src.Flags, ANIM_GRAB_THROW, name, src.Bytes)
    pos = next((i for i, f in enumerate(bnd.Files) if int(f.ID) > ANIM_GRAB_THROW), bnd.Files.Count)
    bnd.Files.Insert(pos, entry)
    for x in list(tae.Animations):
        if int(x.ID) == ANIM_GRAB_THROW:
            tae.Animations.Remove(x)
    grab = next(x for x in tae.Animations if int(x.ID) == ANIM_GRAB)
    na = sf.TAE.Animation(ANIM_GRAB_THROW, False, 0, -1, "a01_3023.hkxwin")
    n_beh = 0
    for ev in grab.Events:
        p = bytearray(bytes(ev.GetParameterBytes(False)))
        if int(ev.Type) == 1 and len(p) >= 12 and struct.unpack_from("<i", p, 8)[0] == BEH_GRAB:
            struct.pack_into("<i", p, 8, BEH_GRAB_THROW)
            n_beh += 1
        na.Events.Add(sf.TAE.Event(float(ev.StartTime), float(ev.EndTime), ev.Type, ev.Unk04, net_bytes(bytes(p)), False))
    if n_beh != 1:
        raise RuntimeError(f"{ANIM_GRAB} layout changed: {n_beh} attack events with behaviour {BEH_GRAB}")
    pos = next((i for i, x in enumerate(tae.Animations) if int(x.ID) > ANIM_GRAB_THROW), tae.Animations.Count)
    tae.Animations.Insert(pos, na)
    print(f"anibnd: {ANIM_GRAB_THROW} = clip and events of {ANIM_GRAB} ({na.Events.Count}), attack {BEH_GRAB} -> {BEH_GRAB_THROW}")
    tentry.Bytes = to_memory(tae.Write())
    art.Dispose()
    return bnd


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)
    sf = load_soulsformats()
    anibnd = build_anibnd(sf)
    if args.dry_run:
        print("OK (dry-run, nothing written; params: tools/boss_gameparam.py)")
        return 0
    # the source anibnd is memory-mapped while the binder is open: write next to it, close, then replace
    tmp = ANIBND.with_name(ANIBND.name + ".tmp")
    anibnd.Write(str(tmp))
    anibnd.Dispose()
    gc.collect()
    tmp.replace(ANIBND)
    chk = read_binder(sf.BND3, str(ANIBND))
    tae = read_file(sf.TAE, next(f for f in chk.Files if ntpath.basename(str(f.Name)).lower() == "c5370.tae").Bytes)
    ids = {int(a.ID) for a in tae.Animations}
    assert {ANIM_KNEEL, ANIM_PLUNGE, ANIM_GRAB_THROW} <= ids
    print(f"written {ANIBND} ({ANIBND.stat().st_size} B, {chk.Files.Count} entries); "
          f"params: python tools/boss_gameparam.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
