"""QA hints must use observed events, remain advisory and survive missing identity data."""
import hashlib
import json
from pathlib import Path
from threading import Event
from types import SimpleNamespace
from zipfile import ZipFile
import subprocess
import pytest
from PIL import Image
from core import camera_qa, qa_visual, jobs
from core.effects import Template, FFMPEG


@pytest.mark.parametrize('version',['5.10.26-test','5.10.23-test'])
def test_identity_compares_installed_version_and_exact_code_bytes(tmp_path,version):
    (tmp_path/'core').mkdir();(tmp_path/'VERSION.txt').write_text(version)
    (tmp_path/'core/camera.py').write_bytes(b'CAMERA\r\n');(tmp_path/'core/camera_tuning.py').write_bytes(b'TUNING\n')
    identity=camera_qa.camera_build_identity(tmp_path)
    digest=hashlib.sha256(b'CAMERA\r\nTUNING\n').hexdigest()
    assert identity['installed_version']==version
    assert identity['qa_build_version']=='5.10.26-test'
    assert identity['version_mismatch']==(version!='5.10.26-test')
    assert identity['camera_code_sha256']==digest and identity['camera_code_fingerprint']==digest[:16]
    (tmp_path/'core/camera_tuning.py').write_bytes(b'CHANGED')
    assert camera_qa.camera_build_identity(tmp_path)['camera_code_fingerprint']!=digest[:16]


def test_missing_identity_keeps_unknown_and_reports_errors(tmp_path):
    identity=camera_qa.camera_build_identity(tmp_path)
    assert identity['installed_version']=='unknown' and identity['version_mismatch']
    assert identity['camera_code_fingerprint'] is None and len(identity['identity_errors'])==2


@pytest.mark.parametrize('middle_only',[False,True])
def test_single_middle_sky_warns_but_is_never_a_recording_failure(monkeypatch,tmp_path,middle_only):
    frames=[Image.new('RGB',(320,180),(90,110,90)) for _ in range(3)]
    samples=[]
    monkeypatch.setattr(qa_visual,'get_duration',lambda *a,**kw:8.)
    monkeypatch.setattr(qa_visual,'frame_at',lambda path,t:samples.append(t) or frames[len(samples)-1])
    ratios=iter([.1,.538,.1] if middle_only else [.538,.538,.1])
    monkeypatch.setattr(qa_visual,'flat_upper_background_ratio',lambda _image:next(ratios))
    rows=[{'number':9,'side':'BLUE','mode':'lolnam_cinema','outputs':['clip.mp4'],
           'event_time':200,'recording_timing':{'event_video_seconds':[5.25]}}]
    result=qa_visual.make_qa_contact_sheets(tmp_path,rows,[]);row=result['camera'][0]
    assert samples==[4.25,5.25,6.25] and row['event_mapping_verified']
    assert row['kill_sample_basis']=='recording_event_observation'
    assert row['kill_frame_needs_human_review'] and row['framing_needs_human_review']
    assert row['suspected_sky_or_empty_frame']==(not middle_only)
    assert 'failed' not in row and rows[0]['outputs']==['clip.mp4']


@pytest.mark.parametrize('value',[None,float('nan'),999])
def test_unmapped_or_invalid_event_uses_explicit_fraction_fallback(monkeypatch,tmp_path,value):
    monkeypatch.setattr(qa_visual,'get_duration',lambda *a,**kw:1.)
    samples=[];monkeypatch.setattr(qa_visual,'frame_at',lambda path,t:samples.append(t) or Image.new('RGB',(320,180)))
    result=qa_visual.make_qa_contact_sheets(tmp_path,[{'outputs':['clip.mp4'],
        'recording_timing':{'event_video_seconds':[] if value is None else [value]}}],[])
    assert samples==[.2,.5,.82]
    assert not result['camera'][0]['event_mapping_verified']
    assert result['camera'][0]['kill_sample_basis']=='duration_fraction_fallback'


