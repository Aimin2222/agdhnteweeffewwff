# -*- coding: utf-8 -*-
"""v5.10.8: premium kill glow, template colors, gallery, and compatibility."""
from dataclasses import fields
from pathlib import Path
import pytest

from core.effects import Template, NEUTRAL, GRADE_JP, grade_values, one_click_templates
from core.kill_icons import MARK_STYLES, normalize_design, make_badge
from ui.template_gallery import appearance, template_info, render_template_preview


def test_default_color_neutral_and_presets_exposed():
    assert grade_values("default", 1, 1) == NEUTRAL
    for key in ("default", "lolnam", "golden", "iceblue", "neon", "drama", "fade", "highcontrast"):
        assert key in GRADE_JP
        assert len(appearance(key)[1:4]) == 3


def test_template_choices_and_one_click_gold():
    templates = one_click_templates()
    raw = templates["デフォルト（無加工カラー）"]
    assert raw.grade == "default" and raw.grade_strength == 0
    gold = templates["ロイヤルゴールド・キルログ"]
    assert gold.grade == "golden" and gold.kill_icon_style == "cinema"
    assert gold.kill_mark_style == "royal" and gold.kill_glow_strength > 1
    assert template_info(gold)["camera"]


def test_gallery_thumbnail_uses_real_color_pipeline():
    raw = Template(grade="default", grade_strength=0, bloom=0, vignette=0, grain=0)
    gold = Template(grade="golden", grade_strength=1, bloom=0, vignette=0, grain=0)
    a = render_template_preview(raw, 180, 100)
    b = render_template_preview(gold, 180, 100)
    assert a.size == b.size == (180, 100)
    assert a.tobytes() != b.tobytes()


def test_premium_glyphs_are_available_and_none_is_clear(tmp_path):
    from PIL import Image
    for name in ("royal", "lolkill", "none"):
        assert name in MARK_STYLES
        path = make_badge(tmp_path/f"{name}.png","cinema",mark_style=name,glow_enabled=False)
        with Image.open(path) as im:
            assert im.size == (385,116)
            center = im.getpixel((192,58))[3]
            assert center == 0 if name == "none" else center > 0


def test_glow_strongly_changes_transparent_outer_area(tmp_path):
    from PIL import Image, ImageChops
    off = make_badge(tmp_path/"off.png","cinema",glow_enabled=False,mark_style="royal")
    low = make_badge(tmp_path/"low.png","cinema",glow_enabled=True,glow_strength=.2,mark_style="royal")
    high = make_badge(tmp_path/"high.png","cinema",glow_enabled=True,glow_strength=2.,mark_style="royal")
    with Image.open(off) as o, Image.open(low) as l, Image.open(high) as h:
        assert ImageChops.difference(o,h).getbbox() is not None
        # Halo spills beyond the physical left-hand frame.
        x,y=5,53
        assert h.getpixel((x,y))[3] > l.getpixel((x,y))[3] >= o.getpixel((x,y))[3]


def test_grade_preset_parameters_and_intensity_clamp():
    assert normalize_design(glow_strength=9)[3] == 2
    assert normalize_design(glow_strength=-2)[3] == 0
    assert Template(kill_sparkle_intensity=1.5, kill_stack_gap=12).to_dict()["kill_stack_gap"] == 12


def test_full_template_gallery_and_mirror_controls_exist():
    source = (Path(__file__).resolve().parents[1]/"legacy_app.py").read_text("utf-8")
    gallery = (Path(__file__).resolve().parents[1]/"ui"/"template_gallery.py").read_text("utf-8")
    assert "self._open_template_gallery" in source
    assert "A：かんたん色見本カード" in source and "B：全テンプレート図鑑" in source
    assert "self._refresh_template_tone(name)" in source
    assert "self._live_preview.submit(key, (self.source, cw, ch" in source
    assert "render_template_preview(tpl, 320, 180)" in gallery
    assert "self._apply_kill_glow_preset()" in source
