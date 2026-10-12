"""Actual setup scope, unchanged v23 geometry, ZIP bounds and real frames."""
import json
import math
import subprocess
from pathlib import Path
from types import SimpleNamespace
from zipfile import ZipFile, ZIP_STORED

import pytest
from core import camera, jobs
from core.camera_tuning import target_center_rotation, yaw_alignment_error
from core.effects import Template, FFMPEG
from core.players import Player
from tools import reference_video_review as review


def setup(monkeypatch, team, style, side='auto'):
    monkeypatch.setattr(jobs.time,'sleep',lambda _:None)
    monkeypatch.setattr(jobs,'attach_to_player',lambda _a,_p,style,**kw:
        camera.RigInfo(mode='fps',third=style!='fps',h=(-.5,-math.sqrt(.75)),
            v=(7500,1900,-9000),rot={'x':0.,'y':42.,'z':0.},pitch_axis='y',pitch_sign=1.))
    api=SimpleNamespace(set_playback=lambda **kw:None,seek=lambda t:t)
    logs=[]
    p,_=jobs._setup_clip(api,Player(0,'Hero','Hero#JP','Hero','Hero',team),
        Template(name='CameraQA scope',style=style,camera_side=side,cam_height=170),
        10,[SimpleNamespace(time=11)],logs.append)
    evidence=json.loads(next(v.split(' ',1)[1] for v in logs if v.startswith('CAMERA_QA_POSE ')))
    return p,evidence


@pytest.mark.parametrize('team',['ORDER','CHAOS'])
@pytest.mark.parametrize('style',['third','third_cinema','fps','lolnam_cinema','geo_aim'])
def test_real_setup_centers_only_red_auto_third_and_fps(monkeypatch,team,style):
    p,evidence=setup(monkeypatch,team,style)
    expected=team=='CHAOS' and style in ('third','fps')
    assert p._live_red_target_center==evidence['red_target_center_enabled']==expected
    if expected:
        for t in (10,11,12):
            assert p.rotation_at(t)==target_center_rotation(p.offset_at(t))
            assert yaw_alignment_error(p.offset_at(t),p.rotation_at(t))<1e-6
        assert evidence['initial_camera_rotation']==evidence['target_center_rotation']
        assert evidence['applied_angle_bias']=={}
    else:
        assert evidence['target_center_rotation'] is None


@pytest.mark.parametrize('limit,value',[('ZIP_MAX_VIDEOS',1),('ZIP_MAX_VIDEO_BYTES',3),('ZIP_MAX_TOTAL_BYTES',6)])
def test_zip_limits_fail_before_extraction_or_output(monkeypatch,tmp_path,limit,value):
    source=tmp_path/'large.zip'
    with ZipFile(source,'w') as z:
        z.writestr('one.mp4',b'1234');z.writestr('two.mp4',b'5678')
    monkeypatch.setattr(review,limit,value)
    monkeypatch.setattr(review.zipfile.ZipFile,'open',lambda *a,**kw:pytest.fail('Preflight must reject before extraction'))
    with pytest.raises(ValueError,match='上限'):review.create_sheets(source,tmp_path/'out')
    assert not (tmp_path/'out').exists()


def test_crc_corruption_is_reported_without_output_and_temp_is_cleaned(monkeypatch,tmp_path):
    source=tmp_path/'broken.zip'
    with ZipFile(source,'w',compression=ZIP_STORED) as z:z.writestr('one.mp4',b'ORIGINALVIDEO')
    data=bytearray(source.read_bytes());start=data.index(b'ORIGINALVIDEO');data[start]^=1;source.write_bytes(data)
    temps=[];original=review.tempfile.TemporaryDirectory
    def temp(**kw):
        result=original(dir=tmp_path,**kw);temps.append(Path(result.name));return result
    monkeypatch.setattr(review.tempfile,'TemporaryDirectory',temp)
    with pytest.raises(ValueError,match='破損'):review.create_sheets(source,tmp_path/'out')
    assert temps and all(not p.exists() for p in temps) and not (tmp_path/'out').exists()
    assert source.read_bytes()==data


