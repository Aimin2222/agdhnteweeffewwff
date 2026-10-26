# -*- coding: utf-8 -*-
"""Deterministic smart montage plan. No Tk, Replay API, filesystem or FFmpeg."""
from __future__ import annotations


def _count(kill):
    try:
        return max(1, min(5, int(getattr(kill, "multikill", 1))))
    except (ValueError, TypeError, OverflowError):
        return 1


def _time(kill):
    try:
        t = float(getattr(kill, "time", 0.0))
        return t if 0 <= t < 1e9 else 0.0
    except (TypeError, ValueError, OverflowError):
        return 0.0


def score(kill):
    """Multi-kills are climaxes; an assist remains eligible as build-up."""
    value = 4 * _count(kill)
    if getattr(kill, "role", "kill") == "kill":
        value += 3
    return value


def choose_scenes(scenes, *, limit=12):
    """Return selected (kill, scene template) pairs in rising dramatic order.

    Preserve all clips if the scan has <= limit scenes. For very long matches,
    prefer stronger events and avoid repetitive almost-identical neighboring
    kills. Explicit manual scene order is handled by caller (never touched).
    """
    scenes = list(scenes)
    limit = max(2, min(60, int(limit)))
    if len(scenes) <= limit:
        selected = scenes
    else:
        indexed = list(enumerate(scenes))
        by_quality = sorted(indexed,
                            key=lambda pair: (-score(pair[1][0]), _time(pair[1][0]), pair[0]))
        picked = []
        for item in by_quality:
            t = _time(item[1][0])
            if all(abs(t - _time(k[1][0])) > 1.8 for k in picked):
                picked.append(item)
            if len(picked) == limit:
                break
        if len(picked) < limit:
            used = {n for n, _ in picked}
            picked.extend(item for item in by_quality
                          if item[0] not in used and len(picked) < limit)
        selected = [item[1] for item in picked[:limit]]
    # Preserve chronological ordering for equal-strength highlights, ending
    # with the strongest event rather than chopping randomly in mid-fight.
    return sorted(selected,
                  key=lambda item: (score(item[0]), _time(item[0])))
