"""UI-owned v5.10.0 wheel, navigation, selection and settings checks."""
from types import SimpleNamespace
import tkinter as tk
from tkinter import ttk
import pytest

@pytest.fixture
def gui(tmp_path,monkeypatch):
    from legacy_app import App
    import legacy_app
    monkeypatch.setattr(legacy_app,'SETTINGS',tmp_path/'settings.json')
    root=tk.Tk()
    root.geometry('1450x900')
    app=App(root)
    root.update()
    yield app,root
    root.destroy()


def test_nav_opens_real_workspaces(gui):
    a,r=gui
    a._focus_settings()
    assert a.var_edit_mode.get()=='advanced'
    assert a.var_editor_zone.get()=='output'
    a._focus_reference()
    assert a._nav_reference_card.winfo_manager()=='pack'
    a._focus_template()
    assert a._nav_template_card.winfo_manager()=='pack'


def test_wheel_on_detection_combo_never_changes_value(gui):
    a,r=gui
    combos=[]
    def visit(p):
        for widget in p.winfo_children():
            if isinstance(widget,ttk.Combobox) and widget.cget('textvariable')==str(a.var_event_mode):
                combos.append(widget)
            visit(widget)
    visit(r)
    assert len(combos)==1
    widget=combos[0]
    a.var_event_mode.set('キル')
    widget.event_generate('<MouseWheel>',delta=-120)
    r.update()
    assert a.var_event_mode.get()=='キル'
    assert widget.bind('<MouseWheel>')


def test_click_on_bracket_toggles_scene_not_other_columns(gui):
    a,r=gui
    a.kills=[SimpleNamespace(event_id=1,time=23.5,killer='A',victim='B',multikill=1,role='kill')]
    a.checked_kills=set()
    a._fill_kills()
    r.update()
    bbox=a.lb_kills.bbox(0)
    assert bbox
    a.on_scene_selection=lambda:None
    e=SimpleNamespace(x=10,y=bbox[1]+bbox[3]//2)
    assert a._on_kill_list_click(e)=='break'
    assert 0 in a.checked_kills
    assert a._on_kill_list_click(e)=='break'
    assert not a.checked_kills
    assert a._on_kill_list_click(SimpleNamespace(x=90,y=e.y)) is None
    assert not a.checked_kills


def test_global_visual_settings_save_and_reload(gui):
    a,r=gui
    a.var_kill_icon_style.set('シネマ・ゴールド')
    a.var_kill_frame_color.set('#AABBCC')
    a.var_kill_glow_color.set('#2255AA')
    a.var_kill_glow_enabled.set(False)
    a.var_kill_glow_strength.set(.3)
    a.var_kill_frame_width.set(5)
    a.var_kill_mark_style.set('交差する剣')
    a.var_encoder_policy.set('CPU優先（libx264）')
    t=a.current_template()
    assert (t.kill_frame_color,t.kill_glow_color,t.kill_glow_enabled,t.kill_mark_style,t.encoder_policy)==('#AABBCC','#2255AA',False,'swords','cpu')
    a._save_settings()
    a.var_kill_frame_color.set('')
    a.var_kill_glow_enabled.set(True)
    a.var_encoder_policy.set('自動（NVENC優先・失敗時CPU）')
    a._load_settings()
    assert a.var_kill_frame_color.get()=='#AABBCC'
    assert a.var_kill_glow_enabled.get() is False
    assert a.var_encoder_policy.get()=='CPU優先（libx264）'
