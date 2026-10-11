# -*- coding: utf-8 -*-
"""Development-only QA must export badge-motion variants and numeric camera evidence."""
from pathlib import Path
from types import SimpleNamespace
import json

from core.effects import Template
from core.players import Player
from core import camera_qa

def _p(slot,name,team):
    return Player(slot,name,name+"#JP",name,"TestChamp",team)

def test_eight_camera_and_six_badge_motions_have_distinct_outputs(monkeypatch,tmp_path):
    blue=_p(0,"Blue","ORDER")
    red=_p(5,"Red","CHAOS")
    events=[dict(event_id=1,time=100.0,killer="Blue",victim="Red",assisters=[]),
            dict(event_id=2,time=120.0,killer="Red",victim="Blue",assisters=[])]
    calls=[]
    def fake_run(api,source,player,scenes,tpl,outdir,montage,**kwargs):
        outdir.mkdir(parents=True,exist_ok=True)
        p=outdir/"clip.mp4"
        p.write_bytes(b"fake-mp4")
        calls.append(tpl.style)
        kwargs["log"]("CAMERA_QA_POSE "+json.dumps({"side":player.team,"pitch_axis":"x"}))
        return SimpleNamespace(outputs=[p],failed=[])
    monkeypatch.setattr(camera_qa,"run_auto_edit",fake_run)
    from core import montage_fx
    def fake_montage(inputs,dest,style,logger=None):
        dest.write_bytes(b"fake-montage")
        return style
    monkeypatch.setattr(montage_fx,"render_montage",fake_montage)
    def fake_badge(path,style):
        path.write_bytes(b"fake-badge")
        return path
    monkeypatch.setattr(camera_qa,"make_badge",fake_badge)
    def fake_subprocess(command,**kwargs):
        Path(command[-1]).write_bytes(b"fake-render")
        return SimpleNamespace(returncode=0)
    monkeypatch.setattr(camera_qa.subprocess,"run",fake_subprocess)
    report=camera_qa.run_camera_record_test(
        object(),object(),[blue,red],events,None,Template(),
        tmp_path, log=lambda _:None)
    manifest=json.loads(report.read_text(encoding="utf-8"))
    assert manifest["completed_clips"]==8
    assert len(manifest["montage_tests"])==10
    assert len(manifest["badge_motion_tests"])==6
    assert not [row for row in manifest["badge_motion_tests"] if row["failed"]]
    assert len(set(Path(row["outputs"][0]).name for row in manifest["badge_motion_tests"]))==6
    assert all(row["camera_diagnostics"] for row in manifest["outputs"])
    assert calls==["third","third_cinema","fps","lolnam_cinema"]*2


def test_badge_motion_qa_skips_when_no_recorded_video(tmp_path,monkeypatch):
    blue=_p(0,"Blue","ORDER")
    red=_p(5,"Red","CHAOS")
    events=[dict(event_id=1,time=50.0,killer="Blue",victim="Red",assisters=[]),
            dict(event_id=2,time=80.0,killer="Red",victim="Blue",assisters=[])]
    monkeypatch.setattr(camera_qa,"run_auto_edit",lambda *a,**kw:SimpleNamespace(outputs=[],failed=[[1,"no capture"]]))
    result=camera_qa.run_camera_record_test(object(),object(),[blue,red],events,None,Template(),tmp_path)
    manifest=json.loads(result.read_text(encoding="utf-8"))
    assert len(manifest["outputs"])==8 and manifest["completed_clips"]==0
    assert manifest["badge_motion_tests"]==[]



def test_badge_motion_graph_is_accepted_by_real_ffmpeg(tmp_path):
    """A generated MP4, not just matching text, demonstrates real overlay support."""
    import shutil
    import subprocess
    import pytest
    from core.kill_icons import make_badge, with_badges
    from core.gpu_binary import ffmpeg_exe
    exe=str(ffmpeg_exe())
    if not shutil.which(exe) and not Path(exe).is_file():
        pytest.skip("FFmpeg is not installed")
    raw=tmp_path/"base.mp4"
    final=tmp_path/"qa_motion.mp4"
    badge=make_badge(tmp_path/"badge.png","cinema")
    subprocess.run([exe,"-y","-hide_banner","-loglevel","error",
                    "-f","lavfi","-i","color=c=gray:s=640x360:r=30:d=2",
                    "-c:v","libx264","-pix_fmt","yuv420p",str(raw)],
                   check=True,capture_output=True,timeout=40)
    graph=with_badges("[0:v]format=yuv420p[vout]",1,[(badge,.45)],
                      duration=2,seconds=1.2,style="cinema",motion="slide_up")
    subprocess.run([exe,"-y","-hide_banner","-loglevel","error","-i",str(raw),
                    "-loop","1","-framerate","30","-i",str(badge),
                    "-filter_complex",graph,"-map","[vout]","-c:v","libx264",
                    "-preset","ultrafast","-pix_fmt","yuv420p","-t","2",str(final)],
                   check=True,capture_output=True,timeout=60)
    assert final.is_file() and final.stat().st_size>800
