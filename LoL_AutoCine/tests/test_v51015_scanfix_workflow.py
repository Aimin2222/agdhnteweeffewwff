from types import SimpleNamespace
from pathlib import Path
import threading,queue
import pytest
import legacy_app
from core.effects import Template
from core.players import Player
from core.scanner import ScanResult
from core import camera,kill_icons


def bare():
    app=legacy_app.App.__new__(legacy_app.App)
    app.stop_ev=threading.Event();app.q=queue.Queue();app._replay_generation=1
    app.players=[];app.locked=None;app._match_scan_cache=None;app.logs=[];app.log=app.logs.append
    return app


def test_cold_scan_connects_in_worker_and_keeps_new_session(monkeypatch,tmp_path):
    app=bare();app.api=object();events=[]
    def connect():
        events.append('connect');app.players=[object()];app._replay_generation+=1
    app._connect=connect
    def scan(*a,**kw):
        events.append('scan');assert kw['event_mode']=='both';return ScanResult(0,[],10,True,[])
    monkeypatch.setattr(legacy_app,'scan_kills',scan)
    app._scan('キル');assert events==['connect','scan'];assert app._match_scan_cache.complete


def test_cold_scan_does_not_scan_after_connect_failure(monkeypatch):
    app=bare();app._connect=lambda:None
    monkeypatch.setattr(legacy_app,'scan_kills',lambda *a,**k:pytest.fail('must not scan'))
    app._scan('キル');assert app._match_scan_cache is None


def test_cached_scan_without_lock_does_not_reconnect():
    app=bare();app.busy=False;app._match_scan_cache=ScanResult(1,['sample'],10,True,[])
    app._fill_kills=lambda:None;app.on_scan();assert app.kills==['sample'];assert app.checked_kills=={0}


def test_camera_reset_targets_only_selected_player():
    before=dict(camera._TPS_CALIBRATION)
    try:
        camera._TPS_CALIBRATION.clear();camera._TPS_CALIBRATION.update({('Ahri','third_common'):{'a':1},('Lux','third_common'):{'a':2},('Ahri','fps'):{'a':3}})
        camera.clear_tps_calibration('Ahri');assert list(camera._TPS_CALIBRATION)==[('Lux','third_common')]
        camera.clear_tps_calibration();assert not camera._TPS_CALIBRATION
    finally:
        camera._TPS_CALIBRATION.clear();camera._TPS_CALIBRATION.update(before)


def dev_app(tmp_path):
    app=bare();app.api=object();app.out_root=tmp_path
    p=Player(0,'Blue','Blue#JP1','Ahri','Ahri','ORDER')
    return app,{'ORDER':(p,[object(),object()])}


def test_dev_bundle_stops_before_capture(tmp_path):
    app,chosen=dev_app(tmp_path);app.stop_ev.set();app._ensure_source=lambda:pytest.fail('capture after cancel')
    app._make_dev_test_bundle(Template(),chosen,None)


def test_dev_bundle_cancel_stops_remaining_cases_and_releases_source(monkeypatch,tmp_path):
    app,chosen=dev_app(tmp_path);stops=[];calls=[];app._ensure_source=lambda:(SimpleNamespace(stop=lambda:stops.append(True)),True)
    def run(*a,**kw):
        calls.append(a[5]);app.stop_ev.set();return SimpleNamespace(outputs=[],failed=[],montage=None)
    monkeypatch.setattr(legacy_app,'run_auto_edit',run)
    app._make_dev_test_bundle(Template(),chosen,None);assert len(calls)==1;assert stops==[True];assert any('中止' in x for x in app.logs)
    assert not any('一括作成完了' in x for x in app.logs)


def test_dev_bundle_failure_also_releases_owned_source(monkeypatch,tmp_path):
    app,chosen=dev_app(tmp_path);stops=[];app._ensure_source=lambda:(SimpleNamespace(stop=lambda:stops.append(True)),True)
    def fail(*a,**kw):raise RuntimeError('capture failure')
    monkeypatch.setattr(legacy_app,'run_auto_edit',fail)
    with pytest.raises(RuntimeError,match='capture failure'):app._make_dev_test_bundle(Template(),chosen,None)
    assert stops==[True]


def test_old_and_new_badge_labels_refer_to_same_ids():
    assert kill_icons.REVERSE_STYLES['追加素材 08']=='user_frame_08'
    assert kill_icons.REVERSE_STYLES['K/DA風・ローズクリスタル']=='user_frame_08'
    assert kill_icons.REVERSE_STYLES['ローズクリスタル']=='user_frame_08'
    assert kill_icons.REVERSE_STYLES['プレミアム・ゴールド（高発光）']=='premium_gold'
