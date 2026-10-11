# -*- coding: utf-8 -*-
"""v5.10.15 contracts. Windows RED replay visual quality is manual acceptance."""
from pathlib import Path
from types import SimpleNamespace
import tkinter as tk
from core.camera import CameraPlan, RigInfo
from core.kill_icons import STYLES, ASSET_STYLES
from core.effects import GRADE_JP
import legacy_app
import pytest


@pytest.fixture(autouse=True)
def isolate_settings(tmp_path, monkeypatch):
    monkeypatch.setattr(legacy_app, "SETTINGS", tmp_path/"settings.json")

def build():
    root=tk.Tk()
    root.geometry('1510x930')
    app=legacy_app.App(root)
    root.bind('<Destroy>',lambda event: app._live_preview.close() if event.widget is root else None,add='+')
    root.update()
    return root,app


def test_workspace_pages_no_secondary_notebook():
    root,app=build()
    try:
        app.var_edit_mode.set('advanced')
        app._apply_edit_mode(log=False)
        for zone in ('scene','camera','color','fx','output'):
            app.var_editor_zone.set(zone)
            app._apply_editor_zone()
            root.update_idletasks()
            if zone in app._editor_advanced_pages:
                assert app._editor_advanced_pages[zone].winfo_manager() == 'pack'
                assert all(not p.winfo_manager() for k,p in app._editor_advanced_pages.items() if k!=zone)
        assert app._editor_advanced_tabs is None
    finally:
        root.destroy()


def test_dof_switch_shows_settings_and_does_not_reset_values():
    root,app=build()
    try:
        app._focus_editor_zone('fx')
        app.sl['dof_blur'].set(5.5)
        app.var_dof.set(True)
        root.update_idletasks()
        assert app._dof_controls.winfo_manager()=='pack'
        app.var_dof.set(False)
        root.update_idletasks()
        assert not app._dof_controls.winfo_manager()
        assert app.sl['dof_blur'].get()==5.5
    finally:
        root.destroy()


def test_expanded_combobox_does_not_scroll_background():
    root,app=build()
    try:
        cb=app.cb_scene_player_filter
        cb.configure(values=[f'player_{i}' for i in range(35)])
        root.update()
        root.tk.call('ttk::combobox::Post',str(cb))
        root.update()
        assert root._autocine_combobox_popup_open()
        panel=app.right_scroll
        prev=panel.canvas.yview()
        event=SimpleNamespace(widget=cb,x_root=panel.winfo_rootx()+30,
                              y_root=panel.winfo_rooty()+65,delta=-120,num=None)
        assert panel._global_wheel(event)=='break'
        assert panel.canvas.yview()==prev
        root.tk.call('ttk::combobox::Unpost',str(cb))
        root.update()
        assert not root._autocine_combobox_popup_open()
    finally:
        root.destroy()


def test_check_indicator_replaces_unclear_cross():
    root,app=build()
    try:
        assert hasattr(root,'_autocine_check_images')
        from tkinter import ttk
        assert 'AutoCine.Check' in ttk.Style(root).element_names()
    finally:
        root.destroy()


def test_kill_frame_styles_are_named_and_complete():
    assert len(ASSET_STYLES)==37
    assert len(STYLES)==42
    root=Path(__file__).resolve().parents[1]
    assert all((root/'assets'/'kill_badges'/file).exists() for file in ASSET_STYLES.values())
    assert all(not STYLES[f'user_frame_{i:02d}'].startswith('追加素材') for i in range(1,17))
    assert 'K/DA' in STYLES['user_frame_08']
    assert '桜' in STYLES['user_frame_13']


def test_grade_labels_explain_colors():
    assert '青緑' in GRADE_JP['tealorange']
    assert 'ゴールド' in GRADE_JP['golden']
    assert '自然' in GRADE_JP['standard']
    assert len(set(GRADE_JP.values()))==len(GRADE_JP)


def test_red_fps_camera_moves_closer_blue_unchanged():
    rig=RigInfo(mode='fps',third=False,v=(240.,1200.,-400.))
    b=CameraPlan(style='fps',rig=rig,dist_scale=.8,height=40,team='ORDER')
    r=CameraPlan(style='fps',rig=rig,dist_scale=.8,height=40,team='CHAOS')
    bo,ro=b.offset_at(0),r.offset_at(0)
    assert abs(ro[0])<abs(bo[0])
    assert abs(ro[2])<abs(bo[2])
    assert ro[1]<bo[1]
    assert b.offset_at(0)==(192.,1000.,-320.)
