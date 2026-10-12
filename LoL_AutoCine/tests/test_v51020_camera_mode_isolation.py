# -*- coding: utf-8 -*-
"""Mode-specific Windows visual QA fixes must not change approved camera modes."""
from dataclasses import fields
from pathlib import Path
import inspect
import math
import pytest

from core.camera import CameraPlan, RigInfo, attach_to_player
from core.qa_plan import load_qa_plan,validate_plan


def good_rig(h=(-0.21,-0.978)):
    return RigInfo(mode="fps",third=True,h=h,
                   rot={"x":0.0,"y":53.0,"z":0.0},
                   pitch_axis="y",pitch_sign=1.0,pitch_complement=True)


def test_camera_dataclass_abi_preserved_and_cache_isolated_by_mode():
    assert fields(CameraPlan)[-1].name=="team"
    src=inspect.getsource(attach_to_player)
    assert 'cache_key = (sel, str(p.team).upper(), style)' in src
    assert 'third_common' not in src.split("cache_key =",1)[1].split("cached =",1)[0]


def test_blue_cinema_uses_approved_geo_aim_rotation_only_when_live_opt_in():
    rig=good_rig()
    cinema=CameraPlan(style="third_cinema",rig=rig,team="ORDER",
                      third_dist=1060,third_elev=37,side_yaw=-12,kill_time=30)
    reference=CameraPlan(style="geo_aim",rig=rig,team="ORDER",
                         third_dist=1060,third_elev=37,side_yaw=-12,kill_time=30)
    normal=cinema.rotation_at(30)
    cinema._live_blue_geo_look=True
    # Actual frame orientation now uses the same geometric convention as
    # visually good BLUE geo #10, but camera position/zoom remain independent.
    live=cinema.rotation_at(30)
    assert live["z"]==0
    assert math.isfinite(live["x"]) and math.isfinite(live["y"])
    assert live!=normal
    assert reference.rotation_at(30)["z"]==0


def test_blue_normal_third_pull_back_is_opt_in():
    plan=CameraPlan(style="third",rig=good_rig(),team="ORDER",
                    third_dist=1060,third_elev=37,side_yaw=-12)
    before=plan.offset_at(0.0)
    plan._live_blue_pulled_back=True
    after=plan.offset_at(0.0)
    assert math.dist((0,0,0),after)>math.dist((0,0,0),before)*1.19


def test_approved_blue_geo_aim_unchanged_by_new_flags():
    p=CameraPlan(style="geo_aim",rig=good_rig(),team="ORDER",
                 third_dist=1060,third_elev=37,side_yaw=-12)
    result=p.rotation_at(20)
    p._live_blue_geo_look=True
    p._live_blue_pulled_back=True
    p._live_fps_recenter=True
    assert p.rotation_at(20)==result


def test_approved_red_cinema_unchanged_by_blue_opt_in():
    p=CameraPlan(style="third_cinema",rig=good_rig(),team="CHAOS",
                 third_dist=1170,third_elev=42,side_yaw=192,kill_time=20)
    result=p.rotation_at(20)
    p._live_blue_geo_look=True
    assert p.rotation_at(20)==result


def test_fps_live_recenter_has_orientation_but_old_direct_plan_is_compatible():
    rig=RigInfo(mode="fps",third=False,v=(-700.,1900.,-2800.))
    p=CameraPlan(style="fps",rig=rig,team="ORDER")
    assert p.rotation_at(1) is None
    before=p.offset_at(1)
    p._live_fps_recenter=True
    assert p.rotation_at(1) is not None
    assert math.dist((0,0,0),p.offset_at(1)) < math.dist((0,0,0),before)


def test_curated_qa_has_one_flash_and_real_spatial_distinctions():
    plan,source=load_qa_plan(allow_remote=False)
    assert set(plan["montage_styles"])=={"cut","flash","dark"}
    assert len(plan["spatial_transition_previews"])==6
    assert "wipeleft" in plan["spatial_transition_previews"]
    assert "slideright" in plan["spatial_transition_previews"]


def test_simple_color_toggle_expands_adjacent_to_checkbox():
    import tkinter as tk
    from legacy_app import App
    root=tk.Tk()
    try:
        app=App(root)
        app.var_easy_color_custom.set(True)
        app._update_easy_color_controls()
        root.update_idletasks()
        panel=app._easy_color_panel
        assert panel.winfo_manager()=="pack"
        assert str(panel.pack_info()["after"])==str(app._easy_color_toggle)
        app.var_easy_color_custom.set(False)
        app._update_easy_color_controls()
        assert not panel.winfo_manager()
    finally:
        root.destroy()
