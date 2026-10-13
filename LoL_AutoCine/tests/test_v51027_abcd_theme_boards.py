# -*- coding: utf-8 -*-
"""Regression tests for actual ChatGPT concept-board A/B/C/D kill frames."""
from pathlib import Path
import pytest
from PIL import Image, ImageDraw

from core import kill_frame_abcd as abcd
from core import kill_icons as badge

def _icon(path, color):
    Image.new("RGB",(96,96),color).save(path)
    return path

@pytest.mark.parametrize("style", ["abc_a","abc_b","abc_c"])
def test_abc_creates_transparent_live_portraits(tmp_path,style):
    killer=_icon(tmp_path/"killer.png",(255,60,80))
    victim=_icon(tmp_path/"victim.png",(30,110,240))
    dst=tmp_path/"result.png"
    badge.make_badge(dst,style,killer_icon=killer,victim_icon=victim)
    with Image.open(dst) as im:
        assert im.mode=="RGBA"
        assert im.size==(385,116)
        assert im.getpixel((44+34,24+34))[:3]!=(30,110,240)
        assert im.getpixel((273+34,24+34))[:3]!=(255,60,80)
        assert im.getpixel((0,0))[3]==0

def test_board_import_real_pixels_and_style_discovery(tmp_path,monkeypatch):
    monkeypatch.setattr(abcd,"boards_dir",lambda:tmp_path/"actual_boards")
    source=tmp_path/"エルダウッド_原画.png"
    im=Image.new("RGB",(1536,1024),(15,25,38))
    d=ImageDraw.Draw(im)
    # Actual motif at the source position referenced by the weak variant.
    cx,cy=round(1536*.233),round(1024*.31)
    d.line((cx-30,cy-30,cx+30,cy+30),fill=(60,255,118),width=16)
    d.line((cx-30,cy+30,cx+30,cy-30),fill=(60,255,118),width=16)
    # Strong variant deliberately differs from weak.
    cx=round(1536*.707)
    d.line((cx-35,cy-35,cx+35,cy+35),fill=(240,120,245),width=18)
    d.line((cx-35,cy+35,cx+35,cy-35),fill=(240,120,245),width=18)
    im.save(source)
    code,dst=abcd.install_concept_board(source)
    assert code=="elderwood"
    assert dst.read_bytes()[:8]==b"\x89PNG\r\n\x1a\n"
    assert set(abcd.installed_theme_styles())=={"d_elderwood_weak","d_elderwood_strong"}
    # The render is a crop from real source pixels, not a generic fallback.
    left=tmp_path/"left.png";right=tmp_path/"right.png"
    _icon(left,(230,20,30));_icon(right,(20,20,230))
    x=tmp_path/"weak.png";y=tmp_path/"strong.png"
    abcd.render_abcd_badge(x,"d_elderwood_weak",killer_icon=left,victim_icon=right)
    abcd.render_abcd_badge(y,"d_elderwood_strong",killer_icon=left,victim_icon=right)
    assert x.read_bytes()!=y.read_bytes()
    with Image.open(x) as output:
        assert output.size==(385,116)
        assert output.mode=="RGBA"

def test_board_missing_is_not_advertised(tmp_path,monkeypatch):
    monkeypatch.setattr(abcd,"boards_dir",lambda:tmp_path/"empty")
    assert abcd.installed_theme_styles()=={}
    with pytest.raises(FileNotFoundError):
        abcd.render_abcd_badge(tmp_path/"x.png","d_project_strong")

def test_recognition_favors_dark_cosmic_over_cosmic():
    assert abcd.recognize_board("ダークコズミック_キルアイコン図録.png")=="dark_cosmic"
    assert abcd.recognize_board("コズミックキルアイコン設計図.png")=="cosmic"
    assert abcd.recognize_board("サイオプス_キルアイコン設計図.png") is None

def test_intro_keeps_explicit_motion_and_legacy():
    assert abcd.theme_intro_motion("abc_a","instant")=="instant"
    assert abcd.theme_intro_motion("abc_c","instant")=="pop"
    assert abcd.theme_intro_motion("d_project_strong","slide_down")=="slide_down"
    assert abcd.theme_intro_motion("d_project_strong","instant")=="slide_left"
    assert badge.normalize("simple")=="simple"
    assert "user_frame_16" in badge.STYLES
