# -*- coding: utf-8 -*-
"""Shared template color previews for quick cards and the full gallery.

Both formats use the same per-template source data; the thumbnails use
AutoCine's existing grade_rgb calculation, not hand-painted mock thumbnails.
"""
from __future__ import annotations

from typing import Any

GRADE_APPEARANCE = {
    "default": ("補正なし", "#748472", "#A4A993", "#D4C6A3", "元のLoLの色をそのまま使う"),
    "standard": ("自然な色", "#718B74", "#87A7A6", "#DECC93", "自然な明るさと彩度"),
    "film": ("柔らかいフィルム", "#766C67", "#B19B87", "#D9C5A1", "少し落ち着いた映画色"),
    "lolnam": ("映画風ティール＆金", "#355F70", "#9B9F8D", "#EAC189", "青緑の影と暖かいハイライト"),
    "tealorange": ("青緑 × オレンジ", "#2D6170", "#A47863", "#F6A659", "シネマティックな強い色の対比"),
    "golden": ("温かいゴールド", "#735632", "#C69A56", "#FFDC87", "キル瞬間の暖色を印象的に"),
    "iceblue": ("アイスブルー", "#263F6A", "#648CAF", "#BBDCF7", "涼しい青の映像"),
    "neon": ("ネオン", "#48256B", "#9E4BAA", "#65DDE1", "鮮やかな夜光・色の強調"),
    "purple": ("紫", "#35325C", "#8F5A9F", "#C5ABDA", "紫寄りの幻想的な色"),
    "noir": ("モノクロ", "#28292F", "#888A90", "#CFD0D0", "白黒に近い強い映画色"),
    "dark": ("暗め", "#232A34", "#596274", "#A59A8A", "暗い場所の臨場感"),
    "sunset": ("夕焼け", "#6E3432", "#C27854", "#FAC68B", "赤とオレンジの暖かい色"),
    "midnight": ("深夜青", "#1D284B", "#496588", "#A5BDCD", "寒色のミステリアスな色"),
    "drama": ("ドラマ", "#3E4057", "#9B847F", "#E0C4AC", "彩度控えめで人物が引き立つ"),
    "fade": ("フェード", "#687F86", "#A8AFA5", "#E0D6BE", "コントラストが柔らかい淡い色"),
    "highcontrast": ("高コントラスト", "#182D41", "#879999", "#F3CF7A", "陰影の差が強いパンチある色"),
}


def appearance(grade: str):
    return GRADE_APPEARANCE.get(str(grade), GRADE_APPEARANCE["standard"])


def template_info(template: Any) -> dict:
    tone, a, b, c, description = appearance(getattr(template, "grade", "standard"))
    style = getattr(template, "style", "follow")
    camera = {
        "third": "三人称・自然", "third_cinema": "三人称・シネマ",
        "lolnam_cinema": "Lolnam風Orbit", "cinema_top": "俯瞰シネマ",
        "cinema": "シネマ", "orbit": "Orbit", "follow": "追従"
    }.get(style, style)
    fx = getattr(template, "video_effects", {}) or {}
    enabled = [k for k, value in fx.items() if float(value or 0) > 0.01]
    return dict(tone=tone, colors=(a, b, c), description=description,
                camera=camera, effects=", ".join(enabled[:3]) or "追加FXなし",
                use="集団戦・複数キル向け" if "チーム" in template.name or "マルチ" in template.name
                    else "ワンクリック・キル編集向け")


def render_template_preview(template, width=280, height=158):
    """Use real grade pipeline for the color comparison (not a canned image)."""
    from PIL import Image
    from core.preview import sample_scene, grade_rgb
    rgb = sample_scene(width, height)
    return Image.fromarray(grade_rgb(rgb, template))


def draw_color_bars(canvas, colors, y0=1, bar_width=38, bar_height=20):
    canvas.delete("all")
    for i, color in enumerate(colors):
        x = i * (bar_width + 3) + 2
        canvas.create_rectangle(x, y0, x + bar_width, y0 + bar_height,
                                fill=color, outline="#D5DDE7")
