# -*- coding: utf-8 -*-
"""v5.9.5: focused workspaces, compact setup, scene clipboard regression."""
import tkinter as tk
from types import SimpleNamespace
from ui.scene_project import scene_key
from legacy_app import App


def _kill(t, eid):
    return SimpleNamespace(time=t, event_id=eid, killer='Aimin', victim='Enemy', multikill=1, role='kill')


def test_left_workflow_before_references_and_templates():
    root = tk.Tk()
    try:
        app = App(root)
        names = [name for _widget, parent, name in app._mode_sidecards if parent is app.left_scroll.inner]
        assert names[:3] == ['1  リプレイ準備', '2  対象プレイヤー', '3  キル・アシストを探す']
        assert names.index('▣  テンプレート') > 2
    finally:
        root.destroy()


def test_workspace_shows_one_center_zone_and_persists_settings():
    root = tk.Tk()
    try:
        app=App(root)
        app.var_scene_mode.set(True)
        app.scene_vars['yaw'].set(21)
        app.var_edit_mode.set('advanced')
        app._apply_edit_mode(log=False)
        assert app._editor_timeline.winfo_manager()=='pack'
        assert app._editor_scene.winfo_manager()=='pack'
        assert not app._editor_camera.winfo_manager()
        app.var_editor_zone.set('camera'); app._apply_editor_zone()
        assert app._editor_camera.winfo_manager()=='pack'
        assert not app._editor_scene.winfo_manager()
        app.var_editor_zone.set('color'); app._apply_editor_zone()
        assert app._editor_advanced.winfo_manager()=='pack'
        assert app._editor_advanced_tabs.index('current') == 1
        app.var_editor_zone.set('output'); app._apply_editor_zone()
        assert app._editor_advanced_tabs.index('current') == 2
        assert not app._right_quick_output.winfo_manager()
        app.var_editor_zone.set('scene'); app._apply_editor_zone()
        assert app._right_quick_output.winfo_manager()=='pack'
        assert app.scene_vars['yaw'].get() == 21
        assert app.var_scene_mode.get() is True
        app.var_edit_mode.set('easy'); app._apply_edit_mode(log=False)
        assert not app.editor_zone_bar.winfo_manager()
        app.var_edit_mode.set('advanced'); app._apply_edit_mode(log=False)
        assert app._editor_scene.winfo_manager()=='pack'
    finally:
        root.destroy()


def test_shot_copy_paste_undo_preserves_values(monkeypatch):
    root = tk.Tk()
    try:
        app=App(root)
        app.kills=[_kill(15.0,1),_kill(30.0,2)]
        app.lb_kills.insert('end', 'scene1', 'scene2')
        app.lb_kills.selection_set(0)
        app.on_scene_selection()
        app.scene_vars['yaw'].set(47)
        app.on_keyframe_preset('push_pull')
        app.on_copy_scene_settings()
        assert app._scene_settings_clipboard['yaw']==47
        app.lb_kills.selection_clear(0,'end')
        app.lb_kills.selection_set(1)
        app.on_scene_selection()
        monkeypatch.setattr(app, '_schedule_project_save',lambda:None)
        monkeypatch.setattr(app, '_refresh_scene_list',lambda:None)
        app.on_paste_scene_settings()
        shot=app.scene_project.shots[scene_key(app.kills[1])]
        assert shot.yaw==47
        assert len(shot.keyframes)==5
        assert app.var_scene_mode.get() is True
        assert app.scene_project.undo()
        assert scene_key(app.kills[1]) not in app.scene_project.shots
    finally:
        root.destroy()


def test_scene_actions_above_cinematic_inspector_and_workspace_shortcuts():
    root=tk.Tk()
    try:
        app=App(root)
        names=[name for _widget,parent,name in app._mode_sidecards if parent is app.right_scroll.inner]
        assert names[0] == '◉  検出シーン'
        assert names[1] == '☁  出力状況'
        app._focus_editor_zone('camera')
        assert app.var_edit_mode.get() == 'advanced'
        assert app._editor_camera.winfo_manager() == 'pack'
        app._focus_editor_zone('scene')
        assert app._editor_scene.winfo_manager() == 'pack'
    finally:
        root.destroy()


def test_leaving_output_workspace_restores_easy_output_controls():
    root = tk.Tk()
    try:
        app = App(root)
        app.var_fps_ui.set('144 FPS')
        app.checked_kills = {1, 3}
        app._focus_editor_zone('output')
        assert not app._right_quick_output.winfo_manager()
        app.var_edit_mode.set('easy')
        app._apply_edit_mode(log=False)
        assert app._right_quick_output.winfo_manager() == 'pack'
        assert app.var_fps_ui.get() == '144 FPS'
        assert app.checked_kills == {1, 3}
        assert app.canvas.winfo_manager() == 'pack'
        app.var_edit_mode.set('advanced')
        app._apply_edit_mode(log=False)
        assert not app._right_quick_output.winfo_manager()
        app._focus_editor_zone('camera')
        assert app._right_quick_output.winfo_manager() == 'pack'
    finally:
        root.destroy()
