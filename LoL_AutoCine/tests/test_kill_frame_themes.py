# -*- coding: utf-8 -*-
"""Unit tests for the isolated image-backed kill-frame template catalog."""
from pathlib import Path
import pytest
from core.kill_frame_themes import (THEMES, FAMILIES, validate_choice,
                                    source_path, extract_original_motif, intro_timing)


def test_four_families_and_theme_catalog():
    assert tuple(FAMILIES) == ("A", "B", "C", "D")
    assert len(THEMES) >= 30
    assert len({t.source_file for t in THEMES.values()}) == len(THEMES)


@pytest.mark.parametrize("family", ("A", "B", "C"))
def test_abc_selection_never_requires_theme(family):
    assert validate_choice(family, "unused", "weak", "melee")[1] is None


def test_d_requires_real_registered_theme():
    assert validate_choice("D", "project", "strong", "ranged") == (
        "D", "project", "strong", "ranged")
    with pytest.raises(ValueError):
        validate_choice("D", "not_existing")


def test_missing_original_art_is_not_silently_replaced(tmp_path):
    with pytest.raises(FileNotFoundError):
        source_path(tmp_path, "project")


def test_intro_timing_is_bounded_and_theme_specific():
    begin = intro_timing("project", 0)
    end = intro_timing("project", .4)
    assert begin["opacity"] == 0
    assert end["opacity"] == 1
    assert begin["effect"] == "scan_glitch"
    assert intro_timing("star_guardian", .05)["effect"] == "starlight"


def test_motif_extract_uses_actual_input_pixels(tmp_path):
    image = pytest.importorskip("PIL.Image")
    src = image.new("RGB", (600, 400), (245, 245, 245))
    # The output must be visually dependent on actual source image pixels.
    for x in range(245, 355):
        for y in range(290, 360):
            src.putpixel((x, y), (20, 90, 220))
    src.save(tmp_path / THEMES["project"].source_file)
    output = tmp_path / "sprite.png"
    extract_original_motif(tmp_path, "project", "ranged", output,
                           center=(.5, .81), radius_fraction=.12)
    with image.open(output) as im:
        assert im.mode == "RGBA"
        assert any(px[2] > px[0] * 2 and px[3] > 100
                   for px in im.getdata())
