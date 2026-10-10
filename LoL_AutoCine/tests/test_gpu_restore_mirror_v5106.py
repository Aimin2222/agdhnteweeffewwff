"""Preserve the cinematic MP4, but release its temporary camera after capture."""
from types import SimpleNamespace
import pytest
from core import jobs
from core.replay_api import ReplayApiError
from core.audio import AudioError


@pytest.mark.parametrize('fail_first',[False,True])
def test_reset_mode_attachment_target_and_pause_together(fail_first):
    calls=[]
    def render(**kw):
        calls.append(kw)
        if fail_first and len(calls)==1: raise ReplayApiError('temporary failure')
    playback=[]
    api=SimpleNamespace(set_render=render,set_playback=lambda **kw:playback.append(kw))
    jobs.restore_mirror_camera(api,SimpleNamespace(selection_name='LeeSin',champion='Lee Sin'),45)
    assert playback==[{'paused':True,'speed':1.0}]
    assert calls[0]==dict(selectionName='LeeSin',cameraMode='top',cameraAttached=True,
                         selectionOffset={'x':0,'y':0,'z':0},fieldOfView=45)
    if fail_first: assert calls[-1]==dict(cameraMode='top',cameraAttached=True)


@pytest.mark.parametrize('fail_at',['start','validation'])
def test_audio_failure_still_releases_camera_and_restores_hud_fx(tmp_path,monkeypatch,fail_at):
    operations=[]
    player=SimpleNamespace(selection_name='Ahri',champion='Ahri')
    api=SimpleNamespace(set_playback=lambda **kw:None,
                        set_render=lambda **kw:operations.append(('camera',kw)))
    tpl=jobs.Template(game_audio=True,hide_hud=True)
    monkeypatch.setattr(jobs,'_prepare_clip_capture',lambda *a:(jobs.CameraPlan(),SimpleNamespace(v=None,third=True)))
    monkeypatch.setattr(jobs,'hide_hud',lambda *a:{'hud':True})
    monkeypatch.setattr(jobs,'apply_fx',lambda *a,**k:{'fx':True})
    monkeypatch.setattr(jobs,'restore_hud',lambda *a:operations.append(('hud',a[1])))
    monkeypatch.setattr(jobs,'restore_fx',lambda *a:operations.append(('fx',a[1])))
    monkeypatch.setattr(jobs,'_play_until',lambda *a,**k:None)
    director=SimpleNamespace(start=lambda:None,stop=lambda:None,errors=0,api_calls=0,
                             api_slow_calls=0,max_api_latency_ms=0,max_clock_drift=0)
    monkeypatch.setattr(jobs,'CameraDirector',lambda *a:director)
    rec=SimpleNamespace(start=lambda:None,stop=lambda:operations.append(('rec_stop',None)) or 1,
                         started_perf=1)
    monkeypatch.setattr(jobs,'ClipRecorder',lambda *a,**k:rec)
    class Audio:
        def __init__(self,p): self.path=p
        def start(self):
            if fail_at=='start': raise AudioError('start refused')
        def stop(self):
            operations.append(('audio_stop',None));return 1
    with pytest.raises(AudioError):
        jobs.record_one_clip(api,None,player,tpl,0,1,[],tmp_path/'clip.mp4',audio_factory=Audio)
    assert ('hud',{'hud':True}) in operations and ('fx',{'fx':True}) in operations
    top=next(i for i,op in enumerate(operations) if op[0]=='camera' and op[1]['cameraMode']=='top')
    if fail_at=='validation':
        rec_stop=operations.index(('rec_stop',None));audio_stop=operations.index(('audio_stop',None))
        assert rec_stop<top<audio_stop
