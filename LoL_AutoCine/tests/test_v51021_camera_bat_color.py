# -*- coding: utf-8 -*-
"""Safety and UI regressions for v5.10.21."""
from pathlib import Path
import pytest
from core.camera import CameraPlan, RigInfo
from core.camera_tuning import shot_tuning
from tools.reference_video_review import find_reference_videos


def test_single_mp4_can_be_dropped_on_reference_bat(tmp_path):
    video=tmp_path/"reference video (Jhin).mp4"
    video.write_bytes(b"not-a-real-mp4")
    assert find_reference_videos(video)==[video]
    assert find_reference_videos(tmp_path)==[video]
    invalid=tmp_path/"notes.txt"
    invalid.write_text("not a video",encoding="utf-8")
    with pytest.raises(ValueError):
        find_reference_videos(invalid)


def test_cam_modes_are_isolated_and_blue7_is_protected():
    b7=shot_tuning("ORDER","third_cinema")
    assert b7["distance"]==1.0 and b7["angles"]=={}
    assert shot_tuning("CHAOS","third_cinema")["angles"]=={}
    assert shot_tuning("CHAOS","third")["distance"]>1.0
    assert shot_tuning("CHAOS","lolnam_cinema")["angles"]
    assert shot_tuning("ORDER","lolnam_cinema")["angles"]
    assert shot_tuning("ORDER","geo_aim")["angles"]


def test_fps_live_recenter_uses_target_relative_offset_not_distant_stale_camera():
    rig=RigInfo(mode="fps", third=False, h=(-.5,-.8660254),
                v=(7500.,1800.,-9000.),rot={"x":0,"y":56,"z":0})
    plan=CameraPlan(style="fps",rig=rig,team="ORDER",third_dist=950,third_elev=42)
    plan._live_fps_recenter=True
    assert plan.offset_at(2.0)==plan.third_pose_at(2.0)[0]
    assert abs(plan.offset_at(2.0)[0])<2500
    assert abs(plan.offset_at(2.0)[2])<2500


def test_mode_bias_changes_only_enabled_live_plan():
    rig=RigInfo(mode="fps",third=True,h=(-.5,-.866),v=(-475,1800,-823),
                rot={"x":0,"y":42,"z":0},pitch_axis="y",pitch_sign=1)
    plan=CameraPlan(style="geo_aim",rig=rig,team="ORDER",third_dist=950,third_elev=42)
    before=plan.rotation_at(0.0)
    plan._live_angle_bias={"x":2.5}
    after=plan.rotation_at(0.0)
    assert after["x"]==pytest.approx(before["x"]+2.5)
    assert after["y"]==before["y"]
    untouched=CameraPlan(style="geo_aim",rig=rig,team="ORDER",third_dist=950,third_elev=42)
    assert untouched.rotation_at(0.0)==before


def test_easy_color_and_director_panels_follow_checkbox_live():
    import tkinter as tk
    from legacy_app import App
    root=tk.Tk()
    try:
        app=App(root)
        root.update_idletasks()
        assert not app._easy_color_panel.winfo_manager()
        assert not app._auto_director_panel.winfo_manager()
        app.var_easy_color_custom.set(True)
        app.var_auto_director.set(True)
        root.update_idletasks()
        assert app._easy_color_panel.winfo_manager()
        assert app._auto_director_panel.winfo_manager()
        assert len(app._easy_color_panel.winfo_children())==4
        app.var_easy_color_custom.set(False)
        app.var_auto_director.set(False)
        root.update_idletasks()
        assert not app._easy_color_panel.winfo_manager()
        assert not app._auto_director_panel.winfo_manager()
    finally:
        root.destroy()


def test_director_strength_controls_real_automatic_arc_and_dolly():
    import tkinter as tk
    from legacy_app import App
    root=tk.Tk()
    try:
        app=App(root)
        app.kills=[]
        received=[]
        app._set_camera_motion=lambda profile,arc,dolly:received.append((profile,arc,dolly))
        app.var_auto_director_strength.set(.5)
        app._apply_auto_director()
        assert received[-1][1]==pytest.approx(5.0)
        assert received[-1][2]==pytest.approx(1.5)
    finally:
        root.destroy()


def test_bat_usage_mentions_video_and_persistent_log():
    bat=(Path(__file__).resolve().parents[1]/"MAKE_REFERENCE_SHEETS.bat").read_text(encoding="utf-8")
    assert "%~1" in bat
    assert "AutoCine_ReferenceReview_latest.log" in bat
    assert "tools.reference_video_review" in bat
    assert "pause" in bat.lower()


@pytest.mark.parametrize("gain", [0, .5, 1.5])
def test_one_click_snapshots_director_strength_for_worker(gain, monkeypatch):
    import tkinter as tk
    from legacy_app import App
    root=tk.Tk()
    try:
        app=App(root)
        app._need_lock=lambda:True
        app._match_scan_cache=None
        app._scene_render_config=lambda:(False,{},False,[])
        app.var_auto_director.set(True)
        app.var_auto_director_strength.set(gain)
        captured=[]
        app._run_bg=lambda fn,scan,tpl,*args:captured.append(tpl)
        app.on_one_click()
        assert len(captured)==1 and captured[0].auto_director_strength==gain
        assert captured[0].motion_arc==pytest.approx(10*gain)
    finally:
        root.destroy()


def test_invalid_director_strength_stops_before_worker(monkeypatch):
    import tkinter as tk
    import legacy_app
    root=tk.Tk()
    try:
        app=legacy_app.App(root)
        app._need_lock=lambda:True
        app._match_scan_cache=None
        app.var_auto_director.set(True)
        app.var_auto_director_strength.set(float('nan'))
        errors=[];jobs=[]
        monkeypatch.setattr(legacy_app.messagebox,'showerror',lambda *args:errors.append(args))
        app._run_bg=lambda *args:jobs.append(args)
        app.on_one_click()
        assert errors and not jobs
    finally:
        root.destroy()
