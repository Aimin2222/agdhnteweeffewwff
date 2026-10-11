# -*- coding: utf-8 -*-
"""v5.10.15 regression: unified replay workflow, camera pitch and dev QA."""
from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest
from core.players import Player
from core.replay_qa import CAMERA_CASES, build_matrix, run_replay_qa
from core.camera import CameraPlan, RigInfo


def players_and_events():
    blue=Player(0,"blue_test","blue_test#JP1","blue_test","Lux","ORDER")
    red=Player(5,"red_test","red_test#JP1","red_test","Blitzcrank","CHAOS")
    events=[{"event_id":1,"time":70.0,"killer":"blue_test","victim":"red_test","assisters":[]},
            {"event_id":2,"time":120.0,"killer":"red_test","victim":"blue_test","assisters":[]},
            {"event_id":3,"time":150.0,"killer":"blue_test","victim":"red_test","assisters":[]},
            {"event_id":4,"time":190.0,"killer":"red_test","victim":"blue_test","assisters":[]}]
    return [blue,red],events


def test_qa_matrix_is_eight_or_sixteen_real_cases():
    players,events=players_and_events()
    a=build_matrix(players,events,events_per_team=1)
    b=build_matrix(players,events,events_per_team=2)
    assert len(a)==8
    assert len(b)==16
    assert {x["side"] for x in a}=={"BLUE","RED"}
    assert {x["camera"] for x in a}=={x[0] for x in CAMERA_CASES}
    assert all(x["kill"].role=="kill" for x in b)


def test_qa_matrix_skips_missing_team_gracefully():
    players,events=players_and_events()
    result=build_matrix(players,events[:1])
    assert len(result)==4
    assert all(x["side"]=="BLUE" for x in result)


def test_dev_qa_records_report_without_touching_templates(tmp_path,monkeypatch):
    from core.effects import Template
    players,events=players_and_events()
    seen=[]
    def pretend_render(_api,_source,player,kills,tpl,root,**kwargs):
        seen.append((tpl.style,tpl.pre,tpl.post,tpl.bgm_path,kwargs["make_montage"]))
        p=Path(root)/"test"/"sample.mp4"
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_bytes(b"sample")
        return SimpleNamespace(outputs=[p],failed=[])
    import core.jobs
    monkeypatch.setattr(core.jobs,"run_auto_edit",pretend_render)
    original=Template(style="cinema",pre=4.0,post=3.0,bgm_path="user_playlist.mp3")
    report=run_replay_qa(None,None,players,events,original,tmp_path,events_per_team=1)
    assert len(report["cases"])==8
    assert report["passed"]==8 and report["failed"]==0
    assert all(row[1:]==(2.0,2.0,"",False) for row in seen)
    assert original.pre==4.0 and original.bgm_path=="user_playlist.mp3"
    assert (Path(report["outputs_root"])/"replay_qa_report.json").exists()


def test_red_horizontal_orbit_cannot_reverse_vertical_pitch():
    rig=RigInfo(mode="fps",third=True,
                rot={"x":59.,"y":0.,"z":0.},pitch_axis="x",
                pitch_sign=1.,pitch_complement=True,h=(0.,-1.))
    for name in ("third","third_cinema"):
        blue=CameraPlan(style=name,rig=rig,third_elev=35,side_yaw=-12)
        red=CameraPlan(style=name,rig=rig,third_elev=35,side_yaw=192)
        assert red.rotation_at(0)["x"]==pytest.approx(blue.rotation_at(0)["x"])


def test_app_combined_button_and_exclusive_dof():
    import tkinter as tk
    import legacy_app
    root=tk.Tk()
    root.geometry("1450x900")
    app=legacy_app.App(root)
    try:
        root.update_idletasks()
        args=[]
        app._run_bg=lambda fn,*a: args.append((fn.__name__,a))
        app.on_connect_and_scan()
        assert args and args[0][0]=="_connect_and_scan_worker"
        app.var_dof_shape.set("従来の上下ぼかし")
        root.update_idletasks()
        assert app._legacy_dof_panel.winfo_manager()
        assert not app._dof_circle_panel.winfo_manager()
        app.var_dof_shape.set("円形（おすすめ）")
        root.update_idletasks()
        assert app._dof_circle_panel.winfo_manager()
        assert not app._legacy_dof_panel.winfo_manager()
    finally:
        root.destroy()
