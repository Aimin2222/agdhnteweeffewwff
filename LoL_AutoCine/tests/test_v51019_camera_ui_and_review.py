# -*- coding: utf-8 -*-
"""Regression for repeat-cameras, template placement, color opt-in, QA review."""
from pathlib import Path
import math
import tkinter as tk
from types import SimpleNamespace
import pytest

from core.camera import CameraPlan, RigInfo, attach_to_player
from core.players import Player


class FakeRender:
    """Replay /render with deliberately stale top position to mirror RED QA 1."""
    def __init__(self):
        self.attrs={"cameraMode":"top","selectionOffset":{"x":0,"y":0,"z":0}}
        self.P=(7298.0,19.6,8116.0)

    def set_render(self, **attrs):
        self.attrs.update(attrs)

    def render(self):
        mode=self.attrs.get("cameraMode")
        if mode=="top":
            return {"cameraPosition":{"x":13243.0,"y":1911.8,"z":11945.0},
                    "cameraRotation":{"x":42.0,"y":56.0,"z":0.0}}
        off=self.attrs.get("selectionOffset") or {}
        return {"cameraPosition":{"x":self.P[0]+float(off.get("x",0)),
                                  "y":self.P[1]+float(off.get("y",0)),
                                  "z":self.P[2]+float(off.get("z",0))},
                "cameraRotation":self.attrs.get("cameraRotation",{})}


def test_red_normal_third_rejects_unreliable_pitch_x_and_stale_heading(monkeypatch):
    import core.camera as camera
    monkeypatch.setattr(camera.time,"sleep",lambda _s:None)
    camera._TPS_CALIBRATION.clear()
    p=Player(5,"Red","Red#JP","Red","Vi","CHAOS")
    rig=attach_to_player(FakeRender(),p,"third",third_elev=42,third_dist=1170,settle=0)
    assert rig.third
    assert rig.pitch_axis == "y"
    assert rig.rot["z"] == 0
    assert math.isclose(rig.h[0],-.5,abs_tol=.01)
    assert math.isclose(rig.h[1],-.866,abs_tol=.01)
    camera._TPS_CALIBRATION.clear()


def test_red_geo_aim_uses_correct_pitched_axis_and_preserves_blue_baseline():
    rig=RigInfo(mode="fps",third=True,rot={"x":0,"y":48,"z":0},
                pitch_axis="y",h=(-.5,-.866),pitch_sign=1)
    red=CameraPlan(style="geo_aim",team="CHAOS",rig=rig,
                   third_dist=1170,third_elev=42,side_yaw=192)
    r=red.rotation_at(100)
    assert r["x"] == -192
    assert 10<=r["y"]<=80
    assert r["z"] == 0
    blue=CameraPlan(style="geo_aim",team="ORDER",rig=rig,
                    third_dist=1060,third_elev=37,side_yaw=-12)
    assert blue.rotation_at(100)!=r


def test_red_cinema_zoom_limited_but_blue_keeps_existing_cinematic_range():
    rig=RigInfo(mode="fps",third=True,rot={"x":0,"y":48,"z":0},
                pitch_axis="y",h=(-.5,-.866),pitch_sign=1)
    red=CameraPlan(style="third_cinema",team="CHAOS",rig=rig,
                   kill_time=100,third_dist=1170,third_elev=42)
    blue=CameraPlan(style="third_cinema",team="ORDER",rig=rig,
                    kill_time=100,third_dist=1170,third_elev=42)
    red_off,elev=red.third_pose_at(100)
    blue_off,_=blue.third_pose_at(100)
    red_len=math.sqrt(sum(x*x for x in red_off))
    blue_len=math.sqrt(sum(x*x for x in blue_off))
    assert red_len >= 1170*.94-2
    assert red_len > blue_len
    assert elev >=34


def test_template_inside_center_editor_in_both_modes_and_ab_preserved():
    from legacy_app import App
    root=tk.Tk()
    try:
        app=App(root)
        frame=app._nav_template_card
        assert str(frame.master).startswith(str(app.center_edit_scroll))
        assert app.tpl_combo.winfo_exists()
        assert app._template_tone_canvas.winfo_exists()
        assert app._inline_color_cards.winfo_exists()
        app.var_edit_mode.set("advanced")
        app._apply_edit_mode(log=False)
        assert frame.winfo_manager()=="pack"
        app.var_edit_mode.set("easy")
        app._apply_edit_mode(log=False)
        assert frame.winfo_manager()=="pack"
    finally:
        root.destroy()


def test_easy_color_opt_in_shows_the_same_real_sliders():
    from legacy_app import App
    root=tk.Tk()
    try:
        app=App(root)
        assert not app._easy_color_panel.winfo_manager()
        app.var_easy_color_custom.set(True)
        app._update_easy_color_panel()
        assert app._easy_color_panel.winfo_manager()=="pack"
        app.var_easy_color_custom.set(False)
        app._update_easy_color_panel()
        assert not app._easy_color_panel.winfo_manager()
        assert float(app.sl["vignette"].get()) == 0.0
        assert float(app.sl["grain"].get()) == 0.0
    finally:
        root.destroy()


def test_visual_qa_uses_multiple_moments_not_one(monkeypatch,tmp_path):
    from core import qa_visual
    from PIL import Image
    seen=[]
    def fake_frame(path,t,**kwargs):
        seen.append(t)
        return Image.new("RGB",(320,180),(40,50,60))
    monkeypatch.setattr(qa_visual,"frame_at",fake_frame)
    q=qa_visual.make_qa_contact_sheets(
        tmp_path,[{"number":1,"side":"RED","mode":"third","outputs":["fake.mp4"]}],[])
    assert seen==[1.0,3.0,5.0]
    assert q["camera"][0]["sample_times_s"]==[1.0,3.0,5.0]
    assert Path(q["images"][0]).exists()
