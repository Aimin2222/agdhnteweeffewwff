# -*- coding: utf-8 -*-
"""Short temporal luminance/saturation accents, based on actual kill timestamps.

CPU-compatible FFmpeg expressions: no CUDA download/upload, no alpha, no
spatial blur, and no FFmpeg functions that depend on optional plugins.
"""
from __future__ import annotations


def pulse_filters(events, intensity):
    strength = max(0.0, min(1.0, float(intensity)))
    if strength < 0.001 or not events:
        return []
    # Limit expression growth for merged multikills. Max-sum is clamped by min().
    center = [float(a) for a, _ in events[:8]]
    wave = '+'.join(f'exp(-22*abs(t-{at:.3f}))' for at in center)
    # Boost brief highlights while preserving color, instead of washing the whole clip white.
    brightness = f'{0.11*strength:.4f}*min(1,{wave})'
    saturation = f'1+{0.10*strength:.4f}*min(1,{wave})'
    return [f"eq=brightness='{brightness}':saturation='{saturation}':eval=frame"]
