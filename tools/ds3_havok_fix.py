"""Runtime fix for reading Dark Souls III (hk_2014.1.0-r1, 64-bit packfile) animations with soulstruct-havok.

soulstruct's hk2014 animation classes do not match the 64-bit DS3 files (hkReferencedObject = 16 bytes there):
- hkaDefaultAnimatedReferenceFrame (root motion): members at 20 / 36 / 52 / 56; every DS3 clip with root motion
  failed with "Found non-null data at child pointer offset 0x38: 1065353216" (the w = 1.0 of the forward vector
  read as an array pointer). In the files: up 32, forward 48, duration 64, samples 72 (size 96), as in hk2018.
- hkaAnimation: type / duration / numberOfTransformTracks / numberOfFloatTracks at 12 / 16 / 20 / 24, so the
  duration was read as the track count and the spline decompressor failed ("14 is not a valid
  RotationQuantizationType"). In the files: 16 / 20 / 24 / 28, extractedMotion 32, annotationTracks 40 (size 56).
Patched in memory only (toolsy/soulstruct-havok is left untouched), subclasses re-derived. Call apply() after
havokbridge.load_havok() and before reading DS3 files.
"""
from __future__ import annotations

import importlib
import pkgutil


def apply() -> None:
    import soulstruct.havok.types.hk2014._hka as hka_pkg
    from soulstruct.havok.types.hk2014._hka.hkaAnimation import hkaAnimation as A
    from soulstruct.havok.types.hk2014._hka.hkaAnimatedReferenceFrame import hkaAnimatedReferenceFrame as P
    from soulstruct.havok.types.hk2014._hka.hkaDefaultAnimatedReferenceFrame import hkaDefaultAnimatedReferenceFrame as T
    from soulstruct.havok.types.hk2014.core import Member, hkReal, hkVector4
    if getattr(A, "_ds3_fixed", False):
        return
    old = {m.name: m for m in T.local_members}
    T.local_members = (
        Member(32, "up", hkVector4),
        Member(48, "forward", hkVector4),
        Member(64, "duration", hkReal),
        Member(72, "referenceFrameSamples", old["referenceFrameSamples"].type),
    )
    T.members = P.members + T.local_members
    T.byte_size = 96

    oa = {m.name: m for m in A.local_members}
    A.local_members = (
        Member(16, "type", oa["type"].type),
        Member(20, "duration", oa["duration"].type),
        Member(24, "numberOfTransformTracks", oa["numberOfTransformTracks"].type),
        Member(28, "numberOfFloatTracks", oa["numberOfFloatTracks"].type),
        Member(32, "extractedMotion", oa["extractedMotion"].type),
        Member(40, "annotationTracks", oa["annotationTracks"].type),
    )
    base = A.members[: len(A.members) - len(oa)]
    A.members = base + A.local_members
    # subclasses built their member list from the old hkaAnimation.members at class creation
    for info in pkgutil.iter_modules(hka_pkg.__path__):
        mod = importlib.import_module(f"{hka_pkg.__name__}.{info.name}")
        cls = getattr(mod, info.name, None)
        if isinstance(cls, type) and cls is not A and issubclass(cls, A) and hasattr(cls, "local_members"):
            parent = cls.__mro__[1]
            cls.members = parent.members + cls.local_members
    A._ds3_fixed = True