def test_actual_qa_recording_observes_slow_event_without_enabling_effects(monkeypatch,tmp_path):
    director=SimpleNamespace(start=lambda:None,stop=lambda:None,errors=0,api_calls=0,
        api_slow_calls=0,max_api_latency_ms=0,max_clock_drift=0)
    recorder=SimpleNamespace(start=lambda:None,stop=lambda:8.,started_perf=100.)
    monkeypatch.setattr(jobs,'CameraDirector',lambda *a:director)
    monkeypatch.setattr(jobs,'ClipRecorder',lambda *a,**kw:recorder)
    monkeypatch.setattr(jobs,'_prepare_clip_capture',lambda *a:(jobs.CameraPlan(),SimpleNamespace(third=False,v=None)))
    monkeypatch.setattr(jobs,'apply_fx',lambda *a,**kw:{})
    monkeypatch.setattr(jobs,'restore_fx',lambda *a:None)
    monkeypatch.setattr(jobs,'restore_mirror_camera',lambda *a:None)
    def play(*a,observe=None,**kw):
        assert observe is not None
        observe(11.,102.);observe(12.,105.);observe(13.,108.)
    monkeypatch.setattr(jobs,'_play_until',play)
    logs=[];template=Template(name='CameraQA test',hide_hud=False,kill_icon_style='off',smart_composition=False)
    api=SimpleNamespace(set_playback=lambda **kw:None)
    take=jobs.record_one_clip(api,None,None,template,10,13,[SimpleNamespace(time=12)],tmp_path/'raw.mp4',log=logs.append)
    assert take.effect_events is None and take.qa_event_times==[(5.,5.42)]
    timing=json.loads(next(s.split(' ',1)[1] for s in logs if s.startswith('CAMERA_QA_TIMING ')))
    assert timing['event_video_seconds']==[5.] and timing['event_replay_times']==[12.]
    assert timing['recording_duration']==8.


def test_report_identity_notes_and_final_zip_are_consistent(monkeypatch,tmp_path):
    monkeypatch.setattr(camera_qa,'plan_eight_cases',lambda *a:[])
    monkeypatch.setattr(camera_qa,'assemble_side_reels',lambda *a,**kw:{})
    report=camera_qa.run_camera_record_test(None,None,[],[],None,Template(),tmp_path)
    data=json.loads(report.read_text(encoding="utf-8"))
    assert data['version']==data['installed_version']=='5.10.26-test'
    assert not data['version_mismatch']
    notes=(report.parent/'QA_Support/READ_ME_FIRST_JA.md').read_text(encoding="utf-8")
    assert data['camera_code_fingerprint'] in notes and '時間割合' in notes
    with ZipFile(data['qa_archives'][0]) as z:
        assert z.testzip() is None and z.read('results.json')==report.read_bytes()
        assert z.read('QA_Support/READ_ME_FIRST_JA.md')==(report.parent/'QA_Support/READ_ME_FIRST_JA.md').read_bytes()


def test_real_mp4_frames_generate_advisory_metadata_without_mutation(tmp_path):
    video=tmp_path/'単色 60fps.mp4'
    subprocess.run([FFMPEG,'-y','-loglevel','error','-f','lavfi','-i',
        'color=c=0x54735f:s=320x180:r=60:d=2','-c:v','libx264','-pix_fmt','yuv420p',str(video)],
        check=True,capture_output=True,timeout=30)
    before=video.read_bytes()
    report=qa_visual.make_qa_contact_sheets(tmp_path/'review',[{'number':10,'side':'BLUE',
        'mode':'geo_aim','outputs':[str(video)],'recording_timing':{'event_video_seconds':[.75]}}],[])
    row=report['camera'][0]
    assert row['sample_seconds']==[0,.75,1.75] and row['event_mapping_verified']
    assert row['suspected_sky_or_empty_frame'] and row['framing_needs_human_review']
    assert video.read_bytes()==before and len(report['images'])==2
