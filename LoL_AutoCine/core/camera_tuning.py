# -*- coding: utf-8 -*-
"""Independent framing policies and the measured Replay Euler contract.

Keep historic SHOT_TUNING values for compatibility. Current live policies
follow the 2026-10-13 QA evaluation: RED FPS/geo_aim are protected; BLUE and
RED third_cinema/lolnam use target-facing axes. Windows recheck is required.
"""
from __future__ import annotations
import math


def target_center_rotation(camera_offset: tuple) -> dict:
    """Replay camera Euler convention: X=azimuth, Y=downward elevation.

    camera_offset is camera_position - target_position in LoL world axes.
    Windows QA shows the earlier BLUE X=pitch/Y=yaw assumption points at sky.
    The API axis contract is shared; per-mode framing settings remain separate.
    Camera must point from its actual offset towards the attached target.
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
    """Return absolute angular mismatch (degrees) in Replay camera axes."""
    aimed = target_center_rotation(camera_offset)["x"]
    yaw = float(rotation["x"])
    return abs((yaw - aimed + 180.0) % 360.0 - 180.0)


# Independent immutable entries: changing one mode cannot mutate another.
# True: use the measured Replay axis contract, including zero roll.
# RED FPS/geo_aim keep their accepted position/rotation path exactly.
LIVE_FRAMING_POLICIES = {
    ("BLUE", "third"): (True, 1.0),
    ("BLUE", "third_cinema"): (True, 1.0),
    ("BLUE", "fps"): (True, 1.0),
    ("BLUE", "lolnam_cinema"): (True, 1.0),
    ("BLUE", "geo_aim"): (True, 1.0),
    ("RED", "third"): (False, 1.08),  # modest 8% pullback, auto only
    ("RED", "third_cinema"): (True, 1.0),
    ("RED", "fps"): (False, 1.0),
    ("RED", "lolnam_cinema"): (True, 1.0),
    ("RED", "geo_aim"): (False, 1.0),
}


def live_framing_policy(team: str, style: str) -> dict:
    side = "RED" if str(team).upper() in ("CHAOS", "RED") else "BLUE"
    target_lock, distance = LIVE_FRAMING_POLICIES.get((side, style), (False, 1.0))
    if type(target_lock) is not bool or not math.isfinite(distance) or not 1.0 <= distance <= 1.15:
        raise ValueError("Invalid per-mode camera framing policy")
    return {"target_lock": target_lock, "distance_extra": distance}



SHOT_TUNING = {
    # Side, camera mode -> relative distance, Euler-axis screen adjustment.
    ("RED", "third"):       {"distance": 1.13, "angles": {}},
    ("RED", "third_cinema"):{"distance": .96, "angles": {}},
    ("RED", "fps"):         {"distance": 1.0, "angles": {}, "fps_back": 1.60},
    ("RED", "lolnam_cinema"):{"distance": 1.0, "angles": {"x": -3.0, "y": -3.0}},
    ("RED", "geo_aim"):     {"distance": 1.12, "angles": {"x": -4.0}},
    ("BLUE", "third"):      {"distance": 1.10, "angles": {"x": -2.0}},
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
    if any(k not in ("x", "y", "z") or not math.isfinite(float(v)) or abs(float(v)) > 8.0 for k, v in angles.items()):
        raise ValueError("Unsafe camera framing compensation")
    fps_back = float(config.get("fps_back", 1.0))
    if not 1.0 <= fps_back <= 1.65:
        raise ValueError("Unsafe FPS camera distance")
    return {"side": side, "mode": str(style), "distance": distance,
            "angles": angles, "fps_back": fps_back}