def test_real_unicode_zip_flattens_paths_and_maps_duplicate_names(monkeypatch,tmp_path):
    video=tmp_path/'元 動画.mp4'
    subprocess.run([FFMPEG,'-y','-loglevel','error','-f','lavfi','-i',
        'testsrc2=size=320x180:rate=60:duration=1','-c:v','libx264','-pix_fmt','yuv420p',str(video)],
        check=True,capture_output=True,timeout=30)
    source=tmp_path/'参照 動画.zip';media=video.read_bytes()
    names=['../映像.mp4',r'C:\outside\映像.mp4']
    with ZipFile(source,'w') as z:
        for name in names:z.writestr(name,media)
        z.writestr('ignored.exe',b'not executed')
    original=source.read_bytes();temps=[];tempdir=review.tempfile.TemporaryDirectory
    def temp(**kw):
        result=tempdir(dir=tmp_path,**kw);temps.append(Path(result.name));return result
    monkeypatch.setattr(review.tempfile,'TemporaryDirectory',temp)
    result=review.create_sheets(source,tmp_path/'sheets',logger=lambda _:None)
    with ZipFile(result) as z:
        assert z.testzip() is None
        mapping=json.loads(z.read('reference_archive_names.json'))
        assert [r['archived_name'] for r in mapping['items']]==names
        assert len({r['extracted_name'] for r in mapping['items']})==2
        assert all('/' not in r['extracted_name'] and '\\' not in r['extracted_name'] for r in mapping['items'])
        rows=json.loads(z.read('reference_review.json'))['items']
        assert len(rows)==2 and all(len(r['samples'])==6 and not r['errors'] for r in rows)
        assert len([n for n in z.namelist() if n.endswith('.jpg')])==2
        assert not any(n.endswith(('.mp4','.zip','.exe')) for n in z.namelist())
    assert all(not p.exists() for p in temps)
    assert source.read_bytes()==original and video.read_bytes()==media
    assert not (tmp_path.parent/'映像.mp4').exists()


def test_bad_zip_cli_fails_before_opening_explorer(monkeypatch,tmp_path):
    source=tmp_path/'invalid.zip';source.write_bytes(b'notzip')
    monkeypatch.setattr('sys.argv',['reference_video_review',str(source),'--open-output'])
    monkeypatch.setattr(review.subprocess,'Popen',lambda *a,**kw:pytest.fail('No explorer on failure'))
    with pytest.raises(ValueError,match='ZIP'):review.main()
    assert not (tmp_path/'_AutoCineReferenceReview_invalid').exists()


@pytest.mark.parametrize('ci',[False,True])
def test_picker_success_opens_actual_folder_only_outside_ci(monkeypatch,tmp_path,ci,capsys):
    source=tmp_path/'日本語.zip';output=tmp_path/'日本語 結果'/'ReferenceReview_contact_sheets.zip'
    monkeypatch.setattr(review,'choose_source',lambda:source)
    monkeypatch.setattr(review,'create_sheets',lambda *a,**kw:output)
    monkeypatch.setattr('sys.argv',['reference_video_review','--open-output'])
    # A module-local OS substitute avoids changing pathlib's host path type.
    monkeypatch.setattr(review,'os',SimpleNamespace(name='nt',environ={'CI':'1'} if ci else {}))
    calls=[];monkeypatch.setattr(review.subprocess,'Popen',lambda command:calls.append(command))
    review.main()
    assert calls==([] if ci else [['explorer.exe',str(output.resolve().parent)]])
    assert str(output.resolve()) in capsys.readouterr().out

