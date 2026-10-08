# -*- coding: utf-8 -*-
"""Reference-informed but original highlight director.

Pure decision layer: no API, Tk, FFmpeg, or GPU calls. Only supported event
metadata (role, multikill) is used; we cannot infer enemy position or combat
motion from a kill event alone. Camera keyframes remain target-relative.
"""
from __future__ import annotations
from dataclasses import replace
from .scene_project import Shot, recommend, validate_keyframes

SMART_STYLES = {
    'auto': 'おまかせ（キル数から自動判断）',
    'chase': '追走シネマ（ゆっくり寄る）',
    'impact': 'キル瞬間を強調',
    'teamfight': '集団戦（広い画角）',
}
SMART_STYLES_REVERSE = {label: key for key, label in SMART_STYLES.items()}


def decide_style(kill, style='auto'):
    if style in ('chase', 'impact', 'teamfight'):
        return style
    if getattr(kill, 'role', 'kill') == 'assist':
        return 'chase'
    try:
        multi = int(getattr(kill, 'multikill', 1))
    except (TypeError, ValueError):
        multi = 1
    return 'teamfight' if multi >= 3 else ('impact' if multi == 2 else 'chase')


def recommend_highlight(kill, pre=4.0, post=3.0, style='auto') -> Shot:
    """Create a restrained five-point camera envelope around a kill.

    Keep ±camera deltas small and return to zero at both ends. The core camera
    owns target-lock and orientation; this generator must never alter axes.
    """
    kind = decide_style(kill, style)
    base = recommend(kill, pre, post)
    pre = max(2.5, min(15.0, float(base.pre)))
    post = max(2.2, min(15.0, float(base.post)))
    if kind == 'teamfight':
        # Preserve context and allies: avoid dramatic push-in during multikills.
        values = [(-2.4, -4, -3, 3.0), (-0.85, -2, -2, 2.0),
                  (0.0, 2, 0, 2.5), (0.75, 3, -1, 1.5), (2.0, 0, 0, 0)]
        pulse, arc, dolly, profile = 0.35, 10.0, 2.0, 'cinematic'
    elif kind == 'impact':
        values = [(-2.4, -5, 0, 1.0), (-0.85, -2, 4, -0.5),
                  (0.0, 4, 8, -2.5), (0.75, 6, 4, -1.0), (2.0, 0, 0, 0)]
        pulse, arc, dolly, profile = 0.7, 11.0, 4.0, 'cinematic'
    else:
        values = [(-2.4, -4, 0, 1.0), (-0.85, -1, 3, 0),
                  (0.0, 3, 6, -1.5), (0.75, 5, 3, -0.5), (2.0, 0, 0, 0)]
        pulse, arc, dolly, profile = 0.3, 8.0, 3.0, 'smooth'
    # Start/end at neutral offset to avoid a visible jump at scene boundaries.
    values[0] = (-pre, 0, 0, 0)
    values[-1] = (post, 0, 0, 0)
    frames = validate_keyframes([
        dict(time=t, yaw=yaw, zoom=zoom, fov=fov)
        for t, yaw, zoom, fov in values
    ])
    return replace(base, profile=profile, arc=arc, dolly=dolly,
                   pre=pre, post=post, keyframes=frames,
                   highlight_pulse=pulse)
