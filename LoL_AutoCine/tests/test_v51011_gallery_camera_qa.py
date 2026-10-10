# -*- coding: utf-8 -*-
"""v5.10.11 source-of-truth checks, no LoL/Windows driver required."""
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from PIL import Image

from core.camera import _pitch_calibration, CameraPlan, RigInfo
from core.kill_icons import ASSET_STYLES, STYLES, make_badge
from core.auto_qa import run_checks
from ui.template_gallery import render_scene_comparison


def test_pitches_support_two_conventions_and_reject_uncalibrated():
    assert _pitch_calibration({'x': 28, 'y': 180, 'z': 0}, 28) == ('x',False)
    assert _pitch_calibration({'x': 59, 'y': 180, 'z': 0}, 31) == ('x',True)
    assert _pitch_calibration({'x': 0, 'y': 180, 'z': 0}, 39)[0] is None


def test_third_person_complement_is_preserved():
    rig=RigInfo(mode='fps',third=True,rot={'x':59.,'y':10.,'z':0.},
                pitch_axis='x',pitch_sign=1.,pitch_complement=True,h=(0.,-1.))
    a=CameraPlan(style='third',rig=rig,third_elev=31)
    assert a.rotation_at(0.)['x'] == pytest.approx(59.)


def test_every_previous_kill_frame_asset_is_selectable_and_size_stable(tmp_path):
    assert len(ASSET_STYLES)>=21
    portrait=tmp_path/'test.png'
    Image.new('RGB',(80,80),'slateblue').save(portrait)
    for code in ASSET_STYLES:
        assert code in STYLES
        result=tmp_path/(code+'.png')
        make_badge(result,code,killer_icon=portrait,victim_icon=portrait)
        with Image.open(result) as img:
            assert img.mode=='RGBA' and img.size == (385,116)


def test_real_frame_large_compare_has_width_for_visual_judgement():
    from core.effects import Template
    original=Image.new('RGB',(1920,1080),'teal')
    comparison=render_scene_comparison(original,Template(),415,234)
    assert comparison.size==(833,234)


def test_automatic_bot_writes_a_machine_readable_report(tmp_path):
    root=Path(__file__).resolve().parents[1]
    output=tmp_path/'report.json'
    result=run_checks(root,report_file=output)
    disk=json.loads(output.read_text('utf-8'))
    assert disk['failed']==0, disk
    assert disk['passed']>=7 and len(disk['checks'])>=8
    assert any('三人称' in n or 'カメラ' in n for n in disk['notes']+list(x['name'] for x in disk['checks']))


def test_ui_has_dynamic_camera_label_and_explicit_mirror_stop():
    src=(Path(__file__).resolve().parents[1]/'legacy_app.py').read_text('utf-8')
    assert 'textvariable=self.var_camera_status' in src
    assert 'self._kill_badge_toggle_button.configure(' in src
    assert 'command=self.on_mirror_start' in src
    assert 'on_mirror_stop(reason=' in src
    assert 'self._scroll_to_kill_detail' in src
    assert 'on_automatic_qa' in src
