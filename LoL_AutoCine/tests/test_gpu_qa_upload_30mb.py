"""Real media, cancellation and bounded archives for temporary CameraQA uploads."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from threading import Event, Timer
from zipfile import ZipFile
import pytest
from core import camera_qa, qa_upload, qa_plan
from core.effects import Template
from core.qa_package import split_test_results


def test_30mb_archive_uses_copies_preserves_originals_and_omits_raw(tmp_path):
    root = tmp_path / 'CameraQA_Test'; root.mkdir()
    originals, copies = {}, {}
    for name in ('RED/kill_001.mp4', 'BLUE/kill_001.mp4'):
        source = root / name; source.parent.mkdir(); source.write_bytes(b'original' * 4_500_000)
        originals[name] = hashlib.sha256(source.read_bytes()).hexdigest()
        copy = root / '.qa_upload' / name; copy.parent.mkdir(parents=True)
        copy.write_bytes(b'upload' * 3_900_000); copies[name] = copy
    raw = root / 'RED/raw/raw_001.mp4'; raw.parent.mkdir(); raw.write_bytes(b'raw' * 11_000_000)
    report = root / 'results.json'; report.write_text('{}')
    def update(paths): report.write_text(json.dumps({'qa_archives': [str(p) for p in paths]}))
    archives = split_test_results(root, max_bytes=30_000_000, source_overrides=copies,
                                  exclude_dirs=qa_upload.EXCLUDE_DIRS, report_update=update)
    assert len(archives) == 2
    packed = {}
    for path in archives:
        assert path.stat().st_size <= 30_000_000
        with ZipFile(path) as z:
            assert z.testzip() is None
            packed.update({name: z.read(name) for name in z.namelist()})
    assert packed['results.json'] == report.read_bytes()
    assert all(packed[name] == copy.read_bytes() for name, copy in copies.items())
    assert all(hashlib.sha256((root / name).read_bytes()).hexdigest() == digest
               for name, digest in originals.items())
    assert not any('raw/' in name or '.qa_upload/' in name or '.mp4.part' in name for name in packed)
    assert raw.stat().st_size == 33_000_000


def test_external_upload_override_is_rejected(tmp_path):
    root = tmp_path / 'QA'; root.mkdir(); (root / 'clip.mp4').write_bytes(b'original')
    outside = tmp_path / 'private.mp4'; outside.write_bytes(b'private')
    with pytest.raises(ValueError, match='inside'):
        split_test_results(root, source_overrides={'clip.mp4': outside})
    assert not list(root.glob('*.zip'))


@pytest.mark.parametrize('cap', [30, 500])
def test_cameraqa_caps_old_remote_plan_and_keeps_settings(tmp_path, monkeypatch, cap):
    monkeypatch.setattr(camera_qa, 'plan_eight_cases', lambda *a, **kw: [])
    monkeypatch.setattr(camera_qa, 'assemble_side_reels', lambda *a, **kw: {})
    observed = []
    def export(*args, **kw):
        observed.append(kw['max_bytes']); return split_test_results(*args, **kw)
    monkeypatch.setattr(camera_qa, 'split_test_results', export)
    original = Template(fps=144, capture_fps=144); snapshot = original.to_dict()
    report = camera_qa.run_camera_record_test(None, None, [], [], None, original, tmp_path,
                                            plan={'schema_version': 1, 'max_zip_mb': cap})
    data = json.loads(report.read_text())
    assert observed == [30_000_000] and original.to_dict() == snapshot
    assert data['qa_upload']['profile'] == 'dev-30mb-540p60'
    assert qa_plan.validate_plan({'schema_version': 1})['max_zip_mb'] == 30
    with ZipFile(data['qa_archives'][0]) as z: assert z.read('results.json') == report.read_bytes()


@pytest.mark.parametrize('repeats', [1, 3])
def test_real_ffmpeg_540p60_preserves_frames_audio_and_original(tmp_path, repeats):
    ffmpeg = str(qa_upload.ffmpeg_exe())
    source, destination = tmp_path / 'source.mp4', tmp_path / '.qa_upload/clip.mp4'
    subprocess.run([ffmpeg, '-nostdin', '-hide_banner', '-loglevel', 'error',
                    '-f', 'lavfi', '-i', 'testsrc2=size=1280x720:rate=60:duration=1',
                    '-f', 'lavfi', '-i', 'sine=frequency=440:sample_rate=48000:duration=1',
                    '-c:v', 'libx264', '-preset', 'ultrafast', '-c:a', 'aac', '-b:a', '192k',
                    '-shortest', str(source)], check=True, capture_output=True, timeout=30)
    if repeats > 1:
        from core.effects import concat_clips
        reel = tmp_path / 'reel.mp4'; concat_clips([source] * repeats, reel); source = reel
    original = source.read_bytes()
    metadata = qa_upload.make_upload_video(source, destination, encoder_policy='cpu')
    assert metadata['encoder'] == 'libx264' and metadata['bytes'] <= 24_000_000
    assert source.read_bytes() == original
    raw = subprocess.run([ffmpeg, '-v', 'error', '-xerror', '-i', str(destination),
                          '-map', '0:v:0', '-fps_mode', 'passthrough', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                         capture_output=True, check=True, timeout=30).stdout
    assert len(raw) == repeats * 60 * 960 * 540 * 3
    audio = [subprocess.run([ffmpeg, '-v', 'error', '-i', str(path), '-map', '0:a:0',
                             '-c:a', 'copy', '-f', 'adts', '-'], capture_output=True,
                            check=True, timeout=30).stdout for path in (source, destination)]
    assert audio[0] == audio[1] and audio[0]
    assert abs(qa_upload.get_duration(destination, ffmpeg=ffmpeg) -
               qa_upload.get_duration(source, ffmpeg=ffmpeg)) <= 1 / 60


def test_nvenc_retry_keeps_bitrate_limit_audio_mapping_and_reports_cpu(tmp_path, monkeypatch):
    from core import effects
    source = tmp_path / 'source.mp4'; source.write_bytes(b'original')
    monkeypatch.setattr(qa_upload, 'get_duration', lambda *a, **kw: 35.)
    monkeypatch.setattr(effects, 'encoder_args', lambda *a, **kw: ['-c:v', 'h264_nvenc'])
    commands = []
    def execute(cmd, stop):
        commands.append(cmd)
        if len(commands) == 1: return 1, 'driver unavailable'
        Path(cmd[-1]).write_bytes(b'output'); return 0, ''
    monkeypatch.setattr(qa_upload, '_run', execute)
    outcome = qa_upload.make_upload_video(source, tmp_path / 'upload.mp4')
    assert outcome['encoder'] == 'libx264' and 'driver unavailable' in outcome['encoder_retry_reason']
    for cmd in commands:
        assert int(cmd[cmd.index('-b:v') + 1]) <= 3_000_000
        assert cmd[cmd.index('-c:a') + 1] == 'copy' and '0:a:0?' in cmd
        assert '-shortest' not in cmd
        assert cmd[cmd.index('-fps_mode') + 1] == 'passthrough' and '-r' not in cmd


def test_cancel_reaps_process_without_overwriting_original(tmp_path, monkeypatch):
    source = tmp_path / 'source.mp4'; source.write_bytes(b'original')
    destination = tmp_path / 'upload.mp4'
    stop = Event(); processes = []; real_popen = subprocess.Popen
    monkeypatch.setattr(qa_upload, 'get_duration', lambda *a, **kw: 6.)
    def start(cmd, **kw):
        p = real_popen([sys.executable, '-c', 'import time; time.sleep(20)'], **kw)
        processes.append(p); return p
    monkeypatch.setattr(qa_upload.subprocess, 'Popen', start)
    timer = Timer(.3, stop.set); timer.start()
    try:
        with pytest.raises(qa_upload.QAUploadCanceled):
            qa_upload.make_upload_video(source, destination, stop=stop, encoder_policy='cpu')
    finally: timer.cancel(); timer.join()
    assert processes and all(p.poll() is not None for p in processes)
    assert source.read_bytes() == b'original' and not destination.exists()
    assert not list(tmp_path.glob('*.encoding.mp4'))


def test_failed_compression_keeps_original_as_archive_fallback(tmp_path, monkeypatch):
    source = tmp_path / 'clip.mp4'; source.write_bytes(b'original')
    def fail(*a, **kw): raise RuntimeError('error')
    monkeypatch.setattr(qa_upload, 'make_upload_video', fail)
    copies, report = qa_upload.prepare_upload_copies(tmp_path)
    assert copies == {} and report['files'][0]['archive_fallback'] == 'original_or_numbered_binary_parts'
    assert source.read_bytes() == b'original'


def test_repackage_existing_qa_preserves_report_and_prior_archives(tmp_path, monkeypatch):
    from tools.make_cameraqa_upload import repackage
    report = tmp_path / 'results.json'
    original = json.dumps({'kind': 'live_replay_camera_test', 'qa_archives': ['previous.zip']}).encode()
    report.write_bytes(original)
    source = tmp_path / 'clip.mp4'; source.write_bytes(b'original')
    def encode(src, dest, **kw):
        Path(dest).parent.mkdir(parents=True, exist_ok=True); Path(dest).write_bytes(b'upload')
        return {'bytes': 6, 'encoder': 'libx264'}
    monkeypatch.setattr(qa_upload, 'make_upload_video', encode)
    first = repackage(tmp_path, encoder_policy='cpu', log=lambda _m: None)
    before = first[0].read_bytes()
    again = repackage(tmp_path, encoder_policy='cpu', log=lambda _m: None)
    assert first[0].read_bytes() == before and not set(first) & set(again)
    assert source.read_bytes() == b'original'
    backups = list((tmp_path / '.qa_upload').rglob('results_original*.json'))
    assert any(p.read_bytes() == original for p in backups)
    assert (tmp_path / '.qa_upload/export002/clip.mp4').read_bytes() == b'upload'
    with ZipFile(again[0]) as z:
        assert z.read('clip.mp4') == b'upload' and z.read('results.json') == report.read_bytes()
