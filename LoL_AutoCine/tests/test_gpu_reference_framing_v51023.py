"""The reference picker must retain Unicode paths and camera changes stay scoped."""
from pathlib import Path
import json
import math
import subprocess
from zipfile import ZipFile
import pytest
from core.camera import CameraPlan, RigInfo
from core.effects import FFMPEG
from core import qa_support
from tools import reference_video_review as review


@pytest.mark.parametrize('heading',[0,180,192])
def test_red_pitch_follows_real_height_without_changing_manual_heading(heading):
    plan=CameraPlan(style='fps',team='CHAOS',rig=RigInfo(mode='fps',third=False,h=(0,-1),v=(0,1800,-9000)),height=170)
    plan._live_fps_recenter=True;plan._live_fps_back=1.6;plan._live_fps_side_heading=heading
    for height in (0,170):
        plan.height=height;x,y,z=plan.offset_at(0)
        rotation=plan.rotation_at(0)
        expected=max(18,min(52,math.degrees(math.atan2(y,math.hypot(x,z)))+3))
        assert rotation['x']==-heading and rotation['y']==pytest.approx(expected) and rotation['z']==0
    direct=CameraPlan(style='fps',team='CHAOS',rig=plan.rig)
    assert direct.rotation_at(0) is None  # old plans remain opt-in


@pytest.mark.parametrize('selected,folder',[('file',''),('', 'folder'),('', '')])
def test_picker_file_folder_cancel_and_root_cleanup(monkeypatch,tmp_path,selected,folder):
    import tkinter as tk
    from tkinter import filedialog
    roots=[];destroyed=[];original=tk.Tk
    def create_root():
        root=original();roots.append(root);destroy=root.destroy
        def close():destroyed.append(root);destroy()
        root.destroy=close;return root
    monkeypatch.setattr(tk,'Tk',create_root)
    calls=[]
    def file_dialog(**kw):assert kw['parent'] is roots[0];return str(tmp_path/'動画.mp4') if selected else ''
    def folder_dialog(**kw):
        assert kw['parent'] is roots[0];calls.append('folder')
        return str(tmp_path/'動画フォルダ') if folder else ''
    monkeypatch.setattr(filedialog,'askopenfilename',file_dialog)
    monkeypatch.setattr(filedialog,'askdirectory',folder_dialog)
    result=review.choose_source()
    assert destroyed==roots and len(roots)==1
    assert bool(calls)==(not selected)
    assert result==(tmp_path/'動画.mp4' if selected else tmp_path/'動画フォルダ' if folder else None)


def test_cli_cancel_does_not_create_output(monkeypatch,tmp_path):
    monkeypatch.setattr(review,'choose_source',lambda:None)
    monkeypatch.setattr(review,'create_sheets',lambda *a,**kw:pytest.fail('No writes after cancel'))
    monkeypatch.setattr('sys.argv',['reference_video_review','--output',str(tmp_path/'unused')])
    review.main();assert not (tmp_path/'unused').exists()


def test_unicode_video_stems_get_distinct_destinations(monkeypatch,tmp_path):
    calls=[]
    monkeypatch.setattr(review,'create_sheets',lambda source,dest:calls.append(dest) or dest/'ReferenceReview_contact_sheets.zip')
    for name in ('参照一.mp4','参照二.mp4'):
        monkeypatch.setattr('sys.argv',['reference_video_review',str(tmp_path/name)])
        review.main()
    assert calls[0]!=calls[1]
    assert calls==[tmp_path/'_AutoCineReferenceReview_参照一',tmp_path/'_AutoCineReferenceReview_参照二']


def test_selected_unicode_video_generates_real_sheets_without_mutation(monkeypatch,tmp_path):
    video=tmp_path/'参照 動画.mp4'
    subprocess.run([FFMPEG,'-y','-loglevel','error','-f','lavfi','-i','testsrc2=size=320x180:rate=60:duration=1',
                    '-c:v','libx264','-pix_fmt','yuv420p',str(video)],check=True,capture_output=True,timeout=30)
    original=video.read_bytes();monkeypatch.setattr(review,'choose_source',lambda:video)
    monkeypatch.setattr('sys.argv',['reference_video_review']);review.main()
    archive=tmp_path/'_AutoCineReferenceReview_参照 動画'/'ReferenceReview_contact_sheets.zip'
    with ZipFile(archive) as z:
        assert z.testzip() is None
        row=json.loads(z.read('reference_review.json'))['items'][0]
        assert row['original_name']==video.name and len(row['samples'])==6 and not row['errors']
        assert row['contact_sheet'] in z.namelist()
    assert video.read_bytes()==original


def test_reference_failure_log_included_as_bounded_original_bytes(tmp_path):
    origin=tmp_path/'diagnostics';origin.mkdir()
    data=b'REFERENCE FAILURE'+bytes(range(256))*5000
    source=origin/'reference_review_latest.log';source.write_bytes(data)
    report=qa_support.collect_qa_support(tmp_path/'QA',diagnostics=origin)
    assert 'QA_Support/reference_review_latest.log' in report['files']
    assert (tmp_path/'QA/QA_Support/reference_review_latest.log').read_bytes()==data[-qa_support.TAIL_LIMIT_BYTES:]
    assert source.read_bytes()==data
