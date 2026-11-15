"""Height of a boss's body over time in its DSR and ported clips (read-only): mean and lowest bone height (model
space, relative to the rest pose) every --step seconds, and the moment the body falls fastest / stops falling.
Used to place hits and shock waves on the real landing frame (Gaping Dragon 3007 / 3009, 2026-11-15).

  python tools\\clip_height_timeline.py --dsr c5260 --ported c5260_ai --anims 3007 3009
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from boss_anim_port import BP, parents_of, ref_arrays, to_model_space  # noqa: E402
from boss_clip_compare import load_clip  # noqa: E402
from havokbridge import load_havok  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dsr", required=True)
    ap.add_argument("--ported")
    ap.add_argument("--anims", type=int, nargs="+", required=True)
    ap.add_argument("--step", type=float, default=0.1)
    args = ap.parse_args(argv)
    load_havok()
    from soulstruct.havok.fromsoft import darksouls1r as d

    DD = BP / f"dsr_{args.dsr}" / "anibnd"
    skel = d.SkeletonHKX.from_path(next(p for p in DD.iterdir() if p.name.lower() == "skeleton.hkx")).skeleton
    par = parents_of(skel)
    ref = ref_arrays(skel)
    Pref, _ = to_model_space(par, ref[0][None], ref[1][None])
    rest_mean, rest_min = float(Pref[0, :, 1].mean()), float(Pref[0, :, 1].min())
    srcs = [("DSR", DD)] + ([("port", BP / "nr_ported" / args.ported)] if args.ported else [])
    for aid in args.anims:
        for tag, folder in srcs:
            path = folder / f"a00_{aid:04d}.hkx"
            if not path.exists():
                print(f"== {aid} {tag}: no {path}")
                continue
            P, dur = load_clip(d, path, par, ref)
            F = len(P)
            dt = dur / max(F - 1, 1)
            mean = P[:, :, 1].mean(axis=1) - rest_mean
            low = P[:, :, 1].min(axis=1) - rest_min
            vel = np.gradient(mean, dt)
            fall = int(np.argmin(vel))
            # landing = first frame after the fastest fall where the body stops going down
            land = next((i for i in range(fall, F) if vel[i] > -0.5), F - 1)
            print(f"== {aid} {tag}: {dur:.2f} s | highest mean {mean.max():+.2f} m at {mean.argmax() * dt:.2f} s | "
                  f"fastest fall {vel[fall]:.1f} m/s at {fall * dt:.2f} s | landing ~{land * dt:.2f} s")
            t = 0.0
            row = []
            while t <= dur + 1e-6:
                i = min(int(round(t / dt)), F - 1)
                row.append(f"{t:.1f}:{mean[i]:+.1f}/{low[i]:+.1f}")
                t += args.step
            for k in range(0, len(row), 10):
                print("   " + "  ".join(row[k:k + 10]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
