# -*- coding: utf-8 -*-
from __future__ import annotations
from types import SimpleNamespace
from core.effects import Template, build_graph
from core.highlight_pulse import pulse_filters
from ui.scene_project import Shot, SceneProject, scene_key, apply_shot
from ui.scene_batch import build_scene_templates
from ui.highlight_director import recommend_highlight, decide_style, SMART_STYLES


def kill(event=1, time=100, multikill=1, role='kill'):
    return SimpleNamespace(event_id=event, time=time, killer='Aimin', victim='enemy',
                           multikill=multikill, role=role)


def test_smart_types_are_grounded_in_metadata():
    assert decide_style(kill(multikill=1)) == 'chase'
    assert decide_style(kill(multikill=2)) == 'impact'
    assert decide_style(kill(multikill=4)) == 'teamfight'
    assert decide_style(kill(role='assist')) == 'chase'
    assert decide_style(kill(multikill=1), 'teamfight') == 'teamfight'
    assert len(SMART_STYLES) == 4


def test_smart_shot_five_frames_closes_at_neutral():
    for style in ('auto', 'chase', 'impact', 'teamfight'):
        shot = recommend_highlight(kill(multikill=2), pre=4, post=3, style=style)
        assert len(shot.keyframes) == 5
        assert shot.keyframes[0] == dict(time=-4, yaw=0, zoom=0, fov=0)
        assert shot.keyframes[-1]['time'] >= 3
        assert all(shot.keyframes[-1][k] == 0 for k in ('yaw','zoom','fov'))
        assert 0 < shot.highlight_pulse <= 1
        assert shot.dolly <= 4


def test_teamfight_is_wide_and_low_pulse():
    wide = recommend_highlight(kill(multikill=4), style='auto')
    big = recommend_highlight(kill(multikill=2), style='auto')
    assert wide.highlight_pulse < big.highlight_pulse
    assert wide.keyframes[2]['fov'] > big.keyframes[2]['fov']
    assert wide.keyframes[2]['zoom'] <= big.keyframes[2]['zoom']


def test_normal_render_has_no_smart_changes():
    base = Template(style='third', game_audio=True)
    old = list(build_scene_templates([kill()], base, {}, auto=True))[0][1]
    assert old.scene_keyframes == [] and old.highlight_pulse == 0
    assert base.highlight_pulse == 0
    plain = list(build_scene_templates([kill()], base, {}, auto=False))[0][1]
    assert plain.style == 'third' and plain.highlight_pulse == 0


def test_explicit_smart_render_and_no_mutation():
    base = Template(style='third', game_audio=True, smart_highlight_enabled=True, smart_highlight_style='impact')
    planned = list(build_scene_templates([kill()], base, {}, auto=True))[0][1]
    assert planned.style == 'lolnam_cinema'
    assert planned.game_audio is True
    assert planned.highlight_pulse == 0.7
    assert len(planned.scene_keyframes) == 5
    assert base.style == 'third' and base.scene_keyframes == []


def test_custom_overrides_take_precedence():
    k = kill()
    base = Template(style='third_cinema', smart_highlight_enabled=True)
    custom = Shot(profile='smooth', arc=7, highlight_pulse=0.12)
    t = list(build_scene_templates([k], base, {scene_key(k):vars(custom)}, auto=True))[0][1]
    assert t.motion_arc == 7 and t.highlight_pulse == 0.12


def test_legacy_scene_project_remains_loadable():
    p = SceneProject.from_dict({'schema_version':3, 'application':'LoL AutoCine',
                                'shots':{'scene': {'arc': 12}},'sequence':['scene']})
    assert p.shots['scene'].highlight_pulse == 0
    p.put('scene', recommend_highlight(kill()))
    assert p.undo() and p.shots['scene'].highlight_pulse == 0
    assert p.redo() and p.shots['scene'].highlight_pulse > 0
    assert SceneProject.from_dict(p.to_dict()).shots['scene'].highlight_pulse > 0


def test_pulse_is_temporal_and_opt_in():
    t = Template(grade='standard', bloom=0, grain=0, vignette=0, bars=0,
                 transition='cut', highlight_pulse=0)
    old = build_graph(t, 7, False, effect_events=[(4, 4.4)])
    assert 'exp(-22*abs(t-' not in old
    t.highlight_pulse=0.4
    new = build_graph(t, 7, False, effect_events=[(4, 4.4)])
    assert 'exp(-22*abs(t-4.000))' in new
    assert 'saturation=' in new
    assert 'exp(-22*abs(t-' not in build_graph(t, 7, False, still=True, effect_events=[(4,4.4)])


def test_pulse_multiple_kills_uses_all_events():
    f = pulse_filters([(1.5,1.92), (3.1,3.52)], 0.7)[0]
    assert 't-1.500' in f and 't-3.100' in f
    assert 'eval=frame' in f


def test_easy_ui_smart_button_enables_only_explicit_mode(monkeypatch):
    import tkinter as tk
    from legacy_app import App
    root = tk.Tk()
    try:
        app = App(root)
        assert app.current_template().smart_highlight_enabled is False
        captured = []
        monkeypatch.setattr(app, 'on_one_click', lambda smart=False: captured.append(smart))
        app.var_smart_highlight_style.set(SMART_STYLES['teamfight'])
        app.on_smart_one_click()
        assert captured == [True]
        assert app.current_template().smart_highlight_enabled is True
        assert app.current_template().smart_highlight_style == 'teamfight'
        assert app.var_scene_mode.get() is True
    finally:
        root.destroy()


def test_detailed_smart_apply_is_one_undo(monkeypatch):
    import tkinter as tk
    from legacy_app import App
    root = tk.Tk()
    try:
        app = App(root)
        app.kills = [kill(1), kill(2, 140, 3)]
        monkeypatch.setattr(app, '_schedule_project_save', lambda: None)
        monkeypatch.setattr(app, '_refresh_scene_list', lambda: None)
        app.var_smart_highlight_style.set(SMART_STYLES['auto'])
        app.on_highlight_plan_all()
        assert len(app.scene_project.shots) == 2
        assert app.scene_project.shots[scene_key(app.kills[0])].highlight_pulse == .3
        assert app.scene_project.shots[scene_key(app.kills[1])].highlight_pulse == .35
        assert app.scene_project.undo()
        assert not app.scene_project.shots
    finally:
        root.destroy()


def test_normal_one_click_after_smart_does_not_reenable_automatic_highlights(monkeypatch):
    import tkinter as tk
    from legacy_app import App
    root = tk.Tk()
    try:
        app = App(root)
        monkeypatch.setattr(app, '_need_lock', lambda: True)
        captured = []
        monkeypatch.setattr(app, '_run_bg', lambda *args: captured.append(args))
        app.var_edit_mode.set('advanced')
        app.on_smart_one_click()
        assert captured[-1][2].smart_highlight_enabled is True
        app.on_one_click()
        assert captured[-1][2].smart_highlight_enabled is False
        # The regular action must keep advanced saved edits, while selecting the old planner.
        assert app.var_scene_mode.get() is True
        assert app.var_smart_highlight_enabled.get() is True
    finally:
        root.destroy()
