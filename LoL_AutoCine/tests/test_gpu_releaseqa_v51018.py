"""Archive restoration, final reports, data-only plans and real camera geometry."""
from pathlib import Path
from zipfile import ZipFile
import json
import math
from types import SimpleNamespace
import pytest
from core import qa_plan, qa_visual, camera_qa
from core.qa_package import split_test_results
from core.camera import CameraPlan, RigInfo
from core.effects import Template


def test_large_video_split_restores_bytes_keeps_original_and_final_report(tmp_path):
    folder = tmp_path / 'QA'; folder.mkdir()
    data = bytes(range(256)) * 13000
    original = folder / 'large.mp4'; original.write_bytes(data)
    report = folder / 'results.json'; report.write_text('{"qa_archives":[]}')
    def update(paths): report.write_text(json.dumps({'qa_archives':[str(p) for p in paths]}))
    archives = split_test_results(folder, max_bytes=2_000_000, report_update=update)
    assert len(archives) >= 2 and original.read_bytes() == data
    pieces = {}; found_report = False
    for archive in archives:
        assert archive.stat().st_size <= 2_000_000
        with ZipFile(archive) as z:
            assert z.testzip() is None and not any(n.endswith('.zip') for n in z.namelist())
            for name in z.namelist():
                if name.startswith('large.mp4.part'): pieces[name] = z.read(name)
                if name == 'results.json':
                    assert z.read(name) == report.read_bytes(); found_report = True
    assert found_report and b''.join(pieces[n] for n in sorted(pieces)) == data
    first = {p:p.read_bytes() for p in archives}
    again = split_test_results(folder, max_bytes=2_000_000)
    assert not set(again) & set(archives)
    assert all(p.read_bytes() == content for p,content in first.items())
    assert not list(folder.glob('.qa_split_*'))


def test_archive_never_includes_external_symlink(tmp_path):
    private = tmp_path / 'private.json'; private.write_text('PRIVATE')
    folder = tmp_path/'QA'; folder.mkdir(); (folder/'results.json').write_text('{}')
    (folder/'outside.json').symlink_to(private)
    archives = split_test_results(folder, max_bytes=2_000_000)
    with ZipFile(archives[0]) as z: assert 'outside.json' not in z.namelist()


@pytest.mark.parametrize('bad', [ {'schema_version':True},
    {'badge_motions':['run_code']}, {'include_visual_comparison':'false'}, {'max_zip_mb':999}])
def test_plan_rejects_unknown_operations_and_wrong_types(bad):
    with pytest.raises(ValueError): qa_plan.validate_plan({'schema_version':1}|bad)


def test_remote_plan_failure_falls_back_to_bundled_data(monkeypatch):
    monkeypatch.setattr(qa_plan, 'urlopen', lambda *a,**k: (_ for _ in ()).throw(OSError('offline')))
    config, source = qa_plan.load_qa_plan()
    assert source == 'bundled' and config['schema_version'] == 1
    assert set(config['camera_modes']) <= set(qa_plan.ALLOWED_CAMERA)


@pytest.mark.parametrize('heading', [0,90,180,270])
def test_geo_aim_rotates_from_actual_relative_offset_without_changing_other_modes(heading):
    rig = RigInfo(mode='fps', third=True, h=(0,-1), rot={'x':30,'y':0,'z':0}, pitch_axis='x')
    plan = CameraPlan(style='geo_aim', rig=rig, third_elev=37, third_dist=1000, side_yaw=heading)
    x,y,z = plan.offset_at(0)
    rot = plan.rotation_at(0)
    assert rot['x'] == pytest.approx(math.degrees(math.atan2(y,math.hypot(x,z))))
    assert rot['y'] == pytest.approx(math.degrees(math.atan2(-x,-z)) % 360)
    assert rot['z'] == 0
    assert CameraPlan(style='third', rig=rig, side_yaw=heading).rotation_at(0) is not None


def test_short_clip_contact_sheet_samples_inside_video(monkeypatch, tmp_path):
    from PIL import Image
    samples = []
    monkeypatch.setattr(qa_visual,'get_duration',lambda *a,**k:1.0)
    def frame(path, seconds, **kw):
        samples.append(seconds); return Image.new('RGB',(320,180))
    monkeypatch.setattr(qa_visual,'frame_at',frame)
    report = qa_visual.make_qa_contact_sheets(tmp_path,[{'number':1,'side':'RED','mode':'third','outputs':['short.mp4']}],[])
    assert samples == [.2,.5,.82] and all(0 <= t < 1 for t in samples)
    assert len(report['images']) == 2


def test_qa_plan_filters_cases_keeps_gpu_policy_and_final_archive(monkeypatch,tmp_path):
    cases = [('RED',SimpleNamespace(label=lambda:'Red'),SimpleNamespace(time=20),'geo_aim','geo'),
             ('BLUE',SimpleNamespace(label=lambda:'Blue'),SimpleNamespace(time=20),'geo_aim','geo')]
    def plan(*a, modes=None): assert modes == ['geo_aim']; return cases
    monkeypatch.setattr(camera_qa,'plan_eight_cases',plan)
    def record(*a, **kw):
        p=Path(a[5]).with_suffix('.mp4');p.write_bytes(b'clip')
        kw['log']('CAMERA_QA_POSE '+json.dumps({'style':'geo_aim','third_person_enabled':True}))
        return SimpleNamespace(outputs=[p],failed=[])
    monkeypatch.setattr(camera_qa,'run_auto_edit',record)
    from core import montage_fx
    def montage(clips,dest,**kw): assert kw['style']=='cut'; dest.write_bytes(b'montage');return 'cut'
    monkeypatch.setattr(montage_fx,'render_montage',montage)
    monkeypatch.setattr(camera_qa,'get_duration',lambda *a,**k:2)
    def badge(source,dest,image,theme,motion,duration,**kw):
        assert motion == 'pop' and kw['encoder_policy']=='gpu'
        dest.write_bytes(b'badge');return {'gpu_effects_confirmed':True}
    monkeypatch.setattr(camera_qa,'render_badge_motion',badge)
    config={'schema_version':1,'camera_modes':['geo_aim'],'montage_styles':['cut'],
            'badge_motions':['pop'],'include_visual_comparison':False}
    report=camera_qa.run_camera_record_test(None,None,[],[],None,Template(encoder_policy='gpu'),tmp_path,plan=config)
    data=json.loads(report.read_text())
    assert data['expected_clips']==data['completed_clips']==2
    assert len(data['montage_tests'])==len(data['badge_motion_tests'])==1
    assert data['outputs'][0]['camera_diagnostics'][0]['geometry_validation']
    assert 'visual_qa' not in data and data['qa_archives']
    with ZipFile(data['qa_archives'][0]) as z: assert z.read('results.json')==report.read_bytes()
