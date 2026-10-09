# -*- coding: utf-8 -*-
"""Kill-feed decoration as an optional post-render overlay.

The original HUD is not modified. We render original geometric badges with PIL,
then time them to the clip's actual kill events in FFmpeg. No LoL HUD textures
or third-party assets are copied. The four templates work with HUD hidden.
"""
from __future__ import annotations

from pathlib import Path

STYLES = {
    "off": "なし（従来どおり）",
    "simple": "シンプル",
    "cinema": "シネマ・ゴールド",
    "neon": "ネオン・ブルー",
    "impact": "インパクト・レッド",
}
REVERSE_STYLES = {label: code for code, label in STYLES.items()}
COLORS = {
    "simple": (196, 208, 223),
    "cinema": (247, 197, 102),
    "neon": (160, 139, 255),
    "impact": (255, 122, 125),
}


def normalize(style: str) -> str:
    return str(style) if style in STYLES else "off"


def make_badge(path: Path, style: str, count: int = 1) -> Path:
    """Build a transparent kill-feed card; fonts/icons are self-contained.

    Count describes events in the current merged clip, not the player's
    lifetime kill count.
    """
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    style = normalize(style)
    if style == "off":
        raise ValueError("Kill decoration is disabled")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    color = COLORS[style]
    width, height = 385, 116
    base = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    glow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    if style != "simple":
        gd.rounded_rectangle((16, 15, 368, 102), radius=18, outline=(*color, 160), width=8)
        glow = glow.filter(ImageFilter.GaussianBlur(12))
        base = Image.alpha_composite(base, glow)
    d = ImageDraw.Draw(base)
    fill = (13, 19, 30, 190 if style == "simple" else 215)
    d.rounded_rectangle((17, 17, 367, 100), radius=16, fill=fill, outline=(*color, 225), width=3)
    d.rounded_rectangle((26, 26, 93, 91), radius=14, fill=(*color, 45), outline=(*color, 255), width=2)
    # Two crossed blades: an original, resolution-independent KILL symbol.
    d.line((44, 44, 77, 78), fill=(*color, 255), width=6)
    d.line((77, 44, 44, 78), fill=(*color, 255), width=6)
    d.ellipse((41, 41, 49, 49), fill=(255, 255, 255, 235))
    d.ellipse((72, 72, 80, 80), fill=(255, 255, 255, 235))
    try:
        font = ImageFont.truetype("arialbd.ttf", 32)
        subfont = ImageFont.truetype("arial.ttf", 18)
    except OSError:
        font = ImageFont.load_default()
        subfont = ImageFont.load_default()
    n = max(1, min(99, int(count)))
    d.text((109, 33), f"KILL  x{n}", font=font, fill=(255, 255, 255, 255), stroke_width=0)
    d.text((111, 74), {"simple": "HIGHLIGHT", "cinema": "CINEMATIC", "neon": "NEON FINISH", "impact": "IMPACT"}[style],
           font=subfont, fill=(*color, 245))
    if style == "impact":
        d.rectangle((344, 26, 351, 90), fill=(*color, 230))
    elif style == "neon":
        d.line((109, 96, 322, 96), fill=(*color, 220), width=3)
    base.save(path, format="PNG")
    return path


def with_badge(graph: str, badge_input: int, events, *, duration: float) -> str:
    """Add a timed compositing stage to an existing [vout] filter graph."""
    if not graph.endswith("[vout]"):
        raise ValueError("Existing video graph has no [vout]")
    clauses = []
    for start, _end in list(events or [])[:12]:
        center = max(0.0, min(float(duration), float(start)))
        lo = max(0.0, center - 0.14)
        hi = min(float(duration), center + 1.55)
        if hi > lo:
            clauses.append(f"between(t,{lo:.3f},{hi:.3f})")
    if not clauses:
        return graph
    return (graph[:-6] + "[pre_kill_badge];"
            + f"[{int(badge_input)}:v]format=rgba[kill_badge];"
            + "[pre_kill_badge][kill_badge]"
            + f"overlay=x=W-w-32:y=62:format=auto:shortest=1:enable='{'+'.join(clauses)}',"
            + "format=yuv420p[vout]")
