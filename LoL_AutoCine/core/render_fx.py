# -*- coding: utf-8 -*-
"""Replay API上のゲーム内Fog / DOFを適用・復元する(v1.2機能)。"""
from __future__ import annotations
from typing import Optional
from .replay_api import ReplayAPI, ReplayApiError

FOG_PRESETS = {
    "teal":    {"depth": (0.00, 0.62, 0.66), "height": (0.00, 0.63, 0.63)},
    "sand":    {"depth": (0.83, 0.78, 0.65), "height": (0.35, 0.30, 0.22)},
    "white":   {"depth": (1.00, 1.00, 1.00), "height": (0.90, 0.95, 1.00)},
    "emerald": {"depth": (0.20, 0.66, 0.50), "height": (0.10, 0.55, 0.40)},
    "cream":   {"depth": (1.00, 1.00, 0.80), "height": (0.95, 0.92, 0.75)},
}

def _rgba(c):
    return {"r": c[0], "g": c[1], "b": c[2], "a": 1.0}

def fog_values(name: str, strength: float) -> dict:
    p = FOG_PRESETS.get(name)
    if not p or strength <= 0:
        return {}
    k = max(0.0, min(1.0, float(strength)))
    return {
        "depthFogEnabled": True, "depthFogColor": _rgba(p["depth"]),
        "depthFogStart": 2500.0, "depthFogEnd": 5250.0, "depthFogIntensity": k,
        "heightFogEnabled": True, "heightFogColor": _rgba(p["height"]),
        "heightFogStart": 100.0, "heightFogEnd": 1400.0, "heightFogIntensity": k,
    }

def dof_values(cam_dist: float, blur: float) -> dict:
    d = max(300.0, float(cam_dist))
    return {"depthOfFieldEnabled": True, "depthOfFieldCircle": float(max(0.0, blur)),
            "depthOfFieldMid": d, "depthOfFieldWidth": d * 0.6,
            "depthOfFieldNear": d * 0.4, "depthOfFieldFar": d * 2.5}

def apply_fx(api: ReplayAPI, t, cam_dist: Optional[float] = None) -> dict:
    vals = {}
    if getattr(t, "fog_enabled", False):
        vals.update(fog_values(getattr(t, "fog_preset", "teal"), getattr(t, "fog_strength", 0.0)))
    if getattr(t, "dof_enabled", False) and cam_dist and getattr(t, "dof_blur", 0.0) > 0:
        vals.update(dof_values(cam_dist, getattr(t, "dof_blur", 0.0)))
    if not vals:
        return {}
    try:
        before = api.render()
    except ReplayApiError:
        before = {}
    saved = {k: before[k] for k in vals if k in before}
    for k in vals:
        if k.endswith("Enabled") and k not in saved:
            saved[k] = False
    api.set_render(**vals)
    return saved

def restore_fx(api: ReplayAPI, saved: Optional[dict]) -> None:
    if not saved:
        return
    try:
        api.set_render(**saved)
    except ReplayApiError:
        pass
