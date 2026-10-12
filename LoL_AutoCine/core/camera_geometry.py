# -*- coding: utf-8 -*-
"""Numeric target/camera geometry checks; no guesswork about screen contents."""
from __future__ import annotations
import math


def target_direction(camera_position, target_position):
    """3D unit vector pointing from camera to a known target position."""
    try:
        delta = tuple(float(t) - float(c) for c, t in zip(camera_position, target_position))
        if len(delta) != 3 or not all(math.isfinite(v) for v in delta):
            return None
        size = math.sqrt(sum(v*v for v in delta))
        return tuple(v / size for v in delta) if size > 0.0001 else None
    except (TypeError, ValueError, OverflowError):
        return None


def inspect_rig(diagnostic, *, expected_distance=950.0):
    """Classify calibration quality without asserting that a person is visible.

    Replay API top and fps positions can be sampled at different logical
    times; a baseline separated by thousands of world units is suspicious.
    This is evidence, not an automatic BLUE/RED axis flip.
    """
    flags = []
    style = str(diagnostic.get("style", ""))
    third_mode = style in ("third", "third_cinema", "lolnam_cinema", "geo_aim")
    if third_mode and not diagnostic.get("third_person_enabled", False):
        flags.append("third_person_fell_back_to_top_or_fps")
    offset = diagnostic.get("baseline_offset")
    magnitude = None
    horizontal = None
    try:
        v = [float(x) for x in offset]
        if len(v)==3 and all(math.isfinite(x) for x in v):
            horizontal = math.hypot(v[0], v[2])
            magnitude = math.sqrt(sum(x*x for x in v))
    except (ValueError, TypeError, OverflowError):
        pass
    if third_mode and horizontal is not None and horizontal > max(3800.0, 4.0*expected_distance):
        flags.append("baseline_camera_far_from_target_possible_stale_read")
    if third_mode and diagnostic.get("pitch_axis") == "y":
        flags.append("pitch_axis_y_differs_from_common_x_axis_check_required")
    if third_mode and diagnostic.get("initial_camera_rotation") is None:
        flags.append("no_explicit_target_rotation")
    return {
        "flags": flags,
        "baseline_distance": round(magnitude, 1) if magnitude is not None else None,
        "baseline_horizontal_distance": round(horizontal, 1) if horizontal is not None else None,
        "needs_visual_review": bool(flags) or third_mode,
    }
