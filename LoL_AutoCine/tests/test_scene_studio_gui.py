# -*- coding: utf-8 -*-
"""GUI contract: run `xvfb-run -a python -m pytest tests/test_scene_studio_gui.py`."""
import tkinter as tk
from core.scanner import Kill
from core.players import Player
from ui.motion_graph import sample_motion
from ui.scene_project import Shot, scene_key
from legacy_app import App


def test_camera_curve_is_computed():
    values=sample_motion(Shot(profile='dynamic',arc=22,dolly=8),samples=31)
    assert len(values)==31
    assert min(v[2] for v in values) < max(v[2] for v in values)
    assert min(v[1] for v in values) < max(v[1] for v in values)


def test_saved_scene_dispatch(monkeypatch,tmp_path):
    root=tk.Tk()
    try:
        app=App(root)
        app.scene_project_path=tmp_path/'project.json'
        app.locked=Player(1,'Aimin','Aimin#1','Aimin','Lee Sin','ORDER')
        app.kills=[Kill(111,100,'Aimin','E1',[]),Kill(222,200,'Aimin','E2',[],multikill=3)]
        app.checked_kills={0,1}
        app._fill_kills()
        app.lb_kills.selection_set(0)
        app.on_scene_selection()
        app.scene_vars['arc'].set(44)
        app.var_shot_profile.set('dynamic')
        app.on_save_scene()
        key=scene_key(app.kills[0])
        assert app.scene_project.shots[key].arc==44
        assert app.var_scene_mode.get() is True
        assert '✎' in app.lb_kills.get(0)
        app.on_scene_undo()
        assert key not in app.scene_project.shots
        app.on_scene_redo()
        assert app.scene_project.shots[key].arc==44
        app._autosave_project()
        assert app.scene_project_path.exists()
        captured=[]
        app._run_bg=lambda fn,*args:captured.append((fn,args))
        app._need_lock=lambda:True
        app.on_make_checked()
        assert captured and captured[-1][0].__name__=='_make_list'
        args=captured[-1][1]
        assert args[3] is True and args[4][key]['arc']==44
        app.on_smart_one_click()
        assert captured[-1][0].__name__=='_make'
        assert captured[-1][1][-4] is True
    finally:
        root.destroy()
