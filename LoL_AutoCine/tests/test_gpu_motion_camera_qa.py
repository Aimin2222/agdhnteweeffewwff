"""Recording reuse, cancellation, cache lifecycle and GPU animation contracts."""
import json
from pathlib import Path
from types import SimpleNamespace
from threading import Event

import pytest
from core import camera, camera_qa as qa, montage_fx, gpu_full
from core.effects import Template
from core.kill_icons import MOTION_STYLES


def cases():
    return [(side, SimpleNamespace(label=lambda: side), SimpleNamespace(time=20), mode, mode)
            for side in ('RED', 'BLUE') for mode, _ in qa.QA_MODES]


@pytest.mark.parametrize('cancel_after', [None, 2])
def test_qa_records_once_reuses_clips_and_preserves_audio_encoder(tmp_path, monkeypatch, cancel_after):
    stop = Event(); recorded = []; montages = []; audio = object()
    original = Template(fps=144, capture_fps=144, pre=9, post=0.2, encoder_policy='gpu')
    snapshot = original.to_dict()
    monkeypatch.setattr(qa, 'get_duration', lambda *a, **k: 2.0)
    monkeypatch.setattr(qa, 'render_badge_motion', lambda source, dest, *a, **k: (Path(dest).write_bytes(b'badge') and {'gpu_effects_confirmed': True}))
    monkeypatch.setattr(qa, 'plan_eight_cases', lambda *a: cases())
    def record(api, source, player, scenes, tpl, dest, merge, **kw):
        assert kw['audio_factory'] is audio and kw['stop'] is stop
        assert tpl.fps == tpl.capture_fps == 60 and tpl.pre == 3 and tpl.post == 1
        assert not merge and not tpl.merge_multikill and not tpl.smart_montage
        assert tpl.kill_icon_style == 'off' and tpl.camera_side == 'auto'
        kw['log']('SMART_CAMERA_DECISION ' + json.dumps({'mode':tpl.camera_control_mode, 'style':tpl.style}))
        p = Path(dest).with_suffix('.mp4'); p.write_bytes(b'clip')
        recorded.append(p)
        if len(recorded) == cancel_after: stop.set()
        return SimpleNamespace(outputs=[p], failed=[])
    def montage(clips, dest, **kw):
        assert list(clips) == [recorded[1], recorded[5]] and kw['encoder_policy'] == 'gpu'
        montages.append(kw['style']); Path(dest).write_bytes(b'montage')
        return kw['style']
    monkeypatch.setattr(qa, 'run_auto_edit', record)
    monkeypatch.setattr(montage_fx, 'render_montage', montage)
    report = qa.run_camera_record_test(None, None, [], [], None, original, tmp_path,
                                      stop=stop, audio_factory=audio)
    data = json.loads(report.read_text())
    assert data['version'] == (Path(qa.__file__).parents[1] / 'VERSION.txt').read_text().strip()
    assert original.to_dict() == snapshot
    assert data['completed_clips'] == (cancel_after or 8)
    assert data['canceled'] is bool(cancel_after)
    assert data['camera_control_mode'] is None
    assert all(row['camera_control_mode'] is None and row['camera_decisions'][0]['mode'] is None
               for row in data['outputs'])
    assert montages == ([] if cancel_after else list(montage_fx.MONTAGE_LABELS))
    assert len(recorded) == (cancel_after or 8)


def test_qa_reports_capture_failure_and_transition_fallback(tmp_path, monkeypatch):
    monkeypatch.setattr(qa, 'get_duration', lambda *a, **k: 2.0)
    monkeypatch.setattr(qa, 'render_badge_motion', lambda source, dest, *a, **k: (Path(dest).write_bytes(b'badge') and {'gpu_effects_confirmed': True}))
    monkeypatch.setattr(qa, 'plan_eight_cases', lambda *a: cases())
    count = 0
    def record(*args, **kw):
        nonlocal count
        count += 1
        if count == 1: raise RuntimeError('camera unavailable')
        p = Path(args[5]).with_suffix('.mp4'); p.write_bytes(b'clip')
        return SimpleNamespace(outputs=[p], failed=[])
    def montage(clips, dest, **kw):
        Path(dest).write_bytes(b'clip'); return 'cut'
    monkeypatch.setattr(qa, 'run_auto_edit', record)
    monkeypatch.setattr(montage_fx, 'render_montage', montage)
    data = json.loads(qa.run_camera_record_test(None, None, [], [], None, Template(), tmp_path).read_text())
    assert data['completed_clips'] == 7 and 'camera unavailable' in data['outputs'][0]['failed'][0][1]
    assert len(data['montage_tests']) == len(montage_fx.MONTAGE_LABELS)
    assert all(row['failed'] for row in data['montage_tests'] if row['style'] != 'cut')


