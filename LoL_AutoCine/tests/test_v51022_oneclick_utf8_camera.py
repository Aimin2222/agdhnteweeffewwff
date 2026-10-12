# -*- coding: utf-8 -*-
"""Windows/LoL QA entry and per-camera isolation regression tests."""
from pathlib import Path
from types import SimpleNamespace
import pytest

from core.camera_tuning import shot_tuning
from tools.check_text_encoding import audit


def test_red2_red4_blue7_blue9_approved_camera_profiles_untouched():
    assert shot_tuning("RED", "third_cinema")["angles"] == {}
    assert shot_tuning("RED", "third_cinema")["distance"] == .96
    assert shot_tuning("RED", "lolnam_cinema")["distance"] == 1.0
    assert shot_tuning("RED", "lolnam_cinema")["angles"] == {"x": -3.0, "y": -3.0}
    assert shot_tuning("ORDER", "third_cinema")["angles"] == {}
    assert shot_tuning("ORDER", "lolnam_cinema")["distance"] == 1.08  # v5.10.23 BLUE retreat


def test_red1_and_fps_and_blue8_are_independent_tuning():
    assert shot_tuning("CHAOS", "third")["distance"] > 1.0
    assert shot_tuning("CHAOS", "fps")["fps_back"] > 1.4
    assert shot_tuning("ORDER", "fps")["fps_back"] > 1.1
    assert shot_tuning("CHAOS", "geo_aim")["distance"] > 1.0
    assert shot_tuning("ORDER", "fps")["angles"] == {}
    assert shot_tuning("ORDER", "geo_aim")["fps_back"] == 1.0


def test_bat_sources_only_have_ascii():
    root = Path(__file__).resolve().parents[1]
    for p in root.glob("*.bat"):
        assert p.read_bytes().isascii(), f"cmd.exe encoding risk: {p.name}"


def test_encoding_audit_detects_invalid_utf8_and_legacy_batch(tmp_path):
    script = tmp_path / "notes.txt"
    script.write_bytes(b"valid ascii")
    assert audit(tmp_path) == []
    script.write_bytes(b"\x82\xa0")
    assert any("UTF-8" in message for message in audit(tmp_path))
    script.unlink()
    bat = tmp_path / "RUN.bat"
    bat.write_text("echo 日本語", encoding="utf-8")
    assert any("ASCII-only" in message for message in audit(tmp_path))


def test_one_click_qa_scans_from_unconnected_state(monkeypatch):
    import tkinter as tk
    from legacy_app import App
    root = tk.Tk()
    try:
        app = App(root)
        sequence = []
        app.players = []
        app._match_scan_cache = None
        app.stop_ev.clear()
        def fake_connect():
            sequence.append("connect")
            app.players = [SimpleNamespace(team="ORDER")]
        def fake_scan(mode):
            sequence.append("scan:" + mode)
            app._match_scan_cache = SimpleNamespace(
                complete=True, events=[SimpleNamespace(time=22.0)])
        app._connect = fake_connect
        app._scan = fake_scan
        app._record_camera_qa = lambda *args: sequence.append("record")
        app._run_one_click_camera_qa(object(), Path("/tmp/qa"))
        assert sequence == ["connect", "scan:キル", "record"]
    finally:
        root.destroy()


def test_one_click_qa_reuses_existing_full_scan(monkeypatch):
    import tkinter as tk
    from legacy_app import App
    root = tk.Tk()
    try:
        app = App(root)
        app.players = [SimpleNamespace(team="ORDER")]
        app._match_scan_cache = SimpleNamespace(
            complete=True, events=[SimpleNamespace(time=22.0)])
        app._scan = lambda *a: pytest.fail("Do not rescan completed match")
        calls = []
        app._record_camera_qa = lambda *args: calls.append(args)
        app._run_one_click_camera_qa(object(), Path("/tmp/qa"))
        assert len(calls) == 1
    finally:
        root.destroy()


