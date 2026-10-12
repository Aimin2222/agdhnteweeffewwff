"""Actual dispatch/fallback semantics and read-only camera evidence."""
from pathlib import Path
from types import SimpleNamespace
import json
import subprocess
import pytest
from core import gpu_badge_qa as qa, jobs
from core.effects import Template
from core.camera import RigInfo
from core.players import Player


@pytest.mark.parametrize('failure', [None, 'driver', 'timeout', 'unverified', 'cpu'])
def test_gpu_motion_qa_preserves_audio_clock_policy_and_cleanup(tmp_path, monkeypatch, failure):
    source = tmp_path / 'input.mp4'; source.write_bytes(b'source')
    badge = tmp_path / 'badge.png'; badge.write_bytes(b'badge')
    dst = tmp_path / 'output.mp4'; calls = []; stages = []
    monkeypatch.setattr(qa, 'detect', lambda: SimpleNamespace(full_gpu_runtime_ok=failure != 'unverified', full_probe_reason='no GPU'))
    monkeypatch.setattr(qa.gpu_full, 'mode', lambda: 'cpu' if failure == 'cpu' else 'full')
    monkeypatch.setattr(qa.gpu_full, 'decode_probe', lambda *a: (True, ''))
    policies = []
    def encoding(fps, policy):
        policies.append((fps, policy)); return ['-c:v', 'h264_nvenc', '-pix_fmt', 'yuv420p']
    monkeypatch.setattr(qa, 'encoder_args', encoding)
    class Stage:
        def __init__(self, tpl, duration, events, **kwargs):
            assert tpl.kill_icon_motion == 'slide_up' and tpl.fps == 60
            assert kwargs['badges'] == [(badge, .45)] and duration == 2.25
            self.lut = tmp_path / 'lut.png'; self.lut.write_bytes(b'LUT')
            self.graph = '[0:v]program_opencl=kernel=badge_0[vout]'
            self.effects = {'kill_icons', 'kill_icon_motion'}; stages.append(self)
        def close(self): self.lut.unlink()
    monkeypatch.setattr(qa.gpu_full, 'GPUFullStage', Stage)
    def render(cmd, **kw):
        gpu = kw['pipeline_info']['full_gpu_pipeline']; calls.append((cmd, kw))
        assert cmd[cmd.index('-map')+1] == '[vout]' and '0:a?' in cmd
        assert cmd[cmd.index('-c:a')+1] == 'copy' and cmd[cmd.index('-t')+1] == '2.250'
        assert kw['pipeline_info']['output_fps'] == 60
        if gpu:
            assert '-loop' not in cmd and '-hwaccel' in cmd and 'rgba' in cmd
            assert kw['gpu_effects'] == {'kill_icons', 'kill_icon_motion'}
            if failure == 'timeout': raise subprocess.TimeoutExpired(cmd, 180)
            if failure == 'driver': return SimpleNamespace(returncode=1, stderr='driver failure')
        else:
            assert '-init_hw_device' not in cmd and '-hwaccel' not in cmd
            assert 'overlay=' in kw['pipeline_info']['filter_graph'] and not kw['gpu_effects']
            assert 'fps=fps=60' in kw['pipeline_info']['filter_graph']
        dst.write_bytes(b'video')
        return SimpleNamespace(returncode=0, args=cmd, encoder_retry_reason=None)
    monkeypatch.setattr(qa, 'run_render', render)
    data = qa.render_badge_motion(source, dst, badge, 'cinema', 'slide_up', 2.25, encoder_policy='gpu')
    assert data['gpu_effects_confirmed'] is (failure is None)
    assert len(calls) == (2 if failure in ('driver', 'timeout') else 1)
    assert all(p == (60, 'gpu') for p in policies)
    assert not (tmp_path / 'lut.png').exists() and source.read_bytes() == b'source'
    if failure: assert data['fallback_reason']


def test_nvenc_cpu_retry_is_reported_without_losing_gpu_effects(tmp_path, monkeypatch):
    source = tmp_path / 'in.mp4'; source.write_bytes(b'source')
    dst = tmp_path / 'out.mp4'
    monkeypatch.setattr(qa, 'detect', lambda: SimpleNamespace(full_gpu_runtime_ok=True))
    monkeypatch.setattr(qa.gpu_full, 'decode_probe', lambda *a: (False, 'unsupported'))
    monkeypatch.setattr(qa.gpu_full, 'mode', lambda: 'full')
    stage = SimpleNamespace(graph='graph', lut=tmp_path/'lut', effects={'kill_icons'}, close=lambda: None)
    monkeypatch.setattr(qa.gpu_full, 'GPUFullStage', lambda *a, **kw: stage)
    monkeypatch.setattr(qa, 'encoder_args', lambda *a, **k: ['-c:v','h264_nvenc','-pix_fmt','yuv420p'])
    def render(cmd, **kw):
        dst.write_bytes(b'video')
        assert '-hwaccel' not in cmd
        return SimpleNamespace(returncode=0, args=['-c:v','libx264'], encoder_retry_reason='NVENC rejected')
    monkeypatch.setattr(qa, 'run_render', render)
    data = qa.render_badge_motion(source, dst, tmp_path/'badge', 'cinema', 'pop', 1)
    assert data['gpu_effects_confirmed'] and data['encoder'] == 'libx264'
    assert data['encoder_retry_reason'] == 'NVENC rejected'


def test_camera_numeric_evidence_does_not_add_api_writes(monkeypatch):
    monkeypatch.setattr(jobs.time, 'sleep', lambda _: None)
    rig = RigInfo(mode='fps', third=True, P=(0, 0, 0), v=(0, 400, -1000),
                  rot={'x':20,'y':0,'z':0}, pitch_axis='x', pitch_sign=1, h=(0,-1))
    monkeypatch.setattr(jobs, 'attach_to_player', lambda *a, **k: rig)
    player = Player(5, 'Red', 'Red#JP', 'Red', 'Ahri', 'CHAOS')
    scene = SimpleNamespace(time=10); logs = []; calls = []
    api = SimpleNamespace(set_playback=lambda **kw:calls.append(('playback',kw)),
                          seek=lambda t:(calls.append(('seek',t)) or t))
    jobs._setup_clip(api, player, Template(style='third'), 9, [scene], lambda _:None)
    ordinary = list(calls); calls.clear()
    plan, returned = jobs._setup_clip(api, player, Template(name='CameraQA RED 通常三人称', style='third'), 9, [scene], logs.append)
    assert calls == ordinary and returned is rig
    evidence = json.loads(next(row for row in logs if row.startswith('CAMERA_QA_POSE ')).split(' ',1)[1])
    assert evidence['side'] == 'CHAOS' and evidence['pitch_axis'] == 'x'
    assert evidence['baseline_rotation'] == rig.rot
    assert evidence['side_heading_degrees'] == plan.side_yaw == 184
    assert evidence['initial_camera_offset'] == list(plan.offset_at(9))
