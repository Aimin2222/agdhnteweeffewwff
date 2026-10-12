# -*- coding: utf-8 -*-
"""Conservative shot-specific framing: never share fixes across camera modes.

v5.10.21 Windows visual review: BLUE third_cinema #7 and RED third_cinema #2
were accepted compositions; no new yaw/pitch adjustment is applied to them.
Angle signs must still be verified in real Windows LoL replay footage.
"""
from __future__ import annotations
import math


def target_center_rotation(camera_offset: tuple) -> dict:
    """RED Replay camera Euler convention: X=azimuth, Y=downward elevation.

    camera_offset is camera_position - target_position in LoL world axes.
    The stable BLUE geometric convention uses X=pitch/Y=yaw, but confirmed
    RED #2 and #4 clips instead use X=yaw/Y=pitch. DO NOT share Euler axis
    layout across teams or modes. Camera must point from offset towards 0.
    """
    dx, dy, dz = (float(v) for v in camera_offset)
    if not all(math.isfinite(v) for v in (dx, dy, dz)):
        raise ValueError("Non-finite camera offset")
    horizontal = math.hypot(dx, dz)
    if horizontal < 1.0:
        raise ValueError("Camera offset has no stable horizontal heading")
    # atan2 wraps the 180-degree boundary stably, with no additional roll.
    return {
        "x": math.degrees(math.atan2(-dx, -dz)),
        "y": max(14.0, min(72.0, math.degrees(math.atan2(dy, horizontal)))),
        "z": 0.0,
    }


def yaw_alignment_error(camera_offset: tuple, rotation: dict) -> float:
    """Return absolute angular mismatch (degrees) in RED camera axes."""
    aimed = target_center_rotation(camera_offset)["x"]
    yaw = float(rotation["x"])
    return abs((yaw - aimed + 180.0) % 360.0 - 180.0)



SHOT_TUNING = {
    # Side, camera mode -> relative distance, Euler-axis screen adjustment.
    ("RED", "third"):       {"distance": 1.13, "angles": {}},
    ("RED", "third_cinema"):{"distance": .96, "angles": {}},
    ("RED", "fps"):         {"distance": 1.0, "angles": {}, "fps_back": 1.60},
    ("RED", "lolnam_cinema"):{"distance": 1.0, "angles": {"x": -3.0, "y": -3.0}},
    ("RED", "geo_aim"):     {"distance": 1.12, "angles": {"x": -4.0}},
    ("BLUE", "third"):      {"distance": 1.10, "angles": {"x": -2.0}},  # #6: shift subject lower in frame, no orbit/distance changes
    ("BLUE", "third_cinema"):{"distance": 1.08, "angles": {}},   # modest backward only
    ("BLUE", "fps"):        {"distance": 1.0, "angles": {}, "fps_back": 1.38},
    ("BLUE", "lolnam_cinema"):{"distance": 1.08, "angles": {"x": 2.5}},
    ("BLUE", "geo_aim"):    {"distance": 1.08, "angles": {"x": 2.5}},
}


def shot_tuning(team: str, style: str) -> dict:
    side = "RED" if str(team).upper() in ("CHAOS", "RED") else "BLUE"
    config = SHOT_TUNING.get((side, str(style)), {})
    distance = float(config.get("distance", 1.0))
    if not .87 <= distance <= 1.30:
        raise ValueError("Invalid camera distance multiplier")
    angles = dict(config.get("angles", {}))
    if any(k not in ("x", "y", "z") or abs(float(v)) > 8.0 for k, v in angles.items()):
        raise ValueError("Unsafe camera framing compensation")
    fps_back = float(config.get("fps_back", 1.0))
    if not 1.0 <= fps_back <= 1.65:
        raise ValueError("Unsafe FPS camera distance")
    return {"side": side, "mode": str(style), "distance": distance,
            "angles": angles, "fps_back": fps_back}
