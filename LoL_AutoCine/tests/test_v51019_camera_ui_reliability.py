# -*- coding: utf-8 -*-
"""v5.10.19: RED axis, retained BLUE geometry, template/QA output regression."""
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from core.camera import CameraPlan, RigInfo
from core.effects import Template, one_click_templates
from core.qa_reels import assemble_side_reels


def _rig(*, pitch_axis="x"):
    return RigInfo(mode="fps",third=True,rot={"x":42.0,"y":56.0,"z":0.0},
                   pitch_axis=pitch_axis,pitch_sign=1.0,pitch_complement=False,
                   h=(-0.52,-0.854166),v=(-940,1890,-2220))


@pytest.mark.parametrize("side,yaw,expected_x", [
    ("CHAOS",184.0,-184.0),("ORDER",-12.0,12.0)])
def test_normal_third_uses_horizontal_x_pitch_y_and_never_roll(side,yaw,expected_x):
    plan=CameraPlan(style="third",rig=_rig(),third_elev=42,third_dist=1170,
                    side_yaw=yaw,team=side)
    plan._camera_axis_safety=True
    rot=plan.rotation_at(2.0)
    assert rot["x"]==pytest.approx(expected_x)
    assert rot["y"]==pytest.approx(42.0)
    assert rot["z"]==0.0


def test_red_geo_aim_uses_calibrated_pitch_axis_not_yaw_in_y_slot():
    plan=CameraPlan(style="geo_aim",rig=_rig(pitch_axis="y"),
                    third_elev=42,third_dist=1170,side_yaw=192,team="CHAOS")
    plan._camera_axis_safety=True
    rot=plan.rotation_at(1.0)
    assert rot["x"]==pytest.approx(-192.0)
    assert rot["y"]==pytest.approx(42.0)
    assert rot["z"]==0.0


def test_blue_geo_aim_keeps_previous_formula():
    plan=CameraPlan(style="geo_aim",rig=_rig(pitch_axis="y"),
                    third_elev=37,third_dist=1060,side_yaw=-12,team="ORDER")
    offset,elev=plan.third_pose_at(1.0)
    import math
    x,y,z=offset
    old={"x":math.degrees(math.atan2(y,math.hypot(x,z))),
         "y":math.degrees(math.atan2(-x,-z))%360.0,
         "z":0.0}
    assert plan.rotation_at(1.0)==old


def test_red_cinematic_no_longer_zooms_in_too_close():
    rig=_rig(pitch_axis="y")
    for style in ("third_cinema","lolnam_cinema"):
        plan=CameraPlan(style=style,rig=rig,third_elev=42,third_dist=1170,
                        side_yaw=192,team="CHAOS",kill_time=5.0,
                        kill_times=(5.0,),intensity=1.0)
        offset,_=plan.third_pose_at(5.0)
        import math
        assert math.sqrt(sum(v*v for v in offset)) >= 1170*.89


def test_no_unrequested_color_filter_or_dark_corners_on_first_launch():
    plain=Template()
    assert plain.grade=="default"
    assert plain.vignette==0
    assert plain.grain==0
    assert plain.bloom==0
    assert plain.transition=="cut"
    presets=one_click_templates()
    assert list(presets)[0]=="デフォルト（無加工カラー）"
    assert presets["デフォルト（無加工カラー）"].vignette==0
    assert presets["ゴールド・フィニッシュ"].grade != presets["アイスブルー・シネマ"].grade


def test_side_review_videos_use_only_their_own_side(monkeypatch,tmp_path):
    rows=[]
    for side in ("RED","BLUE"):
        for j in range(2):
            file=tmp_path/side/f"{j}.mp4"
            file.parent.mkdir(parents=True,exist_ok=True)
            file.write_bytes(b"data")
            rows.append({"side":side,"outputs":[str(file)]})
    observed={}
    def concat(inputs,target):
        observed[target.parent.name]=[str(x) for x in inputs]
        target.write_bytes(b"review")
    result=assemble_side_reels(tmp_path,rows,concatenate=concat)
    assert len(result["RED"]["outputs"])==len(result["BLUE"]["outputs"])==1
    assert all("RED" in Path(p).parts for p in observed["RED"])
    assert all("BLUE" in Path(p).parts for p in observed["BLUE"])


def test_editors_share_preset_choice_and_easy_color_is_opt_in():
    import tkinter as tk
    from legacy_app import App
    root=tk.Tk()
    try:
        app=App(root)
        root.update_idletasks()
        assert app.tpl_combo.master is app._nav_template_card
        assert app._nav_template_card.winfo_parent()==str(app._mode_easy_section)
        assert app.advanced_tpl_combo.get()==app.tpl_combo.get()
        assert not app._easy_color_panel.winfo_manager()
        app.var_easy_color_custom.set(True)
        app._update_easy_color_controls()
        assert app._easy_color_panel.winfo_manager()
        app.var_easy_color_custom.set(False)
        app._update_easy_color_controls()
        assert not app._easy_color_panel.winfo_manager()
    finally:
        root.destroy()
