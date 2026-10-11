# -*- coding: utf-8 -*-
"""v5.10.15 regression: scan integration, live-camera test plan and DOF UI."""
from pathlib import Path
import tkinter as tk

from core.camera_qa import QA_MODES, plan_eight_cases
from core.kill_icons import ASSET_STYLES, STYLES, REVERSE_STYLES
from core.players import Player


def _player(slot, name, team):
    return Player(slot, name, name+"#JP", name, "TestChamp", team)


def _events():
    return [
        {"event_id": 11, "time": 85.0, "killer": "BluePlayer",
         "victim": "Enemy1", "assisters": []},
        {"event_id": 12, "time": 102.0, "killer": "RedPlayer",
         "victim": "Enemy2", "assisters": []},
    ]


def test_eight_camera_plan_has_four_per_side_and_real_events():
    blue = _player(0,"BluePlayer","ORDER")
    red = _player(5,"RedPlayer","CHAOS")
    cases = plan_eight_cases([blue,red],_events(),preferred=blue)
    assert len(cases)==8
    assert [x[0] for x in cases] == ["RED"]*4 + ["BLUE"]*4
    assert [x[3] for x in cases[:4]] == [m for m,_ in QA_MODES]
    assert cases[0][1] == red and cases[4][1] == blue
    assert cases[0][2].time == 102.0 and cases[4][2].time == 85.0


def test_missing_team_rejected_before_recorder_start():
    blue=_player(0,"BluePlayer","ORDER")
    try:
        plan_eight_cases([blue],_events())
    except ValueError as exc:
        assert "RED" in str(exc)
    else:
        raise AssertionError("Must reject absent RED team")


def test_kill_style_names_identify_skin_theme_and_remain_unique():
    assert "スターガーディアン" in STYLES["star_guardian"]
    assert "スターガーディアン" in STYLES["star_magic"]
    assert "K/DA" in STYLES["kda_style"]
    assert "精霊の花祭り" in STYLES["spirit_blossom"]
    assert "ハイヌーン" in STYLES["high_noon"]
    assert "PROJECT" in STYLES["project_style"]
    assert len(STYLES) == len(REVERSE_STYLES)
    assert len(ASSET_STYLES)==37


def test_scan_one_button_and_exclusive_dof_panels():
    from legacy_app import App
    root = tk.Tk()
    app = App(root)
    try:
        root.update_idletasks()
        assert hasattr(app,"_connect_then_scan")
        calls=[]
        app._run_bg=lambda fn,*args:calls.append((fn.__name__,args))
        app.players=[]
        app.on_scan()
        assert calls and calls[-1][0] == "_connect_then_scan"
        app._focus_editor_zone("fx")
        app.var_dof.set(True)
        app.var_dof_shape.set("円形（おすすめ）")
        root.update_idletasks()
        assert app._circle_dof_panel.winfo_manager()
        assert not app._legacy_dof_panel.winfo_manager()
        app.var_dof_shape.set("従来の上下ぼかし")
        root.update_idletasks()
        assert app._legacy_dof_panel.winfo_manager()
        assert not app._circle_dof_panel.winfo_manager()
        app.var_dof_shape.set("円形（おすすめ）")
        assert app._circle_dof_panel.winfo_manager()
    finally:
        root.destroy()


def test_galleries_and_test_capture_have_nonblocking_handlers():
    root=Path(__file__).resolve().parents[1]
    gallery=(root/"ui"/"kill_frame_gallery.py").read_text("utf-8")
    app=(root/"legacy_app.py").read_text("utf-8")
    assert "def _on_canvas_resize" in gallery
    assert "Thread(target=work" in gallery
    assert "self._preview_ready.put" in gallery
    assert "自動カメラ・録画テスト（RED/BLUE 計8本）" in app
    assert "_run_auto_camera_record_test" in app
    assert "接続して10人を取得" not in app


def test_v51015_documentation_in_distribution():
    root=Path(__file__).resolve().parents[1]
    assert (root/"README_v5.10.15_JA.md").is_file()
    assert (root/"TESTLIST_v5.10.15_JA.md").is_file()

def test_eight_clip_worker_uses_existing_render_path_without_touching_gui(monkeypatch,tmp_path):
    import json
    from types import SimpleNamespace
    from core.effects import Template
    from core import camera_qa
    blue=_player(0,"BluePlayer","ORDER")
    red=_player(5,"RedPlayer","CHAOS")
    calls=[]
    def fake_run(api,source,player,scenes,tpl,outdir,montage,**kwargs):
        calls.append((player.team,tpl.style,tpl.fps,tpl.camera_side,tpl.game_audio,montage))
        return SimpleNamespace(outputs=[outdir/"out.mp4"],failed=[])
    monkeypatch.setattr(camera_qa,"run_auto_edit",fake_run)
    t=Template()
    t.game_audio=True
    report=camera_qa.run_camera_record_test(
        api=object(),source=object(),players=[blue,red],events=_events(),
        preferred=blue,template=t,destination=tmp_path,log=lambda msg:None)
    data=json.loads(report.read_text("utf-8"))
    assert len(data["outputs"])==8 and data["completed_clips"]==8
    assert [x[0] for x in calls]==["CHAOS"]*4+["ORDER"]*4
    assert all(x[2]==60 and x[3]=="auto" and x[4] is True and x[5] is False for x in calls)
    assert t.style=="cinema"  # input template stays untouched
