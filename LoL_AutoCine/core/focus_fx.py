# -*- coding: utf-8 -*-
"""Image-space circular depth-of-field blur (sharp center, soft surroundings).

All positions are normalized screen coordinates. TargetLock generally keeps its
subject near the center, but the user can adjust x/y for atypical angles.
"""
from __future__ import annotations


def clamp(value, lo, hi):
    try:
        return max(lo, min(hi, float(value)))
    except (TypeError, ValueError):
        return lo


def focus_settings(template):
    return (clamp(getattr(template, 'dof_center_x', .50), .05, .95),
            clamp(getattr(template, 'dof_center_y', .54), .05, .95),
            clamp(getattr(template, 'dof_radius', .29), .08, .65),
            clamp(getattr(template, 'dof_feather', .12), .025, .35))


def mask_expression(cx, cy, radius, feather):
    """Outside blur mask at low resolution. Circles remain round at 16:9.

    The center stays sharp (mask 0), and pixels beyond the radius
    transition smoothly to the blurred source (mask 255).
    """
    distance = (f'sqrt(pow((X/W-{cx:.5f})*W/H,2)'
                f'+pow(Y/H-{cy:.5f},2))')
    ramp = f'clip(({distance}-{radius:.5f})/{feather:.5f},0,1)'
    return f'255*{ramp}'


def blend_graph(source_effect: str, mask_expr: str, *, tag='focus'):
    """Unfiltered original + optional effect image merged through circular mask.

    Returns a single FFmpeg filter chain fragment. This is designed to be
    joined with the legacy comma-separated graph; no modification of audio.
    """
    return (f'split=3[{tag}src][{tag}effect][{tag}mask];'
            f'[{tag}effect]{source_effect}[{tag}fx];'
            f'[{tag}mask]scale=480:270:flags=bilinear,format=gray,'
            f"geq=lum='{mask_expr}',scale=1920:1080:flags=bilinear[{tag}alpha];"
            f'[{tag}src][{tag}fx][{tag}alpha]maskedmerge')


def circular_dof_filter(template) -> str:
    cx, cy, radius, feather = focus_settings(template)
    sigma = clamp(getattr(template, 'dof_blur', 0), .1, 20) * 1.15
    effect = (f'scale=960:540:flags=bilinear,gblur=sigma={sigma:.2f}:steps=1,'
              'scale=1920:1080:flags=bilinear,format=rgba')
    return blend_graph(effect, mask_expression(cx, cy, radius, feather), tag='cdof')
