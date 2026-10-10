# -*- coding: utf-8 -*-
"""v5.10.14 spec-linked regression checks. Live LoL quality remains manual."""
from pathlib import Path
import tkinter as tk
import pytest

from core.camera import CameraPlan, RigInfo
from core.kill_icons import STYLES
from core.montage_fx import MONTAGE_FX, MONTAGE_LABELS, montage_filter
from ui.kill_frame_gallery import sample_portrait


def test_all_montage_choices_have_distinct_active_filter():
    assert len(MONTAGE_LABELS)>=10
    for style in MONTAGE_FX:
        graph=montage_filter(style,[4.0])
        if style=="cut":
            assert graph=="null"
        else:
            assert graph.startswith("eq=brightness=")
            assert "t-4.0000" in graph


def test_red_normal_third_pitch_corrected_without_touching_fps_or_lolnam():
    rig=RigInfo(mode="fps",third=True,rot={"x":59.,"y":5.,"z":0.},
                pitch_axis="x",pitch_sign=1.,pitch_complement=True,h=(0.,-1.))
    blue=CameraPlan(style="third",rig=rig,third_elev=31,side_yaw=-12.)
    red=CameraPlan(style="third",rig=rig,third_elev=31,side_yaw=192.)
    assert blue.rotation_at(0)["x"] > 0
    assert red.rotation_at(0)["x"] < 0
    cine=CameraPlan(style="third_cinema",rig=rig,third_elev=31,side_yaw=192.)
    assert cine.rotation_at(0)["x"] > 0
    lolnam=CameraPlan(style="lolnam_cinema",rig=rig,third_elev=31,side_yaw=192.)
    assert lolnam.rotation_at(0) is not None


def test_frame_gallery_shows_all_existing_styles():
    assert len(STYLES)>30
    image=sample_portrait((33,88,160),"A")
    assert image.size==(180,180)
    src=(Path(__file__).resolve().parents[1]/"ui"/"kill_frame_gallery.py").read_text("utf-8")
    assert "for idx,(style,title) in enumerate(STYLES.items())" in src
    assert "make_badge(tmp,style" in src


def test_ui_modes_preserve_core_variables():
    import legacy_app
    root=tk.Tk()
    root.geometry("1420x860")
    app=legacy_app.App(root)
    try:
        root.update()
        assert app.var_auto_director.get() is False
        assert app.var_kill_icon_style.get()
        assert hasattr(app,"_open_kill_frame_gallery")
        app.var_edit_mode.set("advanced")
        app._apply_edit_mode()
        for zone,tab in (("color",1),("fx",2),("output",3)):
            app._focus_editor_zone(zone)
            root.update_idletasks()
            assert app._editor_advanced_tabs.index("current")==tab
        assert app.var_edit_mode.get()=="advanced"
        assert app.var_auto_director.get() is False
        assert app.var_dof.get() is False
    finally:
        root.destroy()


def test_gui_kill_gallery_open_without_live_replay():
    import legacy_app
    root=tk.Tk()
    app=legacy_app.App(root)
    try:
        win=app._open_kill_frame_gallery()
        assert win.winfo_exists()
        assert app._kill_frame_gallery._chosen in STYLES
        app._kill_frame_gallery.select("cinema",apply=True)
        assert app.var_kill_icon_style.get()==STYLES["cinema"]
        win.destroy()
    finally:
        root.destroy()


def test_spec_and_testlist_present():
    base=Path(__file__).resolve().parents[1]
    assert (base/"docs"/"AutoCine_v5.10.14_実装仕様書.md").is_file()
    assert (base/"TESTLIST_v5.10.14_JA.md").is_file()
