"""Bounded local diagnostics must keep originals and final archive metadata intact."""
from pathlib import Path
from threading import Event
from types import SimpleNamespace
from zipfile import ZipFile
import json
import pytest
from core import qa_support, camera_qa, camera_tuning
from core.qa_package import split_test_results
from core.effects import Template
from core.camera import CameraPlan, RigInfo


def test_log_tail_is_bounded_byte_exact_and_original_remains(tmp_path):
    origin=tmp_path/'diagnostics';origin.mkdir()
    data=b'first private history'+bytes(range(256))*5000
    original=origin/'runtime.log';original.write_bytes(data)
    outside=tmp_path/'outside.log';outside.write_bytes(b'PRIVATE OUTSIDE')
    (origin/'crash.log').symlink_to(outside)
    output=tmp_path/'QA'
    report=qa_support.collect_qa_support(output,diagnostics=origin)
    tail=output/'QA_Support/runtime.log'
    assert tail.read_bytes()==data[-qa_support.TAIL_LIMIT_BYTES:]
    assert tail.stat().st_size==qa_support.TAIL_LIMIT_BYTES
    assert original.read_bytes()==data and outside.read_bytes()==b'PRIVATE OUTSIDE'
    assert report['truncated']==['runtime.log'] and not report['errors']
    assert not (output/'QA_Support/crash.log').exists()
    assert '時間割合' in (output/'QA_Support/READ_ME_FIRST_JA.md').read_text()


def test_support_write_failure_does_not_invalidate_recording(tmp_path):
    folder=tmp_path/'QA';folder.mkdir();(folder/'QA_Support').write_bytes(b'existing file')
    video=folder/'recorded.mp4';video.write_bytes(b'existing recorded clip')
    report=qa_support.collect_qa_support(folder,diagnostics=tmp_path/'absent')
    assert report['errors'] and video.read_bytes()==b'existing recorded clip'


def test_support_and_final_results_are_in_direct_archive(tmp_path):
    origin=tmp_path/'diagnostics';origin.mkdir();(origin/'runtime.log').write_bytes(b'GPU effects verified')
    folder=tmp_path/'QA';report=qa_support.collect_qa_support(folder,diagnostics=origin)
    data={'qa_support':report,'qa_archives':[]};result=folder/'results.json'
    def update(paths):
        data['qa_archives']=[str(p) for p in paths]
        result.write_text(json.dumps(data))
    update([])
    archives=split_test_results(folder,max_bytes=2_000_000,report_update=update)
    with ZipFile(archives[0]) as z:
        assert z.testzip() is None and not any(n.endswith('.zip') for n in z.namelist())
        assert z.read('results.json')==result.read_bytes()
        assert z.read('QA_Support/runtime.log')==b'GPU effects verified'
        assert 'QA_Support/READ_ME_FIRST_JA.md' in z.namelist()


def test_cancel_skips_support_and_archive_work(monkeypatch,tmp_path):
    stop=Event();stop.set()
    monkeypatch.setattr(camera_qa,'plan_eight_cases',lambda *a:[('RED',None,None,'third','third')])
    monkeypatch.setattr(camera_qa,'collect_qa_support',lambda *a,**kw:pytest.fail('No support on canceled QA'))
    monkeypatch.setattr(camera_qa,'split_test_results',lambda *a,**kw:pytest.fail('No ZIP on canceled QA'))
    p=camera_qa.run_camera_record_test(None,None,[],[],None,Template(),tmp_path,stop=stop)
    report=json.loads(p.read_text());assert report['canceled'] and report['qa_archives']==[]
    assert not (p.parent/'QA_Support').exists()


@pytest.mark.parametrize('value',[float('nan'),float('inf'),.99,1.66])
def test_fps_pullback_rejects_out_of_range_and_nonfinite(monkeypatch,value):
    monkeypatch.setitem(camera_tuning.SHOT_TUNING,('RED','fps'),{'distance':1,'angles':{},'fps_back':value})
    with pytest.raises(ValueError):camera_tuning.shot_tuning('CHAOS','fps')


def test_fps_height_is_not_multiplied_by_automatic_pullback():
    p=CameraPlan(style='fps',rig=RigInfo(mode='fps',third=False,h=(0,-1),v=(0,1800,-9000)),height=0)
    p._live_fps_recenter=True;p._live_fps_back=1.6
    base=p.third_pose_at(0)[0];before=p.offset_at(0)
    assert before==pytest.approx(tuple(v*1.6 for v in base))
    p.height=170;after=p.offset_at(0)
    assert after[1]-before[1]==pytest.approx(170)
    assert after[0]==before[0] and after[2]==before[2]



def test_archive_accepts_only_bounded_named_support_logs(tmp_path):
    folder=tmp_path/'QA';folder.mkdir();support=folder/'QA_Support';support.mkdir()
    (folder/'results.json').write_text('{}')
    (folder/'runtime.log').write_bytes(b'NOT A SUPPORT EXCERPT')
    (support/'unknown.log').write_bytes(b'UNKNOWN LOG')
    (support/'runtime.log').write_bytes(b'BOUNDED EXCERPT')
    (support/'crash.log').write_bytes(b'x'*(qa_support.TAIL_LIMIT_BYTES+1))
    archives=split_test_results(folder,max_bytes=2_000_000)
    with ZipFile(archives[0]) as z:
        assert 'QA_Support/runtime.log' in z.namelist()
        assert 'runtime.log' not in z.namelist()
        assert 'QA_Support/unknown.log' not in z.namelist()
        assert 'QA_Support/crash.log' not in z.namelist()