def test_one_click_qa_adds_fixed_and_full_auto_per_side_without_changing_template(tmp_path, monkeypatch):
    stop=Event();recorded=[]
    original=Template(camera_control_mode='fixed_auto', style='fps')
    snapshot=original.to_dict()
    monkeypatch.setattr(qa,'plan_eight_cases',lambda *a,**k:cases())
    def record(api,source,player,scenes,tpl,dest,merge,**kw):
        recorded.append((player.label(),tpl.style,tpl.camera_control_mode,str(dest)))
        p=Path(dest).with_suffix('.mp4');p.write_bytes(b'clip')
        if len(recorded)==12:
            stop.set()  # keep this test focused on the recording plan
        return SimpleNamespace(outputs=[p],failed=[])
    monkeypatch.setattr(qa,'run_auto_edit',record)
    report=qa.run_camera_record_test(None,None,[],[],None,original,tmp_path,
                                     stop=stop,include_smart_modes=True)
    data=json.loads(report.read_text())
    assert data['expected_clips']==12 and data['completed_clips']==12
    assert data['camera_control_mode']=='mixed_manual_fixed_full'
    assert all(row['camera_control_mode']=='manual' for row in data['outputs'][:8])
    assert [(row['side'],row['camera_control_mode']) for row in data['outputs'][8:]] == [
        ('RED','fixed_auto'),('RED','full_auto'),('BLUE','fixed_auto'),('BLUE','full_auto')]
    assert len({row[3] for row in recorded})==12
    assert original.to_dict()==snapshot


def test_stable_rotation_survives_recalibration_and_clears_on_replay_change():
    old_cal = dict(camera._TPS_CALIBRATION); old_rot = dict(camera._TPS_STABLE_ROTATIONS)
    try:
        camera.clear_tps_calibration()
        key = ('PlayerA', 'ORDER', 'third_cinema')
        rotation = {'x': 17.0, 'y': 180.0, 'z': 0.0}
        camera._cache_success(key, (0, 0, 0), (1, 1, 1), rotation, (0, -1), 'x', 1, lambda _: None, 'ok')
        rotation['y'] = 0
        camera.clear_tps_calibration('PlayerA', preserve_rotation=True)
        assert not camera._TPS_CALIBRATION
        assert camera._TPS_STABLE_ROTATIONS[(*key, 'x')]['y'] == 180
        guarded = camera.stabilize_non_pitch_rotation({'x': 20, 'y': 0, 'z': 0},
                     camera._TPS_STABLE_ROTATIONS[(*key, 'x')], 'x')
        assert guarded == {'x': 20, 'y': 180.0, 'z': 0}
        camera.clear_tps_calibration()
        assert not camera._TPS_STABLE_ROTATIONS
    finally:
        camera._TPS_CALIBRATION.clear(); camera._TPS_CALIBRATION.update(old_cal)
        camera._TPS_STABLE_ROTATIONS.clear(); camera._TPS_STABLE_ROTATIONS.update(old_rot)


@pytest.mark.parametrize('motion', MOTION_STYLES)
def test_motion_is_resident_in_gpu_badge_stage(tmp_path, motion):
    from PIL import Image
    from core.effects import FFMPEG
    p = tmp_path / 'badge.png'; Image.new('RGBA', (96, 48), (255, 0, 0, 255)).save(p)
    tpl = Template(grade='standard', grade_strength=0, bloom=0, vignette=0, grain=0,
                   transition='cut', kill_icon_motion=motion, kill_icon_style='simple')
    stage = gpu_full.GPUFullStage(tpl, 1, [], ffmpeg=FFMPEG, badge_index=1, lut_index=2,
                                  badges=[(p, .45)], size=(320, 180))
    try:
        assert ('kill_icon_motion' in stage.effects) is (motion != 'instant')
        assert 'kernel=badge_0' in stage.graph and 'overlay=' not in stage.graph
        assert stage.graph.count('hwdownload') == 1
        if motion != 'instant': assert '0.350f' in stage.path.read_text()
    finally: stage.close()