def test_one_click_no_players_fails_without_capture():
    import tkinter as tk
    from legacy_app import App
    root = tk.Tk()
    try:
        app=App(root)
        app.players = []
        app._match_scan_cache = None
        app.stop_ev.clear()
        app._connect = lambda: None
        app._record_camera_qa = lambda *args: pytest.fail("Do not record")
        with pytest.raises(RuntimeError, match="接続できません"):
            app._run_one_click_camera_qa(object(), Path("/tmp/qa"))
    finally:
        root.destroy()


def test_canceled_qa_never_starts_connect_or_capture():
    import tkinter as tk
    from legacy_app import App
    root=tk.Tk()
    try:
        app=App(root);app.players=[];app.stop_ev.set()
        app._connect=lambda:pytest.fail('No reconnect after cancel')
        app._record_camera_qa=lambda *a:pytest.fail('No capture after cancel')
        app._run_one_click_camera_qa(object(),Path('/tmp/qa'))
    finally:
        root.destroy()


def test_partial_scan_never_starts_recording():
    import tkinter as tk
    from legacy_app import App
    root=tk.Tk()
    try:
        app=App(root);app.players=[SimpleNamespace(team='ORDER')]
        app._match_scan_cache=None;app.stop_ev.clear()
        app._scan=lambda mode:setattr(app,'_match_scan_cache',SimpleNamespace(complete=False,events=[]))
        app._record_camera_qa=lambda *a:pytest.fail('No capture after partial scan')
        with pytest.raises(RuntimeError,match='完了しません'):
            app._run_one_click_camera_qa(object(),Path('/tmp/qa'))
    finally:
        root.destroy()


def test_invalid_template_snapshot_does_not_start_worker(monkeypatch):
    import tkinter as tk
    import legacy_app
    root=tk.Tk()
    try:
        app=legacy_app.App(root);errors=[]
        app.current_template=lambda:(_ for _ in ()).throw(ValueError('invalid color'))
        app._run_bg=lambda *a:pytest.fail('No worker after invalid snapshot')
        monkeypatch.setattr(legacy_app.messagebox,'showerror',lambda *a:errors.append(a))
        app.on_dev_camera_qa();assert errors
    finally:
        root.destroy()


def test_double_click_starts_only_one_background_sequence(monkeypatch,tmp_path):
    import tkinter as tk
    import threading,time
    from legacy_app import App
    from core.effects import Template
    root=tk.Tk();entered=threading.Event();release=threading.Event();finished=threading.Event()
    try:
        app=App(root);app.players=[];app._match_scan_cache=None
        owner=threading.get_ident();steps=[];snapshots=[]
        actual_snapshot=app.current_template
        def snapshot():
            assert threading.get_ident()==owner
            snapshots.append(owner);return actual_snapshot()
        app.current_template=snapshot
        def connect():
            assert threading.get_ident()!=owner
            steps.append('connect');entered.set();assert release.wait(3)
            app.players=[SimpleNamespace(team='ORDER')]
        def scan(mode):
            assert threading.get_ident()!=owner
            steps.append('scan');app._match_scan_cache=SimpleNamespace(complete=True,events=[SimpleNamespace(time=22)])
        def record(tpl,players,events,preferred,destination):
            assert threading.get_ident()!=owner and isinstance(tpl,Template)
            assert destination==tmp_path and players and events
            steps.append('record');finished.set()
        app.out_root=tmp_path;app._connect=connect;app._scan=scan;app._record_camera_qa=record
        monkeypatch.setattr(__import__('legacy_app').messagebox,'showinfo',lambda *a:None)
        app.on_dev_camera_qa();assert app.busy and entered.wait(3)
        app.on_dev_camera_qa();assert len(snapshots)==1
        release.set();assert finished.wait(3)
        for thread in threading.enumerate():
            if thread.name=='AutoCine-_run_one_click_camera_qa':thread.join(3);assert not thread.is_alive()
        assert steps==['connect','scan','record']
    finally:
        release.set();root.destroy()
