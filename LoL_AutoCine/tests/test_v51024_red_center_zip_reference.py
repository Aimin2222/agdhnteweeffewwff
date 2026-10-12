# -*- coding: utf-8 -*-
"""Camera center from real world-relative geometry; reference ZIP smoke tests."""
from __future__ import annotations
import io
import json
import math
import zipfile
from pathlib import Path
from types import SimpleNamespace

import pytest
from PIL import Image

from core.camera import CameraPlan, RigInfo
from core.camera_tuning import shot_tuning, target_center_rotation, yaw_alignment_error


def make_plan(style, team="CHAOS"):
    rig = RigInfo(mode="fps", third=True, h=(-.52, -.85416626),
                  rot={"x":0.0,"y":42.0,"z":0.0},
                  v=(5945.0, 1892.0, 3829.0),
                  pitch_axis="x", pitch_sign=1.0)
    plan = CameraPlan(style=style, rig=rig, team=team,
                      kill_time=833.64056, third_elev=42.0, third_dist=1170.0,
                      side_yaw=184.0)
    plan._camera_axis_safety=True
    plan._live_red_target_center=True
    plan._live_red_normal_reframe=True
    plan._live_dist_factor=1.13
    plan._live_angle_bias={}
    return plan


def test_red1_rotation_aims_at_exact_camera_relative_position():
    plan = make_plan("third")
    for t in (830.64, 833.64, 836.64):
        offset=plan.offset_at(t)
        assert plan.rotation_at(t)==target_center_rotation(offset)
        assert yaw_alignment_error(offset,plan.rotation_at(t)) < .000001
        assert plan.rotation_at(t)["z"] == 0.0
    assert shot_tuning("RED","third")["angles"]=={}


def test_red3_geometric_target_center_has_no_static_heading_error():
    rig=RigInfo(mode="fps",third=False,h=(-.4898255,-.8718205),
                v=(-500.9,1892.2,-891.6),rot={"x":0,"y":56,"z":0})
    plan=CameraPlan(style="fps", rig=rig, team="CHAOS",
                    kill_time=833.64056, third_elev=28.0, third_dist=950)
    plan._live_red_target_center=True
    plan._live_fps_recenter=True
    plan._live_fps_side_heading=192.0
    plan._live_fps_back=1.6
    for t in (830.64,833.64,836.64):
        pos=plan.offset_at(t)
        rot=plan.rotation_at(t)
        assert rot==target_center_rotation(pos)
        assert yaw_alignment_error(pos, rot) < 1e-6
    assert abs(plan.rotation_at(833.64)["x"]+192.0) > 10.0


def test_approved_red2_red4_red5_not_rewritten():
    for mode in ("third_cinema","lolnam_cinema","geo_aim"):
        assert not bool(shot_tuning("RED",mode).get("aim_target",False))
    assert shot_tuning("RED","third_cinema")["angles"]=={}
    assert shot_tuning("RED","lolnam_cinema")["angles"]=={"x":-3.0,"y":-3.0}
    assert shot_tuning("RED","geo_aim")["angles"]=={"x":-4.0}


def test_geometry_rejects_nonfinite_and_short_camera():
    with pytest.raises(ValueError):
        target_center_rotation((float("nan"),8,2))
    with pytest.raises(ValueError):
        target_center_rotation((0,1,0))
    with pytest.raises(ValueError):
        target_center_rotation((float("inf"),8,2))


def test_reference_zip_extracts_videos_without_extracting_traversal(tmp_path,monkeypatch):
    from tools import reference_video_review as rr
    source=tmp_path/"日本語・動画.zip"
    with zipfile.ZipFile(source,"w") as z:
        z.writestr("../xmedia.mp4",b"not-real-video")
        z.writestr("notes.txt",b"ignored")
    out=tmp_path/"reference_out"
    # Reference extractor is tested with fake media; no game replay needed.
    monkeypatch.setattr("core.montage_fx.get_duration",lambda *_a,**_k:2.0)
    monkeypatch.setattr("core.gpu_binary.ffmpeg_exe",lambda:"ffmpeg")
    picture=Image.new("RGB",(480,270),"#64748b")
    by=io.BytesIO()
    picture.save(by,format="PNG")
    monkeypatch.setattr(rr.subprocess,"run",lambda *_a,**_k:SimpleNamespace(
        returncode=0,stdout=by.getvalue(),stderr=b""))
    result=rr.create_sheets(source,out)
    assert result.is_file()
    assert not (tmp_path/"xmedia.mp4").exists()
    with zipfile.ZipFile(result) as z:
        assert "reference_archive_names.json" in z.namelist()
        assert len([n for n in z.namelist() if n.endswith(".jpg")])==1
    metadata=json.loads((out/"reference_archive_names.json").read_text(encoding="utf-8"))
    assert metadata["items"][0]["archived_name"]=="../xmedia.mp4"


def test_reference_zip_rejects_nonvideo_archive(tmp_path):
    from tools import reference_video_review as rr
    source=tmp_path/"empty_video.zip"
    with zipfile.ZipFile(source,"w") as z:z.writestr("notes.txt","hello")
    with pytest.raises(ValueError,match="MP4"):
        rr.create_sheets(source,tmp_path/"out")


def test_bat_accepts_video_zip_and_shows_exact_result(tmp_path):
    bat=(Path(__file__).resolve().parents[1]/"MAKE_REFERENCE_SHEETS.bat").read_text(encoding="ascii")
    assert 'goto ZIP_INPUT' not in bat
    assert "REVIEW ZIP:" in bat
    assert 'if not defined CI start "" explorer.exe' in bat
