"""Gwyn (c5370, AI 537000) battle script with Soul of Cinder's phase-2 combos (DS3 LastBoss_Gwyn) - build step.

Source: work/boss_ai/537000_battle.soc_ai.lua = the decompiled DS1 script (work/boss_ai/dsr_m18_00/) with the
changes marked "(mod)":
  - Act01: 3000 -> 3011 and 3000 -> 3013 -> 3014 / 3016 next to the DS1 chains (SoC Act01);
  - Act03: thrust 3008 alone 25 %, else into 3012 / 3009 / the grab 3006 (SoC Act03);
  - Act04: lunge 3010 into the two-hand thrust 3015 (SoC Act04);
  - Act09: kick 3021 into the grab 3006 (SoC Act08, grab cooldown timer 0 as in DS1);
  - side steps after combos 30 % instead of always (SoC keeps pressing).
The decompiler writes decimals with a comma (locale); they are turned back into points here. Writes the Kiln of
the First Flame map script (m18_00_00_00) of the Gwyn test package.

--p2 (phase-2 package files_c5370_p2, player decision 2026-11-15: phase 1 = DS1 Gwyn, phase 2 = Soul of Cinder):
one script with both AIs. The DS1 script becomes FirewoodKing537000P1*, the SoC script FirewoodKing537000P2*, and a
small dispatcher keeps the goal name the game calls (FirewoodKing537000Battle_*):
  - phase 2 = SpEffect 53701 (animIdOffset 10000 -> the SoC clips 130xx), given at the sword plunge of 3029
    (tools/gwyn_phase2.py);
  - end of phase 1 at HP <= 1 % (the DLL keeps the boss alive with NoDead, as for Artorias): the transition 3028
    (kneel), then 3029 (sword into the ground, HP refill, phase 2), each an AttackTunableSpin as Artorias' 3016;
    from then until SpEffect 53700 shows it is playing, no phase-1 reaction may replace it, every new Activate asks
    for it and Update asks again every 2 s (timer 1) (see DISPATCH);
  - the goal has an Update now (the DS1 one was registered without), so it ends when its sub-goals are done.

  python tools/make_gwyn_ai.py          # SoC moves over the whole fight (files_c5370_soc)
  python tools/make_gwyn_ai.py --p2     # DS1 phase 1 + SoC phase 2 (files_c5370_p2)
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AI = ROOT / "work" / "boss_ai"
SRC = AI / "537000_battle.soc_ai.lua"
SRC_DS1 = AI / "dsr_m18_00" / "537000_battle.lua"
TMP = AI / "537000_battle.soc_ai.build.lua"
TMP_P2 = AI / "537000_battle.p2.build.lua"
PKG = ROOT / "dist" / "mods" / "bossy_nightreign"
OUT = PKG / "files_c5370_soc" / "script" / "m18_00_00_00.luabnd.dcx"
OUT_P2 = PKG / "files_c5370_p2" / "script" / "m18_00_00_00.luabnd.dcx"

SP_TRANSITION, SP_PHASE2 = 53700, 53701   # tools/gwyn_phase2.py (53700: given at the start of 3028 and of 3029)
ANIM_KNEEL, ANIM_PLUNGE = 3028, 3029
TIMER_RETRY, RETRY_S = 1, 2             # ai:SetTimer slot (both scripts use only timer 0, the grab cooldown)

# Test 2026-11-15 night (log): at HP 1 the first version never asked for 3028 (20 s of phase-1 attacks, then the
# DLL fail-safe let Gwyn die). It differed from the tested Artorias transition in two things: a one-shot
# ai:Number(5) flag in every check and a ComboAttackTunableSpin -> ComboFinal pair. Now as Artorias / the game's own
# 3022-3028 attacks: AttackTunableSpin per animation, and no one-shot flag - "transition running" = SpEffect 53700,
# and a lost request is asked again (timer).
# Tests 2026-11-15 night, second version (retry 5 s, timer also gating Activate and Interupt): the transition
# started 0 s, 5.5 s and 11 s after HP 1, i.e. at the first check or one / two retries later. Between them Gwyn did
# phase-1 attacks that only the DS1 Interupt picks (3008 right as the player drank an Estus, 3012 close up), so the
# queued 3028 was replaced by a phase-1 reaction while the timer blocked a new request. An unset timer reads as
# finished (the 0 s case asked at once). Now: while the transition is due and not playing, Interupt never hands over
# to the phase-1 reactions, Activate always asks, and Update asks again every RETRY_S s.
DISPATCH = f"""
-- (mod) ===== phase dispatcher (tools/make_gwyn_ai.py --p2) =====
-- phase 2 = SpEffect {SP_PHASE2} (animIdOffset 10000: the Soul of Cinder clips 130xx), given at the sword plunge of
-- the transition {ANIM_PLUNGE} (tools/gwyn_phase2.py)
function FirewoodKing537000_Phase2(ai)
    return ai:HasSpecialEffectId(TARGET_SELF, {SP_PHASE2})
end

-- transition playing: SpEffect {SP_TRANSITION} (no damage taken) from the start of {ANIM_KNEEL} until after the plunge
function FirewoodKing537000_InTransition(ai)
    return ai:HasSpecialEffectId(TARGET_SELF, {SP_TRANSITION})
end

-- end of phase 1 (HP 0, the DLL keeps the boss alive) and the transition not playing yet. Nested ifs:
-- `return a and b and c` with comparisons compiles, but the verify decompiler (luadec, Lua 5.0) crashes on it.
function FirewoodKing537000_TransitionDue(ai)
    local due = false
    if ai:GetHpRate(TARGET_SELF) <= 0.01 then
        if FirewoodKing537000_Phase2(ai) == false then
            if FirewoodKing537000_InTransition(ai) == false then
                due = true
            end
        end
    end
    return due
