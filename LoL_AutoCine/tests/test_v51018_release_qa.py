# -*- coding: utf-8 -*-
"""v5.10.18: direct ZIP, optional test plan, geometry and comparison sheets."""
from pathlib import Path
from zipfile import ZipFile
from PIL import Image
import json
import pytest

from core.qa_package import split_test_results
from core.qa_plan import validate_plan, load_qa_plan
from core.camera_geometry import inspect_rig, target_direction
from core.camera import CameraPlan, RigInfo
from core.camera_qa import plan_eight_cases
from core.players import Player
from core.effects import Template


def test_default_color_is_unmodified_and_templates_can_override():
    assert Template().grade == "default"


def test_latest_qa_plan_is_allowlisted_and_geometric_camera_is_opt_in():
    plan, source=load_qa_plan(allow_remote=False)
    assert source=="bundled"
    assert "geo_aim" in plan["camera_modes"]
    assert plan["max_zip_mb"]==500
    with pytest.raises(ValueError):
        validate_plan(dict(plan, camera_modes=["execute_shell_command"]))
    with pytest.raises(ValueError):
        validate_plan(dict(plan, max_zip_mb=1000))


def test_archive_is_direct_and_bounded(tmp_path):
    sub=tmp_path/"CameraQA_Test"
    sub.mkdir()
    (sub/"results.json").write_text('{"ok":true}',encoding="utf-8")
    (sub/"output.mp4").write_bytes(b"video-data"*10000)
    (sub/"camera_comparison.jpg").write_bytes(b"picture")
    out=split_test_results(sub,max_bytes=2_000_000)
    assert len(out)==1 and out[0].suffix==".zip"
    assert out[0].stat().st_size<2_000_000
    with ZipFile(out[0]) as z:
        assert z.testzip() is None
        names=z.namelist()
        assert "output.mp4" in names and "results.json" in names
        assert "camera_comparison.jpg" in names
        assert not any(n.endswith(".zip") for n in names)


def test_geometry_flags_actual_red_fallback_and_blue_stale_baseline():
    red = dict(style="third", third_person_enabled=False,
               baseline_offset=None,pitch_axis="",initial_camera_rotation=None)
    issues=inspect_rig(red)
    assert "third_person_fell_back_to_top_or_fps" in issues["flags"]
    blue=dict(style="third",third_person_enabled=True,
              baseline_offset=[6478,1729,7192],pitch_axis="x",
              initial_camera_rotation={"x":37,"y":56,"z":12})
    issues=inspect_rig(blue)
    assert "baseline_camera_far_from_target_possible_stale_read" in issues["flags"]
    vec=target_direction((5,2,2),(0,2,2))
    assert vec==(-1.0,0.0,0.0)


def test_geo_aim_is_computed_from_relative_target_position():
    rig=RigInfo(mode="fps",third=True,rot={"x":37,"y":56,"z":0},
                pitch_axis="x",h=(1,0),pitch_sign=1)
    plan=CameraPlan(style="geo_aim",rig=rig,third_elev=37,third_dist=1060,side_yaw=0)
    rot=plan.rotation_at(0.0)
    assert rot is not None and set(rot)=={"x","y","z"}
    assert 0 <= rot["y"] < 360 and 5 < rot["x"] < 80
    assert rot["z"]==0


def test_optional_geometric_qa_adds_one_clip_per_team():
    blue=Player(0,"Blue","Blue#JP","Blue","Ahri","ORDER")
    red=Player(5,"Red","Red#JP","Red","LeeSin","CHAOS")
    events=[dict(event_id=1,time=30,killer="Blue",victim="Red",assisters=[]),
            dict(event_id=2,time=40,killer="Red",victim="Blue",assisters=[])]
    assert len(plan_eight_cases([blue,red],events))==8
    rows=plan_eight_cases([blue,red],events,modes=["third","geo_aim"])
    assert len(rows)==4 and [x[3] for x in rows]==["third","geo_aim"]*2


def test_comparison_sheet_written_using_supplied_frame_samples(monkeypatch,tmp_path):
    from core import qa_visual
    monkeypatch.setattr(qa_visual,"frame_at",lambda *args,**kw:Image.new("RGB",(320,180),(30,70,110)))
    monkeypatch.setattr(qa_visual,"get_duration",lambda *args,**kw:2.0)
    report=qa_visual.make_qa_contact_sheets(
        tmp_path, [{"number":1,"side":"RED","mode":"third","outputs":["fake.mp4"]}],
        [{"style":"cut","outputs":["fake.mp4"]},{"style":"flash","outputs":["fake.mp4"]}])
    assert len(report["images"])==2
    assert all(Path(name).exists() for name in report["images"])
    assert report["transitions"][1]["similar_at_join"]
