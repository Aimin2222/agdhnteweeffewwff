# -*- coding: utf-8 -*-
"""Regression tests for independent HUD presets and checked-scene batch editing."""
import tkinter as tk
from types import SimpleNamespace
from dataclasses import asdict

from core.hud import hide_values
from core.effects import Template
from legacy_app import App
from ui.hud_presets import HUD_MODES, hud_flags, hud_mode_from_flags, hud_summary
from ui.scene_project import scene_key, Shot


def sample_kill(n):
    return SimpleNamespace(time=float(n*12), event_id=n, killer='Aimin', victim=f'Enemy{n}', multikill=1, role='kill')


def test_hud_presets_legacy_flags():
    assert hud_flags('hidden') == (True, False)
    assert hud_flags('health') == (True, True)
    assert hud_flags('full') == (False, False)
    assert hud_mode_from_flags(True, True) == 'health'
    assert hud_mode_from_flags(True, False) == 'hidden'
    assert hud_mode_from_flags(False, True) == 'full'
    assert hide_values(True)['healthBarChampions'] is True
    assert all(not v for k, v in hide_values(True).items() if k != 'healthBarChampions')
    assert 'LoL' in hud_summary('health')


def test_gui_presets_and_template_roundtrip(monkeypatch, tmp_path):
    root = tk.Tk()
    try:
        app = App(root)
        monkeypatch.setattr(app, '_save_settings', lambda: None)
        for mode, (hide, bars) in [('hidden',(True,False)),('health',(True,True)),('full',(False,False))]:
            app.var_hud_choice.set(HUD_MODES[mode])
            app._on_hud_choice()
            assert app.var_hud_mode.get() == mode
            assert app.var_hud.get() == hide
            assert app.var_bars.get() == bars
            tpl = app.current_template()
            assert (tpl.hide_hud, tpl.keep_champion_bars) == (hide, bars)
            app.apply_template('三人称 自然め')
            app.apply_template('三人称 自然め')
            app.apply_template('三人称 自然め')
            # Applying the template uses its own legacy HUD flags.
            tpl.hide_hud = hide
            tpl.keep_champion_bars = bars
            app.templates['__HUD TEST__'] = tpl
            app.apply_template('__HUD TEST__')
            assert app.var_hud_mode.get() == mode
        app.var_edit_mode.set('advanced')
        app._apply_edit_mode(log=False)
        app.var_editor_zone.set('output')
        app._apply_editor_zone()
        assert app._editor_advanced_tabs.index('current') == 2
    finally:
        root.destroy()


def test_bulk_apply_is_one_undo_step(monkeypatch):
    root=tk.Tk()
    try:
        app=App(root)
        app.kills=[sample_kill(1), sample_kill(2), sample_kill(3)]
        app.lb_kills.insert('end','first','second','third')
        app.lb_kills.selection_set(0)
        app.on_scene_selection()
        app.scene_vars['yaw'].set(35)
        app.on_keyframe_preset('push_pull')
        app.checked_kills={0,2}
        monkeypatch.setattr('legacy_app.messagebox.askyesno', lambda *a,**k:True)
        monkeypatch.setattr(app, '_schedule_project_save', lambda:None)
        monkeypatch.setattr(app, '_refresh_scene_list', lambda:None)
        app.on_apply_shot_to_checked()
        assert set(app.scene_project.shots)=={scene_key(app.kills[0]),scene_key(app.kills[2])}
        assert app.scene_project.shots[scene_key(app.kills[2])].yaw == 35
        assert len(app.scene_project.shots[scene_key(app.kills[2])].keyframes)>=3
        assert app.var_scene_mode.get() is True
        assert len(app.scene_project._undo) == 1
        assert app.scene_project.undo()
        assert not app.scene_project.shots
    finally:
        root.destroy()


def test_batch_cancel_or_none(monkeypatch):
    root=tk.Tk()
    try:
        app=App(root)
        app.kills=[sample_kill(1)]
        app.lb_kills.insert('end','first')
        app.lb_kills.selection_set(0)
        app.on_scene_selection()
        app.checked_kills={0}
        monkeypatch.setattr('legacy_app.messagebox.askyesno', lambda *a,**k:False)
        app.on_apply_shot_to_checked()
        assert app.scene_project._undo == []
        app.checked_kills=set()
        app.on_apply_shot_to_checked()
        assert app.scene_project._undo == []
    finally:
        root.destroy()


def test_hud_mode_survives_restart(monkeypatch, tmp_path):
    monkeypatch.setattr('legacy_app.SETTINGS', tmp_path/'settings.json')
    root=tk.Tk()
    try:
        app=App(root)
        app.var_hud_choice.set(HUD_MODES['health'])
        app._on_hud_choice('<<ComboboxSelected>>')
        assert (tmp_path/'settings.json').exists()
    finally:
        root.destroy()
    root2=tk.Tk()
    try:
        new_app=App(root2)
        assert new_app.var_hud_mode.get() == 'health'
        assert new_app.var_hud.get() is True
        assert new_app.var_bars.get() is True
        assert __import__('json').loads((tmp_path/'settings.json').read_text(encoding='utf-8'))['hud_mode']=='health'
    finally:
        root2.destroy()
