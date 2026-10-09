# -*- coding: utf-8 -*-
"""Original optional right-side kill-feed overlays for 16:9 LoL highlights.

Do not touch the game's HUD. A transparent PNG is composed into the exported
clip at the exact scene event times, so this works with HUD-hidden recordings.
All editor-supplied options are normalized here, before they reach FFmpeg.
"""
from __future__ import annotations

import math
from pathlib import Path

STYLES = {
    "off": "なし（従来どおり）",
    "simple": "シンプル",
    "cinema": "シネマ・ゴールド",
    "neon": "ネオン・ブルー",
    "impact": "インパクト・レッド",
}
REVERSE_STYLES = {label: code for code, label in STYLES.items()}
POSITIONS = {
    "right-top": "右上（おすすめ）",
    "right-bottom": "右下",
    "left-top": "左上",
    "left-bottom": "左下",
}
REVERSE_POSITIONS = {label: code for code, label in POSITIONS.items()}
COLORS = {
    "simple": (196, 208, 223),
    "cinema": (247, 197, 102),
    "neon": (160, 139, 255),
    "impact": (255, 122, 125),
}


def normalize(style: str) -> str:
    return str(style) if style in STYLES else "off"


def normalize_options(position="right-top", scale=1.0, seconds=1.55, opacity=1.0):
    """Pure validation: keep FFmpeg expressions bounded and injection-safe."""
    def finite(value, fallback, lower, upper):
        try:
            val = float(value)
        except (TypeError, ValueError, OverflowError):
            val = fallback
        return max(lower, min(upper, val)) if math.isfinite(val) else fallback
    pos = position if position in POSITIONS else "right-top"
    return pos, finite(scale, 1.0, .5, 1.8), finite(seconds, 1.55, .45, 4.0), finite(opacity, 1.0, .25, 1.0)


def make_badge(path: Path, style: str, count: int = 1) -> Path:
    """Draw a self-contained transparent badge using original geometric art."""
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
        base = Image.alpha_composite(base, glow.filter(ImageFilter.GaussianBlur(12)))
    d = ImageDraw.Draw(base)
    d.rounded_rectangle((17, 17, 367, 100), radius=16,
                        fill=(13, 19, 30, 190 if style == "simple" else 215),
                        outline=(*color, 225), width=3)
    d.rounded_rectangle((26, 26, 93, 91), radius=14, fill=(*color, 45),
                        outline=(*color, 255), width=2)
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
    d.text((109, 33), f"KILL  x{n}", font=font, fill=(255, 255, 255, 255))
    d.text((111, 74), {"simple": "HIGHLIGHT", "cinema": "CINEMATIC",
                       "neon": "NEON FINISH", "impact": "IMPACT"}[style],
           font=subfont, fill=(*color, 245))
    if style == "impact":
        d.rectangle((344, 26, 351, 90), fill=(*color, 230))
    elif style == "neon":
        d.line((109, 96, 322, 96), fill=(*color, 220), width=3)
    base.save(path, format="PNG")
    return path


def with_badge(graph: str, badge_input: int, events, *, duration: float,
               position: str = "right-top", scale: float = 1.0,
               seconds: float = 1.55, opacity: float = 1.0,
               style: str = "simple") -> str:
    """Append a bounded, kill-synchronized overlay after the existing [vout].

    The output is still named [vout]. No audio graph or gameplay frames change.
    """
    if not graph.endswith("[vout]"):
        raise ValueError("Existing video graph has no [vout]")
    position, scale, seconds, opacity = normalize_options(position, scale, seconds, opacity)
    valid_duration = max(0.0, float(duration))
    times = []
    for event in list(events or [])[:24]:
        try:
            t = float(event[0])
        except (ValueError, TypeError, IndexError):
            continue
        if math.isfinite(t) and 0 <= t <= valid_duration:
            times.append(t)
    if not times:
        return graph
    spans = []
    for center in times:
        lo = max(0.0, center - 0.10)
        hi = min(valid_duration, center + seconds)
        if hi > lo:
            spans.append(f"between(t,{lo:.3f},{hi:.3f})")
    if not spans:
        return graph
    y = "62" if position.endswith("top") else "H-h-62"
    x = "W-w-32" if position.startswith("right") else "32"
    if normalize(style) == "impact":
        # Small, damped kick rather than a disorienting screen shake.
        kick = "+".join(f"7*sin(35*(t-{center:.3f}))*exp(-11*abs(t-{center:.3f}))" for center in times[:6])
        x += "+" + kick
    return (graph[:-6] + "[pre_kill_badge];"
            + f"[{int(badge_input)}:v]format=rgba,"
            + f"scale=w='trunc(iw*{scale:.3f}/2)*2':h='trunc(ih*{scale:.3f}/2)*2',"
            + f"colorchannelmixer=aa={opacity:.3f}[kill_badge];"
            + "[pre_kill_badge][kill_badge]"
            + f"overlay=x='{x}':y='{y}':format=auto:shortest=1:"
            + f"enable='{'+'.join(spans)}',format=yuv420p[vout]")
