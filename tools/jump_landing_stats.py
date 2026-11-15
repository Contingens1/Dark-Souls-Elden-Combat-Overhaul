"""Horizontal speed around landings of plain jumps (anim 900) from an er_engine.log (read only).

Per jump: speed at take-off, in the air (mean), the landing moment (height back to the take-off level after the apex),
then the speed 0.1 / 0.3 / 0.5 / 0.8 s after landing, the lowest speed within 0.8 s and how far the character slid
in the first 0.3 s. Speed = position change of the "fiz" probe lines (x/z) per second.
Used for the player report 2026-11-14: "after a sprint jump the model slides briefly without stepping, after a run
jump the character slows down".

  python tools/jump_landing_stats.py dist/mods/c0000_er_engine_night/bin/er_engine.log [--last 40]
"""
from __future__ import annotations

import argparse
import math
import re
import sys
from pathlib import Path

FIZ = re.compile(r"^\[\s*(\d+) ms\] fiz \+\s*(\d+)ms: .*?\| poz (-?[\d.]+) (-?[\d.]+) (-?[\d.]+) \|")
JUMP = re.compile(r"^\[\s*(\d+) ms\] L7 ctx=\S+ anim=900 ")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("log", type=Path)
    ap.add_argument("--last", type=int, default=40)
    args = ap.parse_args(argv)
    lines = args.log.read_text(encoding="utf-8", errors="replace").splitlines()
    jumps = [i for i, l in enumerate(lines) if JUMP.match(l)][-args.last:]
    print(" jump at ms | take-off | air mean | land s | +0.1  +0.3  +0.5  +0.8 | min<0.8 | slide 0.3s | kind")
    for i in jumps:
        t0 = int(JUMP.match(lines[i]).group(1))
        pts = []
        for l in lines[i:i + 1500]:
            m = FIZ.match(l)
            if m:
                t = int(m.group(1))
                if t - t0 > 2600:
                    break
                pts.append((t, float(m.group(3)), float(m.group(4)), float(m.group(5))))
        if len(pts) < 20:
            continue
        # speed from positions over ~50 ms
        def speed(k):
            j = max(0, k - 3)
            dt = (pts[k][0] - pts[j][0]) / 1000.0
            return math.hypot(pts[k][1] - pts[j][1], pts[k][3] - pts[j][3]) / dt if dt > 0 else 0.0
        y0 = pts[0][2]
        apex = max(range(len(pts)), key=lambda k: pts[k][2])
        if pts[apex][2] - y0 < 0.3:
            continue
        land = next((k for k in range(apex, len(pts)) if pts[k][2] <= y0 + 0.05), None)
        if land is None:
            continue
        tl = pts[land][0]
        def at(dt):
            k = next((k for k in range(land, len(pts)) if pts[k][0] - tl >= dt * 1000), len(pts) - 1)
            return speed(k)
        after = [speed(k) for k in range(land, len(pts)) if pts[k][0] - tl <= 800]
        k3 = next((k for k in range(land, len(pts)) if pts[k][0] - tl >= 300), len(pts) - 1)
        slide = math.hypot(pts[k3][1] - pts[land][1], pts[k3][3] - pts[land][3])
        take = speed(min(3, len(pts) - 1))
        air = sum(speed(k) for k in range(3, land)) / max(1, land - 3)
        kind = "sprint" if take > 5.0 else "run" if take > 2.5 else "walk/stand"
        print(f" {t0:10d} | {take:8.1f} | {air:8.1f} | {(tl - t0) / 1000:6.2f} | {at(0.1):4.1f}  {at(0.3):4.1f}  {at(0.5):4.1f}  "
              f"{at(0.8):4.1f} | {min(after):7.1f} | {slide:9.2f}m | {kind}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
