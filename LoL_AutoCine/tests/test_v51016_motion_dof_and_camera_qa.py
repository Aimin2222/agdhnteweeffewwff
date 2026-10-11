# -*- coding: utf-8 -*-
"""Safe regressions for v5.10.16. Real Windows camera framing is manual QA."""
from pathlib import Path
import tkinter as tk
import pytest
from core.kill_icons import MOTION_STYLES, badge_motion_xy, with_badges, STYLES, ASSET_STYLES
from core.camera_qa import plan_eight_cases
from core.players import Player
from core.effects import Template

def test_entrance_modes_are_bounded_and_keep_instant_legacy():
    assert len(MOTION_STYLES) == 6
    assert badge_motion_xy('right-top','instant',4.0,'W-w-32','62') == ('W-w-32','62')
    for name in MOTION_STYLES:
        x,y=badge_motion_xy('right-top',name,4.0,'W-w-32','62')
        assert isinstance(x,str) and isinstance(y,str)
        assert len(x)<350 and len(y)<350
    assert 'H+20' in badge_motion_xy('right-top','slide_up',4,'W-w-32','62')[1]

def test_motion_reaches_real_overlay_and_unknown_input_is_failsafe():
    badges=[(Path('dummy.png'),4.0)]
    graph=with_badges('[in]null[vout]',1,badges,duration=9.0,motion='slide_left')
    assert 'overlay=x=' in graph and 'W+20' in graph
    assert graph.endswith('[vout]')
    assert with_badges('[in]null[vout]',1,badges,duration=9,motion='unknown').endswith('[vout]')

def test_template_default_keeps_previous_static_kill_frame():
    assert Template().kill_icon_motion == 'instant'
    assert len(ASSET_STYLES)==37
    assert 'K/DA' in STYLES['user_frame_08']

def test_8_camera_plan_uses_both_teams_and_real_events():
    blue=Player(0,'Blue','Blue#JP','Blue','Ahri','ORDER')
    red=Player(5,'Red','Red#JP','Red','LeeSin','CHAOS')
    events=[dict(event_id=1,time=30.0,killer='Blue',victim='Red',assisters=[]),
            dict(event_id=2,time=60.0,killer='Red',victim='Blue',assisters=[])]
    cases=plan_eight_cases([blue,red],events)
    assert len(cases)==8
    assert [x[0] for x in cases]==['RED']*4+['BLUE']*4

def test_dof_radio_panels_never_show_both():
    import legacy_app
    root=tk.Tk()
    try:
        app=legacy_app.App(root)
        app.var_dof_shape.set('円形（おすすめ）')
        root.update_idletasks()
        assert app._circle_dof_panel.winfo_manager()
        assert app._quick_circle_dof.winfo_manager()
        assert not app._legacy_dof_panel.winfo_manager()
        assert not app._quick_band_dof.winfo_manager()
        app.var_dof_shape.set('従来の上下ぼかし')
        root.update_idletasks()
        assert app._legacy_dof_panel.winfo_manager()
        assert app._quick_band_dof.winfo_manager()
        assert not app._circle_dof_panel.winfo_manager()
        assert not app._quick_circle_dof.winfo_manager()
    finally:
        root.destroy()

def test_scan_button_starts_background_before_player_connected():
    import legacy_app
    root=tk.Tk()
    try:
        app=legacy_app.App(root)
        app.players=[]
        calls=[]
        app._run_bg=lambda fn,*args:calls.append((fn.__name__,args))
        app.on_scan()
        assert calls and calls[-1][0]=='_scan'
    finally:
        root.destroy()

def test_dev_camera_qa_requires_completed_whole_match_scan(monkeypatch):
    import legacy_app
    root=tk.Tk()
    try:
        app=legacy_app.App(root)
        shown=[]
        monkeypatch.setattr(legacy_app.messagebox,'showinfo',lambda *args,**kw:shown.append(args))
        app._match_scan_cache=None
        app.on_dev_camera_qa()
        assert shown
    finally:
        root.destroy()

def test_camera_repeated_selection_reuses_stable_non_pitch_axis():
    from core.camera import stabilize_non_pitch_rotation
    prior={'x':35.0,'y':15.0,'z':0.0}
    rolled={'x':35.0,'y':195.0,'z':0.0}
    notes=[]
    chosen=stabilize_non_pitch_rotation(rolled,prior,'x',log=notes.append)
    assert chosen['y']==15.0 and notes
    normal={'x':35.0,'y':20.0,'z':0.0}
    assert stabilize_non_pitch_rotation(normal,prior,'x')['y']==20.0
    assert stabilize_non_pitch_rotation(normal,prior,'y')['x']==35.0

def test_skin_theme_display_names_uniquely_roundtrip_to_style_ids():
    from core.kill_icons import STYLES, REVERSE_STYLES
    assert len(set(STYLES.values())) == len(STYLES)
    for key, label in STYLES.items():
        assert REVERSE_STYLES[label] == key
