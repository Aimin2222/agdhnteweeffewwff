# -*- coding: utf-8 -*-
"""v5.10.15 regression checks: UI layout, checkbox glyph, DOF and RED-only camera."""
import tkinter as tk
from pathlib import Path
import pytest

from core.camera import CameraPlan, RigInfo
from core.effects import GRADE_JP
from core.kill_icons import STYLES


def test_descriptive_grades_and_skin_labels_keep_original_ids():
    assert set(("default","film","neon","golden","tealorange")).issubset(GRADE_JP)
    assert len(GRADE_JP)==len(set(GRADE_JP.values()))
    assert "青緑" in GRADE_JP["tealorange"]
    assert "K/DA風" in STYLES["kda_style"]
    assert "PROJECT風" in STYLES["project_style"]
    assert "スターガーディアン" in STYLES["star_guardian"]
    assert len([k for k in STYLES if k.startswith("user_frame_")])==16


def test_fps_red_offset_differs_but_blue_and_lolnam_are_unchanged():
    rig=RigInfo(mode="fps",third=False,v=(300,1600,100),h=(.95,-.3),rot={"x":0,"y":0,"z":0})
    blue=CameraPlan(style="fps",rig=rig,dist_scale=.8,target_team="ORDER")
    red=CameraPlan(style="fps",rig=rig,dist_scale=.8,target_team="CHAOS")
    assert blue.offset_at(0)==(240,1280,80)
    assert red.offset_at(0)!=blue.offset_at(0)
    assert red.offset_at(0)[1]<blue.offset_at(0)[1]
    assert CameraPlan(style="lolnam_cinema",rig=rig,target_team="CHAOS").offset_at(0)==CameraPlan(style="lolnam_cinema",rig=rig).offset_at(0)


def test_single_layer_editor_and_dof_controls(tmp_path):
    import legacy_app
    root=tk.Tk()
    root.geometry("1400x900")
    app=legacy_app.App(root)
    try:
        root.update_idletasks()
        app.var_edit_mode.set("advanced")
        app._apply_edit_mode()
        assert app._editor_advanced_tabs is None
        for zone in ("scene","camera","color","fx","output"):
            app._focus_editor_zone(zone)
            root.update_idletasks()
            if zone in ("scene","color","fx","output"):
                name="basic" if zone=="scene" else zone
                assert app._editor_advanced_pages[name].winfo_manager()=="pack"
        app._focus_editor_zone("fx")
        app.var_dof.set(True)
        root.update_idletasks()
        assert app._dof_controls.winfo_manager()=="pack"
        assert "詳細を表示中" in app._dof_toggle_widget.cget("text")
        app.var_dof.set(False)
        root.update_idletasks()
        assert not app._dof_controls.winfo_manager()
        layout=str(legacy_app.ttk.Style(root).layout("TCheckbutton"))
        assert "AutoCine.Checkmark" in layout
        assert app.var_preview_quality.get() in ("操作優先","表示サイズで確認")
    finally:
        root.destroy()


def test_ui_has_contextual_helps_and_big_preset_preview():
    source=(Path(__file__).resolve().parents[1]/"legacy_app.py").read_text(encoding="utf-8")
    assert "def _open_large_preset_preview" in source
    assert "動画のつなぎ目" in source
    assert "def _any_dropdown_open" in source
    assert "if self.left_scroll._any_dropdown_open():" in source
    assert "def _update_selected_killer_portrait" in source
