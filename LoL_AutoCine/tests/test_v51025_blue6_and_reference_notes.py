# -*- coding: utf-8 -*-
"""v5.10.25: single-camera framing guard and honest xMedia study metadata."""
import json
from pathlib import Path
import pytest

from core.camera import CameraPlan, RigInfo
from core.camera_tuning import shot_tuning
from core.effects import VIDEO_EFFECT_LABELS


def test_blue6_tilt_moves_subject_down_without_changing_camera_position():
    rig=RigInfo(mode="fps",third=True,h=(-0.52,-0.854166),
                v=(-7173.99,1860.48,4104.70),
                rot={"x":0.0,"y":37.0,"z":0.0},
                pitch_axis="x",pitch_sign=1.0)
    plan=CameraPlan(style="third",team="ORDER",rig=rig,
                    third_dist=950.0,third_elev=37.0,side_yaw=-12.0,
                    kill_time=750.24756)
    plan._live_blue_geo_look=True
    plan._live_blue_pulled_back=True
    plan._camera_axis_safety=True
    plan._live_dist_factor=shot_tuning("ORDER","third")["distance"]
    raw_positions=[plan.offset_at(t) for t in (747.25,750.25,753.25)]
    old_v51024_bias=3.0
    bias=shot_tuning("ORDER","third")["angles"]["x"]
    assert bias == -2.0
    for t in (747.25,750.25,753.25):
        raw=plan._live_geo_look(t)
        rot=plan.rotation_at(t) if hasattr(plan,"_live_angle_bias") else None
        plan._live_angle_bias=dict(shot_tuning("ORDER","third")["angles"])
        rot=plan.rotation_at(t)
        assert rot["x"]==pytest.approx(raw["x"]-2.0)
        assert rot["x"]==pytest.approx((raw["x"]+old_v51024_bias)-5.0)
        assert rot["y"]==raw["y"]
        assert rot["z"]==0.0
        assert 14.0<=rot["x"]<=70.0
    assert raw_positions==[plan.offset_at(t) for t in (747.25,750.25,753.25)]


def test_other_nine_camera_configurations_are_unchanged():
    expected={
      ("RED","third"):(1.13,{},1.0),
      ("RED","third_cinema"):(0.96,{},1.0),
      ("RED","fps"):(1.0,{},1.60),
      ("RED","lolnam_cinema"):(1.0,{"x":-3.0,"y":-3.0},1.0),
      ("RED","geo_aim"):(1.12,{"x":-4.0},1.0),
      ("BLUE","third_cinema"):(1.08,{},1.0),
      ("BLUE","fps"):(1.0,{},1.38),
      ("BLUE","lolnam_cinema"):(1.08,{"x":2.5},1.0),
      ("BLUE","geo_aim"):(1.08,{"x":2.5},1.0),
    }
    for (team,mode),(distance,angles,fps_back) in expected.items():
        actual=shot_tuning(team,mode)
        assert actual["distance"]==distance, (team,mode)
        assert actual["angles"]==angles, (team,mode)
        assert actual["fps_back"]==fps_back, (team,mode)
    assert shot_tuning("BLUE","third")["distance"]==1.10


def test_reference_catalog_is_opt_in_and_supported_labels():
    root=Path(__file__).resolve().parents[1]
    catalog=json.loads((root/"qa"/"xmedia_reference_notes_v51025.json").read_text(encoding="utf-8"))
    assert len(catalog["samples"])==4
    ids={sample["id"] for sample in catalog["samples"]}
    assert ids=={"aegis_lee_sin","ahri_vs_fizz","yasuo_1vs4","samira_combat"}
    assert catalog["policy"]["auto_apply_to_qa"] is False
    assert catalog["policy"]["apply_to_normal_template"] is False
    assert catalog["policy"]["disallow_forced_vignette"] is True
    for sample in catalog["samples"]:
        preset=sample["suggested_preview"]
        assert preset.get("vignette",0)==0
        assert preset.get("bars",0)==0
        for effect,amount in preset.get("video_effects",{}).items():
            assert effect in VIDEO_EFFECT_LABELS, effect
            assert 0<=amount<=1
    mono=next(s for s in catalog["samples"] if s["id"]=="ahri_vs_fizz")
    assert "部分カラー" in " ".join(mono["unimplemented_parts"])
