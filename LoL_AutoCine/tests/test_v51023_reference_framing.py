# -*- coding: utf-8 -*-
"""v5.10.23: check targeted live camera fixes and robust reference launcher."""
from pathlib import Path
import math
import pytest
from core.camera import CameraPlan,RigInfo
from core.camera_tuning import shot_tuning
from tools.reference_video_review import find_reference_videos,choose_source


def test_approved_red2_red4_red5_modes_are_unchanged():
    assert shot_tuning("CHAOS","third_cinema")["distance"]==0.96
    assert shot_tuning("CHAOS","third_cinema")["angles"]=={}
    assert shot_tuning("CHAOS","lolnam_cinema")=={
        "side":"RED","mode":"lolnam_cinema","distance":1.0,
        "angles":{"x":-3.0,"y":-3.0},"fps_back":1.0}
    assert shot_tuning("RED","geo_aim")["distance"]==1.12


def test_red1_has_no_roll_angle_and_aim_bias_is_independent():
    red=shot_tuning("RED","third")
    assert red["angles"]=={} # RED1 geometric look-at replaces manual bias
    assert "z" not in red["angles"]
    assert shot_tuning("BLUE","third")["angles"]=={"x":3.0}


@pytest.mark.parametrize("mode",["third","third_cinema","fps","lolnam_cinema","geo_aim"])
def test_each_blue_camera_pulled_back_without_shared_overrides(mode):
    tuning=shot_tuning("BLUE",mode)
    if mode=="fps":
        assert tuning["fps_back"]>=1.35
    else:
        assert tuning["distance"]>=1.08
    tuning["angles"]["x"]=777  # returned copy must not mutate global configs
    assert shot_tuning("BLUE",mode)["angles"].get("x")!=777


def test_red_fps_live_pitch_matches_relative_vector_not_fixed_42():
    rig=RigInfo(mode="fps",third=False,rot={"x":0.0,"y":56.0,"z":0.0},
                v=(0,0,0),h=(-.49,-.87))
    plan=CameraPlan(style="fps",rig=rig,team="CHAOS",
                    third_dist=950,third_elev=28,side_yaw=0)
    plan._live_fps_recenter=True
    plan._live_fps_side_heading=192.0
    plan._live_fps_back=1.6
    rot=plan.rotation_at(0.0)
    pos=plan.offset_at(0.0)
    reference_pitch=math.degrees(math.atan2(pos[1],math.hypot(pos[0],pos[2])))
    assert rot["x"] == pytest.approx(-192.0)  # legacy plan without LIVE geometric-aim flag
    assert rot["y"] == pytest.approx(reference_pitch+3.0)
    assert rot["z"] == 0.0
    assert rot["y"] < 42.0


def test_reference_launcher_accepts_mp4_and_rejects_zip(tmp_path):
    mp4=tmp_path/"参照 動画.mp4"
    mp4.write_bytes(b"fake")
    assert find_reference_videos(mp4)==[mp4]
    folder=tmp_path/"日本語 フォルダー"
    folder.mkdir()
    assert find_reference_videos(folder)==[]
    from pathlib import Path
    runner=(Path(__file__).resolve().parents[1]/"MAKE_REFERENCE_SHEETS.bat").read_text(encoding="ascii")
    assert "where py" in runner
    assert ":PICK_SOURCE" in runner
    assert ":ZIP_INPUT" not in runner  # valid video ZIP now accepted
    assert "reference_review_latest.log" in runner


def test_cli_can_launch_selector_without_drag_drop(monkeypatch,tmp_path):
    from tools import reference_video_review as r
    fake=tmp_path/"x.mp4"
    fake.write_bytes(b"example")
    monkeypatch.setattr(r,"choose_source",lambda:fake)
    calls=[]
    monkeypatch.setattr(r,"create_sheets",lambda source,out:calls.append((source,out)) or out/"ReferenceReview_contact_sheets.zip")
    monkeypatch.setattr("sys.argv",["reference_video_review"])
    r.main()
    assert calls[0][0]==fake
    assert calls[0][1].parent==fake.parent
