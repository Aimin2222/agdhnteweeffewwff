"""Preserve the existing template ABI, audio and recovery on optional montage FX."""
from dataclasses import fields
from pathlib import Path
from types import SimpleNamespace
import subprocess

import pytest

from core import effects, montage_fx
from core.effects import Template


def test_v596_positional_template_fields_are_preserved():
    previous = Template(fog_enabled=True, scene_keyframes=[{'time': 0, 'yaw': 8}])
    names = [f.name for f in fields(Template)
             if f.name not in {'montage_fx', 'smart_highlight_enabled', 'smart_highlight_style', 'highlight_pulse'}]
    restored = Template(*(getattr(previous, name) for name in names))
    assert restored.fog_enabled
    assert restored.scene_keyframes == previous.scene_keyframes
    assert restored.montage_fx == 'cut'


def setup_montage(tmp_path, monkeypatch):
    clips = [tmp_path / 'one.mp4', tmp_path / 'two.mp4']
    raw_bytes = b'original audio-bearing montage' * 100
    dst = tmp_path / 'montage.mp4'
    def concat(paths, target):
        assert paths == clips
        Path(target).write_bytes(raw_bytes)
    monkeypatch.setattr(montage_fx, 'get_duration', lambda *a, **k: 1)
    return clips, dst, concat, raw_bytes


def test_nvenc_failure_retries_cpu_without_forcing_fps_or_changing_audio(tmp_path, monkeypatch):
    clips, dst, concat, _ = setup_montage(tmp_path, monkeypatch)
    monkeypatch.setattr(effects, 'encoder_args', lambda fps: ['-c:v', 'h264_nvenc', '-r', str(fps)])
    commands, logs = [], []
    def run(cmd, **kwargs):
        commands.append(cmd)
        if len(commands) == 1:
            return SimpleNamespace(returncode=1, stderr='NVENC driver unavailable')
        Path(cmd[-1]).write_bytes(b'encoded video/audio' * 100)
        return SimpleNamespace(returncode=0, stderr='')
    monkeypatch.setattr(montage_fx.subprocess, 'run', run)
    assert montage_fx.render_montage(clips, dst, 'flash', concat=concat, logger=logs.append) == 'flash'
    assert len(commands) == 2
    for cmd in commands:
        assert '-r' not in cmd
        assert cmd[cmd.index('-c:a') + 1] == 'copy'
        assert '0:v:0' in cmd and '0:a?' in cmd
    assert 'libx264' in commands[1]
    assert any('NVENC driver unavailable' in msg for msg in logs)
    assert 'エンコーダー=libx264' in logs[-1] and '映像フィルター=CPU eq' in logs[-1]
    assert not dst.with_name('montage__joined_raw.mp4').exists()


@pytest.mark.parametrize('failure', ['nonzero', 'timeout', 'empty'])
def test_failed_effect_preserves_original_audio_video(tmp_path, monkeypatch, failure):
    clips, dst, concat, original = setup_montage(tmp_path, monkeypatch)
    def run(cmd, **kwargs):
        Path(cmd[-1]).write_bytes(b'partial')
        if failure == 'timeout':
            raise subprocess.TimeoutExpired(cmd, 900)
        return SimpleNamespace(returncode=int(failure == 'nonzero'), stderr='filter failed')
    monkeypatch.setattr(montage_fx.subprocess, 'run', run)
    logs = []
    assert montage_fx.render_montage(clips, dst, 'dark', concat=concat,
                                    encoder=['-c:v', 'libx264'], logger=logs.append) == 'cut (fallback)'
    assert dst.read_bytes() == original
    assert any('通常連結で保存' in msg for msg in logs)
    assert not dst.with_name('montage__joined_raw.mp4').exists()


def test_software_failure_does_not_claim_gpu_failure(tmp_path, monkeypatch):
    clips, dst, concat, original = setup_montage(tmp_path, monkeypatch)
    monkeypatch.setattr(effects, 'encoder_args', lambda fps: ['-c:v', 'libx264', '-r', str(fps)])
    calls, logs = [], []
    def run(cmd, **kwargs):
        calls.append(cmd)
        return SimpleNamespace(returncode=1, stderr='eq not available')
    monkeypatch.setattr(montage_fx.subprocess, 'run', run)
    assert montage_fx.render_montage(clips, dst, 'flash', concat=concat, logger=logs.append) == 'cut (fallback)'
    assert len(calls) == 1 and dst.read_bytes() == original
    assert not any('GPUエンコード失敗' in msg for msg in logs)


def test_duration_works_with_bundled_ffmpeg_without_ffprobe(monkeypatch):
    def run(cmd, **kwargs):
        if cmd[0] == 'missing-ffprobe':
            raise FileNotFoundError
        return SimpleNamespace(stderr='Duration: 00:01:02.35, start: 0.0', returncode=1)
    monkeypatch.setattr(montage_fx.subprocess, 'run', run)
    assert montage_fx.get_duration(Path('clip.mp4'), ffprobe='missing-ffprobe') == 62.35


def test_single_clip_does_not_reencode(tmp_path, monkeypatch):
    clips, dst, _, original = setup_montage(tmp_path, monkeypatch)
    def concat(paths, target):
        assert paths == clips[:1]
        Path(target).write_bytes(original)
    monkeypatch.setattr(montage_fx.subprocess, 'run', lambda *a, **k: pytest.fail('unexpected encode'))
    assert montage_fx.render_montage(clips[:1], dst, 'flash', concat=concat) == 'cut'
    assert dst.read_bytes() == original