# Numerical golden values produced by the preserved v5.10.23 _setup_clip.
BASELINE = {'ORDER:third:auto': [{'offset': [-703.0912777321, 884.1625594140633, -939.3350463532254], 'rotation': {'x': 40.0, 'y': 36.81481481481482, 'z': 0.0}}, {'offset': [-672.9906234523706, 884.1625594140633, -961.1302174396362], 'rotation': {'x': 40.0, 'y': 35.0, 'z': 0.0}}, {'offset': [-738.0136202000837, 884.1625594140633, -912.1532604390229], 'rotation': {'x': 40.0, 'y': 38.975957926371144, 'z': 0.0}}], 'ORDER:third_cinema:auto': [{'offset': [-492.07315517139676, 466.62261281396235, -606.857225075144], 'rotation': {'x': 30.847656250000004, 'y': 39.03703703703704, 'z': 0.0}}, {'offset': [-435.61674579582296, 376.21573155410147, -557.5640086245431], 'rotation': {'x': 28.000000000000004, 'y': 38.0, 'z': 0.0}}, {'offset': [-515.9468669256152, 489.92627741413634, -608.9872465073983], 'rotation': {'x': 31.542274052478135, 'y': 40.271975957926365, 'z': 0.0}}], 'ORDER:fps:auto': [{'offset': [-578.7721471190265, 785.4772188123028, -1002.4627648158829], 'rotation': {'x': 34.159719403199304, 'y': 30.000000000000004, 'z': 0.0}}, {'offset': [-578.7721471190265, 785.4772188123028, -1002.4627648158829], 'rotation': {'x': 34.159719403199304, 'y': 30.000000000000004, 'z': 0.0}}, {'offset': [-578.7721471190265, 785.4772188123028, -1002.4627648158829], 'rotation': {'x': 34.159719403199304, 'y': 30.000000000000004, 'z': 0.0}}], 'ORDER:lolnam_cinema:auto': [{'offset': [-607.6334344931392, 534.6235109244841, -809.6458181531294], 'rotation': {'x': 30.339843749999993, 'y': 36.88796750694375, 'z': 0.0}}, {'offset': [-298.5158081198433, 300.0, -612.0481081602628], 'rotation': {'x': 26.27592342655986, 'y': 26.0, 'z': 0.0}}, {'offset': [-601.74224511797, 552.807735231792, -801.7960578029068], 'rotation': {'x': 31.374052478134104, 'y': 36.887967506943745, 'z': 0.0}}], 'ORDER:geo_aim:auto': [{'offset': [-611.7713469542025, 688.9578385044649, -679.4409141412494], 'rotation': {'x': 39.5, 'y': 42.0, 'z': 0.0}}, {'offset': [-611.7713469542025, 688.9578385044649, -679.4409141412494], 'rotation': {'x': 39.5, 'y': 42.0, 'z': 0.0}}, {'offset': [-611.7713469542025, 688.9578385044649, -679.4409141412494], 'rotation': {'x': 39.5, 'y': 42.0, 'z': 0.0}}], 'CHAOS:third_cinema:auto': [{'offset': [217.31104225687918, 605.1593979030907, 808.9238755153648], 'rotation': {'x': -194.96296296296296, 'y': 35.84765625000001, 'z': 0.0}}, {'offset': [209.6580302232922, 562.7994789985681, 840.8924301822614], 'rotation': {'x': -196.0, 'y': 33.0, 'z': 0.0}}, {'offset': [232.6216767933817, 615.2692696107968, 796.9508790975968], 'rotation': {'x': -193.72802404207363, 'y': 36.54227405247813, 'z': 0.0}}], 'CHAOS:lolnam_cinema:auto': [{'offset': [219.25852693201097, 634.4823573932996, 958.2577088258909], 'rotation': {'x': -200.11203249305626, 'y': 29.83984375, 'z': 0.0}}, {'offset': [131.52705253508395, 515.2639158872693, 935.8636072825733], 'rotation': {'x': -211.0, 'y': 25.6, 'z': 0.0}}, {'offset': [216.66849192295547, 652.1219223393892, 946.9380988281187], 'rotation': {'x': -200.11203249305626, 'y': 30.874052478134104, 'z': 0.0}}], 'CHAOS:geo_aim:auto': [{'offset': [300.92599601629973, 876.8287465726479, 926.1549838474323], 'rotation': {'x': -196.0, 'y': 42.0, 'z': 0.0}}, {'offset': [300.92599601629973, 876.8287465726479, 926.1549838474323], 'rotation': {'x': -196.0, 'y': 42.0, 'z': 0.0}}, {'offset': [300.92599601629973, 876.8287465726479, 926.1549838474323], 'rotation': {'x': -196.0, 'y': 42.0, 'z': 0.0}}], 'CHAOS:third:blue': [{'offset': [-412.34721245867433, 884.6575746670464, -891.7954709246844], 'rotation': {'x': -1.1851851851851851, 'y': 42.0, 'z': 0.0}}, {'offset': [-383.89793411667404, 884.6575746670464, -904.4068563236176], 'rotation': {'x': -3.0, 'y': 42.0, 'z': 0.0}}, {'offset': [-445.68363215246757, 884.6575746670464, -875.6114923958016], 'rotation': {'x': 0.9759579263711475, 'y': 42.0, 'z': 0.0}}], 'CHAOS:third:red': [{'offset': [412.34721245867416, 884.6575746670464, 891.7954709246847], 'rotation': {'x': -181.1851851851852, 'y': 42.0, 'z': 0.0}}, {'offset': [383.8979341166742, 884.6575746670464, 904.4068563236176], 'rotation': {'x': -183.0, 'y': 42.0, 'z': 0.0}}, {'offset': [445.6836321524675, 884.6575746670464, 875.6114923958016], 'rotation': {'x': -179.02404207362886, 'y': 42.0, 'z': 0.0}}], 'CHAOS:fps:blue': [{'offset': [-671.0401705727845, 883.596775434554, -1162.2756693517483], 'rotation': {'x': -0.0, 'y': 36.360045776422524, 'z': 0.0}}, {'offset': [-671.0401705727845, 883.596775434554, -1162.2756693517483], 'rotation': {'x': -0.0, 'y': 36.360045776422524, 'z': 0.0}}, {'offset': [-671.0401705727845, 883.596775434554, -1162.2756693517483], 'rotation': {'x': -0.0, 'y': 36.360045776422524, 'z': 0.0}}], 'CHAOS:fps:red': [{'offset': [671.0401705727846, 883.596775434554, 1162.2756693517483], 'rotation': {'x': -180.0, 'y': 36.360045776422524, 'z': 0.0}}, {'offset': [671.0401705727846, 883.596775434554, 1162.2756693517483], 'rotation': {'x': -180.0, 'y': 36.360045776422524, 'z': 0.0}}, {'offset': [671.0401705727846, 883.596775434554, 1162.2756693517483], 'rotation': {'x': -180.0, 'y': 36.360045776422524, 'z': 0.0}}]}

@pytest.mark.parametrize("key",list(BASELINE))
def test_approved_and_manual_pose_matches_preserved_v23(monkeypatch,key):
    team,style,side=key.split(":")
    plan,evidence=setup(monkeypatch,team,style,side)
    assert not plan._live_red_target_center
    for t,expected in zip((10,11,12),BASELINE[key]):
        assert plan.offset_at(t)==pytest.approx(expected["offset"])
        assert plan.rotation_at(t)==pytest.approx(expected["rotation"])
