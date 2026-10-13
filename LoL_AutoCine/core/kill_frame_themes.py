# -*- coding: utf-8 -*-
"""Non-invasive A/B/C/D kill-frame catalog and original concept-board asset pipeline.

IMPORTANT: The PNG concept boards are *source artwork*. They must be provided
under assets/kill_concepts/<source_file>. We do not fabricate source artwork.
The output sprite is cut from actual board pixels and used in the badge.
This module does NOT touch camera, Replay API, audio or encoding.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal
import math

Family = Literal["A", "B", "C", "D"]
Intensity = Literal["weak", "strong"]
Motif = Literal["melee", "ranged", "hybrid"]

@dataclass(frozen=True)
class Theme:
    id: str
    label: str
    source_file: str
    intro_fx: str
    color: str
    # Approximate location of the 3 sample center emblems in the bottom third
    # of the 1536x1024 concept board. Calibrate on the actual source bitmap.
    motif_centers: tuple[tuple[float, float], ...] = (
        (0.165, 0.884), (0.50, 0.884), (0.832, 0.884)
    )

THEMES = {
    theme.id: theme for theme in [
        Theme("project", "PROJECT", "project_キルアイコンデザインコンセプト.png", "scan_glitch", "#28E1EF"),
        Theme("star_guardian", "スターガーディアン", "スターガーディアン_キルアイコン設計案.png", "starlight", "#FFC6F2"),
        Theme("kda", "K/DA", "k_daキルアイコン_デザインコンセプトボード.png", "stage_pulse", "#F777E2"),
        Theme("heartsteel", "ハートスティール", "ハートスティール_キルアイコン設計図.png", "sound_pulse", "#ED425F"),
        Theme("spirit_blossom", "スピリットブロッサム", "スピリットブロッサム_キルアイコン図録.png", "petal_reveal", "#E6ACDF"),
        Theme("dark_star", "ダークスター", "ダークスター_キルアイコン設計案.png", "void_orbit", "#AD71FB"),
        Theme("high_noon", "ハイヌーン", "灼熱の西部キルアイコン設計図.png", "spark_dust", "#FEA64B"),
        Theme("blood_moon", "血月", "血月キルアイコンデザイン案.png", "blood_moon", "#E34352"),
        Theme("warring_kingdoms", "覇王", "覇王のキルアイコン設計図.png", "banner_slash", "#E4A24F"),
        Theme("pool_party", "プールパーティー", "プールパーティー_キルアイコン図鑑.png", "water_splash", "#5AD9F6"),
        Theme("elderwood", "エルダウッド", "エルダウッド_キルアイコンデザイン案.png", "leaf_bloom", "#64D7A5"),
        Theme("cosmic", "コズミック", "コズミックキルアイコン設計図.png", "star_orbit", "#8FACFE"),
        Theme("dark_cosmic", "ダークコズミック", "ダークコズミック_キルアイコン図録.png", "gravity_well", "#AF64F5"),
        Theme("dawnbringer", "ドーンブリンガー", "ドーンブリンガー_キルアイコン設計図.png", "light_wings", "#F4CE81"),
        Theme("nightbringer", "ナイトブリンガー", "ナイトブリンガー_キルアイコン概念図.png", "ember_wings", "#F06C4C"),
        Theme("infernal", "インフェルナル", "インフェルナル炎獄キルアイコン設計図.png", "flame_burst", "#FF873A"),
        Theme("arcade", "アーケード", "ネオンアーケード_キルアイコンデザイン_концепト.png", "pixel_spawn", "#F565D5"),
        Theme("bewitching", "ビウィッチング", "ビウィッチング_キルアイコン設計図.png", "witch_sparks", "#EA92EC"),
        Theme("porcelain", "磁器", "磁器の華やかキルアイコン図鑑.png", "ceramic_shine", "#94CCFE"),
        Theme("psyops", "PsyOps", "サイオプス_キルアイコン設計図.png", "psi_static", "#78D7F1"),
        Theme("steel_valkyries", "Steel Valkyries", "スティールヴァルキリーズ_デザイン図鑑.png", "plasma_wings", "#8FCBFE"),
        Theme("broken_covenant", "Broken Covenant", "崩れた聖約_ゴシックuiデザインボード.png", "rose_glass", "#DF6E81"),
        Theme("faerie_court", "Faerie Court", "フェアリーコート幻想デザイン図鑑.png", "butterfly_reveal", "#EC9AD9"),
        Theme("space_groove", "Space Groove", "スペースグルーヴ_キルアイコンデザインボード.png", "disco_bounce", "#B997FE"),
        Theme("ocean_song", "Ocean Song", "オーシャンソング_夏祭りデザイン図鑑.png", "ocean_ripple", "#70D4F6"),
        Theme("mecha_kingdoms", "Mecha Kingdoms", "機巧帝国メカキングダムズ図録.png", "imperial_mecha", "#EAB565"),
        Theme("dragonmancer", "Dragonmancer", "龍脈煌めくドラゴンマンサー設定画集.png", "dragon_trace", "#F98A55"),
        Theme("shan_hai_scrolls", "Shan Hai Scrolls", "山海絵巻_神獣と金墨の紋章帖.png", "ink_paint", "#DFC497"),
        Theme("mecha", "メカ", "メカキルアイコン_デザインコンセプト.png", "mecha_assembly", "#71B8FA"),
        Theme("battlecast", "バトルキャスト", "バトルキャスト_機械戦場コンセプトボード.png", "red_assembly", "#F26A53"),
    ]
}

FAMILIES = {
    "A": "シンプル", "B": "高級感", "C": "シネマ", "D": "スキン・地域テーマ",
}
MOTIFS = ("melee", "ranged", "hybrid")
INTENSITIES = ("weak", "strong")


def validate_choice(family="A", theme=None, intensity="weak", motif="hybrid"):
    if family not in FAMILIES:
        raise ValueError("Unknown kill-frame family")
    if intensity not in INTENSITIES or motif not in MOTIFS:
        raise ValueError("Unknown kill-frame variant")
    if family == "D" and theme not in THEMES:
        raise ValueError("Unknown or missing source theme")
    return family, theme if family == "D" else None, intensity, motif


def source_path(source_root, theme_id):
    """Return an existing ORIGINAL concept board or fail closed."""
    if theme_id not in THEMES:
        raise ValueError(f"Unknown theme: {theme_id}")
    root = Path(source_root).resolve()
    source = (root / THEMES[theme_id].source_file).resolve()
    if source.parent != root or not source.is_file():
        raise FileNotFoundError(f"Missing original concept board: {source.name}")
    return source


def _matte_motif(crop, *, softness=14):
    """Extract *real* artwork pixels from a selected concept-board motif.

    Most reference sheets have a light background in the bottom motif gallery.
    Background-keying by corner colors is best-effort; manual review is mandatory.
    """
    from PIL import Image, ImageFilter
    im = crop.convert("RGBA")
    w, h = im.size
    pix = im.load()
    corners = [pix[0, 0][:3], pix[w-1, 0][:3], pix[0, h-1][:3], pix[w-1, h-1][:3]]
    background = tuple(sum(px[c] for px in corners) / 4 for c in range(3))
    alpha = Image.new("L", (w, h))
    a = alpha.load()
    for y in range(h):
        for x in range(w):
            rgb = pix[x, y][:3]
            distance = sum((rgb[i] - background[i]) ** 2 for i in range(3)) ** .5
            edge = min(x, y, w-1-x, h-1-y)
            edge_fade = min(1.0, max(0.0, edge / max(1, softness)))
            a[x, y] = int(255 * edge_fade * min(1.0, max(0, (distance - 19) / 48)))
    alpha = alpha.filter(ImageFilter.GaussianBlur(.75))
    im.putalpha(alpha)
    return im


def extract_original_motif(source_root, theme_id, motif, dst, *, center=None,
                           radius_fraction=0.077):
    """Build a transparent effect sprite using ACTUAL pixels of the original board.

    Coordinates are in normalized (x, y) relative to the actual board size.
    Every extraction requires an eye-check before use in a public template.
    """
    from PIL import Image
    if motif not in MOTIFS:
        raise ValueError("Invalid motif")
    original = source_path(source_root, theme_id)
    with Image.open(original) as im:
        im = im.convert("RGBA")
        w, h = im.size
        x, y = center or THEMES[theme_id].motif_centers[MOTIFS.index(motif)]
        if not (0.03 < x < .97 and 0.03 < y < .97):
            raise ValueError("Motif position outside source board")
        r = max(20, round(w * float(radius_fraction)))
        cx, cy = round(x*w), round(y*h)
        box = (max(0, cx-r), max(0, cy-r), min(w, cx+r), min(h, cy+r))
        crop = _matte_motif(im.crop(box))
    dst = Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    crop.save(dst, "PNG")
    return dst


def intro_timing(theme_id, t, duration=.30, intensity="weak"):
    """Pure easing plan consumed by a later compositor; no engine side effects."""
    if theme_id not in THEMES or intensity not in INTENSITIES:
        raise ValueError("Invalid theme/intensity")
    if not math.isfinite(float(t)):
        raise ValueError("Invalid animation time")
    progress = max(0.0, min(1.0, float(t) / max(.001, duration)))
    smooth = progress * progress * (3 - 2 * progress)
    strength = .45 if intensity == "weak" else 1.0
    return {
        "effect": THEMES[theme_id].intro_fx,
        "progress": smooth, "opacity": smooth,
        "scale": .89 + .11*smooth,
        "glow": strength * (1-progress) * math.sin(math.pi * progress),
    }
