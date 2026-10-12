# -*- coding: utf-8 -*-
"""v5.10.23: desktop MP4 selection, safe camera per-mode framing."""
from pathlib import Path
import math
import pytest

from tools.reference_video_review import output_for_source, choose_video_or_folder, main
from core.camera_tuning import shot_tuning
from core.camera import CameraPlan, RigInfo


def rig():
    return RigInfo(mode="fps", third=False, h=(-.4901085,-.8716614),
                   v=(-497.65,1892.24,-885.07),
                   rot={"x":0.0,"y":56.0,"z":0.0})


def test_reference_video_picker_output_location(tmp_path):
    movie=tmp_path/"日本語 動画 テスト.mp4"
    movie.write_bytes(b"file")
    assert output_for_source(movie)==tmp_path/"_AutoCineReferenceReview_日本語 動画 テスト"
    assert output_for_source(tmp_path)==tmp_path/"_AutoCineReferenceReview"


def test_bat_no_argument_opens_python_file_picker(monkeypatch,tmp_path):
    import tools.reference_video_review as reference
    file=tmp_path/"日本語.mp4"
    file.write_bytes(b"dummy")
    monkeypatch.setattr(reference,"choose_video_or_folder",lambda:file)
    calls=[]
    monkeypatch.setattr(reference,"create_sheets",
                        lambda path,out:calls.append((path,out)))
    monkeypatch.setattr("sys.argv",["reference_video_review"])
    assert reference.main()==0
    assert calls==[(file,tmp_path/"_AutoCineReferenceReview_日本語")]


def test_reference_picker_cancel_exits_cleanly(monkeypatch):
    import tools.reference_video_review as reference
    monkeypatch.setattr(reference,"choose_video_or_folder",lambda:None)
    monkeypatch.setattr("sys.argv",["reference_video_review"])
    assert reference.main()==0


def test_red_approved_modes_unchanged_and_blue_moves_behind():
    red2=shot_tuning("RED","third_cinema")
    red4=shot_tuning("RED","lolnam_cinema")
    red5=shot_tuning("RED","geo_aim")
    assert red2["distance"]==pytest.approx(.96)
    assert red2["angles"]=={}
    assert red4["distance"]==1.0
    assert red4["angles"]=={"x":-3.0,"y":-3.0}
    assert red5["distance"]==1.12
    assert red5["angles"]=={"x":-4.0}
    for style in ("third","third_cinema","lolnam_cinema","geo_aim"):
        assert shot_tuning("BLUE",style)["distance"]>1.0
    assert shot_tuning("BLUE","fps")["fps_back"]>1.22
    assert "z" not in shot_tuning("RED","third")["angles"]


def test_red_fps_uses_approved_geo_camera_rear_direction_only_when_opted_in():
    plan=CameraPlan(style="fps",rig=rig(),team="CHAOS",
                    third_dist=900,third_elev=42,side_yaw=0)
    plan._live_fps_recenter=True
    plan._live_fps_back=1.6
    plan._live_fps_side_heading=192.0
    baseline=plan.offset_at(0.0)
    plan._live_fps_canonical_rear=True
    revised=plan.offset_at(0.0)
    assert baseline != revised
    assert revised[0] < 0.0  # approved RED #5 camera is left/rear
    assert revised[2] > 0.0
    assert math.degrees(math.atan2(revised[1],math.hypot(revised[0],revised[2])))==pytest.approx(42,abs=.5)
    assert math.hypot(revised[0],revised[2]) > 1100


def test_bat_is_ascii_and_shows_reason_if_zip_dropped():
    s=(Path(__file__).resolve().parents[1]/"MAKE_REFERENCE_SHEETS.bat").read_text("ascii")
    assert ":PICKER" in s
    assert 'notepad.exe' in s
    assert ':ZIP_INPUT' in s
    assert '"%SOURCE%"' in s
    assert "%TEMP%\\AutoCine_ReferenceReview_latest.log" in s
