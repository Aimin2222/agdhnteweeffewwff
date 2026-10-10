# -*- coding: utf-8 -*-
"""Regressions: actual-scene gallery, bounded badge sizing, material bloom."""
from pathlib import Path
from types import SimpleNamespace
import numpy as np
from PIL import Image, ImageChops
import pytest

from core.effects import Template
from core.kill_icons import ASSET_STYLES, make_badge
from ui.template_gallery import render_scene_comparison, scene_labels


@pytest.mark.parametrize('style', sorted(ASSET_STYLES))
def test_each_material_is_sized_for_1080p_kill_log(tmp_path, style):
    path=make_badge(tmp_path/f'{style}.png',style)
    with Image.open(path) as img:
        assert img.mode=='RGBA'
        assert img.size==(385,116)
        assert img.getbbox() is not None


def test_material_bloom_changes_with_strength_and_enabled(tmp_path):
    p=[]
    for level in (0, .7, 1.7):
        path=make_badge(tmp_path/f'bloom_{level}.png','premium_gold',glow_strength=level,
                        glow_color='#FFCA5D',sparkle_strength=1.4)
        with Image.open(path) as im: p.append(im.copy())
    assert ImageChops.difference(p[0],p[1]).getbbox() is not None
    assert ImageChops.difference(p[1],p[2]).getbbox() is not None
    off=make_badge(tmp_path/'off.png','premium_gold',glow_enabled=False,glow_strength=2)
    with Image.open(off) as im:
        assert ImageChops.difference(im,p[0]).getbbox() is None


def test_real_scene_is_used_as_left_half_and_grade_changes_right():
    # A stand-in for a captured LoL frame; never loaded from fake stock imagery.
    yy,xx=np.mgrid[:90,:160]
    real=np.zeros((90,160,3),dtype=np.uint8)
    real[...,0]=(xx*3)%256
    real[...,1]=(yy*2)%256
    real[...,2]=87
    inp=Image.fromarray(real,'RGB')
    normal=Template(grade='default',grade_strength=0,bloom=0,vignette=0,grain=0)
    warm=Template(grade='golden',grade_strength=1,bloom=0,vignette=0,grain=0)
    a=render_scene_comparison(inp,normal,160,90)
    b=render_scene_comparison(inp,warm,160,90)
    assert a.size==b.size==(323,90)
    assert np.array_equal(np.array(a)[:,:160],real)
    assert np.array_equal(np.array(b)[:,:160],real)
    assert not np.array_equal(np.array(a)[:,163:],np.array(b)[:,163:])


def test_scene_choices_include_kill_and_assist_labels():
    values=[]
    for id,role in ((1,'kill'),(2,'assist')):
        values.append(SimpleNamespace(event_id=id,time=31.+id,killer='Alpha',victim='Beta',role=role))
    entries=scene_labels(values)
    assert len(entries)==2
    assert 'キル' in entries[0][0]
    assert 'アシスト' in entries[1][0]
    assert entries[0][1]!=entries[1][1]


def test_editor_has_glow_slider_and_resize_centering():
    source=(Path(__file__).resolve().parents[1]/'legacy_app.py').read_text('utf-8')
    assert 'self.var_kill_glow_strength.set(v)' in source
    assert 'self._recenter_preview_placeholder' in source
    assert 'command=self._open_template_gallery' in source
