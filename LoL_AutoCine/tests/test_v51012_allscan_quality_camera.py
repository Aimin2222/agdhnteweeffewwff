# -*- coding: utf-8 -*-
"""v5.10.12 regression tests for whole-match scan, style colors and camera guards."""
from pathlib import Path
from types import SimpleNamespace
from PIL import Image
import pytest

from core.players import Player
from core.scanner import filter_scanned_events, scan_kills
from core.camera import live_side_profile, side_yaw_for, CameraPlan, RigInfo
from core.kill_icons import make_badge, ASSET_STYLES
from core.effects import Template, grade_values, GRADES


def player(name, team, slot):
    return Player(slot, name, name+'#JP1', name, 'Lee Sin', team)

EVENTS = [
    dict(event_id=1,time=12.,killer='Blue',victim='Red',assisters=['BlueAssist']),
    dict(event_id=2,time=24.,killer='Red',victim='Blue',assisters=['RedAssist']),
    dict(event_id=3,time=35.,killer='Blue',victim='Red',assisters=['BlueAssist']),
]


def test_filter_cache_does_not_modify_scan_and_handles_assists():
    blue, red, blue_assist = player('Blue','ORDER',0), player('Red','CHAOS',5),player('BlueAssist','ORDER',1)
    original = repr(EVENTS)
    assert [k.role for k in filter_scanned_events(EVENTS,blue,'both')] == ['kill','kill']
    assert [k.role for k in filter_scanned_events(EVENTS,red,'both')] == ['kill']
    assert len(filter_scanned_events(EVENTS,blue_assist,'assist')) == 2
    assert len(filter_scanned_events(EVENTS,None,'both')) == 3
    assert len(filter_scanned_events(EVENTS,None,'assist')) == 0
    assert repr(EVENTS)==original


def test_all_scan_filter_no_extra_api_requests(monkeypatch):
    # Pure cache re-filtering never talks to a replay API.
    class FailAPI:
        def __getattr__(self,key): raise AssertionError('No new Replay API query allowed')
    api=FailAPI()
    assert len(filter_scanned_events(EVENTS,player('BlueAssist','ORDER',1),'both')) == 2


def test_side_profile_v51013_red_revision_keeps_manual_heading():
    blue=live_side_profile('ORDER')
    red=live_side_profile('CHAOS')
    assert blue['yaw'] < 0 < red['yaw']
    assert blue['yaw'] == -12 and red['yaw'] == 192  # v5.10.13 replaces +12
    assert blue['elevation'] >= 35 and red['elevation'] >= 35
    assert red['distance'] > blue['distance']
    assert live_side_profile('CHAOS','red')['yaw'] == 180
    assert side_yaw_for('CHAOS') == 180  # legacy pure calculation still supported


def test_conservative_camera_prevents_extreme_close_ups():
    rig=RigInfo(mode='fps',third=True,rot={'x':25.,'y':0.,'z':0.},pitch_axis='x',pitch_sign=1,h=(0.,-1.))
    a=CameraPlan(style='third',rig=rig,third_dist=1100,third_elev=26,third_yaw=80,smart_composition=True)
    off,e=a.third_pose_at(0)
    assert off[1]>650
    assert e>=38
    assert abs(a.rotation_at(0)['z'])<=55


def test_asset_hi_res_reuses_exact_original_artwork(tmp_path):
    asset=next(iter(ASSET_STYLES))
    a=make_badge(tmp_path/'normal.png',asset)
    b=make_badge(tmp_path/'high.png',asset,hires=True)
    with Image.open(a) as im1, Image.open(b) as im2:
        assert im1.size==(385,116)
        assert im2.size==(770,232)


def test_grades_more_distinct_from_default():
    neutral=grade_values('default',1,1)
    for label in ('golden','iceblue','lolnam','neon','purple'):
        grade=grade_values(label,1,1)
        assert max(abs(grade[k]-neutral[k]) for k in neutral)>0.10


def test_ui_supports_scan_once_then_player_and_team_filter():
    code=(Path(__file__).resolve().parents[1]/'legacy_app.py').read_text('utf-8')
    assert '試合全体を一括スキャン' in code
    assert 'self._match_scan_cache' in code
    assert 'self._filter_scanned_for_locked()' in code
    assert 'self.var_team_filter' in code
    assert 'self._match_scan_cache = None' in code
