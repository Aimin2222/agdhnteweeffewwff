"""Regression of encoder retries, capture loss and truthful failure telemetry."""
from dataclasses import fields
from pathlib import Path
from types import SimpleNamespace
import json
import subprocess

import numpy as np
import pytest

from core.effects import Template
from core import recorder, performance_diagnostics as perf


def test_v599_pair_template_positions_are_preserved():
    before=Template(kill_icon_players=[{'name':'One'}],smart_composition=True)
    added={'encoder_policy','kill_frame_color','kill_glow_color','kill_glow_enabled',
           'kill_glow_strength','kill_frame_width','kill_mark_style'}
    restored=Template(*(getattr(before,f.name) for f in fields(Template) if f.name not in added))
    assert restored.kill_icon_players==before.kill_icon_players
    assert restored.smart_composition and restored.encoder_policy=='auto'


@pytest.mark.parametrize('fps_args',[[],['-r','144']])
def test_retry_preserves_audio_and_filters_without_requiring_r(fps_args):
    command=['ffmpeg','-i','input','-c:v','h264_nvenc','-preset','p5','-tune','hq',
             '-c:a','copy','-map','0:a?','-vf','eq=brightness=.1',*fps_args,'output.mp4']
    retry=perf.cpu_encoder_retry_command(command)
    assert retry[retry.index('-c:a'):]==command[command.index('-c:a'):]
    assert retry[retry.index('-c:v')+1]=='libx264'
    assert '-tune' not in retry


def test_retry_timeout_does_not_claim_encoder_or_gpu_success(monkeypatch,tmp_path):
    monkeypatch.setattr(perf,'__file__',str(tmp_path/'core/performance_diagnostics.py'))
    monkeypatch.setattr(perf,'_sample_gpu',lambda:{})
    def run(command,**kwargs):
        if 'h264_nvenc' in command:return SimpleNamespace(returncode=1,stderr='driver failed')
        raise subprocess.TimeoutExpired(command,1)
    monkeypatch.setattr(perf.subprocess,'run',run)
    with pytest.raises(subprocess.TimeoutExpired):
        perf.run_render(['ffmpeg','-c:v','h264_nvenc','-r','60','out.mp4'],
                        output=tmp_path/'out.mp4',gpu_effects=['glitch'],effect_values={})
    data=json.loads(next((tmp_path/'diagnostics/performance').glob('render_*.json')).read_text())
    assert data['encoder']=='libx264' and data['returncode'] is None
    assert not data['gpu_effects_confirmed'] and data['error']
    assert '失敗' in perf.latest_render_summary(tmp_path/'diagnostics')
    assert 'エフェクト 未完了' in perf.latest_render_summary(tmp_path/'diagnostics')


def test_capture_probe_failure_switches_cpu_before_frames_are_written(monkeypatch,tmp_path):
    class Source:
        frame_count=1
        def latest(self):return np.zeros((24,32,4),dtype=np.uint8)
    class Thread:
        def __init__(self,*a,**kw):pass
        def start(self):pass
    commands=[]
    monkeypatch.setattr(recorder,'gpu_encoder_available',lambda:True)
    monkeypatch.setattr(recorder,'_nvenc_capture_probe',lambda *a:(False,'driver failure'))
    monkeypatch.setattr(recorder.threading,'Thread',Thread)
    monkeypatch.setattr(recorder.subprocess,'Popen',lambda command,**kw:(commands.append(command) or SimpleNamespace(stdin=object())))
    capture=recorder.ClipRecorder(Source(),tmp_path/'raw.mp4')
    capture.start()
    assert capture.frames==0
    assert 'libx264' in commands[0] and 'h264_nvenc' not in commands[0]
    assert 'driver failure' in capture.encoder_fallback_reason


def test_failed_timing_fix_preserves_raw_and_raises(monkeypatch,tmp_path):
    path=tmp_path/'raw.mp4';path.write_bytes(b'original capture')
    capture=recorder.ClipRecorder(None,path,encoder_policy='cpu')
    monkeypatch.setattr(capture,'_probe_duration',lambda:2)
    monkeypatch.setattr(perf,'run_render',lambda *a,**kw:SimpleNamespace(returncode=1,stderr='all retries failed'))
    with pytest.raises(recorder.CaptureError,match='時間の補正'):
        capture._normalize_duration(4)
    assert path.read_bytes()==b'original capture'


def test_partial_capture_failure_is_not_restarted_or_reported_success(monkeypatch,tmp_path):
    capture=recorder.ClipRecorder(None,tmp_path/'raw.mp4')
    capture.error='partial frame pipe failed';capture.frames=20
    seen=[]
    monkeypatch.setattr(perf,'record_encoding_result',lambda *a,**kw:seen.append(kw))
    monkeypatch.setattr(recorder.subprocess,'Popen',lambda *a,**kw:pytest.fail('Cannot restart missing frames'))
    with pytest.raises(recorder.CaptureError,match='partial frame'):
        capture.stop()
    assert seen[0]['error']==capture.error
