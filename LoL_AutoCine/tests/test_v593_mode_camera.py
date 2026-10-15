# -*- coding: utf-8 -*-
"""Regression coverage for mode UI and continuous camera interpolation."""
import math
import tkinter as tk
from types import SimpleNamespace

from core.camera_clock import SmoothReplayClock
from core.camera import CameraPlan
from legacy_app import App


def test_replay_clock_never_steps_during_small_drift():
    c = SmoothReplayClock(100.0)
    before = c.time
    assert not c.observe(100.18)
    assert c.time == before  # sync may not teleport camera
    intervals = [c.advance(1.0 / 144.0) for _ in range(144)]
    assert all(a < b for a, b in zip(intervals, intervals[1:]))
    assert max(b-a for a,b in zip([before]+intervals, intervals)) < 0.008
    assert 101.0 < c.time < 101.08


def test_replay_clock_external_seek_is_reset():
    c = SmoothReplayClock(100.0)
    assert c.observe(120.0)
    assert c.time == 120.0
    assert c.drift == 0
    assert not c.observe(float('nan'))
    assert c.time == 120.0


def test_keyframes_continuous_velocity_at_internal_marker():
    frames = ({'time':-3.0, 'yaw':-15.0,'zoom':-7.0,'fov':3.0},
              {'time':-1.0, 'yaw':-5.0,'zoom':0.0,'fov':0.0},
              {'time':0.0, 'yaw':10.0,'zoom':7.0,'fov':-2.0},
              {'time':2.0, 'yaw':18.0,'zoom':12.0,'fov':-4.0})
    p = CameraPlan(style='lolnam_cinema', kill_time=100.0, scene_keyframes=frames)
    for channel in range(3):
        h=0.001
        left=(p.keyframe_values(99.0)[channel]-p.keyframe_values(99.0-h)[channel])/h
        right=(p.keyframe_values(99.0+h)[channel]-p.keyframe_values(99.0)[channel])/h
        assert abs(left-right) < 0.06
    samples=[p.keyframe_values(t/20+97.0)[0] for t in range(101)]
    assert min(samples) >= -15.01 and max(samples) <= 18.01


def test_ui_mode_toggle_keeps_scene_state_and_view(monkeypatch, tmp_path):
    root=tk.Tk()
    try:
        app=App(root)
        app.var_scene_mode.set(True)
        app.checked_kills={1,3}
        app.var_edit_mode.set('easy')
        app._apply_edit_mode(log=False)
        assert app._mode_easy_section.winfo_manager() == 'pack'
        assert all(not panel.winfo_manager() for panel in app._mode_detail_sections)
        assert app.canvas.winfo_manager()=='pack'
        app.var_edit_mode.set('advanced')
        app._apply_edit_mode(log=False)
        assert not app._mode_easy_section.winfo_manager()
        assert app._editor_timeline.winfo_manager() == 'pack'
        assert app._editor_scene.winfo_manager() == 'pack'
        assert not app._editor_camera.winfo_manager()
        assert not app._editor_advanced.winfo_manager()
        assert app.var_scene_mode.get() is True
        assert app.checked_kills=={1,3}
        assert app.canvas.winfo_manager()=='pack'
        app.var_edit_mode.set('easy')
        app._apply_edit_mode(log=False)
        assert app._mode_easy_section.winfo_manager()=='pack'
        assert app.txt.winfo_manager()=='pack'
    finally:
        root.destroy()


def test_easy_preset_and_manual_editor_preserves_values():
    root=tk.Tk()
    try:
        app=App(root)
        app._choose_easy_preset('Lolnam風スムーズ')
        assert app.var_tpl.get()=='Lolnam風スムーズ'
        app.on_keyframe_preset('soft_orbit')
        assert len(app._edit_keyframes)==5
        assert app._edit_keyframes[0]['time'] < 0
        app.on_camera_safe_pose()
        assert math.isclose(app.sl['third_yaw'].get(),0.0)
    finally:
        root.destroy()


def test_easy_one_click_does_not_erase_manual_shots(monkeypatch):
    root=tk.Tk()
    try:
        app=App(root)
        app._need_lock=lambda:True
        app._run_bg=lambda fn,*args: setattr(app,'test_dispatched', args)
        app.var_scene_mode.set(True)
        app.var_edit_mode.set('easy')
        app.on_one_click()
        assert app.test_dispatched[-4] is False  # easy/plain create
        assert app.var_scene_mode.get() is True  # saved mode unchanged
        app.on_smart_one_click()
        assert app.test_dispatched[-4] is True
    finally:
        root.destroy()