end

-- kneel {ANIM_KNEEL}, then sword into the ground {ANIM_PLUNGE} (no damage taken, HP refilled, phase 2 from the plunge).
-- The kneel starts when the animation playing now ends (an AI request cannot cut it).
function FirewoodKing537000_Transition(ai, goal)
    ai:SetTimer({TIMER_RETRY}, {RETRY_S})
    goal:ClearSubGoal()
    goal:AddSubGoal(GOAL_COMMON_AttackTunableSpin, 10, {ANIM_KNEEL}, TARGET_ENE_0, DIST_None, 0, 90)
    goal:AddSubGoal(GOAL_COMMON_AttackTunableSpin, 12, {ANIM_PLUNGE}, TARGET_ENE_0, DIST_None, 0, 90)
end

function FirewoodKing537000Battle_Activate(ai, goal)
    if FirewoodKing537000_TransitionDue(ai) then
        FirewoodKing537000_Transition(ai, goal)
        return
    end
    if FirewoodKing537000_Phase2(ai) then
        FirewoodKing537000P2Battle_Activate(ai, goal)
    else
        FirewoodKing537000P1Battle_Activate(ai, goal)
    end
    return
end

-- while due: ask again every {RETRY_S} s, or at once when the queued request is gone
function FirewoodKing537000Battle_Update(ai, goal)
    if FirewoodKing537000_TransitionDue(ai) then
        if ai:IsFinishTimer({TIMER_RETRY}) == true then
            FirewoodKing537000_Transition(ai, goal)
        elseif goal:GetSubGoalNum() <= 0 then
            FirewoodKing537000_Transition(ai, goal)
        end
        return GOAL_RESULT_Continue
    end
    if goal:GetSubGoalNum() <= 0 then
        return GOAL_RESULT_Success
    end
    return GOAL_RESULT_Continue
end

function FirewoodKing537000Battle_Terminate(ai, goal)
    return
end

-- while due or playing, no phase-1 reaction (they clear the sub-goals and would drop the queued transition)
function FirewoodKing537000Battle_Interupt(ai, goal)
    if FirewoodKing537000_TransitionDue(ai) then
        if ai:IsFinishTimer({TIMER_RETRY}) == true then
            FirewoodKing537000_Transition(ai, goal)
            return true
        end
        return false
    end
    if FirewoodKing537000_InTransition(ai) and FirewoodKing537000_Phase2(ai) == false then
        return false
    end
    if FirewoodKing537000_Phase2(ai) then
        return FirewoodKing537000P2Battle_Interupt(ai, goal)
    end
    return FirewoodKing537000P1Battle_Interupt(ai, goal)
end
"""


def decimals(text: str) -> str:
    return re.sub(r"(\d),(\d)", r"\1.\2", text)


def as_phase(text: str, tag: str) -> str:
    """One decompiled battle script as phase `tag`: no goal registration, no final chunk return, functions renamed
    (FirewoodKing537000Battle_* -> FirewoodKing537000<tag>Battle_*, FirewoodKing537000_* -> ...<tag>_*)."""
    lines = [ln for ln in text.splitlines() if not ln.startswith("REGISTER_GOAL")]
    while lines and lines[-1].strip() in ("", "return"):
        lines.pop()
    body = "\n".join(lines)
    renamed, n = re.subn(r"(?<!GOAL_)FirewoodKing537000(?=Battle_|_)", f"FirewoodKing537000{tag}", body)
    if n < 10 or "GOAL_FirewoodKing537000" in renamed:
        raise RuntimeError(f"phase {tag}: unexpected script layout ({n} names renamed)")
    # do ... end: both scripts declare the same file-level locals (Att3000_Dist_min ...); each phase keeps its own
    # (the functions are globals and stay visible outside the block)
    return f"-- (mod) ===== phase {tag[1:]} =====\ndo\n" + renamed + "\nend\n"


def build(src_text: str, tmp: Path, out: Path) -> int:
    tmp.write_text(src_text, encoding="shift_jis")
    out.parent.mkdir(parents=True, exist_ok=True)
    rc = subprocess.call([sys.executable, str(ROOT / "tools" / "ai_lua.py"), "build", "m18_00_00_00",
                          "537000_battle.lua", str(tmp), str(out)])
    if rc == 0:
        rc = subprocess.call([sys.executable, str(ROOT / "tools" / "ai_lua.py"), "verify", str(out), "537000_battle.lua"])
    return rc


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--p2", action="store_true", help="DS1 phase 1 + SoC phase 2 (files_c5370_p2)")
    ap.add_argument("--out", type=Path, help="write the luabnd here instead of the package (e.g. while the game runs)")
    args = ap.parse_args(argv)
    if not args.p2:
        return build(decimals(SRC.read_text(encoding="shift_jis")), TMP, args.out or OUT)
    p1 = as_phase(decimals(SRC_DS1.read_text(encoding="shift_jis")), "P1")
    p2 = as_phase(decimals(SRC.read_text(encoding="shift_jis")), "P2")
    text = ('REGISTER_GOAL(GOAL_FirewoodKing537000_Battle, "FirewoodKing537000Battle")\n'
            "-- (mod) Gwyn phase 1 = DS1 script, phase 2 = Soul of Cinder script (tools/make_gwyn_ai.py --p2)\n"
            + p1 + p2 + DISPATCH + "\nreturn\n")
    return build(text, TMP_P2, args.out or OUT_P2)


if __name__ == "__main__":
    sys.exit(main())
