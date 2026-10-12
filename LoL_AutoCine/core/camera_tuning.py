# -*- coding: utf-8 -*-
"""Conservative shot-specific framing: never share fixes across camera modes.

v5.10.21 Windows visual review: BLUE third_cinema #7 and RED third_cinema #2
were accepted compositions; no new yaw/pitch adjustment is applied to them.
Angle signs must still be verified in real Windows LoL replay footage.
"""
from __future__ import annotations


SHOT_TUNING = {
    # Side, camera mode -> relative distance, Euler-axis screen adjustment.
    ("RED", "third"):       {"distance": .94, "angles": {}},
    ("RED", "third_cinema"):{"distance": .96, "angles": {}},
    ("RED", "fps"):         {"distance": 1.0, "angles": {}},
    ("RED", "lolnam_cinema"):{"distance": 1.0, "angles": {"x": -3.0, "y": -3.0}},
    ("RED", "geo_aim"):     {"distance": 1.0, "angles": {"x": -3.0}},
    ("BLUE", "third"):      {"distance": 1.0, "angles": {"x": 3.0}},
    ("BLUE", "third_cinema"):{"distance": 1.0, "angles": {}},   # protected #7
    ("BLUE", "fps"):        {"distance": 1.0, "angles": {}},
    ("BLUE", "lolnam_cinema"):{"distance": 1.0, "angles": {"x": 2.5}},
    ("BLUE", "geo_aim"):    {"distance": 1.0, "angles": {"x": 2.5}},
}


def shot_tuning(team: str, style: str) -> dict:
    side = "RED" if str(team).upper() in ("CHAOS", "RED") else "BLUE"
    config = SHOT_TUNING.get((side, str(style)), {})
    distance = float(config.get("distance", 1.0))
    if not .87 <= distance <= 1.15:
        raise ValueError("Invalid camera distance multiplier")
    angles = dict(config.get("angles", {}))
    if any(k not in ("x", "y", "z") or abs(float(v)) > 8.0 for k, v in angles.items()):
        raise ValueError("Unsafe camera framing compensation")
    return {"side": side, "mode": str(style), "distance": distance, "angles": angles}
