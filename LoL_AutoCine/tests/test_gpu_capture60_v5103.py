"""Capture cadence follows output without changing camera or media clocks."""
from types import SimpleNamespace
import subprocess

import pytest
from core import jobs, effects, recorder
from core.capture import SyntheticSource


@pytest.mark.parametrize('capture_fps,output_fps,expected', [
    (144,30,30), (144,60,60), (144,120,120), (144,144,144), (30,60,30),
])
def test_job_limits_recording_clock_and_keeps_camera_clock(
        monkeypatch,tmp_path,capture_fps,output_fps,expected):
    tpl=jobs.Template(capture_fps=capture_fps,fps=output_fps,
                      game_audio=False,hide_hud=False)
    api=SimpleNamespace(set_playback=lambda **kw: None,set_render=lambda **kw: None)
    plan=jobs.CameraPlan()
    rig=SimpleNamespace(v=None,third=False)
    monkeypatch.setattr(jobs,'_prepare_clip_capture',lambda *a: (plan,rig))
    monkeypatch.setattr(jobs,'apply_fx',lambda *a,**kw: {})
    monkeypatch.setattr(jobs,'restore_fx',lambda *a: None)
    monkeypatch.setattr(jobs,'restore_hud',lambda *a: None)
    camera=jobs.CameraDirector(api,plan)
    camera.start=lambda: None
    camera.stop=lambda: None
    monkeypatch.setattr(jobs,'CameraDirector',lambda *a: camera)
    seen=[]
    class Recorder:
        started_perf=0
        def __init__(self,source,path,fps):
            self.fps=fps
            seen.append(fps)
        def start(self): pass
        def stop(self): return 2
    monkeypatch.setattr(jobs,'ClipRecorder',Recorder)
    monkeypatch.setattr(jobs,'_play_until',lambda *a,**kw: None)
    take=jobs.record_one_clip(api,SyntheticSource(),None,tpl,10,12,[],tmp_path/'raw.mp4')
    assert seen==[expected]
    assert take.duration==2
    assert tpl.capture_fps==capture_fps and tpl.fps==output_fps
    assert camera.hz==144 and camera.api_hz==60


def test_real_timing_normalization_keeps_60fps_and_wall_duration(tmp_path):
    path=tmp_path/'raw.mp4'
    subprocess.run([effects.FFMPEG,'-v','error','-f','lavfi','-i',
        'testsrc2=size=64x48:rate=60:duration=0.75','-an',
        '-c:v','libx264','-preset','ultrafast',str(path)],
        capture_output=True,check=True,timeout=20)
    rec=recorder.ClipRecorder(SyntheticSource(),path,fps=60,encoder_policy='cpu')
    # Simulate capture backpressure: .75s of encoded frames over 1.5s real time.
    rec._normalize_duration(1.5)
    assert rec._timing_fixed
    # FFmpeg rounds the last stretched frame, and its probe prints hundredths.
    assert abs(rec._probe_duration()-1.5)<=1/60+.01
    result=subprocess.run([effects.FFMPEG,'-v','error','-i',str(path),'-an',
        '-f','framemd5','-'],capture_output=True,text=True,check=True,timeout=20)
    frames=[l for l in result.stdout.splitlines() if l and not l.startswith('#')]
    assert '#tb 0: 1/60' in result.stdout
    assert abs(len(frames)/60-1.5)<=1/60+.00001
    assert [int(l.split(',')[2]) for l in frames]==list(range(len(frames)))
